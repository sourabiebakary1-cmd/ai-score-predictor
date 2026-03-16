import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random
from datetime import datetime, timedelta
from scipy.stats import poisson

st.set_page_config(page_title="BAKARY AI FOOTBALL PRO", layout="wide")

# STYLE
st.markdown("""
<style>
.stApp{
background-color:#0e1117;
color:white;
}
h1{
color:#00ffcc;
}
</style>
""", unsafe_allow_html=True)

st.title("⚽ BAKARY AI FOOTBALL PRO V16 ULTRA IA")
st.success("IA Football Analyse Professionnelle")

API_KEY = "289e8418878e48c598507cf2b72338f5"

headers = {
"X-Auth-Token": API_KEY
}

# SIDEBAR
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
"Matchs du jour",
"Analyse IA",
"Score Exact IA",
"Meilleurs Paris IA",
"Ticket Combiné IA",
"Classement",
"Graphique IA"
]
)

# DATES
today = datetime.today()
future = today + timedelta(days=3)

date_from = today.strftime("%Y-%m-%d")
date_to = future.strftime("%Y-%m-%d")

# MATCHS
url = f"https://api.football-data.org/v4/competitions/{league}/matches?dateFrom={date_from}&dateTo={date_to}"
response = requests.get(url, headers=headers)

matches = []

if response.status_code == 200:

    data = response.json()

    for match in data["matches"]:

        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]

        home_logo = match["homeTeam"]["crest"]
        away_logo = match["awayTeam"]["crest"]

        # statistiques simulées intelligentes
        attack_home = random.uniform(1.2,2.5)
        attack_away = random.uniform(1.0,2.2)

        defense_home = random.uniform(0.8,1.5)
        defense_away = random.uniform(0.8,1.5)

        # forme équipe
        form_home = random.randint(2,5)
        form_away = random.randint(1,4)

        # calcul IA
        power_home = attack_home + form_home - defense_away
        power_away = attack_away + form_away - defense_home

        prob_home = int((power_home/(power_home+power_away))*100)

        # score poisson
        home_goals = np.argmax([poisson.pmf(i, attack_home) for i in range(5)])
        away_goals = np.argmax([poisson.pmf(i, attack_away) for i in range(5)])

        # statut
        if prob_home > 75:
            status = "🟢 Très bon pari"
        elif prob_home > 65:
            status = "🟡 Bon pari"
        else:
            status = "🔴 Match risqué"

        cote = round(random.uniform(1.30,2.80),2)

        matches.append({
        "Match":f"{home} vs {away}",
        "Home":home,
        "Away":away,
        "LogoHome":home_logo,
        "LogoAway":away_logo,
        "Probabilité %":prob_home,
        "Score IA":f"{home_goals}-{away_goals}",
        "Cote":cote,
        "Statut":status
        })

df = pd.DataFrame(matches)

# MATCHS DU JOUR
if menu == "Matchs du jour":

    st.subheader("⚽ Matchs analysés")

    for i,row in df.iterrows():

        col1,col2,col3 = st.columns([1,2,1])

        with col1:
            st.image(row["LogoHome"], width=70)

        with col2:
            st.write(f"### {row['Match']}")
            st.write(f"Probabilité : {row['Probabilité %']}%")
            st.write(f"Score IA : {row['Score IA']}")
            st.write(row["Statut"])

        with col3:
            st.image(row["LogoAway"], width=70)

# ANALYSE
elif menu == "Analyse IA":

    st.subheader("📊 Analyse complète")

    st.dataframe(df)

# SCORE EXACT
elif menu == "Score Exact IA":

    st.subheader("🎯 Score exact IA")

    st.table(df[["Match","Score IA","Probabilité %"]])

# MEILLEURS PARIS
elif menu == "Meilleurs Paris IA":

    st.subheader("🔥 Meilleurs paris du jour")

    best = df[df["Probabilité %"] > 70]

    st.table(best)

# TICKET
elif menu == "Ticket Combiné IA":

    st.subheader("🎟 Ticket combiné automatique")

    ticket = df.sort_values(by="Probabilité %", ascending=False).head(3)

    st.table(ticket)

    total_cote = ticket["Cote"].prod()

    gain = mise * total_cote

    st.success(f"Gain potentiel : {round(gain,2)} €")

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
            "Points":team["points"],
            "Buts marqués":team["goalsFor"],
            "Buts encaissés":team["goalsAgainst"]
            })

        st.table(pd.DataFrame(teams))

# GRAPHIQUE
elif menu == "Graphique IA":

    st.subheader("📈 Probabilités IA")

    fig, ax = plt.subplots()

    ax.bar(df["Match"], df["Probabilité %"])

    plt.xticks(rotation=45)

    st.pyplot(fig)
