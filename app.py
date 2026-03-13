import streamlit as st
import numpy as np
import requests
from scipy.stats import poisson
import pandas as pd
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Bakary AI Predictor V13 ULTRA - Intelligent", layout="wide")
st.title("⚽ BAKARY AI FOOTBALL PREDICTOR V13 ULTRA - Intelligent")

# --- Configuration API ---
API_KEY = "cc99563a7dm"
headers = {"x-apisports-key": API_KEY}

# --- URLs API ---
fixtures_url = "https://v3.football.api-sports.io/fixtures"
teams_url = "https://v3.football.api-sports.io/teams/statistics"

# --- Ligues ---
ligues = {
    "Premier League": 39,
    "Ligue 1": 61,
    "Bundesliga": 78,
    "Serie A": 135,
    "LaLiga": 140
}

selected_ligue = st.selectbox("Choisir la ligue", list(ligues.keys()))
league_id = ligues[selected_ligue]

# Paramètres
last_matches = st.slider("Nombre de derniers matchs pour analyse", 3, 10, 5)
stake = st.number_input("Mise pour calcul combiné (€)", min_value=1, value=100)
recipient_email = st.text_input("Email pour recevoir le rapport PDF")
next_matches = 7  # récupérer plusieurs prochains matchs

# --- Saison intelligente ---
current_year = datetime.today().year
possible_seasons = [current_year, current_year-1, current_year-2]  # essaie 2026, 2025, 2024
matches = []

for season in possible_seasons:
    params = {"league": league_id, "season": season, "next": next_matches}
    r = requests.get(fixtures_url, headers=headers, params=params)
    data = r.json()
    if "response" in data and len(data["response"]) > 0:
        matches = data["response"]
        st.info(f"Matchs trouvés pour la saison {season}")
        break

if matches:
    table_data = []
    probs_list = []

    for m in matches:
        home_team = m["teams"]["home"]["name"]
        away_team = m["teams"]["away"]["name"]
        home_id = m["teams"]["home"]["id"]
        away_id = m["teams"]["away"]["id"]
        match_date = m["fixture"]["date"][:10]

        # Statistiques équipes
        try:
            r1 = requests.get(teams_url, headers=headers, params={"league": league_id, "team": home_id, "season": season, "last": last_matches})
            r2 = requests.get(teams_url, headers=headers, params={"league": league_id, "team": away_id, "season": season, "last": last_matches})
            data_home = r1.json()
            data_away = r2.json()
            home_goals = data_home["response"]["goals"]["for"]["average"]["home"]
            home_conceded = data_home["response"]["goals"]["against"]["average"]["home"]
            away_goals = data_away["response"]["goals"]["for"]["average"]["away"]
            away_conceded = data_away["response"]["goals"]["against"]["average"]["away"]

            home_lambda = float(home_goals) * float(away_conceded)
            away_lambda = float(away_goals) * float(home_conceded)
            max_goals = 7
            home_probs = [poisson.pmf(i, home_lambda) for i in range(max_goals)]
            away_probs = [poisson.pmf(i, away_lambda) for i in range(max_goals)]
            matrix = np.outer(home_probs, away_probs)
            home_win = np.sum(np.tril(matrix, -1))
            draw = np.sum(np.diag(matrix))
            away_win = np.sum(np.triu(matrix, 1))

            favorite = home_team if home_win > away_win else away_team
            table_data.append({
                "Match": f"{home_team} vs {away_team}",
                "Date": match_date,
                "Favori": favorite,
                "Domicile": round(home_win*100,2),
                "Nul": round(draw*100,2),
                "Extérieur": round(away_win*100,2)
            })
            probs_list.append(home_win if favorite==home_team else away_win)

        except:
            continue

    df = pd.DataFrame(table_data)
    st.dataframe(df)

    # --- Calcul combiné ---
    combined_prob = np.prod(probs_list)
    gain_estime = combined_prob * stake
    st.subheader("Pari combiné potentiel")
    st.write(f"Probabilité combiné : {round(combined_prob*100,2)}%")
    st.write(f"Gain estimé pour mise de {stake}€ : {round(gain_estime,2)}€")

    # --- Générer PDF ---
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Rapport prochains {next_matches} matchs - {selected_ligue}", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(5)
    for idx, row in df.iterrows():
        pdf.cell(0, 8, f"{row['Date']} - {row['Match']} | Favori: {row['Favori']} | Domicile {row['Domicile']}% / Nul {row['Nul']}% / Extérieur {row['Extérieur']}%", ln=True)
    pdf.ln(5)
    pdf.cell(0, 8, f"Probabilité combiné : {round(combined_prob*100,2)}%", ln=True)
    pdf.cell(0, 8, f"Gain estimé : {round(gain_estime,2)}€", ln=True)
    pdf_file = f"rapport_prochains_matchs_{selected_ligue}.pdf"
    pdf.output(pdf_file)
    st.success(f"PDF généré : {pdf_file}")

else:
    st.warning("Aucun match trouvé pour cette ligue. Essaie une autre ligue ou vérifie la saison disponible dans l’API.")
