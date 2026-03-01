import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="Bakary Predictor", layout="centered")

st.title("🔥 BAKARY PREDICTOR ULTRA PRO")

# Charger les données
data = pd.read_csv("matches.csv")

teams = sorted(list(set(data["HomeTeam"])))

home_team = st.selectbox("Equipe Domicile", teams)
away_team = st.selectbox("Equipe Extérieure", teams)

if home_team != away_team:

    lambda_home = 1.5
    lambda_away = 1.2
    max_goals = 6

    prob_matrix = np.zeros((max_goals, max_goals))

    for i in range(max_goals):
        for j in range(max_goals):
            prob_matrix[i, j] = (
                poisson.pmf(i, lambda_home) *
                poisson.pmf(j, lambda_away)
            )

    home_win = np.sum(np.tril(prob_matrix, -1))
    draw = np.sum(np.diag(prob_matrix))
    away_win = np.sum(np.triu(prob_matrix, 1))

    over_25 = np.sum(prob_matrix[np.add.outer(range(max_goals), range(max_goals)) > 2])
    under_25 = 1 - over_25
    btts_yes = np.sum(prob_matrix[1:, 1:])
    btts_no = 1 - btts_yes

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

    st.subheader("📊 Probabilités")

    st.write(f"🏠 Victoire {home_team} : {round(home_win*100,2)} %")
    st.write(f"🤝 Match nul : {round(draw*100,2)} %")
    st.write(f"✈️ Victoire {away_team} : {round(away_win*100,2)} %")
# Score exact le plus probable
max_index = np.unravel_index(np.argmax(prob_matrix), prob_matrix.shape)
best_home_goals = max_index[0]
best_away_goals = max_index[1]
best_score_prob = prob_matrix[max_index]

st.subheader("🎯 Score exact le plus probable")
st.info(f"{home_team} {best_home_goals} - {best_away_goals} {away_team} ({round(best_score_prob*100,2)}%)")
    st.subheader("🔥 Meilleur choix")
    st.success(f"{best_market}")

else:
    st.warning("Choisissez deux équipes différentes")
