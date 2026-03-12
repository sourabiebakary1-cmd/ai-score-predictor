import streamlit as st
import numpy as np
import requests
from scipy.stats import poisson
from datetime import datetime

st.set_page_config(page_title="Bakary Predictor AI", layout="centered")

st.title("⚽ BAKARY AI FOOTBALL PREDICTOR V2")
st.write("Analyse intelligente des matchs du jour")

# API KEY
API_KEY = "64907d87f835d9696c8d51b314693e51"

url = "https://v3.football.api-sports.io/fixtures"

headers = {
    "x-apisports-key": API_KEY
}

today = datetime.today().strftime("%Y-%m-%d")

params = {
    "date": today
}

matches = []

st.write("🔎 Recherche des matchs...")

try:
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if "response" in data and len(data["response"]) > 0:
        for match in data["response"]:
            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]
            league = match["league"]["name"]
            matches.append((home, away, league))
    else:
        st.warning("Aucun match trouvé aujourd'hui")

except:
    st.error("Erreur connexion API")

if matches:

    match_names = [f"{m[0]} vs {m[1]} ({m[2]})" for m in matches]

    selected = st.selectbox("Choisir un match", match_names)

    index = match_names.index(selected)

    home_team = matches[index][0]
    away_team = matches[index][1]

    st.subheader("🏟️ Match sélectionné")

    st.write("🏠", home_team)
    st.write("✈️", away_team)

    st.subheader("📊 Paramètres IA")

    home_attack = st.slider("Attaque domicile", 0.5, 3.0, 1.6)
    away_attack = st.slider("Attaque extérieur", 0.5, 3.0, 1.3)

    home_defense = st.slider("Défense domicile", 0.5, 3.0, 1.1)
    away_defense = st.slider("Défense extérieur", 0.5, 3.0, 1.2)

    if st.button("🤖 Lancer analyse IA"):

        home_lambda = home_attack * away_defense
        away_lambda = away_attack * home_defense

        max_goals = 7

        home_probs = [poisson.pmf(i, home_lambda) for i in range(max_goals)]
        away_probs = [poisson.pmf(i, away_lambda) for i in range(max_goals)]

        matrix = np.outer(home_probs, away_probs)

        home_win = np.sum(np.tril(matrix, -1))
        draw = np.sum(np.diag(matrix))
        away_win = np.sum(np.triu(matrix, 1))

        st.subheader("📊 Probabilités résultat")

        st.metric("🏠 Victoire domicile", f"{round(home_win*100,2)} %")
        st.metric("🤝 Match nul", f"{round(draw*100,2)} %")
        st.metric("✈️ Victoire extérieur", f"{round(away_win*100,2)} %")

        best_score = np.unravel_index(matrix.argmax(), matrix.shape)

        st.subheader("🔥 Score le plus probable")

        st.success(f"{home_team} {best_score[0]} - {best_score[1]} {away_team}")

        st.subheader("🎯 Conseils IA")

        if home_win > away_win:
            st.info("💡 Pari conseillé : Victoire domicile")
        elif away_win > home_win:
            st.info("💡 Pari conseillé : Victoire extérieur")
        else:
            st.info("💡 Pari conseillé : Match nul")

else:
    st.warning("Pas de matchs disponibles aujourd'hui")
