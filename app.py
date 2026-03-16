import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from scipy.stats import poisson

st.set_page_config(page_title="BAKARY AI FOOTBALL PRO", layout="wide")

st.title("⚽ BAKARY AI FOOTBALL PRO")
st.success("IA Analyse Football")

# TA CLE API
API_KEY = "289e8418878e48c598507cf2b72338f5"

headers = {"X-Auth-Token": API_KEY}

# SIDEBAR
st.sidebar.title("Paramètres")

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
"Score Exact",
"Over/Under",
"BTTS",
"Top Paris",
"Ticket Combiné",
"Classement",
"Graphique"
]
)

# DATES
today = datetime.today()
future = today + timedelta(days=5)

date_from = today.strftime("%Y-%m-%d")
date_to = future.strftime("%Y-%m-%d")

# API MATCHS
url = f"https://api.football-data.org/v4/competitions/{league}/matches?dateFrom={date_from}&dateTo={date_to}"

response = requests.get(url, headers=headers)

# API CLASSEMENT
table_url = f"https://api.football-data.org/v4/competitions/{league}/standings"

table_response = requests.get(table_url, headers=headers)

teams_stats = {}

if table_response.status_code == 200:

    standings = table_response.json()

    for team in standings["standings"][0]["table"]:

        name = team["team"]["name"]

        played = team["playedGames"]

        if played == 0:
            played = 1

        attack = team["goalsFor"] / played
        defense = team["goalsAgainst"] / played

        teams_stats[name] = {
            "attack": attack,
            "defense": defense
        }

matches = []

if response.status_code == 200:

    data = response.json()

    for match in data["matches"]:

        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]

        home_logo = match["homeTeam"]["crest"]
        away_logo = match["awayTeam"]["crest"]

        attack_home = teams_stats.get(home, {}).get("attack", 1.4)
        defense_home = teams_stats.get(home, {}).get("defense", 1.2)

        attack_away = teams_stats.get(away, {}).get("attack", 1.2)
        defense_away = teams_stats.get(away, {}).get("defense", 1.3)

        lambda_home = attack_home * defense_away
        lambda_away = attack_away * defense_home

        home_goals = np.argmax([poisson.pmf(i, lambda_home) for i in range(6)])
        away_goals = np.argmax([poisson.pmf(i, lambda_away) for i in range(6)])

        prob_home = int((lambda_home/(lambda_home+lambda_away))*100)

        total_goals = home_goals + away_goals

        over = "Over 2.5" if total_goals > 2 else "Under 2.5"

        btts = "Oui" if home_goals > 0 and away_goals > 0 else "Non"

        if prob_home > 75:
            status = "🟢 Très bon pari"
        elif prob_home > 65:
            status = "🟡 Bon pari"
        else:
            status = "🔴 Match piège"

        cote = round(1.30 + (100 - prob_home)/100, 2)

        matches.append({
            "Match": f"{home} vs {away}",
            "LogoHome": home_logo,
            "LogoAway": away_logo,
            "Probabilité": prob_home,
            "Score IA": f"{home_goals}-{away_goals}",
            "Over/Under": over,
            "BTTS": btts,
            "Cote": cote,
            "Statut": status
        })

df = pd.DataFrame(matches)

# MATCHS
if menu == "Matchs du jour":

    st.subheader("Matchs analysés")

    if len(df) == 0:
        st.warning("Aucun match trouvé")

    for i, row in df.iterrows():

        c1, c2, c3 = st.columns([1,2,1])

        with c1:
            st.image(row["LogoHome"], width=60)

        with c2:
            st.write(f"### {row['Match']}")
            st.write("Probabilité :", row["Probabilité"], "%")
            st.write("Score IA :", row["Score IA"])
            st.write(row["Statut"])

        with c3:
            st.image(row["LogoAway"], width=60)

# ANALYSE
elif menu == "Analyse IA":

    st.dataframe(df)

# SCORE EXACT
elif menu == "Score Exact":

    st.table(df[["Match","Score IA","Probabilité"]])

# OVER UNDER
elif menu == "Over/Under":

    st.table(df[["Match","Over/Under"]])

# BTTS
elif menu == "BTTS":

    st.table(df[["Match","BTTS"]])

# TOP PARIS
elif menu == "Top Paris":

    top = df.sort_values(by="Probabilité", ascending=False).head(5)

    st.table(top)

# TICKET
elif menu == "Ticket Combiné":

    ticket = df.sort_values(by="Probabilité", ascending=False).head(3)

    st.table(ticket)

    cote_total = ticket["Cote"].prod()

    gain = mise * cote_total

    st.success(f"Gain potentiel : {round(gain,2)} €")

# CLASSEMENT
elif menu == "Classement":

    if table_response.status_code == 200:

        teams = []

        for team in standings["standings"][0]["table"]:

            teams.append({
                "Position": team["position"],
                "Equipe": team["team"]["name"],
                "Points": team["points"]
            })

        st.table(pd.DataFrame(teams))

# GRAPHIQUE
elif menu == "Graphique":

    fig, ax = plt.subplots()

    ax.bar(df["Match"], df["Probabilité"])

    plt.xticks(rotation=45)

    st.pyplot(fig)
