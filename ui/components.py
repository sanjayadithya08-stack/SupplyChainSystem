import streamlit as st
import pandas as pd

def load_premium_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
        }
        
        /* Highly Visible Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #0061ff 0%, #60efff 100%);
            color: white !important;
            border: 2px solid #0050d5 !important;
            border-radius: 12px;
            padding: 0.8rem 1.5rem;
            font-size: 1.2rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            box-shadow: 0 6px 15px rgba(0, 97, 255, 0.4);
            width: 100%;
        }
        .stButton > button p {
            color: white !important;
            font-size: 1.1rem !important;
            font-weight: 800 !important;
        }
        .stButton > button:hover {
            transform: translateY(-4px) scale(1.02);
            box-shadow: 0 10px 25px rgba(0, 97, 255, 0.6);
            background: linear-gradient(135deg, #60efff 0%, #0061ff 100%);
            border-color: #60efff !important;
        }
        .stButton > button:active {
            transform: translateY(2px) scale(0.98);
        }
        
        /* Premium Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
        }
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            white-space: pre-wrap;
            background-color: var(--secondary-background-color);
            border-radius: 6px 6px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
            padding-left: 15px;
            padding-right: 15px;
            color: var(--text-color);
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background-color: var(--background-color);
            border-bottom: 3px solid #0061ff;
            color: var(--text-color);
            font-weight: 700;
        }
        
        /* Inputs and Text Areas */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            border-radius: 8px;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }
        .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
            border-color: #0061ff;
            box-shadow: 0 0 0 0.2rem rgba(0, 97, 255, 0.25);
        }
        
        /* General styling */
        h1, h2, h3 {
            font-weight: 700;
        }
        </style>
    """, unsafe_allow_html=True)

def get_risk_color(risk: str) -> str:
    colors = {
        "LOW": "#28a745", "MEDIUM": "#ffc107", 
        "HIGH": "#fd7e14", "CRITICAL": "#dc3545", "UNKNOWN": "#6c757d"
    }
    return colors.get(risk.upper(), colors["UNKNOWN"])

def render_risk_card(prediction: dict):
    try:
        risk = prediction.get("label", "UNKNOWN")
        color = get_risk_color(risk)
        st.markdown(
            f"""
            <div style="padding: 20px; border-radius: 10px; background-color: {color}15; border: 2px solid {color}; margin-bottom: 15px;">
                <h3 style="color: {color}; margin-top: 0; margin-bottom: 5px;">Risk Level: {risk.upper()}</h3>
                <p style="margin:0;"><strong>Type:</strong> {prediction.get('disruption_type', 'Unknown')} | 
                <strong>Regions:</strong> {", ".join(prediction.get('affected_regions', []))} |
                <strong>Duration:</strong> {prediction.get('estimated_duration_days', 0)} days</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"Error rendering risk card: {e}")

def render_action_checklist(actions: list, title: str):
    if not actions: return
    st.markdown(f"**{title}**")
    for act in actions:
        st.checkbox(act, key=f"chk_{act}")

def render_prevention_plan(plan: dict):
    try:
        st.subheader("🛡️ Prevention Action Plan")
        
        priority = plan.get("priority", "P3")
        cost = plan.get("estimated_cost_impact", "Unknown")
        st.info(f"**Priority:** {priority} | **Est. Cost Impact:** {cost}")
        
        t1, t2, t3 = st.tabs(["⚡ Immediate (1h)", "⏱️ Short-term (24h)", "📅 Long-term (1w)"])
        with t1: render_action_checklist(plan.get("immediate_actions", []), "Immediate Actions")
        with t2: render_action_checklist(plan.get("short_term_actions", []), "Short-term Actions")
        with t3: render_action_checklist(plan.get("long_term_actions", []), "Long-term Actions")
        
        alts = plan.get("supplier_alternatives", [])
        if alts:
            st.markdown("---")
            st.markdown("**🔄 Recommended Supplier Alternatives:**")
            for alt in alts:
                st.write(f"- {alt['name']} ({alt['country']} - Tier {alt['tier']})")
                
    except Exception as e:
        st.error(f"Error rendering prevention plan: {e}")

def render_route_map(routes: list):
    try:
        if not routes:
            st.warning("No routes found.")
            return
        df = pd.DataFrame([r for r in routes])
        
        def highlight_risk(val):
            color = get_risk_color(val)
            return f'background-color: {color}20; color: {color}; font-weight: bold;'
            
        st.dataframe(df.style.map(highlight_risk, subset=['risk_level']), use_container_width=True)
    except Exception as e:
        st.error(f"Error rendering routes: {e}")

def render_supplier_table(suppliers: list):
    try:
        if not suppliers:
            st.warning("No suppliers found.")
            return
        df = pd.DataFrame([s for s in suppliers])
        
        def highlight_supplier_risk(val):
            if val >= 0.7: return 'background-color: rgba(220, 53, 69, 0.2); color: #dc3545; font-weight: bold;'
            elif val >= 0.4: return 'background-color: rgba(255, 193, 7, 0.2); color: #b58500; font-weight: bold;'
            else: return 'background-color: rgba(40, 167, 69, 0.2); color: #28a745;'

        st.dataframe(
            df.style.map(highlight_supplier_risk, subset=['risk_score']),
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error rendering suppliers: {e}")

def render_alert_banner(level: str, message: str):
    colors = {"INFO": "blue", "WARNING": "orange", "CRITICAL": "red", "EMERGENCY": "darkred"}
    color = colors.get(level, "gray")
    st.markdown(
        f'<div style="padding:10px; background-color:{color}; color:white; border-radius:5px; margin-bottom:20px;">'
        f'<strong>{level} ALERT:</strong> {message}</div>', 
        unsafe_allow_html=True
    )

def render_confidence_bar(confidence: float):
    st.write(f"**Confidence:** {int(confidence * 100)}%")
    st.progress(confidence)

def render_keyword_tags(keywords: list):
    if not keywords: return
    tags_html = "".join([f'<span style="background-color: #e9ecef; color: #495057; padding: 5px 10px; border-radius: 15px; margin-right: 5px; font-size: 0.9em; display: inline-block; margin-bottom: 5px;">{kw}</span>' for kw in keywords])
    st.markdown(tags_html, unsafe_allow_html=True)
