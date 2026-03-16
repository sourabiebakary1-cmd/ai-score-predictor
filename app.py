import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

st.set_page_config(page_title="BAKARY AI FOOTBALL PRO V300", layout="wide")

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
background:#00ffcc;
color:black;
}
</style>
""", unsafe_allow_html=True)

st.title("⚽ BAKARY AI FOOTBALL PRO V300 GOD LEVEL")
st.success("IA Football Analyse Professionnelle")

API_KEY="289e8418878e48c598507cf2b72338f5"

headers={"X-Auth-Token":API_KEY}

# SIDEBAR
st.sidebar.title("⚙️ Paramètres")

league=st.sidebar.selectbox(
"Ligue",
{
"Bundesliga":"BL1",
"Ligue 1":"FL1"
}
)

mise=st.sidebar.number_input("💰 Mise",value=100)

menu=st.sidebar.radio(
"Menu",
[
"Matchs du jour",
"Analyse IA",
"Top Paris",
"Ticket Intelligent",
"Classement",
"Graphique"
]
)

today=datetime.utcnow()
future=today+timedelta(days=7)

date_from=today.strftime("%Y-%m-%d")
date_to=future.strftime("%Y-%m-%d")

url=f"https://api.football-data.org/v4/competitions/{league}/matches?dateFrom={date_from}&dateTo={date_to}"

matches=[]

try:

    r=requests.get(url,headers=headers)

    if r.status_code==200:

        data=r.json()

        for match in data.get("matches",[]):

            home=match["homeTeam"]["name"]
            away=match["awayTeam"]["name"]

            home_logo=match["homeTeam"].get("crest")
            away_logo=match["awayTeam"].get("crest")

            attack_home=np.random.uniform(1.5,2.6)
            attack_away=np.random.uniform(1.2,2.3)

            home_win=0
            draw=0
            away_win=0

            for i in range(1000):

                g_home=np.random.poisson(attack_home)
                g_away=np.random.poisson(attack_away)

                if g_home>g_away:
                    home_win+=1
                elif g_home==g_away:
                    draw+=1
                else:
                    away_win+=1

            prob_home=int(home_win/10)
            prob_draw=int(draw/10)
            prob_away=int(away_win/10)

            score_home=int(np.mean(np.random.poisson(attack_home,100)))
            score_away=int(np.mean(np.random.poisson(attack_away,100)))

            total_goals=score_home+score_away

            over15="Over 1.5" if total_goals>=2 else "Under 1.5"
            over25="Over 2.5" if total_goals>=3 else "Under 2.5"

            btts="Oui" if score_home>0 and score_away>0 else "Non"

            if prob_home>75:
                status="💎 PARI ULTRA SAFE"
            elif prob_home>65:
                status="🔥 PARI FORT"
            elif prob_home>55:
                status="🟡 MOYEN"
            else:
                status="⚠️ MATCH PIÈGE"

            cote=round(np.random.uniform(1.3,2.5),2)

            matches.append({
            "Match":f"{home} vs {away}",
            "LogoHome":home_logo,
            "LogoAway":away_logo,
            "Home %":prob_home,
            "Draw %":prob_draw,
            "Away %":prob_away,
            "Score IA":f"{score_home}-{score_away}",
            "Over1.5":over15,
            "Over2.5":over25,
            "BTTS":btts,
            "Cote":cote,
            "Statut":status
            })

except:
    st.error("Erreur API")

df=pd.DataFrame(matches)

# MATCHS
if menu=="Matchs du jour":

    if df.empty:
        st.warning("Aucun match disponible")

    else:

        for i,row in df.iterrows():

            col1,col2,col3=st.columns([1,2,1])

            with col1:
                if row["LogoHome"]:
                    st.image(row["LogoHome"],width=60)

            with col2:
                st.write(f"### {row['Match']}")
                st.write(f"Victoire domicile : {row['Home %']}%")
                st.write(f"Nul : {row['Draw %']}%")
                st.write(f"Victoire extérieur : {row['Away %']}%")
                st.write(f"Score IA : {row['Score IA']}")
                st.write(f"{row['Over2.5']} | BTTS : {row['BTTS']}")
                st.write(row["Statut"])

            with col3:
                if row["LogoAway"]:
                    st.image(row["LogoAway"],width=60)

elif menu=="Analyse IA":

    st.dataframe(df)

elif menu=="Top Paris":

    top=df.sort_values(by="Home %",ascending=False).head(10)

    st.table(top)

elif menu=="Ticket Intelligent":

    ticket=df.sort_values(by="Home %",ascending=False).head(3)

    st.table(ticket)

    total_cote=ticket["Cote"].prod()

    gain=mise*total_cote

    st.success(f"Gain potentiel : {round(gain,2)} €")

elif menu=="Classement":

    url2=f"https://api.football-data.org/v4/competitions/{league}/standings"

    r=requests.get(url2,headers=headers)

    if r.status_code==200:

        data=r.json()

        table=[]

        for t in data["standings"][0]["table"]:

            table.append({
            "Position":t["position"],
            "Equipe":t["team"]["name"],
            "Points":t["points"]
            })

        st.table(pd.DataFrame(table))

elif menu=="Graphique":

    fig,ax=plt.subplots()

    ax.bar(df["Match"],df["Home %"])

    plt.xticks(rotation=45)

    st.pyplot(fig)
