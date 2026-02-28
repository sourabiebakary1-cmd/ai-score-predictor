import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.title("EA Sports FC 25 - Top 3 Scores Probables")

# Charger données
df = pd.read_csv("matches.csv")

team1 = st.text_input("Entrez le nom de l'équipe 1")
team2 = st.text_input("Entrez le nom de l'équipe 2")

def predict_scores(team1, team2):

    # Moyennes attaque / défense
    team1_home = df[df["home_team"] == team1]
    team2_away = df[df["away_team"] == team2]

    if len(team1_home) == 0 or len(team2_away) == 0:
        return None

    avg_team1 = team1_home["home_goals"].mean()
    avg_team2 = team2_away["away_goals"].mean()

    scores = []

    for i in range(5):
        for j in range(5):
            prob = poisson.pmf(i, avg_team1) * poisson.pmf(j, avg_team2)
            scores.append((i, j, prob))

    scores = sorted(scores, key=lambda x: x[2], reverse=True)

    return scores[:3]

if st.button("🚀 Prédire le score"):

    result = predict_scores(team1, team2)

    if result is None:
        st.error("Pas assez de données pour ces équipes")
    else:
        st.subheader("🔥 Top 3 Scores Probables")
        for score in result:
            st.write(f"{team1} {score[0]} - {score[1]} {team2}  |  Probabilité: {round(score[2]*100,2)}%")
