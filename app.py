import streamlit as st
import numpy as np
import requests
import pandas as pd
from scipy.stats import poisson
from datetime import datetime

st.set_page_config(page_title="BAKARY AI", layout="wide")

st.title("🤖⚽ BAKARY AI FOOTBALL PREDICTOR")

API_KEY = "289e8418878e48c598507cf2b72338f5"

headers = {
    "X-Auth-Token": API_KEY
}

ligues = {
    "Premier League":"PL",
    "LaLiga":"PD",
    "Ligue 1":"FL1",
    "Serie A":"SA",
    "Bundesliga":"BL1",
    "Championship":"ELC",
    "Primeira Liga":"PPL"
}

league = st.selectbox("Choisir la ligue", list(ligues.keys()))
league_code = ligues[league]

stake = st.number_input("Mise (€)", min_value=1, value=100)

match_url = f"https://api.football-data.org/v4/competitions/{league_code}/matches"
standings_url = f"https://api.football-data.org/v4/competitions/{league_code}/standings"

try:
    matches_data = requests.get(match_url, headers=headers).json()
    standings_data = requests.get(standings_url, headers=headers).json()
except:
    st.error("Erreur connexion API")
    st.stop()

matches = matches_data.get("matches", [])

today = datetime.utcnow()

future_matches = []

for m in matches:
    try:
        date_match = datetime.fromisoformat(m["utcDate"].replace("Z",""))
        if date_match > today:
            future_matches.append(m)
    except:
        pass

standings = standings_data["standings"][0]["table"]

attack = {}
defense = {}

for team in standings:

    name = team["team"]["name"]
    played = team["playedGames"]

    if played == 0:
        continue

    attack[name] = team["goalsFor"] / played
    defense[name] = team["goalsAgainst"] / played

results = []

for m in future_matches[:10]:

    home = m["homeTeam"]["name"]
    away = m["awayTeam"]["name"]

    home_attack = attack.get(home,1.5)
    away_attack = attack.get(away,1.5)

    home_def = defense.get(home,1.2)
    away_def = defense.get(away,1.2)

    home_lambda = max(0.4, home_attack / away_def)
    away_lambda = max(0.4, away_attack / home_def)

    max_goals = 6

    matrix = np.zeros((max_goals,max_goals))

    for i in range(max_goals):
        for j in range(max_goals):
            matrix[i,j] = poisson.pmf(i,home_lambda) * poisson.pmf(j,away_lambda)

    best = np.unravel_index(np.argmax(matrix), matrix.shape)

    score = f"{best[0]}-{best[1]}"
    prob = matrix[best]*100

    results.append({
        "Match": f"{home} vs {away}",
        "Score probable": score,
        "Probabilité %": round(prob,2)
    })

df = pd.DataFrame(results)

st.subheader("🎯 Scores les plus probables")

st.dataframe(df)

odds = 8

gain = stake * odds

st.subheader("💰 Gain potentiel")

st.write(round(gain,2),"€")
