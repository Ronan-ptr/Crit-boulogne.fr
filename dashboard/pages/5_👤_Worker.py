# dashboard/pages/5_👤_Worker.py

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_loader import load_data, get_valid, PALETTE

st.markdown("## 👤 Worker Profile")
st.markdown("Individual analysis: select a worker to explore their full history.")

df = load_data()

# ── Worker selector ──
# On ne propose que les workers avec un minimum de shifts pour éviter le bruit
worker_counts = df['pax_id'].value_counts()
eligible_ids = worker_counts[worker_counts >= 1].index.tolist()

# Tri par nombre de shifts décroissant pour faciliter l'exploration
sorted_ids = worker_counts.loc[eligible_ids].sort_values(ascending=False).index.tolist()

selected_id = st.selectbox(
    "🔎 Select a worker (sorted by shift count)",
    options=sorted_ids,
    format_func=lambda x: f"ID {x} — {worker_counts[x]} shifts"
)

if selected_id is None:
    st.warning("No worker selected.")
    st.stop()

# ── Filter on selected worker ──
worker_df = df[df['pax_id'] == selected_id].copy()
worker_valid = get_valid(worker_df)

# ── Worker identity ──
st.markdown("---")
identity_cols = st.columns(4)

age = worker_df['age'].iloc[0] if not worker_df['age'].isna().all() else "N/A"
gender = worker_df['gender'].iloc[0] if not worker_df['gender'].isna().all() else "N/A"
dept = worker_df['dept_name'].iloc[0] if not worker_df['dept_name'].isna().all() else "N/A"
first_shift = worker_df['shift_planned_dt'].min()
last_shift = worker_df['shift_planned_dt'].max()
tenure_days = (last_shift - first_shift).days if pd.notna(first_shift) and pd.notna(last_shift) else 0

with identity_cols[0]:
    st.markdown(f"**👤 Gender**<br>{gender}", unsafe_allow_html=True)
with identity_cols[1]:
    st.markdown(f"**🎂 Age**<br>{age}", unsafe_allow_html=True)
with identity_cols[2]:
    st.markdown(f"**📍 Department**<br>{dept}", unsafe_allow_html=True)
with identity_cols[3]:
    st.markdown(f"**📅 Tenure**<br>{tenure_days} days", unsafe_allow_html=True)

st.markdown("---")

# ── KPIs ──
total_shifts = len(worker_df)
no_shows = worker_df['no_show'].sum()
no_show_rate = no_shows / total_shifts * 100 if total_shifts > 0 else 0

# Sur les shifts valides (présents)
if len(worker_valid) > 0:
    median_arrival = worker_valid['stadium_vs_planned'].median()
    median_process = worker_valid['process_time'].median()
    pct_late_start = (worker_valid['start_vs_planned'] > 0).mean() * 100
    pct_on_time = (worker_valid['start_vs_planned'] <= 0).mean() * 100
else:
    median_arrival = median_process = pct_late_start = pct_on_time = 0

st.markdown('<div class="section-title">📊 Key metrics</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
kpis = [
    (c1, f"{total_shifts}",            "Total shifts"),
    (c2, f"{no_show_rate:.1f}%",       f"No-show rate ({no_shows} absences)"),
    (c3, f"{pct_on_time:.1f}%",        "Shifts started on time"),
    (c4, f"{median_arrival:+.0f} min", "Median arrival vs planned"),
    (c5, f"{median_process:.0f} min",  "Median processing time"),
]
for col, val, label in kpis:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{val}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ── Behavior breakdown ──
st.markdown('<div class="section-title">🎯 Reliability profile</div>', unsafe_allow_html=True)

# Catégorisation comportementale
def categorize(row):
    if row['no_show']:
        return 'No-show'
    if pd.isna(row['start_vs_planned']):
        return 'Unknown'
    if row['start_vs_planned'] <= 0:
        return 'On time'
    if row['start_vs_planned'] <= 15:
        return 'Slightly late (≤15 min)'
    return 'Very late (>15 min)'

worker_df['behavior'] = worker_df.apply(categorize, axis=1)
behavior_counts = worker_df['behavior'].value_counts().reset_index()
behavior_counts.columns = ['behavior', 'count']

color_map = {
    'On time': '#2b9348',
    'Slightly late (≤15 min)': '#f4a261',
    'Very late (>15 min)': '#e76f51',
    'No-show': '#e94560',
    'Unknown': '#888888'
}

fig_behavior = px.pie(
    behavior_counts, values='count', names='behavior',
    color='behavior', color_discrete_map=color_map,
    title="Behavioral breakdown across all shifts",
    hole=0.4
)
fig_behavior.update_layout(plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig_behavior, use_container_width=True)

# ── Evolution over time ──
st.markdown('<div class="section-title">📈 Punctuality evolution over time</div>', unsafe_allow_html=True)

if len(worker_valid) >= 3:
    timeline = worker_valid.sort_values('shift_planned_dt').copy()
    timeline['rolling_arrival'] = timeline['stadium_vs_planned'].rolling(window=5, min_periods=1).mean()
    timeline['rolling_start']   = timeline['start_vs_planned'].rolling(window=5, min_periods=1).mean()

    fig_evo = px.line(
        timeline, x='shift_planned_dt',
        y=['stadium_vs_planned', 'start_vs_planned'],
        labels={'value': 'Minutes vs planned', 'shift_planned_dt': 'Date', 'variable': 'Metric'},
        title="Arrival & shift start delay over time",
        color_discrete_sequence=[PALETTE[2], PALETTE[1]]
    )
    fig_evo.add_hline(y=0, line_dash="dash", line_color="white", annotation_text="On time")
    fig_evo.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_evo, use_container_width=True)
else:
    st.info("Not enough valid shifts to display timeline (minimum 3 required).")

# ── Roles distribution ──
st.markdown('<div class="section-title">👷 Roles & teams</div>', unsafe_allow_html=True)

col_left, col_right = st.columns(2)

with col_left:
    if 'job_name' in worker_df.columns:
        roles = worker_df['job_name'].value_counts().reset_index()
        roles.columns = ['job_name', 'count']
        fig_roles = px.bar(
            roles, x='count', y='job_name', orientation='h',
            color='count', color_continuous_scale=['#0f3460', '#e94560'],
            labels={'count': 'Number of shifts', 'job_name': 'Role'},
            title="Roles performed"
        )
        fig_roles.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_roles, use_container_width=True)

with col_right:
    if 'event_type' in worker_df.columns:
        events = worker_df['event_type'].value_counts().reset_index()
        events.columns = ['event_type', 'count']
        fig_events = px.bar(
            events, x='count', y='event_type', orientation='h',
            color='count', color_continuous_scale=['#0f3460', '#2b9348'],
            labels={'count': 'Number of shifts', 'event_type': 'Event type'},
            title="Event types"
        )
        fig_events.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_events, use_container_width=True)

# ── Detailed shift table ──
st.markdown('<div class="section-title">📋 Detailed shift history</div>', unsafe_allow_html=True)

display_cols = ['shift_planned_dt', 'event_name', 'job_name',
                'stadium_vs_planned', 'process_time', 'start_vs_planned', 'behavior']
available_cols = [c for c in display_cols if c in worker_df.columns]

table_df = worker_df[available_cols].sort_values('shift_planned_dt', ascending=False).copy()

# Formatage propre
if 'shift_planned_dt' in table_df.columns:
    table_df['shift_planned_dt'] = table_df['shift_planned_dt'].dt.strftime('%Y-%m-%d %H:%M')
for col in ['stadium_vs_planned', 'process_time', 'start_vs_planned']:
    if col in table_df.columns:
        table_df[col] = table_df[col].round(0)

table_df.columns = [c.replace('_', ' ').title() for c in table_df.columns]
st.dataframe(table_df, use_container_width=True, height=400)
