import streamlit as st
import pandas as pd
import math
import os
from sklearn.linear_model import LogisticRegression

FILE = "data.csv"

st.set_page_config(page_title="BAKARY AI PRO MAX ULTIMATE", layout="wide")

st.title("🤖 BAKARY AI PRO MAX ULTIMATE")
st.write("🔥 IA + Score Exact + Over/Under + BTTS + FIFA FC 25")

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

    # ✅ sécurité si aucune donnée
    if len(games) == 0:
        return 2.5, 2.5

    games = games.tail(5)

    gf, ga = [], []

    for _, row in games.iterrows():
        if row["teamA"] == team:
            gf.append(row["scoreA"])
            ga.append(row["scoreB"])
        else:
            gf.append(row["scoreB"])
            ga.append(row["scoreA"])

    # ✅ sécurité anti bug
    if len(gf) == 0 or len(ga) == 0:
        return 2.5, 2.5

    return sum(gf)/len(gf), sum(ga)/len(ga)

# -------------------------
# ML
# -------------------------

def train_model():
    if len(df) < 15:
        return None

    X, y = [], []

    for _, row in df.iterrows():
        a_atk, a_def = get_stats(row["teamA"])
        b_atk, b_def = get_stats(row["teamB"])

        X.append([a_atk, a_def, b_atk, b_def])

        if row["scoreA"] > row["scoreB"]:
            y.append(0)
        elif row["scoreA"] == row["scoreB"]:
            y.append(1)
        else:
            y.append(2)

    model = LogisticRegression(max_iter=500)
    model.fit(X, y)
    return model

model = train_model()

# -------------------------
# PREDICTION
# -------------------------

if st.button("PRÉDIRE"):

    if teamA == "" or teamB == "":
        st.error("⚠️ Remplis les équipes")
    else:

        a_atk, a_def = get_stats(teamA)
        b_atk, b_def = get_stats(teamB)

        # ML
        if model:
            probA_ml, probD_ml, probB_ml = model.predict_proba([[a_atk, a_def, b_atk, b_def]])[0]
        else:
            probA_ml, probD_ml, probB_ml = 0.4, 0.2, 0.4

        # -------------------------
        # POISSON AMÉLIORÉ
        # -------------------------

        lambdaA = (a_atk + b_def) / 2 * 1.4
        lambdaB = (b_atk + a_def) / 2 * 1.4

        probA_p = probD_p = probB_p = 0
        score_matrix = {}

        for i in range(0, 6):
            for j in range(0, 6):
                p = poisson(i, lambdaA) * poisson(j, lambdaB)
                score_matrix[(i, j)] = p

                if i > j:
                    probA_p += p
                elif i == j:
                    probD_p += p
                else:
                    probB_p += p

        # Fusion
        probA = probA_ml * 0.6 + probA_p * 0.4
        probD = probD_ml * 0.6 + probD_p * 0.4
        probB = probB_ml * 0.6 + probB_p * 0.4

        st.subheader("📊 Probabilités")
        st.write(f"{teamA}: {probA*100:.2f}%")
        st.write(f"Nul: {probD*100:.2f}%")
        st.write(f"{teamB}: {probB*100:.2f}%")

        # SCORE EXACT
        best_score = max(score_matrix, key=score_matrix.get)
        st.subheader("🎯 Score probable")
        st.success(f"{teamA} {best_score[0]} - {best_score[1]} {teamB}")

        # -------------------------
        # ANALYSE BUTS
        # -------------------------

        avg_goals = lambdaA + lambdaB

        st.subheader("⚽ Analyse Buts")

        if avg_goals > 3:
            st.success("🔥 OVER 2.5 buts")
        else:
            st.warning("⚖️ UNDER 2.5 buts")

        # BTTS corrigé
        btts_prob = 1 - (poisson(0, lambdaA) * poisson(0, lambdaB))

        st.subheader("🤝 BTTS (les 2 marquent)")
        if btts_prob > 0.55:
            st.success("✅ OUI")
        else:
            st.warning("❌ NON")

        # -------------------------
        # VALUE BET
        # -------------------------

        valueA = probA * oddA
        valueD = probD * oddD
        valueB = probB * oddB

        st.subheader("💰 Value Bet")
        st.write(f"{teamA}: {valueA:.2f}")
        st.write(f"Nul: {valueD:.2f}")
        st.write(f"{teamB}: {valueB:.2f}")

        # -------------------------
        # DÉCISION AMÉLIORÉE
        # -------------------------

        st.subheader("🎯 Décision Finale")

        best_value = max(valueA, valueD, valueB)
        best_prob = max(probA, probD, probB)

        if best_value < 1.15:
            st.error("🚫 NE PAS PARIER (pas de value)")
        else:
            if best_value == valueA:
                st.success(f"🔥 PARIER sur {teamA}")
            elif best_value == valueD:
                st.warning("⚖️ PARIER NUL")
            else:
                st.success(f"🔥 PARIER sur {teamB}")

            st.progress(int(best_prob * 100))
            st.write(f"🔥 Confiance: {best_prob*100:.2f}%")

# -------------------------
# SAVE
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
