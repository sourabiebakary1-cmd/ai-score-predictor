import streamlit as st
import random

st.title("Prédicteur de score IA ⚽")
st.write("Prédiction des scores EA Sports FC 25")

team1 = st.text_input("Entrez le nom de l'équipe 1")
team2 = st.text_input("Entrez le nom de l'équipe 2")

if st.button("Prédire le score"):
    if team1 and team2:
        st.subheader("Top 3 Scores Probables 🔥")
        for i in range(3):
            score1 = random.randint(0, 4)
            score2 = random.randint(0, 4)
            st.write(f"{team1} {score1} - {score2} {team2}")
    else:
        st.warning("Veuillez entrer les deux équipes.")
