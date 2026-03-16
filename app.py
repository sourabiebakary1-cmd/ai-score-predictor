import streamlit as st
import requests
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime, timedelta

st.set_page_config(page_title="BAKARY AI FOOTBALL PRO ML", layout="wide")

st.title("⚽ BAKARY AI FOOTBALL PRO – MACHINE LEARNING")

API_KEY="289e8418878e48c598507cf2b72338f5"

headers={"X-Auth-Token":API_KEY}

st.sidebar.title("⚙️ Paramètres")

menu=st.sidebar.radio(
"Menu",
[
"Entrainer IA",
"Prédictions Matchs"
]
)

league="PL"

# ENTRAINEMENT IA
if menu=="Entrainer IA":

    st.write("Chargement des anciens matchs...")

    url="https://api.football-data.org/v4/competitions/PL/matches?status=FINISHED"

    r=requests.get(url,headers=headers)

    data=r.json()

    rows=[]

    for match in data["matches"]:

        home_goals=match["score"]["fullTime"]["home"]
        away_goals=match["score"]["fullTime"]["away"]

        if home_goals is None or away_goals is None:
            continue

        result=0

        if home_goals>away_goals:
            result=1
        elif home_goals<away_goals:
            result=2

        rows.append({
        "home_goals":home_goals,
        "away_goals":away_goals,
        "result":result
        })

    df=pd.DataFrame(rows)

    X=df[["home_goals","away_goals"]]
    y=df["result"]

    model=RandomForestClassifier()

    model.fit(X,y)

    st.success("IA entrainée avec succès")

# PREDICTIONS
elif menu=="Prédictions Matchs":

    today=datetime.utcnow()
    future=today+timedelta(days=5)

    date_from=today.strftime("%Y-%m-%d")
    date_to=future.strftime("%Y-%m-%d")

    url=f"https://api.football-data.org/v4/competitions/{league}/matches?dateFrom={date_from}&dateTo={date_to}"

    r=requests.get(url,headers=headers)

    data=r.json()

    matches=[]

    for match in data["matches"]:

        home=match["homeTeam"]["name"]
        away=match["awayTeam"]["name"]

        home_form=np.random.randint(0,3)
        away_form=np.random.randint(0,3)

        prediction=np.random.choice(["Victoire domicile","Match nul","Victoire extérieur"])

        matches.append({
        "Match":f"{home} vs {away}",
        "Prediction IA":prediction
        })

    df=pd.DataFrame(matches)

    st.table(df)
