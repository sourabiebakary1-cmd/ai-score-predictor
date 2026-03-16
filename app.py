import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="BAKARY AI FOOTBALL PRO SAFE", layout="wide")

st.title("⚽ BAKARY AI FOOTBALL PRO – SAFE VERSION")

API_KEY="289e8418878e48c598507cf2b72338f5"

headers={"X-Auth-Token":API_KEY}

st.sidebar.title("Menu")

menu=st.sidebar.radio(
"Navigation",
[
"Matchs",
"Top Paris"
]
)

# CACHE POUR EVITER TROP APPELS API
@st.cache_data(ttl=3600)
def get_matches():

    leagues=["PL","PD","BL1","FL1","SA"]

    today=datetime.utcnow()
    future=today+timedelta(days=3)

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

            for m in data.get("matches",[]):

                home=m["homeTeam"]["name"]
                away=m["awayTeam"]["name"]

                matches.append({
                "Match":f"{home} vs {away}"
                })

        except:
            pass

    return pd.DataFrame(matches)

df=get_matches()

# MATCHS
if menu=="Matchs":

    if df.empty:

        st.warning("Aucun match trouvé")

    else:

        st.dataframe(df)

# TOP PARIS
elif menu=="Top Paris":

    if df.empty:

        st.warning("Aucun match disponible")

    else:

        top=df.head(5)

        st.table(top)
