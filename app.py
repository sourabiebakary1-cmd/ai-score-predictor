import streamlit as st
import numpy as np
import requests
import pandas as pd
from scipy.stats import poisson
from datetime import datetime, timedelta

st.set_page_config(page_title="BAKARY AI V19 ELITE", layout="wide")

st.title("🤖⚽ BAKARY AI FOOTBALL PREDICTOR V19 ELITE")

API_KEY = "289e8418878e48c598507cf2b72338f5"

headers = {
    "X-Auth-Token": API_KEY
}

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

today = datetime.today()
future = today + timedelta(days=7)

match_url = f"https://api.football-data.org/v4/competitions/{league_code}/matches"

params = {
    "dateFrom": today.strftime('%Y-%m-%d'),
    "dateTo": future.strftime('%Y-%m-%d')
}

standings_url = f"https://api.football-data.org/v4/competitions/{league_code}/standings"

try:
    matches_data = requests.get(match_url, headers=headers, params=params).json()
    standings_data = requests.get(standings_url, headers=headers).json()
except:
    st.error("Erreur API")
    st.stop()

matches = matches_data.get("matches", [])

table = standings_data["standings"][0]["table"]

rank = {}

for team in table:
    rank[team["team"]["name"]] = team["position"]

if matches:

    results = []

    for m in matches:

        home = m["homeTeam"]["name"]
        away = m["awayTeam"]["name"]
        date = m["utcDate"][:10]

        home_rank = rank.get(home,10)
        away_rank = rank.get(away,10)

        # ajustement force équipe
        home_lambda = 1.6 + (away_rank-home_rank)*0.05
        away_lambda = 1.2 + (home_rank-away_rank)*0.05

        home_lambda = max(0.5,home_lambda)
        away_lambda = max(0.5,away_lambda)

        max_goals = 6

        home_probs = [poisson.pmf(i, home_lambda) for i in range(max_goals)]
        away_probs = [poisson.pmf(i, away_lambda) for i in range(max_goals)]

        matrix = np.outer(home_probs,away_probs)

        home_win = np.sum(np.tril(matrix,-1))
        draw = np.sum(np.diag(matrix))
        away_win = np.sum(np.triu(matrix,1))

        if home_win > away_win:
            favorite = home
            prob = home_win
        else:
            favorite = away
            prob = away_win

        idx = np.unravel_index(matrix.argmax(),matrix.shape)
        score = f"{idx[0]} - {idx[1]}"

        over25 = sum(matrix[i][j] for i in range(max_goals) for j in range(max_goals) if i+j>2)

        results.append({
            "Date":date,
            "Match":f"{home} vs {away}",
            "Favori IA":favorite,
            "Probabilité %":round(prob*100,2),
            "Score IA":score,
            "Over 2.5 %":round(over25*100,2)
        })

    df = pd.DataFrame(results)

    st.subheader("Analyse IA des matchs")
    st.dataframe(df,use_container_width=True)

    top = df.sort_values("Probabilité %",ascending=False).head(5)

    st.subheader("🔥 TOP 5 PARIS IA")
    st.dataframe(top)

    top_probs = top["Probabilité %"].values/100

    combined_prob = np.prod(top_probs)

    gain = stake*(1/combined_prob) if combined_prob>0 else 0

    st.subheader("💰 Simulation Ticket IA")

    st.write("Probabilité combiné :",round(combined_prob*100,2),"%")
    st.write("Gain potentiel estimé :",round(gain,2),"€")

else:

    st.warning("Aucun match trouvé")
