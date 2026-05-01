import streamlit as st
import requests
import sys, os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Config
from ui.components import (
    THEME, load_premium_css, section_header, stat_card,
    render_risk_card, render_prevention_plan, render_confidence_bar,
    render_route_map, render_supplier_table, render_alert_card,
    render_health_badge, render_donut_chart
)

st.set_page_config(
    page_title="SupplyChain AI — Command Center",
    page_icon="🚢", layout="wide",
    initial_sidebar_state="collapsed"
)
load_premium_css()

_host = "127.0.0.1" if Config.API_HOST == "0.0.0.0" else Config.API_HOST
API = f"http://{_host}:{Config.API_PORT}"

# ── Header ─────────────────────────────────────────────────────────────────────
def api_get(path, params=None, timeout=4):
    try:
        r = requests.get(f"{API}{path}", params=params, timeout=timeout)
        return r.json() if r.status_code == 200 else None
    except: return None

def api_post(path, json=None, timeout=8):
    try:
        r = requests.post(f"{API}{path}", json=json, timeout=timeout)
        return r.json() if r.status_code == 200 else None
    except: return None

health = api_get("/monitor/health")

# ── Topbar ─────────────────────────────────────────────────────────────────────
col_logo, col_status = st.columns([3, 1])
with col_logo:
    st.markdown(f"""
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:4px;">
            <span style="font-size:2.2rem;">🚢</span>
            <div>
                <h1 style="margin:0;background:linear-gradient(90deg,{THEME['cyan']},{THEME['blue']});
                           -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                           font-size:1.7rem;font-weight:800;">SupplyChain AI</h1>
                <p style="margin:0;color:{THEME['muted']};font-size:0.8rem;">
                    Antigravity V2 · Predictive &amp; Preventive Intelligence Platform
                </p>
            </div>
        </div>""", unsafe_allow_html=True)
with col_status:
    if health:
        status = health.get("status", "unknown")
        uptime = round(health.get("uptime_seconds", 0) / 60, 1)
        c = THEME["green"] if status == "healthy" else THEME["amber"]
        st.markdown(f"""
            <div style="text-align:right;margin-top:6px;">
                <div style="color:{c};font-weight:700;font-size:0.85rem;">● {status.upper()}</div>
                <div style="color:{THEME['muted']};font-size:0.72rem;">API · {uptime}m uptime</div>
                <div style="color:{THEME['muted']};font-size:0.72rem;">Model: {'✅' if health.get('model_loaded') else '❌'}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align:right;color:{THEME['red']};font-weight:700;font-size:0.85rem;margin-top:10px;'>● API OFFLINE</div>", unsafe_allow_html=True)

st.markdown(f"<hr style='border-color:{THEME['border']};margin:0.6rem 0 1rem;'>", unsafe_allow_html=True)

if not health:
    st.error("⚠️ API unreachable. Antigravity mode — UI stays active.")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📝 Analyze", "🧩 Multi-Signal", "📡 Live Radar",
    "📚 Batch", "🗺️ Network Map", "📊 Monitor"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Single Analysis
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    section_header("Single Scenario Analysis", "Select a live headline or type any custom event")
    c_pick, c_input = st.columns([1, 1], gap="large")

    with c_pick:
        st.markdown(f"<div style='color:{THEME['cyan']};font-weight:700;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;'>📡 Live Headlines</div>", unsafe_allow_html=True)
        try:
            news = api_get("/news", {"region": "global"}) or []
            if news:
                opts = {f"{n['headline']}  ({n['source']})": n["headline"] for n in news}
                sel = st.selectbox("Choose a headline:", list(opts.keys()), label_visibility="collapsed")
                sel_text = opts[sel]
                sev = next((n["severity_hint"] for n in news if n["headline"] == sel_text), "")
                c = get_risk_color if False else {"HIGH": THEME["amber"], "CRITICAL": THEME["red"]}.get(sev, THEME["muted"])
                if sev:
                    st.markdown(f"<span style='color:{c};font-size:0.78rem;font-weight:600;'>Severity Hint: {sev}</span>", unsafe_allow_html=True)
            else:
                sel_text = ""
                st.info("No live news available.")
        except:
            sel_text = ""
            st.error("Failed to fetch news.")

    with c_input:
        st.markdown(f"<div style='color:{THEME['cyan']};font-weight:700;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;'>✍️ Or Type Manually</div>", unsafe_allow_html=True)
        text_input = st.text_area("Event description:", value=sel_text, height=110, label_visibility="collapsed", placeholder="Describe the disruption event…")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔍 Analyze & Generate Prevention Plan", type="primary"):
        if not text_input.strip():
            st.warning("Please enter an event description.")
        else:
            with st.spinner("Running AI analysis…"):
                res = api_get("/analyze", {"text": text_input})
            if not res:
                st.error("API call failed.")
            else:
                r1, r2 = st.columns([1, 1.4], gap="large")
                with r1:
                    render_risk_card(res["prediction"])
                    render_confidence_bar(res["prediction"]["confidence"])
                with r2:
                    render_prevention_plan(res["plan"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Multi-Signal
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    section_header("Multi-Signal Synthesis", "Combine News + Weather + Geopolitical data for compound risk scoring")
    c_sel, c_in = st.columns([1, 1], gap="large")

    txt_n = txt_w = txt_g = ""
    with c_sel:
        st.markdown(f"<div style='color:{THEME['cyan']};font-weight:700;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;'>📡 Live Signal Selectors</div>", unsafe_allow_html=True)
        try:
            news = api_get("/news", {"region": "global"}) or []
            n_opts = {n["headline"]: n["headline"] for n in news}
            sel_n = st.selectbox("📰 News", ["— None —"] + list(n_opts.keys()))
            txt_n = n_opts[sel_n] if sel_n != "— None —" else ""

            sel_w = st.selectbox("🌦️ Weather Region", ["— None —"] + Config.REGIONS)
            if sel_w != "— None —":
                w = api_get("/weather", {"region": sel_w}) or {}
                if w.get("condition"):
                    txt_w = f"{w['condition']} in {w['region']} (Severity: {w['severity']})"
                    st.caption(f"Alerts: {', '.join(w.get('alerts', [])) or 'None'}")

            geo = api_get("/geo") or []
            g_opts = {f"{g['event_type']} in {g['country']}": g["description"] for g in geo}
            sel_g = st.selectbox("🌍 Geo Event", ["— None —"] + list(g_opts.keys()))
            txt_g = g_opts[sel_g] if sel_g != "— None —" else ""
        except Exception as e:
            st.error(f"Failed to fetch signals: {e}")

    with c_in:
        st.markdown(f"<div style='color:{THEME['cyan']};font-weight:700;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;'>✍️ Signal Inputs</div>", unsafe_allow_html=True)
        news_in    = st.text_area("News", value=txt_n, height=70)
        weather_in = st.text_area("Weather", value=txt_w, height=70)
        geo_in     = st.text_area("Geo Event", value=txt_g, height=70)

    if st.button("⚡ Synthesize & Analyze", type="primary"):
        with st.spinner("Synthesizing signals…"):
            res = api_post("/analyze/combined", {"news": news_in, "weather": weather_in, "geo": geo_in})
        if not res:
            st.error("Synthesis failed.")
        else:
            st.info(f"Context: {res.get('context', 'Combined')}")
            r1, r2 = st.columns([1, 1.4], gap="large")
            with r1:
                render_risk_card(res["prediction"])
                render_confidence_bar(res["prediction"]["confidence"])
            with r2:
                render_prevention_plan(res["plan"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Live Radar
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    section_header("Live Global Radar", "Scan all signals for a region and generate an automated threat report")
    region = st.selectbox("🌐 Target Region", Config.REGIONS)
    if st.button("📡 Scan & Analyze Region", type="primary"):
        with st.spinner(f"Scanning {region}…"):
            res = api_get("/analyze/live", {"region": region})
        if not res:
            st.error("Scan failed.")
        else:
            st.info(f"Sources: {res.get('context', '')}")
            r1, r2 = st.columns([1, 1.4], gap="large")
            with r1:
                render_risk_card(res["prediction"])
                render_confidence_bar(res["prediction"]["confidence"])
            with r2:
                render_prevention_plan(res["plan"])
            st.markdown("---")
            if st.button("🚨 Broadcast Emergency Alert to Ops"):
                api_post("/alerts/send", {"level": "CRITICAL", "message": f"Manual scan alert for {region}"})
                st.success("Emergency alert dispatched!")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Batch Analysis
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    section_header("Batch Analysis", "Process dozens of events simultaneously and get a color-coded risk table")

    if "batch_input" not in st.session_state:
        st.session_state["batch_input"] = "Major cyber attack hits Maersk\nCategory 4 hurricane forming in the Atlantic\nTruck driver shortage worsens in UK\nSuez canal blocked by grounded vessel\nMicrochip supplier halts production in Taiwan"

    def _load_news_batch():
        news = api_get("/news", {"region": "global"}) or []
        if news: st.session_state["batch_input"] = "\n".join(n["headline"] for n in news)

    def _load_geo_batch():
        geo = api_get("/geo") or []
        if geo: st.session_state["batch_input"] = "\n".join(g["description"] for g in geo)

    cb1, cb2, cb_text = st.columns([1, 1, 4], gap="medium")
    with cb1: st.button("📰 Load Live News", on_click=_load_news_batch, use_container_width=True)
    with cb2: st.button("🌍 Load Geo Events", on_click=_load_geo_batch, use_container_width=True)
    with cb_text:
        batch_text = st.text_area("Scenarios (one per line):", value=st.session_state["batch_input"], height=140, label_visibility="collapsed")

    if st.button("⚙️ Process Batch", type="primary"):
        lines = [l.strip() for l in batch_text.split("\n") if l.strip()]
        if not lines:
            st.warning("No scenarios entered.")
        else:
            with st.spinner(f"Processing {len(lines)} scenarios…"):
                res = api_post("/analyze/batch", {"texts": lines})
            if not res or "results" not in res:
                st.error("Batch failed.")
            else:
                rows = []
                for line, r in zip(lines, res["results"]):
                    pred = r["prediction"]
                    plan = r["plan"]
                    rows.append({
                        "Scenario": line, "Risk": pred["label"],
                        "Type": pred["disruption_type"].replace("_", " ").title(),
                        "Regions": ", ".join(pred["affected_regions"]),
                        "Duration(d)": pred["estimated_duration_days"],
                        "Top Action": (plan["immediate_actions"] or ["—"])[0],
                        "Priority": plan["priority"],
                        "Cost Impact": plan["estimated_cost_impact"],
                    })
                df = pd.DataFrame(rows)
                def style_risk(val):
                    c = get_risk_color(str(val))
                    return f"background:{c}25;color:{c};font-weight:700;"
                def style_prio(val):
                    c = {"P1": THEME["red"], "P2": THEME["amber"], "P3": THEME["green"]}.get(val, THEME["muted"])
                    return f"color:{c};font-weight:700;"
                st.dataframe(
                    df.style.map(style_risk, subset=["Risk"]).map(style_prio, subset=["Priority"]),
                    use_container_width=True, height=380
                )
                total = len(rows)
                crits = sum(1 for r in rows if r["Risk"] == "CRITICAL")
                highs = sum(1 for r in rows if r["Risk"] == "HIGH")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Scenarios", total)
                m2.metric("🔴 Critical", crits)
                m3.metric("🟠 High", highs)
                m4.metric("✅ Low/Medium", total - crits - highs)

def get_risk_color(risk):
    from ui.components import RISK_COLORS, THEME
    return RISK_COLORS.get(risk.upper(), THEME["muted"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Network Map
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    section_header("Global Supply Chain Network", "Live supplier risk scores and trade route status")
    sup_tab, route_tab = st.tabs(["🏭 Suppliers", "🛳️ Trade Routes"])
    with sup_tab:
        suppliers = api_get("/suppliers") or []
        if suppliers:
            high_risk = sum(1 for s in suppliers if s.get("risk_score", 0) >= 0.7)
            med_risk  = sum(1 for s in suppliers if 0.4 <= s.get("risk_score", 0) < 0.7)
            sm1, sm2, sm3 = st.columns(3)
            sm1.metric("Total Suppliers", len(suppliers))
            sm2.metric("🔴 High Risk", high_risk)
            sm3.metric("🟡 Medium Risk", med_risk)
        render_supplier_table(suppliers)
    with route_tab:
        routes = api_get("/routes") or []
        if routes:
            critical = sum(1 for r in routes if r.get("risk_level") == "CRITICAL")
            rm1, rm2 = st.columns(2)
            rm1.metric("Total Routes", len(routes))
            rm2.metric("🔴 Critical Routes", critical)
        render_route_map(routes)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — Monitor (Redesigned)
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    section_header("System Monitor & Command Center", "Real-time health, prediction stats, and alert history")

    col_refresh = st.columns([1, 5])[0]
    with col_refresh:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    # ── Row 1: Health cards ─────────────────────────────────────────────────
    st.markdown(f"<div style='color:{THEME['cyan']};font-weight:700;font-size:0.82rem;text-transform:uppercase;letter-spacing:0.08em;margin:16px 0 10px;'>System Health</div>", unsafe_allow_html=True)
    if health:
        h1, h2, h3, h4 = st.columns(4)
        status = health.get("status", "unknown")
        uptime_m = round(health.get("uptime_seconds", 0) / 60, 1)
        arts = health.get("artefacts", {})
        with h1: stat_card("API Status", status.upper(), "🟢" if status == "healthy" else "🔴", THEME["green"] if status == "healthy" else THEME["red"])
        with h2: stat_card("Uptime", f"{uptime_m}m", "⏱️", THEME["cyan"])
        with h3: stat_card("Model", "Loaded" if health.get("model_loaded") else "Missing", "🤖", THEME["green"] if health.get("model_loaded") else THEME["red"])
        with h4: stat_card("Artefacts", f"{sum(arts.values())}/{len(arts)}", "📦", THEME["purple"])

        st.markdown(f"<div style='color:{THEME['muted']};font-size:0.78rem;margin-bottom:16px;'>Version: {health.get('version','—')} &nbsp;|&nbsp; Artefacts: {', '.join(f'{k}: {\"✅\" if v else \"❌\"}' for k,v in arts.items())}</div>", unsafe_allow_html=True)
    else:
        st.error("API is OFFLINE — cannot fetch health data.")

    # ── Row 2: Prediction Stats + Donut ─────────────────────────────────────
    st.markdown(f"<div style='color:{THEME['cyan']};font-weight:700;font-size:0.82rem;text-transform:uppercase;letter-spacing:0.08em;margin:8px 0 10px;'>Prediction Statistics</div>", unsafe_allow_html=True)
    stats = api_get("/monitor/stats") or {}
    s1, s2 = st.columns([1.5, 1], gap="large")
    with s1:
        if stats and stats.get("total", 0) > 0:
            ps1, ps2, ps3, ps4, ps5 = st.columns(5)
            ps1.metric("Total", stats.get("total", 0))
            ps2.metric("🔴 Critical", stats.get("CRITICAL", 0))
            ps3.metric("🟠 High", stats.get("HIGH", 0))
            ps4.metric("🟡 Medium", stats.get("MEDIUM", 0))
            ps5.metric("🟢 Low", stats.get("LOW", 0))
            dis = stats.get("disruptions", {})
            if dis:
                st.markdown(f"<div style='color:{THEME['muted']};font-size:0.8rem;margin-top:10px;font-weight:600;'>Top Disruption Types:</div>", unsafe_allow_html=True)
                sorted_dis = sorted(dis.items(), key=lambda x: x[1], reverse=True)[:5]
                for dtype, count in sorted_dis:
                    pct = int(count / max(stats.get("total", 1), 1) * 100)
                    label = dtype.replace("_"," ").title()
                    st.markdown(f"""
                        <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                            <div style="width:100px;color:{THEME['text']};font-size:0.82rem;">{label}</div>
                            <div style="flex:1;background:{THEME['border']};border-radius:4px;height:7px;">
                                <div style="background:{THEME['cyan']};width:{pct}%;height:7px;border-radius:4px;"></div>
                            </div>
                            <div style="color:{THEME['muted']};font-size:0.78rem;width:30px;">{count}</div>
                        </div>""", unsafe_allow_html=True)
        else:
            st.caption("No predictions logged yet. Run an analysis first.")
    with s2:
        render_donut_chart(stats)

    # ── Row 3: Alert history ─────────────────────────────────────────────────
    st.markdown(f"<div style='color:{THEME['cyan']};font-weight:700;font-size:0.82rem;text-transform:uppercase;letter-spacing:0.08em;margin:16px 0 10px;'>Recent Alerts</div>", unsafe_allow_html=True)
    al1, al2 = st.columns([2, 1], gap="large")
    with al1:
        alerts = api_get("/alerts") or []
        if alerts:
            for a in alerts[:8]:
                render_alert_card(a.get("level","INFO"), a.get("message",""), a.get("timestamp",""), a.get("channel","log"))
        else:
            st.markdown(f"<p style='color:{THEME['muted']};font-style:italic;'>No alerts logged yet.</p>", unsafe_allow_html=True)
    with al2:
        st.markdown(f"<div style='color:{THEME['text']};font-weight:600;font-size:0.88rem;margin-bottom:12px;'>📣 Broadcast Alert</div>", unsafe_allow_html=True)
        with st.form("alert_form", clear_on_submit=True):
            lvl = st.selectbox("Level", ["INFO", "WARNING", "CRITICAL", "EMERGENCY"])
            msg = st.text_area("Message", height=90, placeholder="Describe the situation…")
            if st.form_submit_button("📡 Broadcast", use_container_width=True):
                if msg.strip():
                    api_post("/alerts/send", {"level": lvl, "message": msg})
                    st.success("Broadcast dispatched!")
                else:
                    st.warning("Enter a message first.")

        st.markdown(f"<div style='color:{THEME['muted']};font-size:0.75rem;margin-top:12px;'>Channels active: {'✅ Slack' if Config.SLACK_WEBHOOK_URL and 'hooks' in Config.SLACK_WEBHOOK_URL else '❌ Slack'} &nbsp; {'✅ Email' if Config.SMTP_USER else '❌ Email'} &nbsp; ✅ Log</div>", unsafe_allow_html=True)