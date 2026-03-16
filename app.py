import streamlit as st
import requests
import pandas as pd
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta

st.set_page_config(page_title="BAKARY AI FOOTBALL PRO V2000", layout="wide")

st.title("⚽ BAKARY AI FOOTBALL PRO V2000 – IA FORME ÉQUIPE")

API_KEY="289e8418878e48c598507cf2b72338f5"

headers={"X-Auth-Token":API_KEY}

st.sidebar.title("⚙️ Paramètres")

mise=st.sidebar.number_input("💰 Mise",value=100)

menu=st.sidebar.radio(
"Menu",
[
"Matchs IA",
"Top 5 Paris",
"Ticket Intelligent"
]
)

@st.cache_data(ttl=3600)
def get_matches():

    leagues=["PL","PD","BL1","FL1","SA"]

    today=datetime.utcnow()
    future=today+timedelta(days=4)

    date_from=today.strftime("%Y-%m-%d")
    date_to=future.strftime("%Y-%m-%d")

    matches=[]

    for league in leagues:

        try:

            url=f"https://api.football-data.org/v4/competitions/{league}/matches?dateFrom={date_from}&dateTo={date_to}"

            r=requests.get(url,headers=headers)

            if r.status_code!=200:
                continue

            data=r.json()

            for match in data.get("matches",[]):

                home=match["homeTeam"]["name"]
                away=match["awayTeam"]["name"]

                # Simulation forme équipe
                goals_home=np.random.randint(5,12)
                goals_away=np.random.randint(4,10)

                attack_home=goals_home/5
                attack_away=goals_away/5

                max_goals=6

                home_probs=[poisson.pmf(i,attack_home) for i in range(max_goals)]
                away_probs=[poisson.pmf(i,attack_away) for i in range(max_goals)]

                matrix=np.outer(home_probs,away_probs)

                home_win=0
                draw=0
                away_win=0

                scores={}

                for i in range(max_goals):
                    for j in range(max_goals):

                        prob=matrix[i][j]

                        score=f"{i}-{j}"

                        scores[score]=prob

                        if i>j:
                            home_win+=prob
                        elif i==j:
                            draw+=prob
                        else:
                            away_win+=prob

                prob_home=int(home_win*100)
                prob_draw=int(draw*100)
                prob_away=int(away_win*100)

                best_score=max(scores,key=scores.get)

                h=int(best_score.split("-")[0])
                a=int(best_score.split("-")[1])

                total=h+a

                over25="Over 2.5" if total>=3 else "Under 2.5"
                btts="Oui" if h>0 and a>0 else "Non"

                if abs(prob_home-prob_away)<10:
                    status="⚠️ MATCH PIÈGE"
                elif prob_home>70:
                    status="💎 PARI ULTRA SAFE"
                elif prob_home>60:
                    status="🔥 PARI FORT"
                else:
                    status="🟡 MOYEN"

                cote=round(np.random.uniform(1.4,3.0),2)

                matches.append({
                "Match":f"{home} vs {away}",
                "Home %":prob_home,
                "Draw %":prob_draw,
                "Away %":prob_away,
                "Score IA":best_score,
                "Over2.5":over25,
                "BTTS":btts,
                "Cote":cote,
                "Statut":status
                })

        except:
            pass

    return pd.DataFrame(matches)

df=get_matches()

if menu=="Matchs IA":

    if df.empty:
        st.warning("Aucun match trouvé")
    else:
        st.dataframe(df)

elif menu=="Top 5 Paris":

    if not df.empty:

        top=df.sort_values(by="Home %",ascending=False).head(5)

        st.table(top)

elif menu=="Ticket Intelligent":

    if not df.empty:

        ticket=df.sort_values(by="Home %",ascending=False).head(3)

        st.table(ticket)

        total_cote=ticket["Cote"].prod()

        gain=mise*total_cote

        st.success(f"Gain potentiel : {round(gain,2)} €")
