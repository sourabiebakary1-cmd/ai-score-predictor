import streamlit as st
import numpy as np
import requests
import pandas as pd
from scipy.stats import poisson
from datetime import datetime

st.set_page_config(page_title="BAKARY AI FOOTBALL PREDICTOR", layout="wide")

st.title("🤖⚽ BAKARY AI FOOTBALL PREDICTOR QUANTUM PRO")

# TA CLÉ API
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

# récupérer matchs
url = f"https://api.football-data.org/v4/competitions/{league_code}/matches"

response = requests.get(url, headers=headers)

if response.status_code != 200:
    st.error("Erreur API. Vérifie ta clé.")
    st.stop()

data = response.json()

matches = data.get("matches", [])

if len(matches) == 0:
    st.warning("Aucun match trouvé dans l'API")
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

if len(future_matches) == 0:
    st.warning("Aucun match programmé pour aujourd'hui")
    st.stop()

results = []

for m in future_matches[:10]:

    home = m["homeTeam"]["name"]
    away = m["awayTeam"]["name"]

    home_lambda = 1.6
    away_lambda = 1.2

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
        "Prediction": favori,
        "Score probable": f"{score_home}-{score_away}",
        "Probabilité": round(prob*100,2)
    })

df = pd.DataFrame(results)

st.subheader("📊 Prédictions IA")

st.dataframe(df)

ticket = df[df["Probabilité"] > 60].head(5)

st.subheader("🎯 Ticket conseillé")

st.dataframe(ticket)

odds = 1.8

gain = stake * (odds ** len(ticket))

st.subheader("💰 Gain potentiel")

st.write(round(gain,2),"€")
