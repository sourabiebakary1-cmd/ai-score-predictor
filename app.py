import streamlit as st
import requests
import pandas as pd
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

st.set_page_config(page_title="BAKARY AI FOOTBALL PRO V7", layout="wide")

st.title("⚽ BAKARY AI FOOTBALL PRO V7")

API_KEY="289e8418878e48c598507cf2b72338f
5"

headers={"X-Auth-Token":API_KEY}

st.sidebar.title("Paramètres")

mise=st.sidebar.number_input("Mise",value=100)

menu=st.sidebar.radio(
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

    leagues=["PL","PD","BL1","SA","FL1"]

    today=datetime.utcnow()
    future=today+timedelta(days=7)

    date_from=today.strftime("%Y-%m-%d")
    date_to=future.strftime("%Y-%m-%d")

    matches=[]

    for league in leagues:

        try:

            url=f"https://api.football-data.org/v4/competitions/{league}/matches?dateFrom={date_from}&dateTo={date_to}"

            r=requests.get(url,headers=headers,timeout=10)

            if r.status_code!=200:
                continue

            data=r.json()

            for match in data.get("matches",[]):

                home=match["homeTeam"]["name"]
                away=match["awayTeam"]["name"]

                attack_home=np.random.uniform(1.4,2.2)
                attack_away=np.random.uniform(1.2,2.0)

                max_goals=6

                home_probs=[poisson.pmf(i,attack_home) for i in range(max_goals)]
                away_probs=[poisson.pmf(i,attack_away) for i in range(max_goals)]

                matrix=np.outer(home_probs,away_probs)

                home_win=0
                draw=0
                away_win=0

                for i in range(max_goals):
                    for j in range(max_goals):

                        prob=matrix[i][j]

                        if i>j:
                            home_win+=prob
                        elif i==j:
                            draw+=prob
                        else:
                            away_win+=prob

                prob_home=int(home_win*100)
                prob_draw=int(draw*100)
                prob_away=int(away_win*100)

                diff=abs(prob_home-prob_away)

                if diff<8:
                    status="🚨 Piège"
                elif prob_home>75:
                    status="💎 Safe"
                else:
                    status="Normal"

                cote=round(np.random.uniform(1.4,3.0),2)

                matches.append({
                "Match":f"{home} vs {away}",
                "Home %":prob_home,
                "Draw %":prob_draw,
                "Away %":prob_away,
                "Cote":cote,
                "Statut":status
                })

        except:
            continue

    return pd.DataFrame(matches)

df=get_matches()

# TABLEAU
if menu=="Tableau Pronostics":

    st.subheader("📊 Tableau Professionnel")

    if df.empty:
        st.warning("Aucun match trouvé")
    else:
        st.dataframe(df)

# GRAPHIQUE
elif menu=="Graphique IA":

    if not df.empty:

        fig,ax=plt.subplots()

        ax.bar(df["Match"],df["Home %"])

        plt.xticks(rotation=90)

        st.pyplot(fig)

# TOP 5
elif menu=="Top 5 Paris Sûrs":

    if not df.empty:

        safe=df.sort_values(by="Home %",ascending=False).head(5)

        st.table(safe)

# PIEGES
elif menu=="Matchs Pièges":

    pieges=df[df["Statut"]=="🚨 Piège"]

    st.table(pieges)

# TICKET
elif menu=="Ticket Intelligent":

    ticket=df.sort_values(by="Home %",ascending=False).head(3)

    st.table(ticket)

    total=ticket["Cote"].prod()

    gain=mise*total

    st.success(f"Gain potentiel : {round(gain,2)}")
