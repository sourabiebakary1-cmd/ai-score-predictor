import streamlit as st
import numpy as np
import requests
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import poisson
from datetime import datetime

st.set_page_config(page_title="BAKARY AI PRO", layout="wide")

st.title("🤖⚽ BAKARY AI FOOTBALL PRO")
st.success("🧠 IA active - Analyse des matchs")

API_KEY = "289e8418878e48c598507cf2b72338f5"

headers = {"X-Auth-Token": API_KEY}

# MENU
st.sidebar.title("⚙️ Paramètres")

ligues = {
"Premier League": "PL",
"LaLiga": "PD",
"Ligue 1": "FL1",
"Serie A": "SA",
"Bundesliga": "BL1"
}

league = st.sidebar.selectbox("Choisir la ligue", list(ligues.keys()))
code = ligues[league]

stake = st.sidebar.number_input("Mise (€)", min_value=1, value=100)

menu = st.sidebar.radio(
"Navigation",
[
"Analyse matchs",
"Top 5 paris",
"Graphique IA"
]
)

match_url = f"https://api.football-data.org/v4/competitions/{code}/matches"
standings_url = f"https://api.football-data.org/v4/competitions/{code}/standings"

# API
try:
    matches_data = requests.get(match_url, headers=headers).json()
    standings_data = requests.get(standings_url, headers=headers).json()
except:
    st.error("Erreur connexion API")
    st.stop()

matches = matches_data.get("matches", [])

if len(matches) == 0:
    st.warning("Aucun match trouvé")
    st.stop()

# DATE
today = datetime.utcnow()

future_matches = []

for m in matches:
    try:
        d = datetime.fromisoformat(m["utcDate"].replace("Z", ""))
        if d > today:
            future_matches.append(m)
    except:
        pass

# TABLE
try:
    table = standings_data["standings"][0]["table"]
except:
    st.error("Classement indisponible")
    st.stop()

attack = {}
defense = {}

for t in table:

    name = t["team"]["name"]
    played = t["playedGames"]

    if played == 0:
        continue

    attack[name] = t["goalsFor"] / played
    defense[name] = t["goalsAgainst"] / played

results = []

for m in future_matches[:20]:

    home = m["homeTeam"]["name"]
    away = m["awayTeam"]["name"]

    ha = attack.get(home, 1.5)
    aa = attack.get(away, 1.5)

    hd = defense.get(home, 1.2)
    ad = defense.get(away, 1.2)

    home_lambda = max(0.4, ha / ad)
    away_lambda = max(0.4, aa / hd)

    max_goals = 6

    home_probs = [poisson.pmf(i, home_lambda) for i in range(max_goals)]
    away_probs = [poisson.pmf(i, away_lambda) for i in range(max_goals)]

    matrix = np.outer(home_probs, away_probs)

    home_win = np.sum(np.tril(matrix, -1))
    away_win = np.sum(np.triu(matrix, 1))
    draw = np.sum(np.diag(matrix))

    prob = max(home_win, away_win, draw)

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

    confidence = "🟢 Haute" if prob > 0.65 else "🟡 Moyenne" if prob > 0.55 else "🔴 Risqué"

    results.append({

        "Match": f"{home} vs {away}",
        "Prediction": prediction,
        "Score probable": f"{score_home}-{score_away}",
        "Over 2.5": over25,
        "BTTS": btts,
        "Probabilité %": round(prob * 100, 2),
        "Confiance": confidence

    })

df = pd.DataFrame(results)

top5 = df.sort_values(by="Probabilité %", ascending=False).head(5)

# AFFICHAGE

if menu == "Analyse matchs":

    st.subheader("📊 Analyse complète")
    st.dataframe(df)

elif menu == "Top 5 paris":

    st.subheader("🔥 Top 5 paris sûrs")
    st.dataframe(top5)

elif menu == "Graphique IA":

    fig, ax = plt.subplots()

    ax.barh(df["Match"], df["Probabilité %"])

    ax.set_xlabel("Probabilité")

    st.pyplot(fig)

# CALCUL GAIN

odds = 2

gain = stake * (odds ** len(top5))

st.metric("💰 Gain potentiel", round(gain, 2))
