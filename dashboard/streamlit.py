import streamlit as st
import pandas as pd


st.title("CRIT_DASHBOARD EVENT")
st.write("Premier texte du dashboard")
if st.checkbox("AFFICHER") :
	st.write("ICI DU TEXTE DEVRAIS S'AFFICHER")


df = pd.read_csv("/home/prime/Projets/2026_PROJECT-DA/DATA/new_dataset.csv")
st.dataframe(df)


