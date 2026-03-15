import streamlit as st
import numpy as np
import requests
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import poisson
from datetime import datetime

st.set_page_config(page_title="BAKARY AI V36 QUANTUM PRO", layout="wide")

st.title("🤖⚽ BAKARY AI FOOTBALL PREDICTOR V36 QUANTUM PRO")

API_KEY = "TA_CLE_API"

headers = {"X-Auth-Token": API_KEY}

ligues = {
    "Premier League": "PL",
    "Ligue 1": "FL1",
    "Bundesliga": "BL1",
    "Serie A": "SA",
    "LaLiga": "PD"
}

selected_ligue = st.selectbox("Choisir la ligue", list(ligues.keys()))
league_code = ligues[selected_ligue]

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

if len(matches) == 0:
    st.warning("Aucun match trouvé dans l'API")
    st.stop()

# filtrer matchs futurs
today = datetime.utcnow()

future_matches = []

for m in matches:
    try:
        match_date = datetime.fromisoformat(m["utcDate"].replace("Z",""))
        if match_date > today:
            future_matches.append(m)
    except:
        continue

if len(future_matches) == 0:
    st.warning("Pas de matchs futurs disponibles")
    st.stop()

matches = future_matches

standings = standings_data.get("standings", [])

if len(standings) == 0:
    st.warning("Classement indisponible")
    st.stop()

table = standings[0]["table"]

rank = {}
goals_for = {}
goals_against = {}

for team in table:
    name = team["team"]["name"]
    rank[name] = team["position"]
    goals_for[name] = team["goalsFor"]
    goals_against[name] = team["goalsAgainst"]

results = []

for m in matches:

    home = m["homeTeam"]["name"]
    away = m["awayTeam"]["name"]

    home_attack = goals_for.get(home,20)/10
    away_attack = goals_for.get(away,20)/10

    home_def = goals_against.get(home,20)/10
    away_def = goals_against.get(away,20)/10

    home_lambda = max(0.3, 1.8 + home_attack - away_def)
    away_lambda = max(0.3, 1.5 + away_attack - home_def)

    max_goals = 6

    home_probs = [poisson.pmf(i,home_lambda) for i in range(max_goals)]
    away_probs = [poisson.pmf(i,away_lambda) for i in range(max_goals)]

    matrix = np.outer(home_probs,away_probs)

    home_win = np.sum(np.tril(matrix,-1))
    away_win = np.sum(np.triu(matrix,1))
    draw = np.sum(np.diag(matrix))

    prob = max(home_win,away_win,draw)

    if prob == home_win:
        favori = home
    elif prob == away_win:
        favori = away
    else:
        favori = "Draw"

    score_home = np.argmax(home_probs)
    score_away = np.argmax(away_probs)

    results.append({
        "Match": f"{home} vs {away}",
        "Favori IA": favori,
        "Score probable": f"{score_home}-{score_away}",
        "Probabilité %": round(prob*100,2)
    })

df = pd.DataFrame(results)

st.subheader("📊 Analyse IA complète")
st.dataframe(df)

ticket = df[df["Probabilité %"] > 65].head(5)

st.subheader("🎯 Ticket IA automatique")

if len(ticket) > 0:
    st.dataframe(ticket)
else:
    st.write("Pas de ticket aujourd'hui")

odds = 1.8
combined = odds ** len(ticket)

gain = stake * combined

st.subheader("💰 Simulation gain")

st.write("Probabilité moyenne :", round(ticket["Probabilité %"].mean(),2),"%")
st.write("Gain potentiel :", round(gain,2),"€")

fig, ax = plt.subplots()

ax.bar(df["Match"], df["Probabilité %"])

plt.xticks(rotation=90)

st.subheader("📈 Graphique indice IA")

st.pyplot(fig)
