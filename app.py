import streamlit as st
import numpy as np
import requests
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import poisson

st.set_page_config(page_title="BAKARY AI FOOTBALL PRO V3", layout="wide")

st.title("⚽ BAKARY AI FOOTBALL PRO V3")
st.success("🧠 IA Avancée - Analyse intelligente")

API_KEY = "289e8418878e48c598507cf2b72338f5"

headers = {"X-Auth-Token": API_KEY}

# MENU
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
"Top 5 paris sûrs",
"Graphique IA"
]
)

# API URL
match_url = f"https://api.football-data.org/v4/competitions/{code}/matches?status=SCHEDULED"
standings_url = f"https://api.football-data.org/v4/competitions/{code}/standings"

# APPEL API SECURISE
try:
    matches_response = requests.get(match_url, headers=headers)
    standings_response = requests.get(standings_url, headers=headers)

    matches_data = matches_response.json()
    standings_data = standings_response.json()

except:
    st.error("❌ Impossible de récupérer les données API")
    st.stop()

matches = matches_data.get("matches", [])

if len(matches) == 0:
    st.warning("⚠️ Aucun match disponible")
    st.stop()

try:
    table = standings_data["standings"][0]["table"]
except:
    st.error("❌ Classement indisponible")
    st.stop()

attack = {}
defense = {}

for team in table:

    try:
        name = team["team"]["name"]
        played = team["playedGames"]

        if played == 0:
            continue

        attack[name] = team["goalsFor"] / played
        defense[name] = team["goalsAgainst"] / played

    except:
        continue


def score_probable(home_xg, away_xg):

    best_score = "0-0"
    max_prob = 0

    for i in range(6):
        for j in range(6):

            prob = poisson.pmf(i, home_xg) * poisson.pmf(j, away_xg)

            if prob > max_prob:
                max_prob = prob
                best_score = f"{i}-{j}"

    return best_score, round(max_prob*100,2)


data = []

for m in matches[:25]:

    try:

        home = m["homeTeam"]["name"]
        away = m["awayTeam"]["name"]

        if home not in attack or away not in attack:
            continue

        home_attack = attack[home]
        away_attack = attack[away]

        home_def = defense[home]
        away_def = defense[away]

        home_xg = (home_attack + away_def)/2
        away_xg = (away_attack + home_def)/2

        score, prob = score_probable(home_xg, away_xg)

        total = home_xg + away_xg

        over25 = "Oui" if total > 2.5 else "Non"

        if abs(home_attack-away_attack) < 0.15:
            analyse = "⚠️ Match piège"

        elif home_attack > away_attack:
            analyse = "🏠 Avantage domicile"

        else:
            analyse = "🚀 Avantage extérieur"

        data.append({
            "Match": f"{home} vs {away}",
            "Score IA": score,
            "Probabilité %": prob,
            "Over 2.5": over25,
            "Analyse IA": analyse
        })

    except:
        continue

# SECURITE DATAFRAME
if len(data) == 0:
    st.warning("⚠️ Pas assez de données pour analyse")
    st.stop()

df = pd.DataFrame(data)

# ANALYSE
if menu == "Analyse IA":

    st.subheader("📊 Analyse des matchs")
    st.dataframe(df)

# TOP PARIS
if menu == "Top 5 paris sûrs":

    st.subheader("🏆 Top 5 paris les plus sûrs")

    top = df.sort_values("Probabilité %", ascending=False).head(5)

    st.dataframe(top)

    st.subheader("💰 Simulation combiné")

    cote = 1

    for i in range(len(top)):
        cote *= 1.6

    gain = stake * cote

    st.write("Cote estimée :", round(cote,2))
    st.write("Gain potentiel :", round(gain,2),"€")

# GRAPHIQUE
if menu == "Graphique IA":

    st.subheader("📈 Graphique IA")

    fig, ax = plt.subplots()

    ax.bar(df["Match"], df["Probabilité %"])

    plt.xticks(rotation=45)

    st.pyplot(fig)
