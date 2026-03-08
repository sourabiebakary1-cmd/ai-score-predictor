import streamlit as st
import pandas as pd
import numpy as np
import requests
from scipy.stats import poisson

st.set_page_config(page_title="Bakary Predictor", layout="centered")

st.title("🔥 BAKARY PREDICTOR ULTRA PRO")
st.subheader("📅 Matchs du jour")


API_KEY = "cc99563a7....."

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "free-football-api-data.p.rapidapi.com"
}

from datetime import datetime
import requests

today = datetime.today().strftime("%Y-%m-%d")

params = {
    "date": today,
    "timezone": "Europe/Paris"
}

response = requests.get(url, headers=headers, params=params)

data = response.json()

st.write(data)





matches = []

for match in data["response"]:
    home = match["teams"]["home"]["name"]
    away = match["teams"]["away"]["name"]
    matches.append(f"{home} vs {away}")

if matches:
    selected_match = st.selectbox("Choisir un match", matches)
    st.write("Match sélectionné :", selected_match)
else:
    st.write("Aucun match trouvé")
home_team = st.text_input("Equipe domicile")
away_team = st.text_input("Equipe extérieur")

home_goals_avg = st.number_input("Moyenne buts domicile", 0.0, 5.0, 1.5)
away_goals_avg = st.number_input("Moyenne buts extérieur", 0.0, 5.0, 1.2)

if st.button("Analyser le match"):

    max_goals = 5
    prob_matrix = np.zeros((max_goals+1, max_goals+1))

    for home_goals in range(max_goals+1):
        for away_goals in range(max_goals+1):
            prob_matrix[home_goals][away_goals] = poisson.pmf(home_goals, home_goals_avg) * poisson.pmf(away_goals, away_goals_avg)

    home_win = np.sum(np.tril(prob_matrix, -1))
    draw = np.sum(np.diag(prob_matrix))
    away_win = np.sum(np.triu(prob_matrix, 1))

    st.subheader("📊 Probabilités")

    st.write(f"🏠 Victoire {home_team}: {round(home_win*100,2)} %")
    st.write(f"🤝 Match nul: {round(draw*100,2)} %")
    st.write(f"✈️ Victoire {away_team}: {round(away_win*100,2)} %")

    flat = prob_matrix.flatten()
    index = flat.argmax()

    home_score = index // (max_goals+1)
    away_score = index % (max_goals+1)

    st.subheader("🎯 Score exact le plus probable")
    st.success(f"{home_team} {home_score} - {away_score} {away_team}")
