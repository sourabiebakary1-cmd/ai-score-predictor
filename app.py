import streamlit as st
import numpy as np
import requests
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import poisson
from datetime import datetime, timedelta

st.set_page_config(page_title="BAKARY AI V33 QUANTUM GOD", layout="wide")

st.title("🤖⚽ BAKARY AI FOOTBALL PREDICTOR V33 QUANTUM GOD")

API_KEY = "289e8418878e48c598507cf2b72338f5"

headers = {"X-Auth-Token": API_KEY}

ligues = {
    "Premier League": "PL",
    "Ligue 1": "FL1",
    "Bundesliga": "BL1",
    "Serie A": "SA",
    "LaLiga": "PD",
    "Primeira Liga": "PPL",
    "Eredivisie": "DED"
}

selected_ligue = st.selectbox("Choisir la ligue", list(ligues.keys()))
league_code = ligues[selected_ligue]

stake = st.number_input("Mise (€)", min_value=1, value=100)

today = datetime.today()
future = today + timedelta(days=7)

match_url = f"https://api.football-data.org/v4/competitions/{league_code}/matches"
standings_url = f"https://api.football-data.org/v4/competitions/{league_code}/standings"

params = {
    "dateFrom": today.strftime('%Y-%m-%d'),
    "dateTo": future.strftime('%Y-%m-%d')
}

try:
    matches_data = requests.get(match_url, headers=headers, params=params).json()
    standings_data = requests.get(standings_url, headers=headers).json()
except:
    st.error("Erreur connexion API")
    st.stop()

matches = matches_data.get("matches", [])
table = standings_data["standings"][0]["table"]

rank = {}
points = {}
goals_for = {}
goals_against = {}

for team in table:
    name = team["team"]["name"]
    rank[name] = team["position"]
    points[name] = team["points"]
    goals_for[name] = team["goalsFor"]
    goals_against[name] = team["goalsAgainst"]

if matches:

    results = []

    for m in matches:

        home = m["homeTeam"]["name"]
        away = m["awayTeam"]["name"]

        home_rank = rank.get(home,10)
        away_rank = rank.get(away,10)

        home_points = points.get(home,20)
        away_points = points.get(away,20)

        home_attack = goals_for.get(home,20)/10
        away_attack = goals_for.get(away,20)/10

        home_def = goals_against.get(home,20)/10
        away_def = goals_against.get(away,20)/10

        form = (home_points-away_points)*0.07

        home_lambda = 1.9 + home_attack - away_def + form + (away_rank-home_rank)*0.1
        away_lambda = 1.5 + away_attack - home_def - form + (home_rank-away_rank)*0.1

        home_lambda = max(0.3,home_lambda)
        away_lambda = max(0.3,away_lambda)

        max_goals = 6

        home_probs = [poisson.pmf(i,home_lambda) for i in range(max_goals)]
        away_probs = [poisson.pmf(i,away_lambda) for i in range(max_goals)]

        matrix = np.outer(home_probs,away_probs)

        home_win = np.sum(np.tril(matrix,-1))
        away_win = np.sum(np.triu(matrix,1))

        prob = max(home_win,away_win)

        favorite = home if home_win>away_win else away

        over25 = sum(matrix[i][j] for i in range(max_goals) for j in range(max_goals) if i+j>2)

        btts = sum(matrix[i][j] for i in range(1,max_goals) for j in range(1,max_goals))

        idx = np.unravel_index(matrix.argmax(),matrix.shape)
        score = f"{idx[0]} - {idx[1]}"

        confidence = prob*100

        quantum = "⚛️ QUANTUM GOD BET" if confidence > 98 else ""

        results.append({
            "Match":f"{home} vs {away}",
            "Favori IA":favorite,
            "Score probable":score,
            "Probabilité %":round(prob*100,2),
            "BTTS %":round(btts*100,2),
            "Over 2.5 %":round(over25*100,2),
            "Indice IA":round(confidence,2),
            "QUANTUM GOD":quantum
        })

    df = pd.DataFrame(results)

    df["Score IA GLOBAL"] = df["Probabilité %"]*0.5 + df["Over 2.5 %"]*0.3 + df["BTTS %"]*0.2

    st.subheader("📊 Analyse IA complète")
    st.dataframe(df,use_container_width=True)

    quantum = df[df["QUANTUM GOD"]!=""]

    st.subheader("⚛️ QUANTUM GOD BET")
    st.dataframe(quantum)

    ticket = df.sort_values("Score IA GLOBAL",ascending=False).head(5)

    st.subheader("🎯 Ticket IA automatique")
    st.dataframe(ticket)

    probs = ticket["Probabilité %"].values/100

    combined_prob = np.prod(probs)

    gain = stake*(1/combined_prob) if combined_prob>0 else 0

    st.subheader("💰 Simulation gain")

    st.write("Probabilité combiné :",round(combined_prob*100,2),"%")
    st.write("Gain potentiel :",round(gain,2),"€")

    st.subheader("📈 Graphique indice IA")

    fig, ax = plt.subplots()
    ax.bar(df["Match"],df["Indice IA"])
    plt.xticks(rotation=45)

    st.pyplot(fig)

else:

    st.warning("Aucun match trouvé")
