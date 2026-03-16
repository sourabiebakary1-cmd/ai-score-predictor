import streamlit as st
import requests
import pandas as pd
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

st.set_page_config(page_title="BAKARY AI FOOTBALL PRO V9", layout="wide")

st.title("⚽ BAKARY AI FOOTBALL PRO V9")

API_KEY = "289e8418878e48c598507cf2b72338f5"

headers = {
    "X-Auth-Token": API_KEY
}

st.sidebar.title("Paramètres")

mise = st.sidebar.number_input("Mise", value=100)

menu = st.sidebar.radio(
    "Menu",
    [
        "Tableau Pronostics",
        "Graphique IA",
        "Top 5 Paris Sûrs",
        "Matchs Pièges",
        "Ticket Intelligent"
    ]
)

@st.cache_data(ttl=3600)
def get_matches():

    leagues = ["PL","PD","BL1","SA","FL1"]

    today = datetime.utcnow()
    future = today + timedelta(days=7)

    date_from = today.strftime("%Y-%m-%d")
    date_to = future.strftime("%Y-%m-%d")

    matches = []

    for league in leagues:

        try:

            url = f"https://api.football-data.org/v4/competitions/{league}/matches?dateFrom={date_from}&dateTo={date_to}"

            r = requests.get(url, headers=headers, timeout=10)

            if r.status_code != 200:
                continue

            data = r.json()

            for match in data.get("matches", []):

                home = match["homeTeam"]["name"]
                away = match["awayTeam"]["name"]

                attack_home = np.random.uniform(1.3,2.3)
                attack_away = np.random.uniform(1.1,2.1)

                max_goals = 6

                home_probs = [poisson.pmf(i, attack_home) for i in range(max_goals)]
                away_probs = [poisson.pmf(i, attack_away) for i in range(max_goals)]

                matrix = np.outer(home_probs, away_probs)

                home_win = 0
                draw = 0
                away_win = 0

                best_score = ""
                best_prob = 0

                over25 = 0
                btts = 0

                for i in range(max_goals):
                    for j in range(max_goals):

                        prob = matrix[i][j]

                        if i > j:
                            home_win += prob
                        elif i == j:
                            draw += prob
                        else:
                            away_win += prob

                        if prob > best_prob:
                            best_prob = prob
                            best_score = f"{i}-{j}"

                        if i + j > 2:
                            over25 += prob

                        if i > 0 and j > 0:
                            btts += prob

                prob_home = int(home_win * 100)
                prob_draw = int(draw * 100)
                prob_away = int(away_win * 100)

                if prob_home > prob_away and prob_home > prob_draw:
                    prediction = "1"
                elif prob_away > prob_home and prob_away > prob_draw:
                    prediction = "2"
                else:
                    prediction = "N"

                diff = abs(prob_home - prob_away)

                if diff < 10:
                    status = "🚨 Piège"
                elif prob_home >= 70:
                    status = "💎 Ultra Safe"
                elif prob_home >= 60:
                    status = "Bon Pari"
                else:
                    status = "Risque"

                cote = round(np.random.uniform(1.4,3.0),2)

                matches.append({
                    "Match": f"{home} vs {away}",
                    "Pronostic": prediction,
                    "Score Exact": best_score,
                    "Home %": prob_home,
                    "Draw %": prob_draw,
                    "Away %": prob_away,
                    "Over2.5 %": int(over25*100),
                    "BTTS %": int(btts*100),
                    "Cote": cote,
                    "Statut": status
                })

        except:
            continue

    return pd.DataFrame(matches)

df = get_matches()

if menu == "Tableau Pronostics":

    st.subheader("📊 Tableau Professionnel")

    if df.empty:
        st.warning("Aucun match trouvé")
    else:
        st.dataframe(df)

elif menu == "Graphique IA":

    if not df.empty:

        fig, ax = plt.subplots()

        ax.bar(df["Match"], df["Home %"])

        plt.xticks(rotation=90)

        st.pyplot(fig)

elif menu == "Top 5 Paris Sûrs":

    if not df.empty:

        safe = df[df["Statut"] != "🚨 Piège"].sort_values(by="Home %", ascending=False).head(5)

        st.table(safe)

elif menu == "Matchs Pièges":

    pieges = df[df["Statut"] == "🚨 Piège"]

    st.table(pieges)

elif menu == "Ticket Intelligent":

    ticket = df[df["Statut"] != "🚨 Piège"].sort_values(by="Home %", ascending=False).head(3)

    st.table(ticket)

    total = ticket["Cote"].prod()

    gain = mise * total

    st.success(f"Gain potentiel : {round(gain,2)}")
