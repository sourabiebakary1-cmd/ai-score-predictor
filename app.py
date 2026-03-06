import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import requests

API_KEY = "64907d87f835d9696c8d51b314693e51"

url = "https://v3.football.api-sports.io/fixtures?league=39&season=2023"

headers = {
    "x-apisports-key": API_KEY
}

response = requests.get(url, headers=headers)
api_data = response.json()
st.set_page_config(page_title="Bakary Predictor", layout="centered")

st.title("🔥 BAKARY PREDICTOR ULTRA PRO")
mode = st.selectbox("Choisir le mode", ["Championnat Réel", "FIFA 5x5"])

fixtures = api_data["response"]

home_teams = []
away_teams = []

for match in fixtures:
    home_teams.append(match["teams"]["home"]["name"])
    away_teams.append(match["teams"]["away"]["name"])

teams = sorted(list(set(home_teams + away_teams)))
# Charger les données


teams = sorted(list(set(data["HomeTeam"])))

home_team = st.selectbox("Equipe Domicile", teams)
away_team = st.selectbox("Equipe Extérieure", teams)

if home_team != away_team:

    # Calcul automatique des lambdas
    home_matches = data[data["HomeTeam"] == home_team]
    away_matches = data[data["AwayTeam"] == away_team]

    lambda_home = home_matches["HomeGoals"].mean()
    lambda_away = away_matches["AwayGoals"].mean()

    max_goals = 6
    prob_matrix = np.zeros((max_goals, max_goals))

    for i in range(max_goals):
        for j in range(max_goals):
            prob_matrix[i, j] = (
                poisson.pmf(i, lambda_home) *
                poisson.pmf(j, lambda_away)
            )

    home_win = np.sum(np.tril(prob_matrix, -1))
    draw = np.sum(np.diag(prob_matrix))
    away_win = np.sum(np.triu(prob_matrix, 1))

    over_25 = np.sum(prob_matrix[np.add.outer(range(max_goals), range(max_goals)) > 2])
    under_25 = 1 - over_25
    btts_yes = np.sum(prob_matrix[1:, 1:])
    btts_no = 1 - btts_yes

    markets = {
        "Victoire Domicile": home_win,
        "Match Nul": draw,
        "Victoire Extérieur": away_win,
        "Over 2.5": over_25,
        "Under 2.5": under_25,
        "BTTS Oui": btts_yes,
        "BTTS Non": btts_no
    }

    best_market = max(markets, key=markets.get)
    best_probability = markets[best_market]

    st.subheader("📊 Probabilités")

    st.write(f"🏠 Victoire {home_team} : {round(home_win*100,2)} %")
    st.write(f"🤝 Match nul : {round(draw*100,2)} %")
    st.write(f"✈️ Victoire {away_team} : {round(away_win*100,2)} %")

    # 🎯 Top 3 scores exacts
    st.subheader("🎯 Top 3 Scores Exact")

    flat_probs = prob_matrix.flatten()
    top_indices = flat_probs.argsort()[-3:][::-1]

    # On prend la probabilité la plus élevée
best_probability = max(flat_probs)

home_win_prob = best_probability
draw_prob = 0.2
away_win_prob = 1 - home_win_prob - draw_prob

if best_probability > 55:
    confidence = "🟢 Forte Confiance"
elif best_probability > 40:
    confidence = "🟡 Confiance Moyenne"
else:
    confidence = "🔴 Faible Confiance"

st.subheader("🔥 Meilleur choix")
st.success(f"{best_market}")
st.write(confidence)
