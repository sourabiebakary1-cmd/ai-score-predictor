import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import poisson
import random

st.set_page_config(page_title="BAKARY AI FOOTBALL PRO V7", layout="wide")

st.title("BAKARY AI FOOTBALL PRO V7")
st.success("IA Football professionnelle")

# CLE API
API_KEY = "289e8418878e48c598507cf2b72338f5"

headers = {
    "X-Auth-Token": API_KEY
}

# MENU
st.sidebar.title("Paramètres")

ligues = {
    "Premier League": "PL",
    "LaLiga": "PD",
    "Ligue 1": "FL1",
    "Serie A": "SA",
    "Bundesliga": "BL1"
}

league = st.sidebar.selectbox("Choisir la ligue", list(ligues.keys()))
code = ligues[league]

stake = st.sidebar.number_input("Mise (€)", min_value=1, value=100)

menu = st.sidebar.radio(
    "Navigation",
    [
        "Analyse IA",
        "Top 5 paris sûrs",
        "Graphique IA"
    ]
)

# FAUX DONNÉES MATCH (simulation)
data = {
    "Match": [
        "Team A vs Team B",
        "Team C vs Team D",
        "Team E vs Team F",
        "Team G vs Team H",
        "Team I vs Team J"
    ],
    "Probabilite %": [78, 74, 81, 69, 73]
}

df = pd.DataFrame(data)

top = df.sort_values(by="Probabilite %", ascending=False).head(5)

# ANALYSE IA
if menu == "Analyse IA":
    st.subheader("Analyse IA des matchs")
    st.dataframe(df)

# TOP 5 PARIS
if menu == "Top 5 paris sûrs":
    st.subheader("Top 5 paris les plus sûrs")
    st.dataframe(top)

    st.subheader("Simulation combiné")

    cote = 1

    for i in range(len(top)):
        cote *= 1.45

    gain = stake * cote

    st.write("Cote estimée :", round(cote,2))
    st.write("Gain potentiel :", round(gain,2), "€")

# GRAPHIQUE IA
if menu == "Graphique IA":
    st.subheader("Graphique probabilités")

    fig, ax = plt.subplots()

    ax.bar(df["Match"], df["Probabilite %"])

    plt.xticks(rotation=45)

    st.pyplot(fig)
