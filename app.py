import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.title("EA Sports FC 25 - Modèle Pro 🔥")

df = pd.read_csv("matches.csv")

team1 = st.text_input("Entrez le nom de l'équipe 1")
team2 = st.text_input("Entrez le nom de l'équipe 2")

def weighted_average(goals):
    if len(goals) == 0:
        return 0
    weights = np.arange(1, len(goals)+1)
    return np.average(goals, weights=weights)

def analyse_match(team1, team2):

    if team1 not in df["home_team"].values or team2 not in df["away_team"].values:
        return None

    league_home_avg = df["home_goals"].mean()
    league_away_avg = df["away_goals"].mean()

    # 5 derniers matchs domicile team1
    team1_home = df[df["home_team"] == team1].tail(5)
    team1_attack = weighted_average(team1_home["home_goals"]) / league_home_avg
    team1_defense = weighted_average(team1_home["away_goals"]) / league_away_avg

    # 5 derniers matchs extérieur team2
    team2_away = df[df["away_team"] == team2].tail(5)
    team2_attack = weighted_average(team2_away["away_goals"]) / league_away_avg
    team2_defense = weighted_average(team2_away["home_goals"]) / league_home_avg

    lambda_home = team1_attack * team2_defense * league_home_avg
    lambda_away = team2_attack * team1_defense * league_away_avg

    max_goals = 6
    prob_matrix = np.zeros((max_goals, max_goals))

    for i in range(max_goals):
        for j in range(max_goals):
            prob_matrix[i][j] = poisson.pmf(i, lambda_home) * poisson.pmf(j, lambda_away)

    home_win = np.sum(np.tril(prob_matrix, -1))
    draw = np.sum(np.diag(prob_matrix))
    away_win = np.sum(np.triu(prob_matrix, 1))

    over_25 = sum(prob_matrix[i][j] for i in range(max_goals) for j in range(max_goals) if i+j > 2)
    btts = sum(prob_matrix[i][j] for i in range(max_goals) for j in range(max_goals) if i>0 and j>0)

    scores = [(i, j, prob_matrix[i][j]) for i in range(max_goals) for j in range(max_goals)]
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
    st.error("Equipe non trouvée")

else:

    if "top_scores" in result:
        st.subheader("🔥 Top 3 Scores Probables")
        for score in result["top_scores"]:
            st.write(f"{team1} {score[0]} - {score[1]} {team2}")

    if "home_win" in result:
        st.subheader("📊 Probabilités 1X2")
        st.write(f"Victoire {team1} : {round(result['home_win']*100,1)}%")
        st.write(f"Match nul : {round(result['draw']*100,1)}%")
        st.write(f"Victoire {team2} : {round(result['away_win']*100,1)}%")

    if "over_25" in result:
        st.subheader("⚽ Marchés supplémentaires")
        st.write(f"Over 2.5 buts : {round(result['over_25']*100,1)}%")
        st.write(f"BTTS : {round(result['btts']*100,1)}%")
        st.subheader("🔥 Top 3 Scores Probables")
        for score in result["top_scores"]:
            st.write(f"{team1} {score[0]} - {score[1]} {team2} | {round(score[2]*100,2)}%")

        st.subheader("📊 Probabilités 1X2")
        st.write(f"Victoire {team1} : {round(result['home_win']*100,2)}%")
        st.write(f"Match nul : {round(result['draw']*100,2)}%")
        st.write(f"Victoire {team2} : {round(result['away_win']*100,2)}%")

        st.subheader("⚽ Marchés supplémentaires")
        st.write(f"Over 2.5 buts : {round(result['over_25']*100,2)}%")
        st.write(f"BTTS : {round(result['btts']*100,2)}%")
