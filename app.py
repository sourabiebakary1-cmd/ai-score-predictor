import streamlit as st
import numpy as np
import requests
from scipy.stats import poisson
from datetime import datetime, timedelta

st.set_page_config(page_title="Bakary AI Predictor V9", layout="centered")

st.title("⚽ BAKARY AI FOOTBALL PREDICTOR V9")

API_KEY = "TA_CLE_API_ICI"

headers = {
    "x-apisports-key": API_KEY
}

fixtures_url = "https://v3.football.api-sports.io/fixtures"
teams_url = "https://v3.football.api-sports.io/teams/statistics"

ligues = {
    "Premier League": 39,
    "Ligue 1": 61,
    "Bundesliga": 78,
    "Serie A": 135,
    "LaLiga": 140
}

selected_ligue = st.selectbox("Choisir la ligue", list(ligues.keys()))
league_id = ligues[selected_ligue]

matches = []
params = {
    "league": league_id,
    "season": 2024,
    "next": 10
}

r = requests.get(fixtures_url, headers=headers, params=params)

data = r.json()

matches = []

if "response" in data:

    for m in data["response"]:

        home = m["teams"]["home"]["name"]
        away = m["teams"]["away"]["name"]

        home_id = m["teams"]["home"]["id"]
        away_id = m["teams"]["away"]["id"]

        matches.append({
            "home": home,
            "away": away,
            "home_id": home_id,
            "away_id": away_id
        })


        break

if matches:

    match_list = [f"{m['home']} vs {m['away']}" for m in matches]

    selected_match = st.selectbox("Choisir un match", match_list)

    index = match_list.index(selected_match)

    match = matches[index]

    home_team = match["home"]
    away_team = match["away"]

    home_id = match["home_id"]
    away_id = match["away_id"]

    st.subheader(f"{home_team} vs {away_team}")

    if st.button("Analyser le match"):

        params_home = {
            "league": league_id,
            "team": home_id,
            "season": 2024
        }

        params_away = {
            "league": league_id,
            "team": away_id,
            "season": 2024
        }

        r1 = requests.get(teams_url, headers=headers, params=params_home)
        r2 = requests.get(teams_url, headers=headers, params=params_away)

        data_home = r1.json()
        data_away = r2.json()

        try:

            home_goals = data_home["response"]["goals"]["for"]["average"]["home"]
            home_conceded = data_home["response"]["goals"]["against"]["average"]["home"]

            away_goals = data_away["response"]["goals"]["for"]["average"]["away"]
            away_conceded = data_away["response"]["goals"]["against"]["average"]["away"]

            home_lambda = float(home_goals) * float(away_conceded)
            away_lambda = float(away_goals) * float(home_conceded)

            max_goals = 7

            home_probs = [poisson.pmf(i, home_lambda) for i in range(max_goals)]
            away_probs = [poisson.pmf(i, away_lambda) for i in range(max_goals)]

            matrix = np.outer(home_probs, away_probs)

            home_win = np.sum(np.tril(matrix, -1))
            draw = np.sum(np.diag(matrix))
            away_win = np.sum(np.triu(matrix, 1))

            st.subheader("Probabilité résultat")

            st.write("Victoire domicile :", round(home_win*100,2), "%")
            st.write("Match nul :", round(draw*100,2), "%")
            st.write("Victoire extérieur :", round(away_win*100,2), "%")

            scores = []

            for i in range(max_goals):
                for j in range(max_goals):

                    scores.append(((i,j), matrix[i][j]))

            scores.sort(key=lambda x: x[1], reverse=True)

            st.subheader("Top 3 scores probables")

            for s in scores[:3]:

                st.write(f"{home_team} {s[0][0]} - {s[0][1]} {away_team} : {round(s[1]*100,2)}%")

        except:

            st.error("Erreur récupération statistiques")

else:

    st.warning("Aucun match trouvé")
