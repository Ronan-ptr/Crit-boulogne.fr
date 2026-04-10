# dashboard/pages/2_⏱️_Punctuality.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from scipy import stats
from utils.data_loader import load_data, get_valid, PALETTE

st.markdown("## ⏱️ Punctuality")
st.markdown("Arrival behavior analysis and its real impact on shift start times.")

df = load_data()
df_valid = get_valid(df)

# ── 1. Distribution: arrival at stadium vs planned ──
st.markdown('<div class="section-title">Stadium arrival vs call time</div>', unsafe_allow_html=True)

fig1 = px.histogram(
    df_valid, x='stadium_vs_planned', nbins=60,
    color_discrete_sequence=[PALETTE[1]],
    labels={'stadium_vs_planned': 'Minutes before/after call time'},
    title="Stadium arrival distribution"
)
fig1.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Call time")
fig1.add_vline(x=df_valid['stadium_vs_planned'].median(), line_dash="dash", line_color="orange",
               annotation_text=f"Median: {df_valid['stadium_vs_planned'].median():.0f} min")
fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig1, use_container_width=True)

# ── 2. Scatter: stadium arrival → shift start delay ──
st.markdown('<div class="section-title">Correlation: stadium arrival → shift start delay</div>', unsafe_allow_html=True)

sample = df_valid[['stadium_vs_planned', 'start_vs_planned']].dropna().sample(
    min(3000, len(df_valid)), random_state=42
)
r, _ = stats.pearsonr(sample['stadium_vs_planned'], sample['start_vs_planned'])

fig2 = px.scatter(
    sample, x='stadium_vs_planned', y='start_vs_planned',
    opacity=0.3, color_discrete_sequence=[PALETTE[0]],
    trendline='ols', trendline_color_override=PALETTE[1],
    labels={
        'stadium_vs_planned': 'Stadium arrival vs planned (min)',
        'start_vs_planned': 'Shift start vs planned (min)'
    },
    title=f"Stadium arrival vs Shift start — r = {r:.2f}"
)
fig2.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="On time")
fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig2, use_container_width=True)

strength = "weak" if abs(r) < 0.3 else "moderate" if abs(r) < 0.5 else "strong"
st.info(f"**r = {r:.2f}** — {strength.capitalize()} correlation. "
        "Stadium arrival time explains little of the shift start delay. The root cause is internal processing.")

# ── 3. On-time rate by arrival bucket ──
st.markdown('<div class="section-title">On-time rate by arrival window</div>', unsafe_allow_html=True)

bins = [-120, -90, -60, -45, -30, -15, 0, 30]
labels_b = ['>90min early', '60-90min', '45-60min', '30-45min', '15-30min', '0-15min', 'After call']
df_valid['arrival_bucket'] = pd.cut(df_valid['stadium_vs_planned'], bins=bins, labels=labels_b)

bucket_stats = df_valid.groupby('arrival_bucket', observed=True).agg(
    total=('start_vs_planned', 'count'),
    on_time=('start_vs_planned', lambda x: (x <= 0).sum())
).assign(pct_on_time=lambda x: x['on_time'] / x['total'] * 100).reset_index()

fig3 = px.bar(
    bucket_stats, x='arrival_bucket', y='pct_on_time',
    color='pct_on_time', color_continuous_scale=['#e94560', '#2b9348'],
    labels={'arrival_bucket': 'Arrival window', 'pct_on_time': '% on time at shift start'},
    title="Earlier arrival = more likely on time — but how early is enough?"
)
fig3.add_hline(y=50, line_dash="dot", line_color="white", annotation_text="50%")
fig3.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig3, use_container_width=True)

# ── 4. Boxplot: arrival by gender ──
st.markdown('<div class="section-title">Arrival by gender</div>', unsafe_allow_html=True)

fig4 = px.box(
    df_valid.dropna(subset=['gender']),
    x='gender', y='stadium_vs_planned',
    color='gender', color_discrete_sequence=[PALETTE[1], PALETTE[2]],
    labels={'stadium_vs_planned': 'Arrival vs planned (min)', 'gender': 'Gender'},
    title="Stadium arrival distribution by gender"
)
fig4.add_hline(y=0, line_dash="dash", line_color="red")
fig4.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig4, use_container_width=True)

# ── 5. Boxplot: arrival by department ──
st.markdown('<div class="section-title">Arrival by department</div>', unsafe_allow_html=True)

dept_data = df_valid.dropna(subset=['dept_name'])
dept_order = dept_data.groupby('dept_name')['stadium_vs_planned'].median().sort_values().index.tolist()

fig5 = px.box(
    dept_data, x='dept_name', y='stadium_vs_planned',
    category_orders={'dept_name': dept_order},
    color_discrete_sequence=[PALETTE[2]],
    labels={'stadium_vs_planned': 'Arrival vs planned (min)', 'dept_name': 'Department'},
    title="Stadium arrival by department — does distance cause delays?"
)
fig5.add_hline(y=0, line_dash="dash", line_color="red")
fig5.update_layout(plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig5, use_container_width=True)
