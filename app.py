import streamlit as st
import numpy as np
import requests
from scipy.stats import poisson
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Bakary AI Predictor V7", layout="centered")
st.title("⚽ BAKARY AI FOOTBALL PREDICTOR V7")
st.write("Tableau de bord interactif pro pour paris football")

API_KEY = "64907d87f835d9696c8d51b314693e51"
headers = {"x-apisports-key": API_KEY}

fixture_url = "https://v3.football.api-sports.io/fixtures"
standings_url = "https://v3.football.api-sports.io/standings"

# Ligues disponibles
ligues = {
    "Premier League (Angleterre)": 39,
    "Ligue 1 (France)": 61,
    "Bundesliga (Allemagne)": 78,
    "Serie A (Italie)": 135,
    "LaLiga (Espagne)": 140
}

selected_ligue_name = st.selectbox("Choisir la ligue", list(ligues.keys()))
selected_league_id = ligues[selected_ligue_name]

# Recherche prochains matchs
matches = []
search_days = 7
for i in range(search_days):
    date_to_check = (datetime.today() + timedelta(days=i)).strftime("%Y-%m-%d")
    params = {"date": date_to_check, "season": 2025, "league": selected_league_id}
    try:
        r = requests.get(fixture_url, headers=headers, params=params)
        data = r.json()
        if "response" in data and len(data["response"]) > 0:
            for m in data["response"]:
                home = m["teams"]["home"]["name"]
                away = m["teams"]["away"]["name"]
                matches.append({"home": home, "away": away, "date": date_to_check})
            if matches:
                break
    except:
        st.error("Erreur connexion API.")
        break

if matches:
    st.write(f"🔎 Matchs trouvés pour {selected_ligue_name} le {matches[0]['date']}")
    match_names = [f"{m['home']} vs {m['away']}" for m in matches]
    selected = st.selectbox("Choisir un match", match_names)
    index = match_names.index(selected)
    match = matches[index]

    home_team = match["home"]
    away_team = match["away"]

    st.subheader("🏟 Match sélectionné")
    st.write(home_team, "vs", away_team)

    st.subheader("⚙ Paramètres IA")
    home_attack = st.slider("Attaque domicile", 0.5, 3.0, 1.7)
    away_attack = st.slider("Attaque extérieur", 0.5, 3.0, 1.3)
    home_def = st.slider("Défense domicile", 0.5, 3.0, 1.0)
    away_def = st.slider("Défense extérieur", 0.5, 3.0, 1.2)

    if st.button("🤖 Lancer IA"):
        home_lambda = home_attack * away_def
        away_lambda = away_attack * home_def
        max_goals = 7

        # Probabilités
        home_probs = [poisson.pmf(i, home_lambda) for i in range(max_goals)]
        away_probs = [poisson.pmf(i, away_lambda) for i in range(max_goals)]
        matrix = np.outer(home_probs, away_probs)

        home_win = np.sum(np.tril(matrix, -1))
        draw = np.sum(np.diag(matrix))
        away_win = np.sum(np.triu(matrix, 1))

        st.subheader("📊 Probabilités générales")
        prob_df = {
            "Résultat": ["Victoire domicile", "Match nul", "Victoire extérieur"],
            "Probabilité (%)": [round(home_win*100,2), round(draw*100,2), round(away_win*100,2)]
        }
        fig = px.bar(prob_df, x="Résultat", y="Probabilité (%)", color="Résultat",
                     text="Probabilité (%)", color_discrete_map={
                         "Victoire domicile": "blue",
                         "Match nul": "gray",
                         "Victoire extérieur": "red"})
        st.plotly_chart(fig)

        # Top 5 scores probables
        scores = [((i,j), matrix[i,j]) for i in range(max_goals) for j in range(max_goals)]
        scores.sort(key=lambda x: x[1], reverse=True)
        st.subheader("🎯 Top 5 scores probables")
        score_labels = [f"{home_team} {s[0][0]} - {s[0][1]} {away_team}" for s in scores[:5]]
        score_values = [round(s[1]*100,2) for s in scores[:5]]
        fig_scores = px.bar(x=score_labels, y=score_values, text=score_values, labels={"x":"Score","y":"Probabilité (%)"},
                            color=score_values, color_continuous_scale="Reds")
        st.plotly_chart(fig_scores)

        # Over / Under 2.5
        over = sum(matrix[i][j] for i in range(max_goals) for j in range(max_goals) if i+j > 2)
        under = sum(matrix[i][j] for i in range(max_goals) for j in range(max_goals) if i+j <= 2)
        st.subheader("📈 Over / Under 2.5")
        over_under_df = {
            "Type": ["Over 2.5", "Under 2.5"],
            "Probabilité (%)": [round(over*100,2), round(under*100,2)]
        }
        fig_ou = px.pie(over_under_df, names="Type", values="Probabilité (%)", color="Type",
                        color_discrete_map={"Over 2.5":"red", "Under 2.5":"blue"})
        st.plotly_chart(fig_ou)

        # Conseil pari + gains simulés
        st.subheader("💡 Conseil pari avec gains estimés")
        mise = 100  # Exemple mise virtuelle
        if home_win > away_win:
            st.success(f"Victoire domicile recommandée ({home_team})")
            st.write(f"Gain estimé : {round(home_win*mise,2)} €")
        elif away_win > home_win:
            st.success(f"Victoire extérieur recommandée ({away_team})")
            st.write(f"Gain estimé : {round(away_win*mise,2)} €")
        else:
            st.info("Match nul probable")
            st.write(f"Gain estimé : {round(draw*mise,2)} €")

else:
    st.warning(f"Aucun match trouvé dans les {search_days} prochains jours pour {selected_ligue_name}")
