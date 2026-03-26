import streamlit as st
import pandas as pd
import math
import os
from sklearn.linear_model import LogisticRegression

FILE = "data.csv"

st.set_page_config(page_title="BAKARY AI - IA RÉELLE", layout="wide")

st.title("🤖 BAKARY AI - IA RÉELLE")
st.write("Machine Learning + Poisson FIFA FC 25 (3x3)")

# Charger données
if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=["teamA","teamB","scoreA","scoreB"])

teamA = st.text_input("Equipe A")
teamB = st.text_input("Equipe B")

oddA = st.number_input("Cote A", min_value=1.01, value=2.0)
oddD = st.number_input("Cote Nul", min_value=1.01, value=3.0)
oddB = st.number_input("Cote B", min_value=1.01, value=2.5)

# -------------------------
# FONCTIONS
# -------------------------

def poisson(k, lam):
    return (lam**k * math.exp(-lam)) / math.factorial(k)

def get_stats(team):
    games = df[(df["teamA"] == team) | (df["teamB"] == team)]

    if len(games) < 3:
        return 1.5, 1.5

    goals_for = []
    goals_against = []

    for _, row in games.iterrows():
        if row["teamA"] == team:
            goals_for.append(row["scoreA"])
            goals_against.append(row["scoreB"])
        else:
            goals_for.append(row["scoreB"])
            goals_against.append(row["scoreA"])

    return sum(goals_for)/len(goals_for), sum(goals_against)/len(goals_against)

# -------------------------
# MACHINE LEARNING
# -------------------------

def train_model():
    if len(df) < 20:
        return None

    X = []
    y = []

    for _, row in df.iterrows():

        a_attack, a_def = get_stats(row["teamA"])
        b_attack, b_def = get_stats(row["teamB"])

        X.append([a_attack, a_def, b_attack, b_def])

        if row["scoreA"] > row["scoreB"]:
            y.append(0)  # A
        elif row["scoreA"] == row["scoreB"]:
            y.append(1)  # Draw
        else:
            y.append(2)  # B

    model = LogisticRegression(max_iter=200)
    model.fit(X, y)

    return model

model = train_model()

# -------------------------
# PRÉDICTION
# -------------------------

if st.button("PRÉDIRE"):

    if teamA == "" or teamB == "":
        st.error("⚠️ Remplis les équipes")
    else:

        a_attack, a_def = get_stats(teamA)
        b_attack, b_def = get_stats(teamB)

        # IA prediction
        if model:
            probs = model.predict_proba([[a_attack, a_def, b_attack, b_def]])[0]
            probA_ml, probD_ml, probB_ml = probs
        else:
            probA_ml, probD_ml, probB_ml = 0.33, 0.33, 0.33

        # Poisson
        lambdaA = a_attack
        lambdaB = b_attack

        probA_p = probD_p = probB_p = 0

        for i in range(5):
            for j in range(5):
                p = poisson(i, lambdaA) * poisson(j, lambdaB)
                if i > j:
                    probA_p += p
                elif i == j:
                    probD_p += p
                else:
                    probB_p += p

        # 🔥 Fusion IA + Poisson
        probA = (probA_ml * 0.6 + probA_p * 0.4)
        probD = (probD_ml * 0.6 + probD_p * 0.4)
        probB = (probB_ml * 0.6 + probB_p * 0.4)

        st.subheader("📊 Probabilités IA")
        st.write(f"{teamA} : {probA*100:.2f}%")
        st.write(f"Nul : {probD*100:.2f}%")
        st.write(f"{teamB} : {probB*100:.2f}%")

        # Value bet
        valueA = probA * oddA
        valueD = probD * oddD
        valueB = probB * oddB

        st.subheader("💰 Value Bet")
        st.write(f"{teamA} : {valueA:.2f}")
        st.write(f"Nul : {valueD:.2f}")
        st.write(f"{teamB} : {valueB:.2f}")

        # Décision
        best = max({"A":valueA,"D":valueD,"B":valueB}, key=lambda x: {"A":valueA,"D":valueD,"B":valueB}[x])
        confidence = max(probA, probD, probB)

        st.subheader("🎯 Décision")

        if confidence < 0.55 or max(valueA,valueD,valueB) < 1:
            st.error("🚫 NE PAS PARIER")
        else:
            if best == "A":
                st.success(f"Parier sur {teamA}")
            elif best == "D":
                st.warning("Parier sur Nul")
            else:
                st.success(f"Parier sur {teamB}")

            st.progress(int(confidence*100))
            st.write(f"🔥 Confiance : {confidence*100:.2f}%")

# -------------------------
# ENREGISTRER
# -------------------------

st.subheader("📥 Ajouter résultat réel")

scoreA = st.number_input("Score A", min_value=0)
scoreB = st.number_input("Score B", min_value=0)

if st.button("ENREGISTRER"):
    if teamA == "" or teamB == "":
        st.error("⚠️ Remplis les équipes")
    else:
        new_data = pd.DataFrame([[teamA, teamB, scoreA, scoreB]],
                                columns=["teamA","teamB","scoreA","scoreB"])
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(FILE, index=False)
        st.success("✅ Match enregistré !")
