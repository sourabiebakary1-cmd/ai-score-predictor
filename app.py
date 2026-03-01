import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.title("⚽ AI Score Predictor - Italy (PRO Version)")

# Charger données
data = pd.read_csv("matches.csv")

teams = list(set(data["HomeTeam"]).union(set(data["AwayTeam"])))

home_team = st.selectbox("Equipe Domicile", teams)
away_team = st.selectbox("Equipe Extérieur", teams)

if home_team == away_team:
    st.error("⚠️ Choisissez deux équipes différentes")
else:

    if st.button("Prédire"):

        # Moyennes championnat
        avg_home_goals = data["HomeGoals"].mean()
        avg_away_goals = data["AwayGoals"].mean()

        # Force attaque domicile
        home_attack = data[data["HomeTeam"] == home_team]["HomeGoals"].mean() / avg_home_goals

        # Défense extérieur (faiblesse)
        away_defense = data[data["AwayTeam"] == away_team]["HomeGoals"].mean() / avg_home_goals

        # Force attaque extérieur
        away_attack = data[data["AwayTeam"] == away_team]["AwayGoals"].mean() / avg_away_goals

        # Défense domicile (faiblesse)
        home_defense = data[data["HomeTeam"] == home_team]["AwayGoals"].mean() / avg_away_goals

        # Expected Goals
        expected_home_goals = avg_home_goals * home_attack * away_defense
        expected_away_goals = avg_away_goals * away_attack * home_defense

        scores = []

        for i in range(6):
            for j in range(6):
                prob = poisson.pmf(i, expected_home_goals) * poisson.pmf(j, expected_away_goals)
                scores.append((i, j, prob))

        scores = sorted(scores, key=lambda x: x[2], reverse=True)[:3]

        st.subheader("🔥 Top 3 Scores Probables")

        for s in scores:
            st.write(f"{home_team} {s[0]} - {s[1]} {away_team} | {round(s[2]*100,2)}%")
