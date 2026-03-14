import streamlit as st
import numpy as np
import requests
from scipy.stats import poisson
import pandas as pd
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Bakary AI Predictor V13 ULTRA - Intelligent", layout="wide")
st.title("⚽ BAKARY AI FOOTBALL PREDICTOR V13 ULTRA - Intelligent")

# --- Configuration API RapidAPI ---
API_KEY = "cc99563a7dmsh7b90e353380edb4p113eb4jsnf530a296e8c2"
headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
}

# --- Ligues (IDs RapidAPI) ---
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

# --- Récupérer les matchs du jour
today = datetime.today().strftime('%Y-%m-%d')
fixtures_url = "https://free-api-live-football-data.p.rapidapi.com/football-matches"

params = {
    "league_id": league_id,
    "date_from": today,
    "date_to": today
}

r = requests.get(fixtures_url, headers=headers, params=params)
data = r.json()
matches = data.get("data", [])

if matches:
    table_data = []
    probs_list = []

    for m in matches:
        home_team = m["home_team"]["name"]
        away_team = m["away_team"]["name"]
        match_date = m["match_start"][:10]

        # Poisson simplifié (API RapidAPI ne fournit pas toutes les stats)
        home_lambda = 1.5
        away_lambda = 1.2
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
    pdf.cell(0, 10, f"Rapport prochains matchs - {selected_ligue}", ln=True, align="C")
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
    st.warning("❌ Aucun match trouvé pour aujourd'hui. Essaie une autre ligue ou vérifie la date.")
