import streamlit as st
import requests
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Config
from ui.components import (
    render_risk_card, render_prevention_plan, render_confidence_bar, 
    render_route_map, render_supplier_table, render_alert_banner,
    load_premium_css
)

st.set_page_config(page_title="Supply Chain Predict & Prevent", page_icon="🚢", layout="wide")
load_premium_css()

_api_host = "127.0.0.1" if Config.API_HOST == "0.0.0.0" else Config.API_HOST
API_BASE_URL = f"http://{_api_host}:{Config.API_PORT}"

def check_api_health():
    try:
        response = requests.get(f"{API_BASE_URL}/monitor/health", timeout=2)
        if response.status_code == 200: return response.json()
    except Exception: pass
    return None

health = check_api_health()
if not health:
    st.error(f"⚠️ API unreachable at {API_BASE_URL}. Antigravity mode engaged (UI active but API down).")
elif health.get("status") != "healthy":
    st.warning("⚠️ API degraded (Model missing). Predictions will fallback to UNKNOWN.")

st.title("🚢 Supply Chain Disruption Predictor & Preventer")
st.markdown("Antigravity V2: *Predict risk AND generate actionable prevention plans.*")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📝 Live Analysis", "🧩 Combined Signals", "📡 Live Feed", 
    "📚 Batch Analysis", "🗺️ Supply Chain Map", "📊 Monitor & Alerts"
])

# --- TAB 1: Live Analysis ---
with tab1:
    st.header("Single Scenario Analysis")
    
    c_live, c_manual = st.columns(2)
    
    with c_live:
        st.subheader("📡 Select from Live News")
        try:
            news_items = requests.get(f"{API_BASE_URL}/news", params={"region": "global"}).json()
            if news_items:
                news_options = {f"{n['headline']} ({n['source']})": n['headline'] for n in news_items}
                selected_news_title = st.selectbox("Live Headlines:", list(news_options.keys()))
                selected_news_text = news_options[selected_news_title]
            else:
                selected_news_text = ""
                st.info("No live news available.")
        except Exception:
            selected_news_text = ""
            st.error("Failed to fetch news.")
            
    with c_manual:
        st.subheader("✍️ Or Enter Manually")
        text_input = st.text_area("Custom event description:", value=selected_news_text, height=100)
    
    if st.button("Predict & Prevent", type="primary"):
        with st.spinner("Analyzing..."):
            try:
                res = requests.get(f"{API_BASE_URL}/analyze", params={"text": text_input}).json()
                if "error" in res and res["error"]:
                    st.error(f"API Error: {res['error']}")
                else:
                    c1, c2 = st.columns([1, 1.5])
                    with c1:
                        render_risk_card(res["prediction"])
                        render_confidence_bar(res["prediction"]["confidence"])
                    with c2:
                        render_prevention_plan(res["plan"])
            except Exception as e:
                st.error("Failed to connect to API.")

# --- TAB 2: Combined Signals ---
with tab2:
    st.header("Multi-Signal Synthesis")
    
    col_sel, col_in = st.columns(2)
    with col_sel:
        st.subheader("📡 Live Signal Selectors")
        try:
            news_items = requests.get(f"{API_BASE_URL}/news", params={"region": "global"}).json()
            n_opts = {f"{n['headline']}": n['headline'] for n in news_items} if news_items else {}
            sel_n = st.selectbox("News Headline", ["None"] + list(n_opts.keys()))
            txt_n = n_opts[sel_n] if sel_n != "None" else ""
            
            w_opts = Config.REGIONS
            sel_w = st.selectbox("Weather Region", ["None"] + w_opts)
            txt_w = ""
            if sel_w != "None":
                w = requests.get(f"{API_BASE_URL}/weather", params={"region": sel_w}).json()
                if w and "condition" in w: txt_w = f"{w['condition']} in {w['region']} (Severity: {w['severity']})"
                
            geo_items = requests.get(f"{API_BASE_URL}/geo").json()
            g_opts = {f"{g['event_type']} in {g['country']}": g['description'] for g in geo_items} if geo_items else {}
            sel_g = st.selectbox("Geo Event", ["None"] + list(g_opts.keys()))
            txt_g = g_opts[sel_g] if sel_g != "None" else ""
        except Exception:
            txt_n, txt_w, txt_g = "", "", ""
            st.error("Failed to fetch signals.")
            
    with col_in:
        st.subheader("✍️ Signal Inputs")
        news_in = st.text_area("News Headline", value=txt_n)
        weather_in = st.text_area("Weather", value=txt_w)
        geo_in = st.text_area("Geo Event", value=txt_g)
        
    if st.button("Synthesize & Analyze", type="primary"):
        with st.spinner("Processing..."):
            try:
                res = requests.post(f"{API_BASE_URL}/analyze/combined", json={"news": news_in, "weather": weather_in, "geo": geo_in}).json()
                col1, col2 = st.columns([1, 1.5])
                with col1:
                    st.markdown(f"**Context Used:**\n> {res.get('context')}")
                    render_risk_card(res["prediction"])
                with col2:
                    render_prevention_plan(res["plan"])
            except Exception as e:
                st.error("Failed to connect to API.")

# --- TAB 3: Live Feed ---
with tab3:
    st.header("Live Global Intelligence Feed")
    region = st.selectbox("Monitor Region", Config.REGIONS)
    if st.button("Fetch Live Signals & Analyze"):
        with st.spinner(f"Scanning {region}..."):
            try:
                res = requests.get(f"{API_BASE_URL}/analyze/live", params={"region": region}).json()
                st.info(f"Sources: {res.get('context')}")
                
                col1, col2 = st.columns([1, 1.5])
                with col1: render_risk_card(res["prediction"])
                with col2: render_prevention_plan(res["plan"])
                
                if st.button("Trigger Emergency Alert to Ops", type="secondary"):
                    alert_res = requests.post(f"{API_BASE_URL}/alerts/send", json={"level": "CRITICAL", "message": f"Manual trigger for {region}"})
                    st.success("Alert sent!")
            except Exception as e:
                st.error("Failed to fetch live data.")

# --- TAB 4: Batch Analysis ---
with tab4:
    st.header("Batch Analysis")
    
    if "batch_input" not in st.session_state:
        st.session_state["batch_input"] = "Major cyber attack hits Maersk\\nCategory 4 hurricane forming in the Atlantic\\nTruck driver shortage worsens in UK"
        
    def load_news_batch():
        try:
            news = requests.get(f"{API_BASE_URL}/news", params={"region": "global"}).json()
            if news: st.session_state["batch_input"] = "\\n".join([n['headline'] for n in news])
        except: pass
        
    def load_geo_batch():
        try:
            geo = requests.get(f"{API_BASE_URL}/geo").json()
            if geo: st.session_state["batch_input"] = "\\n".join([g['description'] for g in geo])
        except: pass
        
    col_btn, col_text = st.columns([1, 4])
    with col_btn:
        st.markdown("**Auto-fill options:**")
        st.button("📰 Load All Live News", on_click=load_news_batch, use_container_width=True)
        st.button("🌍 Load All Geo Events", on_click=load_geo_batch, use_container_width=True)
        
    with col_text:
        batch_text = st.text_area("Enter scenarios (one per line):", value=st.session_state["batch_input"], height=150)
        
    if st.button("Process Batch", type="primary"):
        lines = [l.strip() for l in batch_text.split("\n") if l.strip()]
        if lines:
            with st.spinner(f"Processing {len(lines)}..."):
                try:
                    res = requests.post(f"{API_BASE_URL}/analyze/batch", json={"texts": lines}).json()
                    df_data = []
                    for line, r in zip(lines, res.get("results", [])):
                        pred = r["prediction"]
                        plan = r["plan"]
                        df_data.append({
                            "Scenario": line,
                            "Risk": pred["label"],
                            "Type": pred["disruption_type"],
                            "Top Action": plan["immediate_actions"][0] if plan["immediate_actions"] else "None",
                            "Cost": plan["estimated_cost_impact"]
                        })
                    st.dataframe(pd.DataFrame(df_data), use_container_width=True)
                except Exception as e:
                    st.error("Failed to process batch.")

# --- TAB 5: Supply Chain Map ---
with tab5:
    st.header("Global Supply Chain Status")
    try:
        st.subheader("Suppliers & Risk Scores")
        suppliers = requests.get(f"{API_BASE_URL}/suppliers").json()
        render_supplier_table(suppliers)
        
        st.subheader("Trade Routes")
        routes = requests.get(f"{API_BASE_URL}/routes").json()
        render_route_map(routes)
    except Exception as e:
        st.error("Failed to fetch supply chain map data.")

# --- TAB 6: Monitor & Alerts ---
with tab6:
    st.header("System Monitor & Command Center")
    if st.button("Refresh Monitor Dashboard"): st.rerun()
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("System Health")
        if health:
            st.json(health)
        else:
            st.error("API OFFLINE")
        
        st.subheader("Prediction Stats")
        try:
            stats = requests.get(f"{API_BASE_URL}/monitor/stats").json()
            st.json(stats)
        except: pass
        
    with c2:
        st.subheader("Recent Alerts")
        try:
            alerts = requests.get(f"{API_BASE_URL}/alerts").json()
            if alerts:
                for a in alerts:
                    render_alert_banner(a["level"], f"{a['timestamp']} - {a['message']}")
            else:
                st.info("No recent alerts.")
        except: pass
        
        st.subheader("Manual Override Alert")
        with st.form("alert_form"):
            lvl = st.selectbox("Level", ["INFO", "WARNING", "CRITICAL", "EMERGENCY"])
            msg = st.text_input("Message")
            if st.form_submit_button("Broadcast"):
                requests.post(f"{API_BASE_URL}/alerts/send", json={"level": lvl, "message": msg})
                st.success("Broadcast sent!")