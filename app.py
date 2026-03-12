import streamlit as st
import numpy as np
import requests
from scipy.stats import poisson
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

st.set_page_config(page_title="Bakary AI Predictor V6", layout="centered")
st.title("⚽ BAKARY AI FOOTBALL PREDICTOR V6")
st.write("Tableau de bord interactif avec probabilités et top paris")

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

    # Classement ligue
    st.subheader("📊 Classement ligue")
    try:
        stand_r = requests.get(standings_url, headers=headers, params={"league": selected_league_id, "season": 2025})
        standings = stand_r.json()
        if "response" in standings:
            table = standings["response"][0]["league"]["standings"][0]
            for t in table:
                if t["team"]["name"] == home_team:
                    st.write(f"🏠 {home_team} : {t['rank']}ème place, Points: {t['points']}")
                if t["team"]["name"] == away_team:
                    st.write(f"✈ {away_team} : {t['rank']}ème place, Points: {t['points']}")
    except:
        st.warning("Impossible de récupérer le classement")

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

        st.subheader("📊 Probabilités")
        st.write("🏠 Victoire domicile :", round(home_win*100,2), "%")
        st.write("🤝 Match nul :", round(draw*100,2), "%")
        st.write("✈ Victoire extérieur :", round(away_win*100,2), "%")

        # Heatmap des scores probables
        st.subheader("🔥 Heatmap des scores probables")
        fig, ax = plt.subplots()
        im = ax.imshow(matrix, cmap='Reds')

        ax.set_xticks(range(max_goals))
        ax.set_yticks(range(max_goals))
        ax.set_xlabel(f"💨 {away_team} Goals")
        ax.set_ylabel(f"🏠 {home_team} Goals")
        ax.set_title("Probabilité de chaque score")

        # Annoter les probabilités
        for i in range(max_goals):
            for j in range(max_goals):
                text = f"{matrix[i,j]*100:.1f}%"
                ax.text(j, i, text, ha="center", va="center", color="black", fontsize=8)

        st.pyplot(fig)

        # Top 3 scores
        scores = [((i,j), matrix[i,j]) for i in range(max_goals) for j in range(max_goals)]
        scores.sort(key=lambda x: x[1], reverse=True)
        st.subheader("🎯 Top scores probables")
        for s in scores[:3]:
            st.write(f"{home_team} {s[0][0]} - {s[0][1]} {away_team} ({round(s[1]*100,2)}%)")

        # Over / Under 2.5
        over = sum(matrix[i][j] for i in range(max_goals) for j in range(max_goals) if i+j > 2)
        under = sum(matrix[i][j] for i in range(max_goals) for j in range(max_goals) if i+j <= 2)
        st.subheader("📈 Over / Under 2.5")
        st.write(f"Over 2.5 : {round(over*100,2)}%")
        st.write(f"Under 2.5 : {round(under*100,2)}%")

        # Conseil pari
        st.subheader("💡 Conseil pari")
        if home_win > away_win:
            st.success(f"Victoire domicile recommandée ({home_team})")
        elif away_win > home_win:
            st.success(f"Victoire extérieur recommandée ({away_team})")
        else:
            st.info("Match nul probable")

else:
    st.warning(f"Aucun match trouvé dans les {search_days} prochains jours pour {selected_ligue_name}")
