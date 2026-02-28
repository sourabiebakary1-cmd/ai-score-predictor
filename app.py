import streamlit as st
import pandas as pd

# Charger les données
try:
    data = pd.read_csv("matches.csv")
except:
    data = None

st.title("🤖 AI Score Predictor")

# Sélection équipes
team1 = st.text_input("Equipe 1")
team2 = st.text_input("Equipe 2")

def analyse_match(team1, team2):
    if data is None:
        return None

    # Simulation simple (on améliorera après)
    return {
        "top_scores": [(1,0),(2,1),(2,0)],
        "home_win": 0.45,
        "draw": 0.30,
        "away_win": 0.25,
        "over_25": 0.55,
        "btts": 0.60
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
            st.write(f"Victoire {team1}: {round(result['home_win']*100,1)}%")
            st.write(f"Match nul : {round(result['draw']*100,1)}%")
            st.write(f"Victoire {team2}: {round(result['away_win']*100,1)}%")

        if "over_25" in result:
            st.subheader("⚽ Marchés supplémentaires")
            st.write(f"Over 2.5 buts : {round(result['over_25']*100,1)}%")
            st.write(f"BTTS : {round(result['btts']*100,1)}%")
