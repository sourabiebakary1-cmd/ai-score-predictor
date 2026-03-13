import streamlit as st
import numpy as np
import requests
from scipy.stats import poisson
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="Bakary AI Predictor V8", layout="centered")

st.title("⚽ BAKARY AI FOOTBALL PREDICTOR V8")

API_KEY = "TA_CLE_API_ICI"

headers = {
    "x-apisports-key": API_KEY
}

fixture_url = "https://v3.football.api-sports.io/fixtures"

ligues = {
    "Premier League": 39,
    "Ligue 1": 61,
    "Bundesliga": 78,
    "Serie A": 135,
    "LaLiga": 140
}

selected_ligue_name = st.selectbox("Choisir la ligue", list(ligues.keys()))
league_id = ligues[selected_ligue_name]

matches = []

for i in range(7):
    date_check = (datetime.today() + timedelta(days=i)).strftime("%Y-%m-%d")

    params = {
        "date": date_check,
        "season": 2025,
        "league": league_id
    }

    r = requests.get(fixture_url, headers=headers, params=params)
    data = r.json()

    if "response" in data and len(data["response"]) > 0:

        for m in data["response"]:

            home = m["teams"]["home"]["name"]
            away = m["teams"]["away"]["name"]

            matches.append({
                "home": home,
                "away": away,
                "date": date_check
            })

        break


if matches:

    st.success("Matchs trouvés")

    match_names = [f"{m['home']} vs {m['away']}" for m in matches]

    selected = st.selectbox("Choisir un match", match_names)

    index = match_names.index(selected)

    match = matches[index]

    home_team = match["home"]
    away_team = match["away"]

    st.subheader(f"{home_team} vs {away_team}")

    st.subheader("Paramètres IA")

    home_attack = st.slider("Attaque domicile", 0.5, 3.0, 1.6)
    away_attack = st.slider("Attaque extérieur", 0.5, 3.0, 1.3)

    home_def = st.slider("Défense domicile", 0.5, 3.0, 1.0)
    away_def = st.slider("Défense extérieur", 0.5, 3.0, 1.2)

    if st.button("Lancer la prédiction IA"):

        home_lambda = home_attack * away_def
        away_lambda = away_attack * home_def

        max_goals = 7

        home_probs = [poisson.pmf(i, home_lambda) for i in range(max_goals)]
        away_probs = [poisson.pmf(i, away_lambda) for i in range(max_goals)]

        matrix = np.outer(home_probs, away_probs)

        home_win = np.sum(np.tril(matrix, -1))
        draw = np.sum(np.diag(matrix))
        away_win = np.sum(np.triu(matrix, 1))

        st.subheader("Probabilités résultat")

        results = {
            "Résultat": ["Victoire domicile", "Nul", "Victoire extérieur"],
            "Probabilité": [home_win*100, draw*100, away_win*100]
        }

        fig = px.bar(results, x="Résultat", y="Probabilité", text="Probabilité")

        st.plotly_chart(fig)

        scores = []

        for i in range(max_goals):
            for j in range(max_goals):

                scores.append(((i, j), matrix[i][j]))

        scores.sort(key=lambda x: x[1], reverse=True)

        st.subheader("Top 5 scores probables")

        for s in scores[:5]:

            st.write(f"{home_team} {s[0][0]} - {s[0][1]} {away_team} : {round(s[1]*100,2)} %")

        over15 = sum(matrix[i][j] for i in range(max_goals) for j in range(max_goals) if i+j > 1)
        over25 = sum(matrix[i][j] for i in range(max_goals) for j in range(max_goals) if i+j > 2)
        over35 = sum(matrix[i][j] for i in range(max_goals) for j in range(max_goals) if i+j > 3)

        st.subheader("Over / Under")

        st.write("Over 1.5 :", round(over15*100,2), "%")
        st.write("Over 2.5 :", round(over25*100,2), "%")
        st.write("Over 3.5 :", round(over35*100,2), "%")

        btts = sum(matrix[i][j] for i in range(1, max_goals) for j in range(1, max_goals))

        st.subheader("BTTS")

        st.write("Les deux équipes marquent :", round(btts*100,2), "%")

else:

    st.warning("Aucun match trouvé")
