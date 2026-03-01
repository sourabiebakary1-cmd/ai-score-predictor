import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
st.markdown("""
    <style>
    body {
        background-color: #0e0e0e;
        color: white;
    }
    .stApp {
        background-color: #0e0e0e;
    }
    h1, h2, h3 {
        color: #ff2b2b;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)
st.title("🔥 BAKARY PREDICTOR ULTRA PRO 🔥")

# Charger les données
data = pd.read_csv("matches.csv")

teams = sorted(list(set(data["HomeTeam"])))

home_team = st.selectbox("Equipe Domicile", teams)
away_team = st.selectbox("Equipe Extérieur", teams)

if home_team != away_team:

    st.subheader("📊 Probabilités du match")

    max_goals = 6
    prob_matrix = np.zeros((max_goals, max_goals))
lambda_home = 1.5
lambda_away = 1.2
    for i in range(max_goals):
        for j in range(max_goals):
            prob_matrix[i, j] = poisson.pmf(i, lambda_home) * poisson.pmf(j, lambda_away)

    home_win = np.sum(np.tril(prob_matrix, -1))
    draw = np.sum(np.diag(prob_matrix))
    away_win = np.sum(np.triu(prob_matrix, 1))

    st.write(f"🏠 Victoire {home_team} : {round(home_win*100,2)} %")
    st.write(f"🤝 Match nul : {round(draw*100,2)} %")
    st.write(f"✈️ Victoire {away_team} : {round(away_win*100,2)} %")

    # Top 3 scores
    scores = []
    for i in range(max_goals):
        for j in range(max_goals):
            scores.append((i, j, prob_matrix[i,j]))

    top_scores = sorted(scores, key=lambda x: x[2], reverse=True)[:3]

    st.subheader("🎯 Top 3 Scores Probables")

    for score in top_scores:
        st.write(f"{score[0]} - {score[1]}  ({round(score[2]*100,2)} %)")
    st.write(f"🔥 BTTS Oui : {round(btts_yes*100,2)}%")
    st.write(f"❌ BTTS Non : {round(btts_no*100,2)}%")

    # ===== PARI RECOMMANDÉ =====

    st.subheader("💎 PARI RECOMMANDÉ")

    markets = {
        "Victoire Domicile": home_win,
        "Match Nul": draw,
        "Victoire Extérieur": away_win,
        "Over 2.5": over_25,
        "Under 2.5": under_25,
        "BTTS Oui": btts_yes,
        "BTTS Non": btts_no
    }

    best_market = max(markets, key=markets.get)

    st.success(f"🔥 Meilleur choix : {best_market}")
else:
    st.warning("Choisissez deux équipes différentes")
