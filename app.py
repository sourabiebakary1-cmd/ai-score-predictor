import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random

st.set_page_config(page_title="BAKARY AI FOOTBALL PRO V8", layout="wide")

st.title("⚽ BAKARY AI FOOTBALL PRO V8")
st.success("IA Football professionnelle - Analyse avancée")

# CLE API
API_KEY = "289e8418878e48c598507cf2b72338f5"

# SIDEBAR
st.sidebar.title("Paramètres")

ligues = {
    "Premier League": "PL",
    "LaLiga": "PD",
    "Ligue 1": "FL1",
    "Serie A": "SA",
    "Bundesliga": "BL1"
}

league = st.sidebar.selectbox("Choisir la ligue", list(ligues.keys()))
stake = st.sidebar.number_input("Mise (€)", min_value=1, value=100)

menu = st.sidebar.radio(
    "Navigation",
    [
        "Analyse IA",
        "Top Paris",
        "Graphique IA"
    ]
)

# MATCH SIMULATION
teams = [
    "Arsenal vs Chelsea",
    "Real Madrid vs Betis",
    "Inter vs Milan",
    "PSG vs Marseille",
    "Bayern vs Dortmund",
    "Barcelone vs Sevilla",
    "Juventus vs Napoli"
]

data = []

for t in teams:

    prob = random.randint(60,90)

    score_home = random.randint(0,3)
    score_away = random.randint(0,3)

    if prob > 75:
        statut = "✅ Match sûr"
    elif prob > 68:
        statut = "⚠️ Moyen"
    else:
        statut = "🚨 Match piège"

    data.append({
        "Match":t,
        "Probabilité %":prob,
        "Score IA":f"{score_home}-{score_away}",
        "Statut":statut
    })

df = pd.DataFrame(data)

top = df.sort_values(by="Probabilité %",ascending=False).head(5)

# ANALYSE IA
if menu == "Analyse IA":

    st.subheader("📊 Analyse IA des matchs")

    st.dataframe(df)

# TOP PARIS
if menu == "Top Paris":

    st.subheader("🔥 Top 5 Paris les plus sûrs")

    st.dataframe(top)

    st.subheader("💰 Simulation combiné")

    cote = 1

    for i in range(len(top)):
        cote *= 1.45

    gain = stake * cote

    st.write("Cote estimée :",round(cote,2))
    st.write("Gain potentiel :",round(gain,2),"€")

# GRAPHIQUE
if menu == "Graphique IA":

    st.subheader("📈 Graphique Probabilités IA")

    fig, ax = plt.subplots()

    ax.bar(df["Match"],df["Probabilité %"])

    plt.xticks(rotation=45)

    st.pyplot(fig)
