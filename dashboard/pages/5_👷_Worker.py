import streamlit as st
import pandas as pd
import plotly.express as px


def render(df, pax):
    st.title("🔎 Détail par Pax")
    st.caption("Dossier individuel complet d'un participant.")

    # --- Sélection ---
    pax_ids = sorted(df["pax_id"].dropna().unique())

    if not pax_ids:
        st.warning("Aucun pax disponible pour le filtre actuel.")
        return

    selected = st.selectbox(
        f"Sélectionne un pax_id ({len(pax_ids)} disponibles)",
        pax_ids,
    )

    pax_data = df[df["pax_id"] == selected].sort_values("shift_planned")

    if pax_data.empty:
        st.warning("Aucune donnée pour ce pax.")
        return

    # --- Bloc 1 : Identité ---
    st.subheader("🪪 Identité")
    pax_info = pax[pax["pax_id"] == selected]

    if not pax_info.empty:
        row = pax_info.iloc[0]
        age = None
        if pd.notna(row["birth_date"]):
            age = int((pd.Timestamp.now() - row["birth_date"]).days / 365.25)

        anciennete = None
        if pd.notna(row["registration_date"]):
            anciennete = int((pd.Timestamp.now() - row["registration_date"]).days / 30)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Genre", "Homme" if row["is_male"] else "Femme")
        c2.metric("Âge", f"{age} ans" if age else "N/A")
        c3.metric("Code postal", str(row["postal_code"]))
        c4.metric("Ancienneté", f"{anciennete} mois" if anciennete else "N/A")
    else:
        st.info("Pas d'infos identité disponibles pour ce pax.")

    st.divider()

    # --- Bloc 2 : KPIs personnels ---
    st.subheader("📊 KPIs personnels")

    total = len(pax_data)
    noshows = int(pax_data["is_noshow"].sum())
    lates = int(pax_data["is_late"].sum())
    noshow_rate = round(noshows / total * 100, 1) if total else 0
    late_rate = round(lates / total * 100, 1) if total else 0
    avg_delay = round(pax_data["delay_start_min"].mean(), 1)
    avg_duration = round(pax_data["actual_duration_h"].mean(), 1)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Shifts totaux", total)
    c2.metric("Taux No-Show", f"{noshow_rate}%")
    c3.metric("Taux Retard", f"{late_rate}%")
    c4.metric("Retard moyen", f"{avg_delay} min")
    c5.metric("Durée moy.", f"{avg_duration} h")

    # --- Bloc 3 : Comparaison vs moyenne ---
    st.subheader("🎯 Performance vs moyenne globale")

    global_noshow = round(df["is_noshow"].mean() * 100, 1)
    global_late = round(df["is_late"].mean() * 100, 1)
    global_delay = round(df["delay_start_min"].mean(), 1)

    delta_noshow = round(noshow_rate - global_noshow, 1)
    delta_late = round(late_rate - global_late, 1)
    delta_delay = round(avg_delay - global_delay, 1)

    c1, c2, c3 = st.columns(3)
    c1.metric(
        "No-Show vs moyenne",
        f"{noshow_rate}%",
        delta=f"{delta_noshow:+.1f} pts",
        delta_color="inverse",
    )
    c2.metric(
        "Retard vs moyenne",
        f"{late_rate}%",
        delta=f"{delta_late:+.1f} pts",
        delta_color="inverse",
    )
    c3.metric(
        "Retard moy. vs moyenne",
        f"{avg_delay} min",
        delta=f"{delta_delay:+.1f} min",
        delta_color="inverse",
    )

    st.caption("🟢 vert = meilleur que la moyenne. 🔴 rouge = pire.")

    st.divider()

    # --- Bloc 4 : Répartition par job ---
    st.subheader("👷 Répartition par poste")

    by_job = (
        pax_data.groupby("job_id")
        .agg(
            shifts=("shift_id", "count"),
            noshow_rate=("is_noshow", lambda x: round(x.mean() * 100, 1)),
            late_rate=("is_late", lambda x: round(x.mean() * 100, 1)),
        )
        .reset_index()
        .sort_values("shifts", ascending=False)
    )

    c1, c2 = st.columns([1, 1])
    with c1:
        fig = px.bar(
            by_job,
            x="job_id",
            y="shifts",
            title="Volume de shifts par job",
            labels={"shifts": "Nb shifts", "job_id": "Job"},
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.dataframe(by_job, use_container_width=True, hide_index=True)

    # --- Bloc 5 : Répartition par location ---
    st.subheader("📍 Répartition par location")

    by_loc = (
        pax_data.groupby("loc_id")
        .agg(
            shifts=("shift_id", "count"),
            noshow_rate=("is_noshow", lambda x: round(x.mean() * 100, 1)),
            late_rate=("is_late", lambda x: round(x.mean() * 100, 1)),
        )
        .reset_index()
        .sort_values("shifts", ascending=False)
    )

    c1, c2 = st.columns([1, 1])
    with c1:
        fig = px.pie(
            by_loc,
            values="shifts",
            names="loc_id",
            title="Distribution des locations",
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.dataframe(by_loc, use_container_width=True, hide_index=True)

    # --- Bloc 6 : Liste des événements ---
    st.subheader("📅 Événements parcourus")

    by_event = (
        pax_data.groupby("event_id")
        .agg(
            shifts=("shift_id", "count"),
            noshows=("is_noshow", "sum"),
            retards=("is_late", "sum"),
            premier_shift=("shift_planned", "min"),
            dernier_shift=("shift_planned", "max"),
        )
        .reset_index()
        .sort_values("premier_shift")
    )

    st.dataframe(by_event, use_container_width=True, hide_index=True)

    # --- Bloc 7 : Historique scans ---
    st.subheader("⏱️ Historique des scans")

    show_only_anomalies = st.checkbox("Afficher uniquement les anomalies (no-show ou retard)")

    display_cols = [
        "shift_id", "event_id", "job_id", "loc_id",
        "shift_planned", "shift_start", "shift_stadium",
        "shift_acr", "shift_locker", "shift_end",
        "is_noshow", "is_late", "delay_start_min", "actual_duration_h",
    ]

    historical = pax_data[display_cols].copy()
    if show_only_anomalies:
        historical = historical[(historical["is_noshow"]) | (historical["is_late"])]

    st.dataframe(historical.reset_index(drop=True), use_container_width=True)

    # --- Bloc 8 : Évolution temporelle ---
    st.subheader("📈 Évolution du comportement dans le temps")

    if len(pax_data) >= 3:
        timeline = pax_data.copy()
        timeline["month"] = timeline["shift_planned"].dt.to_period("M").astype(str)

        evol = (
            timeline.groupby("month")
            .agg(
                shifts=("shift_id", "count"),
                noshow_rate=("is_noshow", lambda x: round(x.mean() * 100, 1)),
                late_rate=("is_late", lambda x: round(x.mean() * 100, 1)),
            )
            .reset_index()
        )

        fig = px.line(
            evol,
            x="month",
            y=["noshow_rate", "late_rate"],
            title="Taux de no-show et retard par mois",
            labels={"value": "Taux (%)", "month": "Mois", "variable": "Métrique"},
            markers=True,
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Pas assez de données historiques pour tracer une évolution (min. 3 shifts).")
