# dashboard/app.py
# Crit Agency — HR Analytical Dashboard
# Author: Ronan Potier

import streamlit as st

st.set_page_config(
    page_title="Crit Agency — Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .metric-card {
        background-color: #1a1a2e;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        color: white;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #e94560;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #aaaaaa;
        margin-top: 4px;
    }
    .section-title {
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 1rem;
        border-left: 4px solid #e94560;
        padding-left: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("## 📊 Crit Agency — HR Analytical Dashboard")
st.markdown("Use the **sidebar** to navigate between analysis sections.")
st.markdown("---")
st.markdown("""
### About this dashboard

This tool provides a comprehensive analysis of **event staff punctuality and reliability** 
at the Stade de France, based on historical shift data.

**Sections:**
- **📊 Overview** — Key metrics and high-level conclusions
- **⏱️ Punctuality** — Arrival behavior and its impact on shift start times
- **⚙️ Processing** — Internal processing time analysis (stadium arrival → shift start)
- **🤝 Retention** — Staff profile analysis to guide recruitment & retention strategy

---
*Dashboard v1.0 — Developed by Ronan Potier*
""")
