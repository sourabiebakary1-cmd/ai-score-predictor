import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Charger les données
try:
    data = pd.read_csv("matches.csv")
except:
    data = None

st.title("🤖 AI Score Predictor")

team1 = st.text_input("Equipe 1")
team2 = st.text_input("Equipe 2")

if data is not None:

    le = LabelEncoder()

    data["home_team"] = le.fit_transform(data["home_team"])
    data["away_team"] = le.fit_transform(data["away_team"])

    data["result"] = data.apply(
        lambda row: 1 if row["home_goals"] > row["away_goals"]
        else 0 if row["home_goals"] == row["away_goals"]
        else -1,
        axis=1
    )

    X = data[["home_team", "away_team"]]
    y = data["result"]

    model = RandomForestClassifier()
    model.fit(X, y)

if st.button("🚀 Analyser le match"):

    if data is not None and team1 != "" and team2 != "":

        try:
            home_encoded = le.transform([team1])[0]
            away_encoded = le.transform([team2])[0]

            prediction = model.predict([[home_encoded, away_encoded]])[0]

            if prediction == 1:
                st.success(f"Victoire probable : {team1}")
            elif prediction == 0:
                st.info("Match nul probable")
            else:
                st.success(f"Victoire probable : {team2}")

        except:
            st.error("Equipe non trouvée dans la base de données")

    else:
        st.error("Fichier matches.csv manquant ou équipes vides")
