import streamlit as st
import math

st.set_page_config(page_title="BAKARY AI PRO MAX")

st.title("🤖 BAKARY AI PRO MAX")
st.write("Prédiction FIFA FC 25 (3x3)")

teamA = st.text_input("Equipe A")
teamB = st.text_input("Equipe B")

oddA = st.number_input("Cote A", min_value=1.01)
oddD = st.number_input("Cote Nul", min_value=1.01)
oddB = st.number_input("Cote B", min_value=1.01)

def poisson(k, lam):
    return (lam**k * math.exp(-lam)) / math.factorial(k)

if st.button("PRÉDIRE"):

    pA = 1 / oddA
    pD = 1 / oddD
    pB = 1 / oddB

    total = pA + pD + pB

    pA /= total
    pD /= total
    pB /= total

    avgGoals = 3.5

    lambdaA = avgGoals * pA * 1.2
    lambdaB = avgGoals * pB * 1.2

    scores = []

    for i in range(7):
        for j in range(7):
            prob = poisson(i, lambdaA) * poisson(j, lambdaB)
            scores.append((f"{i}-{j}", prob))

    scores.sort(key=lambda x: x[1], reverse=True)

    st.subheader("TOP 5 SCORES")

    for i in range(5):
        st.write(f"{teamA} {scores[i][0]} {teamB} → {scores[i][1]*100:.2f}%")
