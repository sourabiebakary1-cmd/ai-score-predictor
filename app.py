import streamlit as st
import pandas as pd
import math
import os

FILE = "data.csv"

st.set_page_config(page_title="BAKARY AI PRO MAX")

st.title("🤖 BAKARY AI PRO MAX")
st.write("Prédiction FIFA FC 25 (3x3)")

# Charger données
if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=["teamA","teamB","scoreA","scoreB"])

teamA = st.text_input("Equipe A")
teamB = st.text_input("Equipe B")

oddA = st.number_input("Cote A", min_value=1.01)
oddD = st.number_input("Cote Nul", min_value=1.01)
oddB = st.number_input("Cote B", min_value=1.01)

def poisson(k, lam):
    return (lam**k * math.exp(-lam)) / math.factorial(k)

def get_avg_goals(team):
    games = df[(df["teamA"] == team) | (df["teamB"] == team)]
    if len(games) == 0:
        return 1.5
    goals = []
    for _, row in games.iterrows():
        if row["teamA"] == team:
            goals.append(row["scoreA"])
        else:
            goals.append(row["scoreB"])
    return sum(goals) / len(goals)

if st.button("PRÉDIRE"):

    avgA = get_avg_goals(teamA)
    avgB = get_avg_goals(teamB)

    lambdaA = avgA
    lambdaB = avgB

    scores = []

    for i in range(7):
        for j in range(7):
            prob = poisson(i, lambdaA) * poisson(j, lambdaB)
            scores.append((f"{i}-{j}", prob))

    scores.sort(key=lambda x: x[1], reverse=True)

    st.subheader("TOP 5 SCORES")

    for i in range(5):
        st.write(f"{teamA} {scores[i][0]} {teamB} → {scores[i][1]*100:.2f}%")

# Ajouter résultat réel
st.subheader("Ajouter résultat réel")

scoreA = st.number_input("Score A", min_value=0)
scoreB = st.number_input("Score B", min_value=0)

if st.button("ENREGISTRER"):

    new_data = pd.DataFrame([[teamA, teamB, scoreA, scoreB]],
                            columns=["teamA","teamB","scoreA","scoreB"])

    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(FILE, index=False)

    st.success("Match enregistré !")
