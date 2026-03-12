import streamlit as st
import numpy as np
import requests
from scipy.stats import poisson
from datetime import datetime

st.set_page_config(page_title="Bakary Predictor Pro", layout="centered")

st.title("⚽ BAKARY AI FOOTBALL PREDICTOR PRO")
st.header("📅 Matchs du jour")
matches = [
("Real Madrid", "Barcelona"),
("Manchester City", "Liverpool"),
("PSG", "Marseille"),
("Bayern Munich", "Dortmund")
]



today = datetime.today().strftime("%Y-%m-%d")

params = {
    "date": today
}

matches = []

st.write("🔎 Recherche des matchs...")

try:
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if "response" in data:
        for match in data["response"]:
            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]
            matches.append((home, away))
    else:
        st.warning("Aucun match trouvé")

except:
    st.error("Erreur API")

if matches:

    match_names = [f"{m[0]} vs {m[1]}" for m in matches]

    selected = st.selectbox("Choisir un match", match_names)

    index = match_names.index(selected)

    home_team = matches[index][0]
    away_team = matches[index][1]

    st.write("🏠", home_team)
    st.write("✈️", away_team)

    st.subheader("📊 Statistiques équipes")

    home_attack = st.slider("Force attaque domicile", 0.5, 3.0, 1.5)
    away_attack = st.slider("Force attaque extérieur", 0.5, 3.0, 1.2)

    home_defense = st.slider("Défense domicile", 0.5, 3.0, 1.0)
    away_defense = st.slider("Défense extérieur", 0.5, 3.0, 1.2)

    if st.button("🤖 Lancer analyse IA"):

        home_lambda = home_attack * away_defense
        away_lambda = away_attack * home_defense

        max_goals = 6

        home_goals = [poisson.pmf(i, home_lambda) for i in range(max_goals)]
        away_goals = [poisson.pmf(i, away_lambda) for i in range(max_goals)]

        matrix = np.outer(home_goals, away_goals)

        home_win = np.sum(np.tril(matrix, -1))
        draw = np.sum(np.diag(matrix))
        away_win = np.sum(np.triu(matrix, 1))

        st.subheader("📊 Probabilités")

        st.write("🏠 Victoire domicile :", round(home_win * 100, 2), "%")
        st.write("🤝 Match nul :", round(draw * 100, 2), "%")
        st.write("✈️ Victoire extérieur :", round(away_win * 100, 2), "%")

        st.subheader("🔥 Score le plus probable")

        best_score = np.unravel_index(matrix.argmax(), matrix.shape)

        st.success(f"{home_team} {best_score[0]} - {best_score[1]} {away_team}")
