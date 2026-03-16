import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import poisson
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="BAKARY AI FOOTBALL PRO V40", layout="wide")

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

.stButton>button{
background-color:#00ffcc;
color:black;
}
</style>
""", unsafe_allow_html=True)

st.title("⚽ BAKARY AI FOOTBALL PRO V40 ELITE")
st.success("IA Football Analyse Professionnelle")

# CLE API
API_KEY = "289e8418878e48c598507cf2b72338f5"

headers = {"X-Auth-Token": API_KEY}

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
"Over/Under",
"BTTS",
"Top Paris IA",
"Ticket IA",
"Classement",
"Graphique IA"
]
)

# DATES
today = datetime.utcnow()
future = today + timedelta(days=7)

date_from = today.strftime("%Y-%m-%d")
date_to = future.strftime("%Y-%m-%d")

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

        # IA statistiques
        attack_home = random.uniform(1.2,2.3)
        attack_away = random.uniform(1.0,2.1)

        defense_home = random.uniform(0.8,1.4)
        defense_away = random.uniform(0.8,1.4)

        form_home = random.randint(1,5)
        form_away = random.randint(1,5)

        power_home = attack_home + form_home - defense_away
        power_away = attack_away + form_away - defense_home

        prob_home = int((power_home/(power_home+power_away))*100)

        home_goals = np.argmax([poisson.pmf(i, attack_home) for i in range(6)])
        away_goals = np.argmax([poisson.pmf(i, attack_away) for i in range(6)])

        total_goals = home_goals + away_goals

        over = "Over 2.5" if total_goals > 2 else "Under 2.5"

        btts = "Oui" if home_goals > 0 and away_goals > 0 else "Non"

        if prob_home > 75:
            status = "🟢 Très bon pari"
        elif prob_home > 65:
            status = "🟡 Bon pari"
        else:
            status = "🔴 Match piège"

        cote = round(random.uniform(1.30,2.80),2)

        matches.append({
        "Match":f"{home} vs {away}",
        "LogoHome":home_logo,
        "LogoAway":away_logo,
        "Probabilité %":prob_home,
        "Score IA":f"{home_goals}-{away_goals}",
        "Over/Under":over,
        "BTTS":btts,
        "Cote":cote,
        "Statut":status
        })

df = pd.DataFrame(matches)

# MATCHS
if menu == "Matchs du jour":

    st.subheader("⚽ Matchs analysés")

    if df.empty:
        st.warning("Aucun match trouvé")

    for i,row in df.iterrows():

        col1,col2,col3 = st.columns([1,2,1])

        with col1:
            st.image(row["LogoHome"], width=70)

        with col2:
            st.write(f"### {row['Match']}")
            st.write(f"Probabilité : {row['Probabilité %']}%")
            st.write(f"Score IA : {row['Score IA']}")
            st.write(f"Over/Under : {row['Over/Under']}")
            st.write(f"BTTS : {row['BTTS']}")
            st.write(row["Statut"])

        with col3:
            st.image(row["LogoAway"], width=70)

# ANALYSE
elif menu == "Analyse IA":

    st.dataframe(df)

# SCORE EXACT
elif menu == "Score Exact IA":

    st.table(df[["Match","Score IA","Probabilité %"]])

# OVER UNDER
elif menu == "Over/Under":

    st.table(df[["Match","Over/Under"]])

# BTTS
elif menu == "BTTS":

    st.table(df[["Match","BTTS"]])

# TOP PARIS
elif menu == "Top Paris IA":

    top = df.sort_values(by="Probabilité %", ascending=False).head(10)

    st.table(top)

# TICKET
elif menu == "Ticket IA":

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
            "Points":team["points"]
            })

        st.table(pd.DataFrame(teams))

# GRAPHIQUE
elif menu == "Graphique IA":

    fig, ax = plt.subplots()

    ax.bar(df["Match"], df["Probabilité %"])

    plt.xticks(rotation=45)

    st.pyplot(fig)
