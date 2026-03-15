import streamlit as st
import numpy as np
import requests
import pandas as pd
import random
from scipy.stats import poisson
from datetime import datetime

st.set_page_config(page_title="BAKARY AI FOOTBALL PREDICTOR", layout="wide")

st.title("🤖⚽ BAKARY AI FOOTBALL PREDICTOR QUANTUM PRO")

API_KEY = "289e8418878e48c598507cf2b72338f5"

headers = {"X-Auth-Token": API_KEY}

ligues = {
    "Premier League": "PL",
    "Ligue 1": "FL1",
    "Serie A": "SA",
    "LaLiga": "PD"
}

selected_ligue = st.selectbox("Choisir la ligue", list(ligues.keys()))
league_code = ligues[selected_ligue]

stake = st.number_input("Mise (€)", min_value=1, value=100)

url = f"https://api.football-data.org/v4/competitions/{league_code}/matches"

response = requests.get(url, headers=headers)

if response.status_code != 200:
    st.error("Erreur API")
    st.stop()

data = response.json()
matches = data.get("matches", [])

if len(matches) == 0:
    st.warning("Aucun match trouvé")
    st.stop()

today = datetime.utcnow()

future_matches = []

for m in matches:
    try:
        date_match = datetime.fromisoformat(m["utcDate"].replace("Z",""))
        if date_match > today:
            future_matches.append(m)
    except:
        pass

results = []

for m in future_matches[:10]:

    home = m["homeTeam"]["name"]
    away = m["awayTeam"]["name"]

    # attaque/défense simulée
    home_attack = random.uniform(1.3,2.5)
    away_attack = random.uniform(1.0,2.2)

    home_def = random.uniform(0.8,1.5)
    away_def = random.uniform(0.8,1.5)

    home_lambda = home_attack - away_def + 1.2
    away_lambda = away_attack - home_def + 1.0

    home_lambda = max(0.4, home_lambda)
    away_lambda = max(0.4, away_lambda)

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
        favori = "Match nul"

    score_home = np.argmax(home_probs)
    score_away = np.argmax(away_probs)

    results.append({
        "Match": f"{home} vs {away}",
        "Prediction": favori,
        "Score probable": f"{score_home}-{score_away}",
        "Probabilité %": round(prob*100,2)
    })

df = pd.DataFrame(results)

st.subheader("📊 Prédictions IA")
st.dataframe(df)

ticket = df[df["Probabilité %"] > 55].head(5)

st.subheader("🎯 Ticket conseillé")

if len(ticket) > 0:
    st.dataframe(ticket)
else:
    st.write("Pas de ticket fiable aujourd'hui")

odds = 1.8
gain = stake * (odds ** len(ticket))

st.subheader("💰 Gain potentiel")
st.write(round(gain,2),"€")
