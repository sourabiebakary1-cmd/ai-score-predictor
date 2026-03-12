import streamlit as st
import numpy as np
import requests
from scipy.stats import poisson
from datetime import datetime

st.set_page_config(page_title="Bakary AI Predictor V3", layout="centered")

st.title("⚽ BAKARY AI FOOTBALL PREDICTOR V3")

API_KEY = "64907d87f835d9696c8d51b314693e51"

headers = {
    "x-apisports-key": API_KEY
}

fixture_url = "https://v3.football.api-sports.io/fixtures"

today = datetime.today().strftime("%Y-%m-%d")

params = {
    "date": today
}

matches = []

st.write("🔎 Recherche matchs du jour...")

try:
    r = requests.get(fixture_url, headers=headers, params=params)
    data = r.json()

    for m in data["response"]:
        home = m["teams"]["home"]["name"]
        away = m["teams"]["away"]["name"]
        matches.append((home, away))

except:
    st.error("Erreur API")

if matches:

    match_names = [f"{m[0]} vs {m[1]}" for m in matches]

    selected = st.selectbox("Choisir un match", match_names)

    index = match_names.index(selected)

    home_team = matches[index][0]
    away_team = matches[index][1]

    st.subheader("🏟 Match")

    st.write(home_team, "vs", away_team)

    st.subheader("⚙ Paramètres IA")

    home_attack = st.slider("Attaque domicile", 0.5, 3.0, 1.7)
    away_attack = st.slider("Attaque extérieur", 0.5, 3.0, 1.3)

    home_def = st.slider("Défense domicile", 0.5, 3.0, 1.0)
    away_def = st.slider("Défense extérieur", 0.5, 3.0, 1.2)

    if st.button("🤖 Lancer IA"):

        home_lambda = home_attack * away_def
        away_lambda = away_attack * home_def

        max_goals = 7

        home_probs = [poisson.pmf(i, home_lambda) for i in range(max_goals)]
        away_probs = [poisson.pmf(i, away_lambda) for i in range(max_goals)]

        matrix = np.outer(home_probs, away_probs)

        home_win = np.sum(np.tril(matrix, -1))
        draw = np.sum(np.diag(matrix))
        away_win = np.sum(np.triu(matrix, 1))

        st.subheader("📊 Probabilités")

        st.write("🏠 Victoire domicile :", round(home_win*100,2), "%")
        st.write("🤝 Match nul :", round(draw*100,2), "%")
        st.write("✈ Victoire extérieur :", round(away_win*100,2), "%")

        st.subheader("🎯 Top scores probables")

        scores = []

        for i in range(max_goals):
            for j in range(max_goals):
                scores.append(((i,j), matrix[i][j]))

        scores = sorted(scores, key=lambda x: x[1], reverse=True)

        for s in scores[:3]:
            st.write(f"{home_team} {s[0][0]} - {s[0][1]} {away_team}")

        st.subheader("📈 Over / Under 2.5")

        over = 0
        under = 0

        for i in range(max_goals):
            for j in range(max_goals):
                if i+j > 2:
                    over += matrix[i][j]
                else:
                    under += matrix[i][j]

        st.write("Over 2.5 :", round(over*100,2), "%")
        st.write("Under 2.5 :", round(under*100,2), "%")

else:

    st.warning("Aucun match aujourd'hui")
