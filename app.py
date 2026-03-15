import streamlit as st
import numpy as np
import requests
import pandas as pd
from scipy.stats import poisson
from datetime import datetime

st.set_page_config(page_title="BAKARY AI V18 SUPREME", layout="wide")

st.title("⚽ BAKARY AI FOOTBALL PREDICTOR V18 SUPREME")

# API KEY
API_KEY = "289e8418878e48c598507cf2b72338f5"

headers = {
    "X-Auth-Token": API_KEY
}

# Ligues
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

today = datetime.today().strftime('%Y-%m-%d')

url = f"https://api.football-data.org/v4/competitions/{league_code}/matches"

params = {
    "dateFrom": today,
    "dateTo": today
}

response = requests.get(url, headers=headers, params=params)
data = response.json()

matches = data.get("matches", [])

if matches:

    results = []
    probs = []

    for m in matches:

        home = m["homeTeam"]["name"]
        away = m["awayTeam"]["name"]

        home_lambda = 1.6
        away_lambda = 1.2

        max_goals = 6

        home_probs = [poisson.pmf(i, home_lambda) for i in range(max_goals)]
        away_probs = [poisson.pmf(i, away_lambda) for i in range(max_goals)]

        matrix = np.outer(home_probs, away_probs)

        home_win = np.sum(np.tril(matrix,-1))
        draw = np.sum(np.diag(matrix))
        away_win = np.sum(np.triu(matrix,1))

        favorite = home if home_win > away_win else away
        probs.append(max(home_win,away_win))

        # score exact
        idx = np.unravel_index(matrix.argmax(),matrix.shape)
        score = f"{idx[0]} - {idx[1]}"

        # Over 2.5
        over25 = sum(matrix[i][j] for i in range(max_goals) for j in range(max_goals) if i+j>2)

        # BTTS
        btts = sum(matrix[i][j] for i in range(1,max_goals) for j in range(1,max_goals))

        results.append({
            "Match": f"{home} vs {away}",
            "Favori": favorite,
            "Score probable": score,
            "Over 2.5 %": round(over25*100,2),
            "BTTS %": round(btts*100,2)
        })

    df = pd.DataFrame(results)

    st.subheader("Analyse IA des matchs")
    st.dataframe(df,use_container_width=True)

    # TOP MATCHS
    top = df.sort_values("Over 2.5 %",ascending=False).head(5)

    st.subheader("🔥 Top 5 matchs à fort potentiel")
    st.dataframe(top)

    # COMBINÉ
    combined_prob = np.prod(probs)

    gain = stake / combined_prob if combined_prob>0 else 0

    st.subheader("💰 Simulation ticket combiné")

    st.write(f"Probabilité combiné : {round(combined_prob*100,2)} %")

    st.write(f"Gain potentiel estimé : {round(gain,2)} €")

else:

    st.warning("❌ Aucun match trouvé aujourd'hui.")
