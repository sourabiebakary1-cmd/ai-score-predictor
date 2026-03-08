import streamlit as st
import numpy as np
import requests
from scipy.stats import poisson
from datetime import datetime

st.set_page_config(page_title="Bakary Predictor", layout="centered")

st.title("🔥 BAKARY PREDICTOR ULTRA PRO")
st.subheader("📅 Matchs du jour")

API_KEY = "TA_CLE_RAPIDAPI"

url = "https://free-football-api-data.p.rapidapi.com/football-matches-by-date"

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "free-football-api-data.p.rapidapi.com"
}

today = datetime.today().strftime("%Y-%m-%d")

params = {
    "date": today,
    "timezone": "Europe/Paris"
}

matches = []

st.write("🔎 Recherche des matchs du jour...")

try:
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if "data" in data:
        for match in data["data"]:
            home = match["home_team"]["name"]
            away = match["away_team"]["name"]
            matches.append(f"{home} vs {away}")
    else:
        st.warning("⚠️ Aucun match trouvé aujourd'hui")

except:
    st.error("❌ Erreur connexion API")

st.success(f"{len(matches)} matchs trouvés aujourd'hui")

if matches:
    selected_match = st.selectbox("Choisir un match", matches)
    st.success(f"Match sélectionné : {selected_match}")
else:
    st.write("Aucun match disponible")

st.subheader("⚙️ Analyse IA")

home_goals_avg = st.number_input("Moyenne buts domicile", 0.0, 5.0, 1.5)
away_goals_avg = st.number_input("Moyenne buts extérieur", 0.0, 5.0, 1.2)

if st.button("Analyser le match"):

    max_goals = 5
    prob_matrix = np.zeros((max_goals+1, max_goals+1))

    for home_goals in range(max_goals+1):
        for away_goals in range(max_goals+1):
            prob = poisson.pmf(home_goals, home_goals_avg) * poisson.pmf(away_goals, away_goals_avg)
            prob_matrix[home_goals][away_goals] = prob

    pred_home = np.argmax(prob_matrix) // (max_goals+1)
    pred_away = np.argmax(prob_matrix) % (max_goals+1)

    st.success(f"⚽ Score prédit : {pred_home} - {pred_away}")

    home_win = np.sum(np.tril(prob_matrix, -1))
    draw = np.sum(np.diag(prob_matrix))
    away_win = np.sum(np.triu(prob_matrix, 1))

    st.write("📊 Probabilités :")
    st.write(f"🏠 Victoire domicile : {home_win:.2%}")
    st.write(f"🤝 Match nul : {draw:.2%}")
    st.write(f"🚗 Victoire extérieur : {away_win:.2%}")

    over25 = np.sum(prob_matrix[3:])
    btts = np.sum(prob_matrix[1:,1:])

    st.write("🎯 Paris :")
    st.write(f"🔥 Over 2.5 : {over25:.2%}")
    st.write(f"⚽ BTTS : {btts:.2%}")
