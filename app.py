import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from xgboost import XGBClassifier

st.set_page_config(page_title="BAKARY AI SUPER 90%", layout="wide")

st.title("⚽ BAKARY AI SUPER IA 90% 🔥🧠")

# ================= CONFIG =================
bankroll = st.sidebar.number_input("💰 Bankroll", value=10000)
date = st.sidebar.date_input("📅 Date", datetime.today())

# ================= API =================
API_KEY = "289e8418878e48c598507cf2b72338f5"

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

# ================= LOAD DATA =================
@st.cache_data
def load_data():
    return pd.read_csv("dataset_pro.csv")

df = load_data()

# ================= FEATURE ENGINEERING =================
def create_features(df):
    df["attack_diff"] = df["home_goals"] - df["away_goals"]
    df["defense_diff"] = df["away_goals"] - df["home_goals"]
    df["total"] = df["home_goals"] + df["away_goals"]
    return df

df = create_features(df)

# ================= TRAIN MODEL =================
@st.cache_resource
def train_model():
    X = df[["attack_diff", "defense_diff", "total"]]
    y = df["over25"]

    model = XGBClassifier(n_estimators=150, max_depth=5)
    model.fit(X, y)

    return model

model = train_model()

# ================= API FUNCTIONS =================
def get_matches():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    params = {"date": date.strftime('%Y-%m-%d')}
    res = requests.get(url, headers=HEADERS, params=params)

    if res.status_code != 200:
        return []
    return res.json().get("response", [])

def get_stats(team_id, league):
    url = "https://api-football-v1.p.rapidapi.com/v3/teams/statistics"
    params = {"team": team_id, "league": league, "season": 2023}
    res = requests.get(url, headers=HEADERS, params=params)

    if res.status_code != 200:
        return None
    return res.json().get("response", {})

# ================= FEATURES MATCH =================
def compute_features(stats_home, stats_away):
    try:
        h_for = float(stats_home["goals"]["for"]["average"]["total"])
        h_against = float(stats_home["goals"]["against"]["average"]["total"])

        a_for = float(stats_away["goals"]["for"]["average"]["total"])
        a_against = float(stats_away["goals"]["against"]["average"]["total"])

        attack_diff = h_for - a_against
        defense_diff = a_for - h_against
        total = h_for + a_for

        return [attack_diff, defense_diff, total]
    except:
        return [0, 0, 2.2]

# ================= ANALYSE =================
matches = get_matches()
results = []

if not matches:
    st.warning("🚫 JOUR DANGEREUX")
else:
    for m in matches:
        try:
            home = m["teams"]["home"]["name"]
            away = m["teams"]["away"]["name"]

            home_id = m["teams"]["home"]["id"]
            away_id = m["teams"]["away"]["id"]
            league = m["league"]["id"]

            stats_home = get_stats(home_id, league)
            stats_away = get_stats(away_id, league)

            features = compute_features(stats_home, stats_away)

            prob = model.predict_proba([features])[0][1]

            # VALUE BET (très important)
            if prob > 0.65:
                results.append({
                    "match": f"{home} vs {away}",
                    "prob": round(prob * 100, 2),
                    "prediction": "OVER 2.5"
                })

        except:
            continue

# ================= AFFICHAGE =================
if not results:
    st.error("❌ Aucun match VALUE aujourd’hui")
else:
    st.success(f"🔥 {len(results)} VALUE BETS")

    for r in results:
        st.markdown(f"""
        ### ⚽ {r['match']}
        - 💎 Prédiction : **{r['prediction']}**
        - 📊 Probabilité : **{r['prob']}%**
        """)

# ================= BANKROLL =================
if results:
    stake = bankroll * 0.03
    st.sidebar.write(f"💡 Mise VALUE : {int(stake)} FCFA")
