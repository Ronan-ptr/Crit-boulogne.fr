# dashboard/pages/4_🤝_Retention.py

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_loader import load_data, get_valid, PALETTE

st.markdown("## 🤝 Retention & Staff Profiles")
st.markdown("Profile analysis to guide recruitment and retention strategy.")

df = load_data()
df_valid = get_valid(df)

tab1, tab2, tab3 = st.tabs(["👤 Gender", "📍 Department", "🎂 Age"])

# ── TAB 1: Gender ──
with tab1:
    gender_stats = df.groupby('gender').agg(
        total=('shift_id', 'count'),
        no_show=('no_show', 'sum')
    ).assign(no_show_rate=lambda x: x['no_show'] / x['total'] * 100).reset_index()

    fig_g1 = px.bar(
        gender_stats, x='gender', y='no_show_rate',
        color='gender', color_discrete_sequence=[PALETTE[1], PALETTE[2]],
        labels={'no_show_rate': 'No-show rate (%)', 'gender': 'Gender'},
        title="No-show rate by gender"
    )
    fig_g1.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_g1, use_container_width=True)

    fig_g2 = px.box(
        df_valid.dropna(subset=['gender']),
        x='gender', y='stadium_vs_planned',
        color='gender', color_discrete_sequence=[PALETTE[1], PALETTE[2]],
        labels={'stadium_vs_planned': 'Arrival vs planned (min)', 'gender': 'Gender'},
        title="Punctuality distribution by gender"
    )
    fig_g2.add_hline(y=0, line_dash="dash", line_color="red")
    fig_g2.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_g2, use_container_width=True)

    fig_g3 = px.box(
        df_valid.dropna(subset=['gender']),
        x='gender', y='process_time',
        color='gender', color_discrete_sequence=[PALETTE[1], PALETTE[2]],
        labels={'process_time': 'Processing time (min)', 'gender': 'Gender'},
        title="Processing time by gender"
    )
    fig_g3.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_g3, use_container_width=True)

# ── TAB 2: Department ──
with tab2:
    geo_stats = df.groupby('dept_name').agg(
        total=('shift_id', 'count'),
        no_show=('no_show', 'sum'),
        avg_arrival=('stadium_vs_planned', 'mean')
    ).assign(no_show_rate=lambda x: x['no_show'] / x['total'] * 100)
    geo_stats = geo_stats[geo_stats['total'] > 100].dropna().reset_index()

    fig_d1 = px.scatter(
        geo_stats, x='avg_arrival', y='no_show_rate',
        size='total', color='dept_name',
        text='dept_name', color_discrete_sequence=px.colors.qualitative.Set2,
        labels={
            'avg_arrival': 'Mean arrival vs planned (min)',
            'no_show_rate': 'No-show rate (%)',
            'total': 'Total shifts'
        },
        title="Department: arrival vs no-show rate"
    )
    fig_d1.update_traces(textposition='top center')
    fig_d1.update_layout(plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    st.plotly_chart(fig_d1, use_container_width=True)

    fig_d2 = px.bar(
        geo_stats.sort_values('no_show_rate', ascending=True),
        x='no_show_rate', y='dept_name', orientation='h',
        color='no_show_rate', color_continuous_scale=['#2b9348', '#e94560'],
        labels={'no_show_rate': 'No-show rate (%)', 'dept_name': 'Department'},
        title="No-show rate by department"
    )
    fig_d2.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_d2, use_container_width=True)

# ── TAB 3: Age ──
with tab3:
    age_stats = df.groupby('age_group', observed=True).agg(
        total=('shift_id', 'count'),
        no_show_rate=('no_show', 'mean'),
        median_arrival=('stadium_vs_planned', 'median'),
        median_process=('process_time', 'median'),
        pct_late=('start_vs_planned', lambda x: (x > 0).mean() * 100)
    ).reset_index()
    age_stats['no_show_rate'] = age_stats['no_show_rate'] * 100

    fig_a1 = px.bar(
        age_stats, x='age_group', y='no_show_rate',
        color='no_show_rate', color_continuous_scale=['#2b9348', '#e94560'],
        labels={'age_group': 'Age group', 'no_show_rate': 'No-show rate (%)'},
        title="No-show rate by age group"
    )
    fig_a1.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_a1, use_container_width=True)

    fig_a2 = px.bar(
        age_stats, x='age_group', y='median_arrival',
        color='median_arrival', color_continuous_scale=['#e94560', '#2b9348'],
        labels={'age_group': 'Age group', 'median_arrival': 'Median arrival vs planned (min)'},
        title="Punctuality by age group — is the age hypothesis valid?"
    )
    fig_a2.add_hline(y=-60, line_dash="dash", line_color="orange",
                     annotation_text="Recommended threshold: -60 min")
    fig_a2.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_a2, use_container_width=True)

    fig_a3 = px.bar(
        age_stats, x='age_group', y='pct_late',
        color='pct_late', color_continuous_scale=['#2b9348', '#e94560'],
        labels={'age_group': 'Age group', 'pct_late': '% shifts started late'},
        title="Late shift start rate by age group"
    )
    fig_a3.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_a3, use_container_width=True)

    st.info("These charts empirically validate or invalidate the hypothesis: "
            "do older profiles arrive earlier and start shifts on time more often?")
