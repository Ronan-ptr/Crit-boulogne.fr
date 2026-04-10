# dashboard/app.py
# Crit Agency — HR Analytical Dashboard
# Author: Ronan Potier old app set

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy import stats

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Crit Agency — Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# STYLE
# ─────────────────────────────────────────────
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

PALETTE = ["#1a1a2e", "#e94560", "#0f3460", "#533483", "#2b9348"]

# ─────────────────────────────────────────────
# SIDEBAR — NAVIGATION & DATA LOADER
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://via.placeholder.com/200x60?text=CRIT+AGENCY", use_column_width=True)
    st.markdown("---")

    uploaded_file = st.file_uploader("📂 Charger le dataset CSV", type=["csv"])

    st.markdown("---")
    section = st.radio(
        "Navigation",
        ["🏠 Vue Générale", "⏱️ Ponctualité", "⚙️ Processing", "🤝 Fidélisation"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("Crit Agency — Dashboard v1.0\nDéveloppé par Ronan Potier")

# ─────────────────────────────────────────────
# DATA LOADING & PREPROCESSING
# ─────────────────────────────────────────────
@st.cache_data
def load_data(file):
    df = pd.read_csv(file, low_memory=False)

    df['shift_planned_dt'] = pd.to_datetime(df['shift_planned'], errors='coerce')
    df['shift_stadium_dt'] = pd.to_datetime(df['shift_stadium'], errors='coerce')
    df['shift_start_dt']   = pd.to_datetime(df['shift_start'],   errors='coerce')
    df['shift_end_dt']     = pd.to_datetime(df['shift_end'],     errors='coerce')

    df['no_show']           = df['shift_start'].isna() & df['shift_end'].isna()
    df['stadium_vs_planned'] = (df['shift_stadium_dt'] - df['shift_planned_dt']).dt.total_seconds() / 60
    df['process_time']       = (df['shift_start_dt']   - df['shift_stadium_dt']).dt.total_seconds() / 60
    df['start_vs_planned']   = (df['shift_start_dt']   - df['shift_planned_dt']).dt.total_seconds() / 60
    df['age']                = (pd.Timestamp('2024-01-01') - pd.to_datetime(df['pax_birth'], errors='coerce')).dt.days // 365
    df['gender']             = df['pax_sex'].map({True: 'Homme', False: 'Femme'})

    dept_map = {
        '75': 'Paris', '92': 'Hauts-de-Seine', '93': 'Seine-St-Denis',
        '94': 'Val-de-Marne', '91': 'Essonne', '95': "Val-d'Oise",
        '77': 'Seine-et-Marne', '78': 'Yvelines'
    }
    df['dept'] = df['pax_zip'].astype(str).str[:2]
    df['dept_name'] = df['dept'].map(dept_map)

    age_bins = [16, 20, 25, 30, 35, 40, 50, 99]
    age_labels = ['16-20', '21-25', '26-30', '31-35', '36-40', '41-50', '50+']
    df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=age_labels, right=True)

    return df

# ─────────────────────────────────────────────
# GATE — attendre le CSV
# ─────────────────────────────────────────────
if uploaded_file is None:
    st.markdown("## 📊 Crit Agency — HR Dashboard")
    st.info("👈 Charge le fichier `clean_dataset.csv` depuis la sidebar pour démarrer l'analyse.")
    st.stop()

df = load_data(uploaded_file)

# Filtres globaux pour les métriques (exclure valeurs aberrantes)
df_valid = df[
    df['process_time'].between(0, 180) &
    df['stadium_vs_planned'].between(-120, 60) &
    df['start_vs_planned'].notna()
].copy()

# ─────────────────────────────────────────────
# SECTION 1 — VUE GÉNÉRALE
# ─────────────────────────────────────────────
if section == "🏠 Vue Générale":
    st.markdown("## 🏠 Vue Générale")
    st.markdown("Synthèse globale de l'étude sur la ponctualité et la fiabilité du personnel événementiel.")

    # KPIs
    total_shifts    = len(df)
    no_show_rate    = df['no_show'].mean() * 100
    median_process  = df_valid['process_time'].median()
    pct_late        = (df_valid['start_vs_planned'] > 0).mean() * 100
    median_arrival  = df_valid['stadium_vs_planned'].median()

    c1, c2, c3, c4, c5 = st.columns(5)
    kpis = [
        (c1, f"{total_shifts:,}", "Shifts analysés"),
        (c2, f"{no_show_rate:.1f}%", "Taux de no-show"),
        (c3, f"{median_process:.0f} min", "Processing médian"),
        (c4, f"{pct_late:.1f}%", "Shifts en retard"),
        (c5, f"{median_arrival:+.0f} min", "Arrivée vs prévu (médiane)"),
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

    # Conclusion narrative
    st.markdown('<div class="section-title">🔍 Conclusions clés de l\'étude</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.success("""
        **Le problème est structurel, pas comportemental.**
        Aucune corrélation significative entre l'heure d'arrivée au stade et le retard à la prise de poste.
        Le processing interne (~45 min) est la cause principale.
        """)
        st.warning("""
        **Pour être à l'heure au poste, il faut arriver >1h en avance.**
        La convocation actuelle ne l'intègre pas. C'est un levier immédiat et actionnable.
        """)
    with col_b:
        st.info("""
        **La fidélisation est la stratégie long terme.**
        Un staff expérimenté absorbe le processing plus rapidement et génère moins d'absences de dernière minute.
        """)
        st.error("""
        **Chaque minute de retard = perte sèche non facturée.**
        Quantifier cette perte par événement permet de justifier un investissement dans l'optimisation du process d'accueil.
        """)

    # Répartition no-show par type d'événement
    st.markdown("---")
    st.markdown('<div class="section-title">📅 No-show par type d\'événement</div>', unsafe_allow_html=True)

    if 'event_type' in df.columns:
        event_ns = df.groupby('event_type').agg(
            total=('shift_id', 'count'),
            no_show=('no_show', 'sum')
        ).assign(rate=lambda x: x['no_show'] / x['total'] * 100).reset_index()

        fig = px.bar(
            event_ns.sort_values('rate', ascending=True),
            x='rate', y='event_type', orientation='h',
            color='rate', color_continuous_scale=['#2b9348', '#e94560'],
            labels={'rate': 'Taux de no-show (%)', 'event_type': 'Type d\'événement'},
            title="Taux de no-show par type d'événement"
        )
        fig.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# SECTION 2 — PONCTUALITÉ
# ─────────────────────────────────────────────
elif section == "⏱️ Ponctualité":
    st.markdown("## ⏱️ Ponctualité")
    st.markdown("Analyse du comportement d'arrivée et de son impact réel sur la prise de poste.")

    # Graphique 1 — Distribution arrivée au stade
    st.markdown('<div class="section-title">Arrivée au stade vs heure de convocation</div>', unsafe_allow_html=True)

    fig1 = px.histogram(
        df_valid, x='stadium_vs_planned', nbins=60,
        color_discrete_sequence=[PALETTE[1]],
        labels={'stadium_vs_planned': 'Minutes avant/après convocation'},
        title="Distribution des arrivées au stade (médiane = ligne orange)"
    )
    fig1.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Heure de convocation")
    fig1.add_vline(x=df_valid['stadium_vs_planned'].median(), line_dash="dash",
                   line_color="orange",
                   annotation_text=f"Médiane : {df_valid['stadium_vs_planned'].median():.0f} min")
    fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig1, use_container_width=True)

    # Graphique 2 — Corrélation arrivée → prise de poste
    st.markdown('<div class="section-title">Corrélation : arrivée au stade → retard au poste</div>', unsafe_allow_html=True)

    sample = df_valid[['stadium_vs_planned', 'start_vs_planned']].dropna().sample(
        min(3000, len(df_valid)), random_state=42
    )
    r, _ = stats.pearsonr(sample['stadium_vs_planned'], sample['start_vs_planned'])

    fig2 = px.scatter(
        sample, x='stadium_vs_planned', y='start_vs_planned',
        opacity=0.3, color_discrete_sequence=[PALETTE[0]],
        trendline='ols', trendline_color_override=PALETTE[1],
        labels={
            'stadium_vs_planned': 'Arrivée au stade vs prévu (min)',
            'start_vs_planned': 'Prise de poste vs prévu (min)'
        },
        title=f"Arrivée au stade vs Prise de poste — r = {r:.2f} ({'corrélation faible' if abs(r) < 0.3 else 'corrélation significative'})"
    )
    fig2.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="À l'heure")
    fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig2, use_container_width=True)

    st.info(f"**r = {r:.2f}** — L'heure d'arrivée au stade explique peu le retard à la prise de poste. "
            f"La cause est interne : le processing.")

    # Graphique 3 — % à l'heure selon le délai d'arrivée
    st.markdown('<div class="section-title">Taux de ponctualité selon l\'avance à l\'arrivée</div>', unsafe_allow_html=True)

    bins = [-120, -90, -60, -45, -30, -15, 0, 30]
    labels = ['>90min', '60-90min', '45-60min', '30-45min', '15-30min', '0-15min', 'Après convoc']
    df_valid['arrival_bucket'] = pd.cut(df_valid['stadium_vs_planned'], bins=bins, labels=labels)

    bucket_stats = df_valid.groupby('arrival_bucket', observed=True).agg(
        total=('start_vs_planned', 'count'),
        on_time=('start_vs_planned', lambda x: (x <= 0).sum())
    ).assign(pct_on_time=lambda x: x['on_time'] / x['total'] * 100).reset_index()

    fig3 = px.bar(
        bucket_stats, x='arrival_bucket', y='pct_on_time',
        color='pct_on_time', color_continuous_scale=['#e94560', '#2b9348'],
        labels={'arrival_bucket': 'Avance à l\'arrivée', 'pct_on_time': '% à l\'heure au poste'},
        title="Plus on arrive tôt, plus on est à l'heure au poste — mais jusqu'à quel point ?"
    )
    fig3.add_hline(y=50, line_dash="dot", line_color="white", annotation_text="50%")
    fig3.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig3, use_container_width=True)

# ─────────────────────────────────────────────
# SECTION 3 — PROCESSING
# ─────────────────────────────────────────────
elif section == "⚙️ Processing":
    st.markdown("## ⚙️ Processing")
    st.markdown("Analyse du temps entre l'arrivée au stade et la prise de poste effective.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Processing médian", f"{df_valid['process_time'].median():.0f} min")
    col2.metric("Processing moyen", f"{df_valid['process_time'].mean():.0f} min")
    col3.metric("Processing P90", f"{df_valid['process_time'].quantile(0.9):.0f} min",
                help="90% des shifts ont un processing inférieur à cette durée")

    # Distribution
    st.markdown('<div class="section-title">Distribution du temps de processing</div>', unsafe_allow_html=True)

    fig1 = px.histogram(
        df_valid, x='process_time', nbins=60,
        color_discrete_sequence=[PALETTE[2]],
        labels={'process_time': 'Processing time (min)'},
        title="Distribution du processing time"
    )
    fig1.add_vline(x=df_valid['process_time'].median(), line_dash="dash",
                   line_color="orange",
                   annotation_text=f"Médiane : {df_valid['process_time'].median():.0f} min")
    fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig1, use_container_width=True)

    # Processing par type d'événement
    if 'event_type' in df.columns:
        st.markdown('<div class="section-title">Processing médian par type d\'événement</div>', unsafe_allow_html=True)

        proc_event = df_valid.groupby('event_type')['process_time'].median().reset_index()
        proc_event.columns = ['event_type', 'median_process']

        fig2 = px.bar(
            proc_event.sort_values('median_process', ascending=True),
            x='median_process', y='event_type', orientation='h',
            color='median_process', color_continuous_scale=['#2b9348', '#e94560'],
            labels={'median_process': 'Processing médian (min)', 'event_type': 'Type d\'événement'},
            title="Processing médian par type d'événement"
        )
        fig2.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)

    # Corrélation processing → retard
    st.markdown('<div class="section-title">Corrélation : processing → retard à la prise de poste</div>', unsafe_allow_html=True)

    sample2 = df_valid[['process_time', 'start_vs_planned']].dropna().sample(
        min(3000, len(df_valid)), random_state=42
    )
    r2, _ = stats.pearsonr(sample2['process_time'], sample2['start_vs_planned'])

    fig3 = px.scatter(
        sample2, x='process_time', y='start_vs_planned',
        opacity=0.3, color_discrete_sequence=[PALETTE[2]],
        trendline='ols', trendline_color_override=PALETTE[1],
        labels={
            'process_time': 'Processing time (min)',
            'start_vs_planned': 'Retard à la prise de poste (min)'
        },
        title=f"Processing vs Retard — r = {r2:.2f}"
    )
    fig3.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="À l'heure")
    fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig3, use_container_width=True)

    st.warning(f"**r = {r2:.2f}** — Plus le processing est long, plus le retard s'accumule. "
               "C'est le facteur principal identifié par l'étude.")

# ─────────────────────────────────────────────
# SECTION 4 — FIDÉLISATION
# ─────────────────────────────────────────────
elif section == "🤝 Fidélisation":
    st.markdown("## 🤝 Fidélisation")
    st.markdown("Analyse des profils pour orienter la stratégie de recrutement et de rétention.")

    tab1, tab2, tab3 = st.tabs(["👤 Genre", "📍 Département", "🎂 Âge"])

    # TAB 1 — Genre
    with tab1:
        gender_stats = df.groupby('gender').agg(
            total=('shift_id', 'count'),
            no_show=('no_show', 'sum')
        ).assign(no_show_rate=lambda x: x['no_show'] / x['total'] * 100).reset_index()

        fig_g1 = px.bar(
            gender_stats, x='gender', y='no_show_rate',
            color='gender', color_discrete_sequence=PALETTE,
            labels={'no_show_rate': 'Taux de no-show (%)', 'gender': 'Genre'},
            title="Taux de no-show par genre"
        )
        fig_g1.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_g1, use_container_width=True)

        fig_g2 = px.box(
            df_valid.dropna(subset=['gender', 'stadium_vs_planned']),
            x='gender', y='stadium_vs_planned',
            color='gender', color_discrete_sequence=PALETTE,
            labels={'stadium_vs_planned': 'Arrivée vs prévu (min)', 'gender': 'Genre'},
            title="Ponctualité par genre"
        )
        fig_g2.add_hline(y=0, line_dash="dash", line_color="red")
        fig_g2.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_g2, use_container_width=True)

    # TAB 2 — Département
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
                'avg_arrival': 'Arrivée moyenne vs prévu (min)',
                'no_show_rate': 'Taux de no-show (%)',
                'total': 'Nb shifts'
            },
            title="Département : arrivée au stade vs taux de no-show"
        )
        fig_d1.update_traces(textposition='top center')
        fig_d1.update_layout(plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_d1, use_container_width=True)

    # TAB 3 — Âge
    with tab3:
        age_stats = df_valid.groupby('age_group', observed=True).agg(
            total=('shift_id', 'count'),
            no_show_rate=('no_show', 'mean'),
            median_arrival=('stadium_vs_planned', 'median'),
            pct_late=('start_vs_planned', lambda x: (x > 0).mean() * 100)
        ).reset_index()
        age_stats['no_show_rate'] = age_stats['no_show_rate'] * 100

        fig_a1 = px.bar(
            age_stats, x='age_group', y='no_show_rate',
            color='no_show_rate', color_continuous_scale=['#2b9348', '#e94560'],
            labels={'age_group': 'Tranche d\'âge', 'no_show_rate': 'Taux de no-show (%)'},
            title="Taux de no-show par tranche d'âge"
        )
        fig_a1.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_a1, use_container_width=True)

        fig_a2 = px.bar(
            age_stats, x='age_group', y='median_arrival',
            color='median_arrival', color_continuous_scale=['#e94560', '#2b9348'],
            labels={'age_group': 'Tranche d\'âge', 'median_arrival': 'Arrivée médiane vs prévu (min)'},
            title="Ponctualité par tranche d'âge — l'hypothèse âge validée ou non ?"
        )
        fig_a2.add_hline(y=-60, line_dash="dash", line_color="orange",
                         annotation_text="Seuil recommandé : -60 min")
        fig_a2.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_a2, use_container_width=True)

        st.info("Ce graphique valide ou invalide empiriquement l'hypothèse : "
                "les profils plus âgés arrivent-ils plus tôt ?")
