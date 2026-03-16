import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import poisson
import random

st.set_page_config(page_title="BAKARY AI FOOTBALL PRO V7", layout="wide")

st.title("BAKARY AI FOOTBALL PRO V7")
st.success("IA Football professionnelle")

TA CLE API

API_KEY = "289e8418878e48c598507cf2b72338f5"

headers = {
"X-Auth-Token": API_KEY
}

MENU

st.sidebar.title("Parametres")

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
"Top 5 paris surs",
"Graphique IA"
]
)

URL API

match_url = f"https://api.football-data.org/v4/competitions/{code}/matches?status=SCHEDULED"
standings_url = f"https://api.football-data.org/v4/competitions/{code}/standings"

Connexion API

try:
matches_data = requests.get(match_url, headers=headers).json()
standings_data = requests.get(standings_url, headers=headers).json()
except:
st.error("Erreur connexion API")
st.stop()

matches = matches_data.get("matches", [])

if len(matches) == 0:
st.warning("Aucun match trouve")
st.stop()

try:
table = standings_data["standings"][0]["table"]
except:
st.error("Classement indisponible")
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

def score_prediction(home_xg, away_xg):

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

for m in matches[:40]:

try:

    home = m["homeTeam"]["name"]
    away = m["awayTeam"]["name"]

    if home not in attack or away not in attack:
        continue

    home_attack = attack[home]
    away_attack = attack[away]

    home_def = defense[home]
    away_def = defense[away]

    home_xg = (home_attack * 1.3 + away_def * 0.7) + 0.35
    away_xg = (away_attack * 1.1 + home_def * 0.6)

    home_xg += random.uniform(-0.2,0.4)
    away_xg += random.uniform(-0.2,0.4)

    home_xg = max(0.2, min(home_xg, 3.5))
    away_xg = max(0.2, min(away_xg, 3.5))

    score, prob = score_prediction(home_xg, away_xg)

    total = home_xg + away_xg

    if home_xg > away_xg + 0.4:
        result = "Victoire domicile"
    elif away_xg > home_xg + 0.4:
        result = "Victoire exterieur"
    else:
        result = "Match nul possible"

    over25 = "Oui" if total > 2.5 else "Non"

    if abs(home_attack-away_attack) < 0.15:
        analyse = "Match piege"
    elif abs(home_xg-away_xg) < 0.25:
        analyse = "Match incertain"
    else:
        analyse = "Stable"

    if prob < 8:
        risk = "A eviter"
    else:
        risk = "OK"

    data.append({
        "Match": f"{home} vs {away}",
        "Score IA": score,
        "Probabilite %": prob,
        "Pronostic": result,
        "Over 2.5": over25,
        "Analyse IA": analyse,
        "Risque": risk
    })

except:
    continue

if len(data) == 0:
st.warning("Pas assez de donnees")
st.stop()

df = pd.DataFrame(data)

if menu == "Analyse IA":

st.subheader("Analyse des matchs")
st.dataframe(df)

if menu == "Top 5 paris surs":

st.subheader("Top 5 paris les plus surs")

top = df.sort_values("Probabilite %", ascending=False).head(5)

st.dataframe(top)

st.subheader("Simulation combine")

cote = 1

for i in range(len(top)):
    cote *= 1.45

gain = stake * cote

st.write("Cote estimee :", round(cote,2))
st.write("Gain potentiel :", round(gain,2),"€")

if menu == "Graphique IA":

st.subheader("Graphique probabilites")

fig, ax = plt.subplots()

ax.bar(df["Match"], df["Probabilite %"])

plt.xticks(rotation=45)

st.pyplot(fig)
