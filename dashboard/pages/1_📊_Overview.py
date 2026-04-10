# dashboard/pages/1_📊_Overview.py

import streamlit as st
import plotly.express as px
from utils.data_loader import load_data, get_valid, PALETTE

st.markdown("## 📊 Overview")
st.markdown("Global synthesis of the punctuality and reliability study.")

df = load_data()
df_valid = get_valid(df)

# ── KPIs ──
total_shifts   = len(df)
no_show_rate   = df['no_show'].mean() * 100
median_process = df_valid['process_time'].median()
pct_late       = (df_valid['start_vs_planned'] > 0).mean() * 100
median_arrival = df_valid['stadium_vs_planned'].median()

c1, c2, c3, c4, c5 = st.columns(5)
kpis = [
    (c1, f"{total_shifts:,}",          "Total shifts analyzed"),
    (c2, f"{no_show_rate:.1f}%",        "No-show rate"),
    (c3, f"{median_process:.0f} min",   "Median processing time"),
    (c4, f"{pct_late:.1f}%",            "Shifts started late"),
    (c5, f"{median_arrival:+.0f} min",  "Median arrival vs planned"),
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

# ── Key conclusions ──
st.markdown('<div class="section-title">🔍 Key findings</div>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a:
    st.success("""
    **The problem is structural, not behavioral.**
    No significant correlation between stadium arrival time and shift start delay.
    Internal processing (~45 min) is the primary cause.
    """)
    st.warning("""
    **To start on time, staff must arrive >1h early.**
    Current call times do not account for this. Immediate, actionable fix.
    """)
with col_b:
    st.info("""
    **Retention is the long-term strategy.**
    Experienced staff absorb processing faster and generate fewer last-minute absences.
    """)
    st.error("""
    **Every minute of delay = unbilled loss.**
    Quantifying this per event justifies investment in onboarding process optimization.
    """)

st.markdown("---")

# ── No-show by event type ──
st.markdown('<div class="section-title">📅 No-show rate by event type</div>', unsafe_allow_html=True)

if 'event_type' in df.columns:
    event_ns = df.groupby('event_type').agg(
        total=('shift_id', 'count'),
        no_show=('no_show', 'sum')
    ).assign(rate=lambda x: x['no_show'] / x['total'] * 100).reset_index()

    fig = px.bar(
        event_ns.sort_values('rate', ascending=True),
        x='rate', y='event_type', orientation='h',
        color='rate', color_continuous_scale=['#2b9348', '#e94560'],
        labels={'rate': 'No-show rate (%)', 'event_type': 'Event type'},
        title="No-show rate by event type"
    )
    fig.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# ── No-show by role ──
st.markdown('<div class="section-title">👷 No-show rate by role</div>', unsafe_allow_html=True)

if 'job_name' in df.columns:
    role_ns = df.groupby('job_name').agg(
        total=('shift_id', 'count'),
        no_show=('no_show', 'sum')
    ).assign(rate=lambda x: x['no_show'] / x['total'] * 100)
    role_ns = role_ns[role_ns['total'] > 50].sort_values('rate', ascending=True).reset_index()

    fig_role = px.bar(
        role_ns, x='rate', y='job_name', orientation='h',
        color='rate', color_continuous_scale=['#2b9348', '#e94560'],
        labels={'rate': 'No-show rate (%)', 'job_name': 'Role'},
        title="No-show rate by role (min. 50 shifts)"
    )
    fig_role.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_role, use_container_width=True)
