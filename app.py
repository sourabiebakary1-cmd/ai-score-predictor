import streamlit as st
import numpy as np
import requests
from scipy.stats import poisson
from datetime import datetime

st.set_page_config(page_title="Bakary AI Predictor V4", layout="centered")

st.title("⚽ BAKARY AI FOOTBALL PREDICTOR V4")
st.write("Analyse avancée avec classements et forme récente des équipes")

# 🔑 Clé API
API_KEY = "64907d87f835d9696c8d51b314693e51"

headers = {"x-apisports-key": API_KEY}

# URL API
fixture_url = "https://v3.football.api-sports.io/fixtures"
standings_url = "https://v3.football.api-sports.io/standings"
results_url = "https://v3.football.api-sports.io/fixtures"

today = datetime.today().strftime("%Y-%m-%d")

# Paramètres principaux pour récupérer les matchs
params = {
    "date": today,
    "season": 2025,  # saison 2025/2026
    # "league": 39   # Exemple: Premier League = 39
}

matches = []

st.write("🔎 Recherche des matchs du jour...")

# Récupération matchs
try:
    r = requests.get(fixture_url, headers=headers, params=params)
    data = r.json()
    if "response" in data and len(data["response"]) > 0:
        for m in data["response"]:
            home = m["teams"]["home"]["name"]
            away = m["teams"]["away"]["name"]
            league_id = m["league"]["id"]
            league_name = m["
