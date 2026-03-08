import streamlit as st
import numpy as np
import requests
from scipy.stats import poisson
from datetime import datetime

st.set_page_config(page_title="Bakary Predictor PRO", layout="centered")

st.title("🤖 BAKARY AI FOOTBALL PREDICTOR PRO")
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

st.write("🔎 Recherche des matchs...")

try:
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if "data" in data:
        for match in data["data"]:
            home = match["home_team"]["name"]
            away = match["away_team"]["name"]
            matches.append((home, away))
    else:
        st.warning("Aucun match trouvé")

except:
    st.error("Erreur API")

if matches:
    match_names = [f"{m[0]} vs {m[1]}" for m in matches]
    selected = st.selectbox("Choisir un match", match_names)

    index = match_names.index(selected)
    home_team = matches[index][0]
    away_team = matches[index][1]

    st.write("🏠", home_team)
    st.write("🚗", away_team)

st.subheader("📊 Statistiques équipes")

home_attack = st.slider("Force attaque domicile", 0.5, 3.0, 1.5)
away_attack = st.slider("Force attaque extérieur", 0.5, 3.0, 1.2)

home_defense = st.slider("Défense domicile", 0.5, 3.0, 1.0)
away_defense = st.slider("Défense extérieur", 0.5, 3.0, 1.2)

if st.button("🤖 Lancer analyse IA"):

    home_lambda = home_attack * away_defense
    away_lambda = away_attack * home_defense

    max_goals = 6
    matrix = np.zeros((max_goals+1, max_goals+1))

    for i in range(max_goals+
