import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import os

st.set_page_config(page_title="ROBOT PRO FIFA 3x3", layout="wide")

DATA_FILE = "data.csv"

# ================= DATA =================
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["home","away","home_goals","away_goals"])
    df.to_csv(DATA_FILE, index=False)

df = pd.read_csv(DATA_FILE)

st.title("🤖 ROBOT PRO FIFA 3x3")

# ================= AJOUT MATCH =================
st.subheader("➕ Ajouter un match")

col1, col2 = st.columns(2)
home = col1.text_input("Equipe domicile")
away = col2.text_input("Equipe extérieur")

col3, col4 = st.columns(2)
hg = col3.number_input("Buts domicile", 0, 20)
ag = col4.number_input("Buts extérieur", 0, 20)

if st.button("Ajouter"):
    new = pd.DataFrame([[home, away, hg, ag]], columns=df.columns)
    df = pd.concat([df, new], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.success("Match ajouté ✅")

# ================= STATS =================
st.subheader("📊 Données")

if len(df) > 0:
    teams = pd.concat([df['home'], df['away']]).unique()

    attack = {}
    defense = {}

    for team in teams:
        home_games = df[df['home'] == team]
        away_games = df[df['away'] == team]

        goals_scored = home_games['home_goals'].sum() + away_games['away_goals'].sum()
        goals_conceded = home_games['away_goals'].sum() + away_games['home_goals'].sum()

        games = len(home_games) + len(away_games)

        if games > 0:
            attack[team] = goals_scored / games
            defense[team] = goals_conceded / games

# ================= PRÉDICTION =================
st.subheader("🔮 Prédiction PRO")

col5, col6 = st.columns(2)
team1 = col5.selectbox("Equipe 1", teams)
team2 = col6.selectbox("Equipe 2", teams)

if st.button("Prédire 🔥"):

    avg_goals = df['home_goals'].mean()

    lambda1 = attack[team1] * defense[team2] / avg_goals
    lambda2 = attack[team2] * defense[team1] / avg_goals

    max_goals = 10

    prob_matrix = np.zeros((max_goals, max_goals))

    for i in range(max_goals):
        for j in range(max_goals):
            prob_matrix[i][j] = poisson.pmf(i, lambda1) * poisson.pmf(j, lambda2)

    home_win = np.sum(np.tril(prob_matrix, -1))
    draw = np.sum(np.diag(prob_matrix))
    away_win = np.sum(np.triu(prob_matrix, 1))

    st.write("### 📊 Probabilités")
    st.write(f"🏠 {team1} gagne : {home_win:.2%}")
    st.write(f"🤝 Nul : {draw:.2%}")
    st.write(f"🚀 {team2} gagne : {away_win:.2%}")

    # Score le plus probable
    result = np.unravel_index(np.argmax(prob_matrix), prob_matrix.shape)

    st.write("### 🎯 Score probable")
    st.success(f"{team1} {result[0]} - {result[1]} {team2}")
