import streamlit as st
import numpy as np
import requests
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import poisson

st.set_page_config(page_title="BAKARY AI PRO", layout="wide")

st.title("⚽ BAKARY AI FOOTBALL PRO V2")
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
"Top 3 paris sûrs",
"Graphique IA"
]
)

match_url = f"https://api.football-data.org/v4/competitions/{code}/matches?status=SCHEDULED"
standings_url = f"https://api.football-data.org/v4/competitions/{code}/standings"

matches_data = requests.get(match_url, headers=headers).json()
standings_data = requests.get(standings_url, headers=headers).json()

matches = matches_data.get("matches", [])

table = standings_data["standings"][0]["table"]

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

    return best_score, round(max_prob * 100,2)


def result_prob(home_xg, away_xg):

    home = 0
    draw = 0
    away = 0

    for i in range(5):
        for j in range(5):

            p = poisson.pmf(i, home_xg)*poisson.pmf(j, away_xg)

            if i>j:
                home += p
            elif i==j:
                draw += p
            else:
                away += p

    return round(home*100,1),round(draw*100,1),round(away*100,1)


def detect_piege(home_attack, away_attack):

    diff = abs(home_attack-away_attack)

    if diff < 0.15:
        return "⚠️ Match piège"

    return "✅ Stable"


data=[]

for m in matches[:20]:

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

    score,score_prob = score_probable(home_xg,away_xg)

    ph,pd,pa = result_prob(home_xg,away_xg)

    piege = detect_piege(home_attack,away_attack)

    over25 = "Oui" if home_xg+away_xg>2.5 else "Non"

    data.append({
        "Match":f"{home} vs {away}",
        "Score probable":score,
        "Prob Score %":score_prob,
        "Victoire domicile %":ph,
        "Nul %":pd,
        "Victoire extérieur %":pa,
        "Over 2.5":over25,
        "Analyse":piege
    })

df = pd.DataFrame(data)

# PAGE ANALYSE
if menu=="Analyse IA":

    st.subheader("📊 Analyse IA complète")
    st.dataframe(df)

# TOP PARIS
if menu=="Top 3 paris sûrs":

    st.subheader("🏆 Top 3 paris les plus sûrs")

    top = df.sort_values("Prob Score %",ascending=False).head(3)

    st.dataframe(top)

    gain = stake*15

    st.subheader("💰 Gain potentiel combiné")

    st.write(gain)

# GRAPHIQUE
if menu=="Graphique IA":

    st.subheader("📈 Probabilité Victoire")

    fig, ax = plt.subplots()

    ax.bar(df["Match"],df["Victoire domicile %"])

    plt.xticks(rotation=45)

    st.pyplot(fig)
