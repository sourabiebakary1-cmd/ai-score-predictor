import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.title("🔥 BAKARY PREDICTOR ULTRA PRO 🔥")

# Charger les données
data = pd.read_csv("matches.csv")

teams = sorted(list(set(data["HomeTeam"])))

home_team = st.selectbox("Equipe Domicile", teams)
away_team = st.selectbox("Equipe Extérieur", teams)

if home_team != away_team:

    # Moyennes buts
    home_avg_scored = data[data["HomeTeam"] == home_team]["HomeGoals"].mean()
    home_avg_conceded = data[data["HomeTeam"] == home_team]["AwayGoals"].mean()

    away_avg_scored = data[data["AwayTeam"] == away_team]["AwayGoals"].mean()
    away_avg_conceded = data[data["AwayTeam"] == away_team]["HomeGoals"].mean()

    # Attaque attendue
    lambda_home = (home_avg_scored + away_avg_conceded) / 2
    lambda_away = (away_avg_scored + home_avg_conceded) / 2

    st.subheader("📊 Probabilités du match")

    max_goals = 6
    prob_matrix = np.zeros((max_goals, max_goals))

    for i in range(max_goals):
        for j in range(max_goals):
            prob_matrix[i, j] = poisson.pmf(i, lambda_home) * poisson.pmf(j, lambda_away)

    home_win = np.sum(np.tril(prob_matrix, -1))
    draw = np.sum(np.diag(prob_matrix))
    away_win = np.sum(np.triu(prob_matrix, 1))

    st.write(f"🏠 Victoire {home_team} : {round(home_win*100,2)} %")
    st.write(f"🤝 Match nul : {round(draw*100,2)} %")
    st.write(f"✈️ Victoire {away_team} : {round(away_win*100,2)} %")

    # Top 3 scores
    scores = []
    for i in range(max_goals):
        for j in range(max_goals):
            scores.append((i, j, prob_matrix[i,j]))

    top_scores = sorted(scores, key=lambda x: x[2], reverse=True)[:3]

    st.subheader("🎯 Top 3 Scores Probables")

    for score in top_scores:
        st.write(f"{score[0]} - {score[1]}  ({round(score[2]*100,2)} %)")

else:
    st.warning("Choisissez deux équipes différentes")
