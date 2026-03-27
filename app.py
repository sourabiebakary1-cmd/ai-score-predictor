import streamlit as st
import pandas as pd
import math
import os

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

    if len(games) < 3:
        return 2.2, 2.2

    games = games.tail(5)

    gf, ga = [], []

    for _, row in games.iterrows():
        if row["teamA"] == team:
            gf.append(row["scoreA"])
            ga.append(row["scoreB"])
        else:
            gf.append(row["scoreB"])
            ga.append(row["scoreA"])

    return sum(gf)/len(gf), sum(ga)/len(ga)

# -------------------------
# PREDICTION
# -------------------------

if st.button("PRÉDIRE"):

    if teamA == "" or teamB == "":
        st.error("⚠️ Remplis les équipes")
    else:

        a_atk, a_def = get_stats(teamA)
        b_atk, b_def = get_stats(teamB)

        # PROBA COTES
        invA = 1 / oddA
        invD = 1 / oddD
        invB = 1 / oddB

        total = invA + invD + invB

        probA_odds = invA / total
        probD_odds = invD / total
        probB_odds = invB / total

        # POISSON
        lambdaA = (a_atk + b_def) / 2
        lambdaB = (b_atk + a_def) / 2

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

        # FUSION
        probA = (probA_odds * 0.6) + (probA_p * 0.4)
        probD = (probD_odds * 0.6) + (probD_p * 0.4)
        probB = (probB_odds * 0.6) + (probB_p * 0.4)

        st.subheader("📊 Probabilités")
        st.write(f"{teamA}: {probA*100:.2f}%")
        st.write(f"Nul: {probD*100:.2f}%")
        st.write(f"{teamB}: {probB*100:.2f}%")

        # SCORE
        best_score = max(score_matrix, key=score_matrix.get)
        st.subheader("🎯 Score probable")
        st.success(f"{teamA} {best_score[0]} - {best_score[1]} {teamB}")

        # GOALS
        avg_goals = lambdaA + lambdaB

        st.subheader("⚽ Analyse Buts")

        if avg_goals > 3.5:
            st.success("🔥 OVER 2.5 buts")
        elif avg_goals > 2.5:
            st.warning("⚖️ OVER 2.5 (risqué)")
        else:
            st.error("❄️ UNDER 2.5")

        # BTTS
        btts_prob = 1 - (poisson(0, lambdaA) + poisson(0, lambdaB) - (poisson(0, lambdaA)*poisson(0, lambdaB)))

        st.subheader("🤝 BTTS (les 2 marquent)")
        if btts_prob > 0.6:
            st.success("✅ OUI")
        else:
            st.error("❌ NON")

        # VALUE
        valueA = probA * oddA
        valueD = probD * oddD
        valueB = probB * oddB

        st.subheader("💰 Value Bet")
        st.write(f"{teamA}: {valueA:.2f}")
        st.write(f"Nul: {valueD:.2f}")
        st.write(f"{teamB}: {valueB:.2f}")

        # DECISION PRO MAX 🔥
        best = max({"A":valueA,"D":valueD,"B":valueB}, key=lambda x: {"A":valueA,"D":valueD,"B":valueB}[x])
        confidence = max(probA, probD, probB)

        st.subheader("🎯 Décision Finale")

        if confidence < 0.50:
            st.error("🚫 NE PAS PARIER (match équilibré)")

        elif max(valueA, valueD, valueB) < 1.20:
            st.error("🚫 NE PAS PARIER (pas de value)")

        elif best == "B" and probB < 0.25:
            st.error(f"🚫 PARI PIÈGE sur {teamB}")

        elif best == "A" and probA < 0.25:
            st.error(f"🚫 PARI PIÈGE sur {teamA}")

        else:
            if best == "A":
                st.success(f"🔥 PARIER: {teamA}")
            elif best == "D":
                st.warning("⚖️ PARIER: NUL")
            else:
                st.success(f"🔥 PARIER: {teamB}")

            st.progress(int(confidence * 100))
            st.write(f"🔥 Confiance: {confidence*100:.2f}%")

# SAVE
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
