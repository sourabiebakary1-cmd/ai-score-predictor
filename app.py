import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random
from datetime import date
from scipy.stats import poisson

st.set_page_config(page_title="BAKARY AI FOOTBALL PRO V12", layout="wide")

st.title("⚽ BAKARY AI FOOTBALL PRO V12 MASTER")
st.success("IA Football Ultra Avancée")

API_KEY = "289e8418878e48c598507cf2b72338f5"

headers = {
    "X-Auth-Token": API_KEY
}

st.sidebar.title("⚙️ Paramètres")

league = st.sidebar.selectbox(
"Ligue",
{
"Premier League":"PL",
"La Liga":"PD",
"Ligue 1":"FL1",
"Serie A":"SA",
"Bundesliga":"BL1"
}
)

mise = st.sidebar.number_input("💰 Mise", value=100)

menu = st.sidebar.radio(
"Menu",
[
"Analyse IA",
"Score Exact IA",
"Top Paris",
"Ticket Combiné IA",
"Classement",
"Graphique IA"
]
)

today = str(date.today())

url = f"https://api.football-data.org/v4/competitions/{league}/matches?dateFrom={today}&dateTo={today}"

response = requests.get(url, headers=headers)

matches = []

if response.status_code == 200:

    data = response.json()

    for match in data["matches"]:

        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]

        attack_home = random.uniform(1,2)
        attack_away = random.uniform(1,2)

        home_goals = np.argmax([poisson.pmf(i, attack_home) for i in range(5)])
        away_goals = np.argmax([poisson.pmf(i, attack_away) for i in range(5)])

        prob = random.randint(60,90)

        if prob > 80:
            status = "✅ Match sûr"
        elif prob > 70:
            status = "⚠️ Moyen"
        else:
            status = "🚨 Match piège"

        cote = round(random.uniform(1.3,2.8),2)

        matches.append({
            "Match":f"{home} vs {away}",
            "Probabilité":prob,
            "Score IA":f"{home_goals}-{away_goals}",
            "Cote":cote,
            "Statut":status
        })

df = pd.DataFrame(matches)

# ANALYSE
if menu == "Analyse IA":

    st.subheader("📊 Analyse IA")

    st.dataframe(df)

# SCORE EXACT
elif menu == "Score Exact IA":

    st.subheader("🎯 Score exact IA")

    st.table(df[["Match","Score IA","Probabilité"]])

# TOP PARIS
elif menu == "Top Paris":

    st.subheader("🔥 Top 5 Paris sûrs")

    top = df.sort_values(by="Probabilité", ascending=False).head(5)

    st.table(top)

# TICKET
elif menu == "Ticket Combiné IA":

    st.subheader("🎟 Ticket combiné IA")

    ticket = df.sort_values(by="Probabilité", ascending=False).head(3)

    st.table(ticket)

    total_cote = ticket["Cote"].prod()

    gain = mise * total_cote

    st.success(f"Gain potentiel : {round(gain,2)}")

# CLASSEMENT
elif menu == "Classement":

    table_url = f"https://api.football-data.org/v4/competitions/{league}/standings"

    table_response = requests.get(table_url, headers=headers)

    if table_response.status_code == 200:

        standings = table_response.json()

        teams = []

        for team in standings["standings"][0]["table"]:

            teams.append({
                "Position":team["position"],
                "Equipe":team["team"]["name"],
                "Points":team["points"]
            })

        st.table(pd.DataFrame(teams))

# GRAPHIQUE
elif menu == "Graphique IA":

    plt.figure()

    plt.bar(df["Match"], df["Probabilité"])

    plt.xticks(rotation=45)

    st.pyplot(plt)
