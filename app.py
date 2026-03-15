import streamlit as st
import numpy as np
import requests
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import poisson
from datetime import datetime

st.set_page_config(page_title="BAKARY AI PRO", layout="wide")

st.title("🤖⚽ BAKARY AI FOOTBALL ANALYTICS PRO")

API_KEY = "289e8418878e48c598507cf2b72338f5"
headers = {"X-Auth-Token": API_KEY}

st.sidebar.title("⚙️ Paramètres IA")

ligues = {
    "Premier League":"PL",
    "LaLiga":"PD",
    "Ligue 1":"FL1",
    "Serie A":"SA",
    "Bundesliga":"BL1",
    "Championship":"ELC",
    "Primeira Liga":"PPL",
    "Brazil Serie A":"BSA"
}

league_name = st.sidebar.selectbox("Choisir la ligue", list(ligues.keys()))
league_code = ligues[league_name]

stake = st.sidebar.number_input("Mise (€)", min_value=1, value=100)

menu = st.sidebar.radio(
    "Navigation",
    ["📊 Analyse matchs","🔥 Top paris","📈 Statistiques"]
)

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

standings = standings_data.get("standings", [])

if not standings:
    st.warning("Classement indisponible")
    st.stop()

table = standings[0]["table"]

attack = {}
defense = {}

for team in table:
    name = team["team"]["name"]
    played = team["playedGames"]

    if played == 0:
        continue

    attack[name] = team["goalsFor"] / played
    defense[name] = team["goalsAgainst"] / played

results = []

for m in future_matches[:15]:

    home = m["homeTeam"]["name"]
    away = m["awayTeam"]["name"]

    home_attack = attack.get(home,1.5)
    away_attack = attack.get(away,1.5)

    home_def = defense.get(home,1.2)
    away_def = defense.get(away,1.2)

    home_lambda = home_attack / away_def
    away_lambda = away_attack / home_def

    home_lambda = max(0.4,home_lambda)
    away_lambda = max(0.4,away_lambda)

    max_goals = 6

    home_probs = [poisson.pmf(i,home_lambda) for i in range(max_goals)]
    away_probs = [poisson.pmf(i,away_lambda) for i in range(max_goals)]

    matrix = np.outer(home_probs,away_probs)

    home_win = np.sum(np.tril(matrix,-1))
    away_win = np.sum(np.triu(matrix,1))
    draw = np.sum(np.diag(matrix))

    prob = max(home_win,away_win,draw)

    if prob == home_win:
        prediction = home
    elif prob == away_win:
        prediction = away
    else:
        prediction = "Draw"

    score_home = np.argmax(home_probs)
    score_away = np.argmax(away_probs)

    total_goals = home_lambda + away_lambda

    over25 = "Oui" if total_goals > 2.5 else "Non"
    btts = "Oui" if home_lambda > 1 and away_lambda > 1 else "Non"

    trap = "⚠️ Match piège" if prob < 0.55 else "OK"

    results.append({
        "Match":f"{home} vs {away}",
        "Prediction":prediction,
        "Score probable":f"{score_home}-{score_away}",
        "Over 2.5":over25,
        "BTTS":btts,
        "Probabilité %":round(prob*100,2),
        "Analyse":trap
    })

df = pd.DataFrame(results)

top5 = df.sort_values(by="Probabilité %", ascending=False).head(5)

if menu == "📊 Analyse matchs":
    st.subheader("Analyse IA complète")
    st.dataframe(df)

elif menu == "🔥 Top paris":
    st.subheader("Top 5 paris les plus sûrs")
    st.dataframe(top5)

elif menu == "📈 Statistiques":

    fig, ax = plt.subplots()

    ax.bar(df["Match"], df["Probabilité %"])

    plt.xticks(rotation=90)

    st.pyplot(fig)

odds = 2.0
gain = stake * (odds ** len(top5))

st.subheader("💰 Gain potentiel")

st.write(round(gain,2),"€")
