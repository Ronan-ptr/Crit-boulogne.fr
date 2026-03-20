import streamlit as st
import pandas as pd


st.title("EVENT ANALYSIS")
#st.write("Premier texte du dashboard")
#if st.checkbox("AFFICHER") :
#	st.write("ICI DU TEXTE DEVRAIS S'AFFICHER")

# DATA LOADING
df = pd.read_csv("/home/prime/Projets/2026_PROJECT-DA/DATA/new_dataset.csv")
#st.dataframe(df) # Print the raw dataframe

# EVENT SELECTION

#st.write("Pick up an event : ")
event_list = list(df["event_file"].unique())
st.selectbox("Pick up an event :", options=event_list)

