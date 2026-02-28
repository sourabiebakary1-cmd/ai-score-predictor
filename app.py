import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.title("EA Sports FC 25 - Analyse Complète")

df = pd.read_csv("matches.csv")

team1 = st.text_input("Entrez le nom de l'équipe 1")
team2 = st.text_input("Entrez le nom de l'équipe 2")

def analyse_match(team1, team2):

    team1_home = df[df["home_team"] == team1]
    team2_away = df[df["away_team"] == team2]

    if len(team1_home) == 0 or len(team2_away) == 0:
        return None

    avg_team1 = team1_home["home_goals"].mean()
    avg_team2 = team2_away["away_goals"].mean()

    max_goals = 5

    prob_matrix = np.zeros((max_goals, max_goals))

    for i in range(max_goals):
        for j in range(max_goals):
            prob_matrix[i][j] = poisson.pmf(i, avg_team1) * poisson.pmf(j, avg_team2)

    home_win = np.sum(np.tril(prob_matrix, -1))
    draw = np.sum(np.diag(prob_matrix))
    away_win = np.sum(np.triu(prob_matrix, 1))

    over_25 = 0
    btts = 0

    for i in range(max_goals):
        for j in range(max_goals):
            if i + j > 2:
                over_25 += prob_matrix[i][j]
            if i > 0 and j > 0:
                btts += prob_matrix[i][j]

    scores = []
    for i in range(max_goals):
        for j in range(max_goals):
            scores.append((i, j, prob_matrix[i][j]))

    scores = sorted(scores, key=lambda x: x[2], reverse=True)

    return {
        "top_scores": scores[:3],
        "home_win": home_win,
        "draw": draw,
        "away_win": away_win,
        "over_25": over_25,
        "btts": btts
    }

if st.button("🚀 Analyser le match"):

    result = analyse_match(team1, team2)

    if result is None:
        st.error("Pas assez de données")
    else:
        st.subheader("🔥 Top 3 Scores Probables")
        for score in result["top_scores"]:
            st.write(f"{team1} {score[0]} - {score[1]} {team2} | {round(score[2]*100,2)}%")

        st.subheader("📊 Probabilités 1X2")
        st.write(f"Victoire {team1} : {round(result['home_win']*100,2)}%")
        st.write(f"Match nul : {round(result['draw']*100,2)}%")
        st.write(f"Victoire {team2} : {round(result['away_win']*100,2)}%")

        st.subheader("⚽ Marchés supplémentaires")
        st.write(f"Over 2.5 buts : {round(result['over_25']*100,2)}%")
        st.write(f"BTTS (les deux équipes marquent) : {round(result['btts']*100,2)}%")
