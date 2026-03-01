import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.title("⚽ AI Score Predictor - Italy")

# Charger les données
data = pd.read_csv("matches.csv")

teams = list(set(data["HomeTeam"]).union(set(data["AwayTeam"])))

home_team = st.selectbox("Equipe Domicile", teams)
away_team = st.selectbox("Equipe Extérieur", teams)

if st.button("Prédire"):

    home_avg = data[data["HomeTeam"] == home_team]["HomeGoals"].mean()
    away_avg = data[data["AwayTeam"] == away_team]["AwayGoals"].mean()

    scores = []

    for i in range(5):
        for j in range(5):
            prob = poisson.pmf(i, home_avg) * poisson.pmf(j, away_avg)
            scores.append((i, j, prob))

    scores = sorted(scores, key=lambda x: x[2], reverse=True)[:3]

    st.subheader("Top 3 Scores Probables")

    for s in scores:
        st.write(f"{home_team} {s[0]} - {s[1]} {away_team}")
