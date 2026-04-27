# dashboard/utils/data_loader.py

import pandas as pd
import streamlit as st
import os


DATA_PATH = os.environ.get("DATA_PATH", "/app/data") + "/clean_dataset.csv"



DEPT_MAP = {
    '75': 'Paris', '92': 'Hauts-de-Seine', '93': 'Seine-St-Denis',
    '94': 'Val-de-Marne', '91': 'Essonne', '95': "Val-d'Oise",
    '77': 'Seine-et-Marne', '78': 'Yvelines'
}

PALETTE = ["#1a1a2e", "#e94560", "#0f3460", "#533483", "#2b9348"]


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, low_memory=False)

    df['shift_planned_dt'] = pd.to_datetime(df['shift_planned'], errors='coerce')
    df['shift_stadium_dt'] = pd.to_datetime(df['shift_stadium'], errors='coerce')
    df['shift_start_dt']   = pd.to_datetime(df['shift_start'],   errors='coerce')
    df['shift_end_dt']     = pd.to_datetime(df['shift_end'],     errors='coerce')

    df['no_show']            = df['shift_start'].isna() & df['shift_end'].isna()
    df['stadium_vs_planned'] = (df['shift_stadium_dt'] - df['shift_planned_dt']).dt.total_seconds() / 60
    df['process_time']       = (df['shift_start_dt']   - df['shift_stadium_dt']).dt.total_seconds() / 60
    df['start_vs_planned']   = (df['shift_start_dt']   - df['shift_planned_dt']).dt.total_seconds() / 60
    df['age'] = (pd.Timestamp('2024-01-01') - pd.to_datetime(df['pax_birth'], errors='coerce')).dt.days // 365
    df['gender'] = df['pax_sex'].map({True: 'Male', False: 'Female'})
    df['dept']      = df['pax_zip'].astype(str).str[:2]
    df['dept_name'] = df['dept'].map(DEPT_MAP)

    age_bins   = [16, 20, 25, 30, 35, 40, 50, 99]
    age_labels = ['16-20', '21-25', '26-30', '31-35', '36-40', '41-50', '50+']
    df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=age_labels, right=True)

    return df


def get_valid(df):
    """Filter out outliers for metric computation."""
    return df[
        df['process_time'].between(0, 180) &
        df['stadium_vs_planned'].between(-120, 60) &
        df['start_vs_planned'].notna()
    ].copy()
