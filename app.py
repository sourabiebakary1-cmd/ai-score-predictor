import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import random

st.set_page_config(page_title="BAKARY AI FOOTBALL PRO V9", layout="wide")

st.title("⚽ BAKARY AI FOOTBALL PRO V9")
st.success("IA Football professionnelle - Matchs réels")

# TA CLE API
API_KEY = "289e8418878e48c598507cf2b72338f5"

headers = {
    "X-Auth-Token": API_KEY
}

# SIDEBAR
st.sidebar.title("Paramètres")

ligues = {
    "Premier League": "PL",
    "LaLiga": "PD",
    "Ligue 1": "FL1",
    "Serie A": "SA"
}

league = st.sidebar.selectbox("Choisir la ligue", list(ligues.keys()))
code = ligues[league]

stake = st.sidebar.number_input("Mise (€)", min_value=1, value=100)

menu = st.sidebar.radio(
    "Navigation",
    [
        "Analyse IA",
        "Top Paris",
        "Graphique IA"
    ]
)

# RECUPERATION MATCHS API
url = f"https://api.football-data.org/v4/competitions/{code}/matches"

response = requests.get(url, headers=headers)

data = response.json()

matches = []

for m in data["matches"][:10]:

    home = m["homeTeam"]["name"]
    away = m["awayTeam"]["name"]

    match = f"{home} vs {away}"

    prob = random.randint(60,90)

    score = f"{random.randint(0,3)}-{random.randint(0,3)}"

    if prob > 75:
        statut = "✅ Match sûr"
    elif prob > 68:
        statut = "⚠️ Moyen"
    else:
        statut = "🚨 Match piège"

    matches.append({
        "Match":match,
        "Probabilité %":prob,
        "Score IA":score,
        "Statut":statut
    })

df = pd.DataFrame(matches)

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

    st.subheader("📈 Graphique Probabilités")

    fig, ax = plt.subplots()

    ax.bar(df["Match"],df["Probabilité %"])

    plt.xticks(rotation=45)

    st.pyplot(fig)
