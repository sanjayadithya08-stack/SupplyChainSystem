import os
import sys
import time
from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Config
from utils.text_preprocessing import combine_inputs
from ml.predict import predict_risk, batch_predict, PIPELINE
from ml.prevention_engine import generate_prevention_plan
from ml.model_monitor import log_prediction, get_stats
from services.news_service import fetch_headlines
from services.weather_service import fetch_weather
from services.geo_service import fetch_geo_events
from services.supplier_service import get_all_suppliers, get_alternates
from services.route_service import get_all_routes, get_alternate_routes
from services.alert_service import send_alert, get_recent_alerts, send_prevention_plan

from api.schemas import (
    PredictionResponse, CombinedInput, BatchInput, HealthResponse,
    FullAnalysisResponse, PreventionPlan, AlertRequest
)
from api.middleware import AntigravityMiddleware

START_TIME = time.time()

app = FastAPI(title="Supply Chain Disruption Prediction & Prevention System", version="2.0.0")
app.add_middleware(AntigravityMiddleware)

def _build_full_analysis(text: str, context: str = None) -> FullAnalysisResponse:
    pred = predict_risk(text)
    plan = generate_prevention_plan(pred)
    
    # Enrich plan with alternates
    if pred.get("affected_regions"):
        region = pred["affected_regions"][0]
        # Just grab the first alternate we find for demo
        alts = get_alternates("S001")
        if alts: plan["supplier_alternatives"] = [a.__dict__ for a in alts]
        
    log_prediction(pred, plan)
    
    # Auto-alert on critical
    if pred.get("label") == "CRITICAL":
        send_prevention_plan(plan, Config.ALERT_RECIPIENTS)
        
    return FullAnalysisResponse(
        prediction=PredictionResponse(**pred),
        plan=PreventionPlan(**plan),
        context=context
    )

@app.get("/", summary="Health check with system status")
async def root():
    return {"status": "online", "message": "Antigravity V2 Active"}

@app.get("/predict", response_model=PredictionResponse)
async def predict_text_only(text: str = Query(...)):
    """Predict only, no plan."""
    try:
        return predict_risk(text)
    except Exception as e:
        return PredictionResponse(label=Config.DEFAULT_RISK, confidence=0.0, disruption_type="normal", affected_regions=[], estimated_duration_days=0, error=str(e))

@app.get("/analyze", response_model=FullAnalysisResponse)
async def analyze_text(text: str = Query(...)):
    """Predict + full prevention plan."""
    try:
        return _build_full_analysis(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/combined", response_model=FullAnalysisResponse)
async def analyze_combined(payload: CombinedInput):
    try:
        combined_text = combine_inputs(payload.news, payload.weather, payload.geo)
        return _build_full_analysis(combined_text, context="Combined Signals")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze/live", response_model=FullAnalysisResponse)
async def analyze_live(region: str = Query(...)):
    try:
        news_items = fetch_headlines(query=region, max_results=5)
        news_str = ". ".join([n.headline for n in news_items])
        
        weather = fetch_weather(region)
        weather_str = f"{weather.condition}, Severity: {weather.severity}"
        
        geo_events = fetch_geo_events()
        geo_str = " ".join([e.description for e in geo_events if e.country.lower() in region.lower() or region == "global"])
            
        combined_text = combine_inputs(news_str, weather_str, geo_str)
        context_str = f"Sources Used: News({len(news_items)}), Weather({weather.condition}), Geo({len(geo_events)})"
        
        return _build_full_analysis(combined_text, context=context_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/batch")
async def analyze_batch(payload: BatchInput):
    try:
        results = []
        for text in payload.texts:
            results.append(_build_full_analysis(text))
        return {"results": results}
    except Exception as e:
        return {"error": str(e), "results": []}

# ── Company-Specific Endpoints ─────────────────────────────────────────────────
@app.post("/company/predict")
async def company_predict_event(event: dict):
    """Predict disruption for a structured company supply chain event."""
    try:
        from ml.company_predict import predict_event
        return predict_event(event)
    except Exception as e:
        return {"label": "UNKNOWN", "error": str(e)}

@app.get("/company/history")
async def company_history():
    """Return all historical events with model predictions."""
    try:
        from ml.company_predict import predict_all_historical
        return predict_all_historical()
    except Exception as e:
        return []

@app.get("/company/dataset")
async def company_dataset():
    """Return raw company dataset as JSON."""
    try:
        import pandas as pd
        from utils.config import Config
        df = pd.read_csv(Config.DATA_DIR + "/company_dataset.csv")
        return df.to_dict(orient="records")
    except Exception as e:
        return []

@app.get("/company/stats")
async def company_stats():
    """Return aggregated stats from company dataset."""
    try:
        import pandas as pd
        from utils.config import Config
        df = pd.read_csv(Config.DATA_DIR + "/company_dataset.csv")
        return {
            "total_events": int(len(df)),
            "total_revenue_at_risk": int(df["revenue_at_risk_usd"].sum()),
            "total_units_affected": int(df["affected_units"].sum()),
            "avg_delay_days": round(float(df[df["delay_days"] > 0]["delay_days"].mean()), 1),
            "by_label": df["label"].value_counts().to_dict(),
            "by_disruption_type": df["disruption_type"].value_counts().to_dict(),
            "by_supplier": df.groupby("supplier_name")["revenue_at_risk_usd"].sum().sort_values(ascending=False).head(5).to_dict(),
            "by_region": df.groupby("region")["revenue_at_risk_usd"].sum().sort_values(ascending=False).to_dict(),
            "worst_events": df.nlargest(5, "revenue_at_risk_usd")[["event_id","date","supplier_name","disruption_type","revenue_at_risk_usd","label"]].to_dict(orient="records"),
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/news")
async def get_live_news(region: str = Query("global")):
    try:
        from services.news_service import fetch_by_region
        return fetch_by_region(region)
    except Exception as e:
        return []

@app.get("/weather")
async def get_live_weather(region: str = Query("global")):
    try:
        from services.weather_service import fetch_weather
        w = fetch_weather(region)
        return {"region": region, "condition": w.condition, "severity": w.severity, "alerts": w.alerts}
    except Exception as e:
        return {}

@app.get("/geo")
async def get_live_geo():
    try:
        from services.geo_service import fetch_geo_events
        return fetch_geo_events()
    except Exception as e:
        return []

@app.get("/suppliers")
async def list_suppliers():
    try:
        return get_all_suppliers()
    except Exception as e:
        return []

@app.get("/routes")
async def list_routes():
    try:
        return get_all_routes()
    except Exception as e:
        return []

@app.get("/alerts")
async def list_alerts():
    try:
        return get_recent_alerts(20)
    except Exception as e:
        return []

@app.post("/alerts/send")
async def trigger_alert(payload: AlertRequest, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(send_alert, payload.level, payload.message, Config.ALERT_RECIPIENTS)
        return {"status": "Alert queued"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/monitor/stats")
async def monitor_stats():
    try:
        return get_stats()
    except Exception as e:
        return {"error": "Could not fetch stats"}

@app.get("/monitor/health", response_model=HealthResponse)
async def monitor_health():
    try:
        uptime = time.time() - START_TIME
        artefacts_status = {
            "model.pkl": os.path.exists(Config.MODEL_PATH),
            "pipeline.pkl": os.path.exists(Config.PIPELINE_PATH),
            "dataset.csv": os.path.exists(Config.DATASET_PATH)
        }
        status = "healthy" if PIPELINE is not None else "degraded"
        return HealthResponse(
            status=status, model_loaded=PIPELINE is not None,
            uptime_seconds=round(uptime, 2), artefacts=artefacts_status
        )
    except Exception as e:
        return HealthResponse(status="error", model_loaded=False, uptime_seconds=0.0, artefacts={})