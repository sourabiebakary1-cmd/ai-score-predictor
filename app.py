import streamlit as st
import numpy as np
import requests
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import poisson

st.set_page_config(page_title="BAKARY AI FOOTBALL PRO V2", layout="wide")

st.title("⚽ BAKARY AI FOOTBALL PRO V2")
st.success("🧠 IA Avancée - Analyse intelligente")

API_KEY = "289e8418878e48c598507cf2b72338f5"
headers = {"X-Auth-Token": API_KEY}

# SIDEBAR
st.sidebar.title("⚙️ Paramètres")

ligues = {
"Premier League": "PL",
"LaLiga": "PD",
"Ligue 1": "FL1",
"Serie A": "SA",
"Bundesliga": "BL1"
}

league = st.sidebar.selectbox("Choisir la ligue", list(ligues.keys()))
code = ligues[league]

stake = st.sidebar.number_input("Mise (€)", min_value=1, value=100)

menu = st.sidebar.radio(
"Navigation",
[
"Analyse IA",
"Top 3 paris sûrs",
"Graphique IA"
]
)

# API URL
match_url = f"https://api.football-data.org/v4/competitions/{code}/matches?status=SCHEDULED"
standings_url = f"https://api.football-data.org/v4/competitions/{code}/standings"

# API REQUEST
try:
    matches_data = requests.get(match_url, headers=headers).json()
    standings_data = requests.get(standings_url, headers=headers).json()
except:
    st.error("❌ Erreur connexion API")
    st.stop()

matches = matches_data.get("matches", [])

if not matches:
    st.warning("⚠️ Aucun match trouvé pour cette ligue")
    st.stop()

# CLASSEMENT
try:
    table = standings_data["standings"][0]["table"]
except:
    st.error("❌ Classement indisponible")
    st.stop()

attack = {}
defense = {}

for team in table:

    name = team["team"]["name"]
    played = team["playedGames"]

    if played == 0:
        continue

    attack[name] = team["goalsFor"] / played
    defense[name] = team["goalsAgainst"] / played


def score_probable(home_xg, away_xg):

    max_prob = 0
    best_score = "0-0"

    for i in range(5):
        for j in range(5):

            prob = poisson.pmf(i, home_xg) * poisson.pmf(j, away_xg)

            if prob > max_prob:
                max_prob = prob
                best_score = f"{i}-{j}"

    return best_score, round(max_prob * 100, 2)


data = []

for m in matches[:20]:

    try:

        home = m["homeTeam"]["name"]
        away = m["awayTeam"]["name"]

        if home not in attack or away not in attack:
            continue

        home_attack = attack[home]
        away_attack = attack[away]

        home_def = defense[home]
        away_def = defense[away]

        home_xg = (home_attack + away_def) / 2
        away_xg = (away_attack + home_def) / 2

        score, prob = score_probable(home_xg, away_xg)

        over25 = "Oui" if home_xg + away_xg > 2.5 else "Non"

        piege = "⚠️ Match piège" if abs(home_attack-away_attack) < 0.15 else "✅ Stable"

        data.append({
            "Match": f"{home} vs {away}",
            "Score probable": score,
            "Probabilité %": prob,
            "Over 2.5": over25,
            "Analyse": piege
        })

    except:
        continue


if len(data) == 0:
    st.warning("⚠️ Pas assez de données pour analyse")
    st.stop()

df = pd.DataFrame(data)

# ANALYSE
if menu == "Analyse IA":

    st.subheader("📊 Analyse des matchs")
    st.dataframe(df)

# TOP PARIS
if menu == "Top 3 paris sûrs":

    st.subheader("🏆 Top 3 paris les plus sûrs")

    top = df.sort_values("Probabilité %", ascending=False).head(3)

    st.dataframe(top)

    gain = stake * 15

    st.subheader("💰 Gain potentiel")
    st.write(gain)

# GRAPHIQUE
if menu == "Graphique IA":

    st.subheader("📈 Graphique Probabilité")

    fig, ax = plt.subplots()

    ax.bar(df["Match"], df["Probabilité %"])

    plt.xticks(rotation=45)

    st.pyplot(fig)
