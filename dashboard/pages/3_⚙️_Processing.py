# dashboard/pages/3_⚙️_Processing.py

import streamlit as st
import plotly.express as px
import pandas as pd
from scipy import stats
from utils.data_loader import load_data, get_valid, PALETTE

st.markdown("## ⚙️ Processing Time Analysis")
st.markdown("Time between stadium arrival and effective shift start.")

df = load_data()
df_valid = get_valid(df)

# ── KPIs ──
c1, c2, c3 = st.columns(3)
c1.metric("Median processing", f"{df_valid['process_time'].median():.0f} min")
c2.metric("Mean processing", f"{df_valid['process_time'].mean():.0f} min")
c3.metric("P90 processing", f"{df_valid['process_time'].quantile(0.9):.0f} min",
          help="90% of shifts have processing below this duration")

# ── 1. Distribution ──
st.markdown('<div class="section-title">Processing time distribution</div>', unsafe_allow_html=True)

fig1 = px.histogram(
    df_valid, x='process_time', nbins=60,
    color_discrete_sequence=[PALETTE[2]],
    labels={'process_time': 'Processing time (min)'},
    title="Processing time distribution"
)
fig1.add_vline(x=df_valid['process_time'].median(), line_dash="dash", line_color="orange",
               annotation_text=f"Median: {df_valid['process_time'].median():.0f} min")
fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig1, use_container_width=True)

# ── 2. Processing by event type ──
if 'event_type' in df.columns:
    st.markdown('<div class="section-title">Median processing by event type</div>', unsafe_allow_html=True)

    proc_event = df_valid.groupby('event_type')['process_time'].median().reset_index()
    proc_event.columns = ['event_type', 'median_process']

    fig2 = px.bar(
        proc_event.sort_values('median_process', ascending=True),
        x='median_process', y='event_type', orientation='h',
        color='median_process', color_continuous_scale=['#2b9348', '#e94560'],
        labels={'median_process': 'Median processing (min)', 'event_type': 'Event type'},
        title="Median processing by event type"
    )
    fig2.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig2, use_container_width=True)

# ── 3. Processing vs event size ──
st.markdown('<div class="section-title">Processing vs event size</div>', unsafe_allow_html=True)

event_size = df.groupby('event_id').agg(
    event_name=('event_name', 'first'),
    event_type=('event_type', 'first'),
    total_shifts=('shift_id', 'count'),
    median_process=('process_time', 'median'),
    no_show_rate=('no_show', 'mean')
).reset_index()
event_size = event_size[event_size['median_process'] > 0].dropna(subset=['median_process'])

fig3 = px.scatter(
    event_size, x='total_shifts', y='median_process',
    size='no_show_rate', color='event_type' if 'event_type' in event_size.columns else None,
    hover_data=['event_name'],
    labels={
        'total_shifts': 'Event size (nb shifts)',
        'median_process': 'Median processing (min)',
        'no_show_rate': 'No-show rate'
    },
    title="Do larger events increase processing time?"
)
fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig3, use_container_width=True)

# ── 4. Processing by team (job_team) ──
if 'job_team' in df.columns:
    st.markdown('<div class="section-title">Median processing by team</div>', unsafe_allow_html=True)

    team_stats = df_valid.groupby('job_team')['process_time'].agg(['median', 'count']).reset_index()
    team_stats = team_stats[team_stats['count'] > 50].sort_values('median', ascending=True)

    fig4 = px.bar(
        team_stats, x='median', y='job_team', orientation='h',
        color='median', color_continuous_scale=['#2b9348', '#e94560'],
        labels={'median': 'Median processing (min)', 'job_team': 'Team'},
        title="Median processing by team — do some teams wait longer?"
    )
    global_med = df_valid['process_time'].median()
    fig4.add_vline(x=global_med, line_dash="dash", line_color="red",
                   annotation_text=f"Global median: {global_med:.0f} min")
    fig4.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig4, use_container_width=True)

# ── 5. Processing by location type ──
if 'loc_type' in df.columns:
    st.markdown('<div class="section-title">Median processing by location type</div>', unsafe_allow_html=True)

    loc_stats = df_valid.groupby('loc_type')['process_time'].agg(['median', 'count']).reset_index()
    loc_stats = loc_stats[loc_stats['count'] > 100].sort_values('median', ascending=False)

    fig5 = px.bar(
        loc_stats, x='median', y='loc_type', orientation='h',
        color='median', color_continuous_scale=['#2b9348', '#e94560'],
        labels={'median': 'Median processing (min)', 'loc_type': 'Location type'},
        title="Median processing by location — are some posts harder to reach?"
    )
    fig5.add_vline(x=global_med, line_dash="dash", line_color="red",
                   annotation_text=f"Global median: {global_med:.0f} min")
    fig5.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig5, use_container_width=True)

# ── 6. Processing by floor ──
if 'loc_floor' in df.columns:
    st.markdown('<div class="section-title">Median processing by floor/zone</div>', unsafe_allow_html=True)

    floor_stats = df_valid.groupby('loc_floor')['process_time'].agg(['median', 'count']).reset_index()
    floor_stats = floor_stats[floor_stats['count'] > 50].sort_values('median', ascending=True)

    fig6 = px.bar(
        floor_stats, x='median', y='loc_floor', orientation='h',
        color='median', color_continuous_scale=['#2b9348', '#e94560'],
        labels={'median': 'Median processing (min)', 'loc_floor': 'Floor / Zone'},
        title="Median processing by floor — does floor level affect processing?"
    )
    fig6.add_vline(x=global_med, line_dash="dash", line_color="red",
                   annotation_text=f"Global median: {global_med:.0f} min")
    fig6.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig6, use_container_width=True)

# ── 7. Correlation: processing → shift start delay ──
st.markdown('<div class="section-title">Correlation: processing → shift start delay</div>', unsafe_allow_html=True)

sample = df_valid[['process_time', 'start_vs_planned']].dropna().sample(
    min(3000, len(df_valid)), random_state=42
)
r2, _ = stats.pearsonr(sample['process_time'], sample['start_vs_planned'])

fig7 = px.scatter(
    sample, x='process_time', y='start_vs_planned',
    opacity=0.3, color_discrete_sequence=[PALETTE[2]],
    trendline='ols', trendline_color_override=PALETTE[1],
    labels={
        'process_time': 'Processing time (min)',
        'start_vs_planned': 'Shift start delay (min)'
    },
    title=f"Processing vs Shift start delay — r = {r2:.2f}"
)
fig7.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="On time")
fig7.update_layout(plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig7, use_container_width=True)

st.warning(f"**r = {r2:.2f}** — The longer the processing, the later the shift starts. "
           "This is the primary factor identified by the study.")
