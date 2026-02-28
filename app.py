import streamlit as st
import pandas as pd

st.title("EA Sports FC 25 - Top 3 Scores Probables")

team1 = st.text_input("Entrez le nom de l'équipe 1")
team2 = st.text_input("Entrez le nom de l'équipe 2")

if st.button("🚀 Prédire le score"):
    if team1 and team2:

        # Charger le fichier CSV
        data = pd.read_csv("matches.csv")

        # Filtrer les confrontations entre les deux équipes
        matches = data[
            ((data["home_team"] == team1) & (data["away_team"] == team2)) |
            ((data["home_team"] == team2) & (data["away_team"] == team1))
        ]

        if len(matches) == 0:
            st.warning("Aucune donnée trouvée pour ces équipes.")
        else:
            scores = matches.groupby(
                ["home_goals", "away_goals"]
            ).size().reset_index(name="count")

            top_scores = scores.sort_values(
                by="count", ascending=False
            ).head(3)

            st.subheader("🔥 Top 3 Scores Probables")

            for _, row in top_scores.iterrows():
                st.write(f"{team1} {row['home_goals']} - {row['away_goals']} {team2}")
