import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from xgboost import XGBClassifier
from scipy.stats import poisson

st.set_page_config(page_title="BAKARY AI PRO MAX FINAL", layout="wide")

st.title("⚽ BAKARY AI PRO MAX FINAL 🔥🧠")

# ================= CONFIG =================
bankroll = st.sidebar.number_input("💰 Bankroll", value=10000)
date = st.sidebar.date_input("📅 Date", datetime.today())

# ================= API =================
API_KEY = "289e8418878e48c598507cf2b72338f5"

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

# ================= TELEGRAM =================
def send_telegram(msg):
    try:
        TOKEN = "TON_TOKEN"
        CHAT_ID = "TON_CHAT_ID"
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

# ================= LOAD DATA =================
@st.cache_data
def load_data():
    try:
        return pd.read_csv("dataset_pro.csv")
    except:
        st.error("❌ dataset_pro.csv manquant")
        st.stop()

df = load_data()

# ================= FEATURES DATASET =================
def create_features(df):
    df["attack_diff"] = df["home_goals"] - df["away_goals"]
    df["defense_diff"] = df["away_goals"] - df["home_goals"]
    df["total"] = df["home_goals"] + df["away_goals"]
    return df

df = create_features(df)

# ================= MODEL =================
@st.cache_resource
def train_model():
    try:
        X = df[["attack_diff", "defense_diff", "total"]]
        y = df["over25"]

        model = XGBClassifier(n_estimators=150, max_depth=5)
        model.fit(X, y)
        return model
    except:
        st.error("❌ Erreur modèle IA")
        st.stop()

model = train_model()

# ================= API =================
def get_matches():
    try:
        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
        params = {"date": date.strftime('%Y-%m-%d')}
        res = requests.get(url, headers=HEADERS, params=params)

        if res.status_code != 200:
            st.error(f"❌ Erreur API: {res.status_code}")
            return []

        data = res.json()
        return data.get("response", [])
    except:
        return []

def get_stats(team_id, league):
    try:
        url = "https://api-football-v1.p.rapidapi.com/v3/teams/statistics"
        params = {"team": team_id, "league": league, "season": 2023}
        res = requests.get(url, headers=HEADERS, params=params)

        if res.status_code != 200:
            return None

        return res.json().get("response", {})
    except:
        return None

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

        return attack_diff, defense_diff, total
    except:
        return 0, 0, 2.2

# ================= SCORE EXACT =================
def predict_score(home_xg, away_xg):
    best = (0, 0)
    max_prob = 0

    for i in range(6):
        for j in range(6):
            prob = poisson.pmf(i, home_xg) * poisson.pmf(j, away_xg)
            if prob > max_prob:
                max_prob = prob
                best = (i, j)

    return best

# ================= VALUE BET =================
def is_value(prob, odd):
    try:
        return prob > (1 / odd)
    except:
        return False

# ================= ANALYSE =================
matches = get_matches()
results = []

if not matches:
    st.warning("🚫 JOUR DANGEREUX - Aucun match")
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

            attack_diff, defense_diff, total = compute_features(stats_home, stats_away)

            prob = model.predict_proba([[attack_diff, defense_diff, total]])[0][1]

            home_xg = max(0.5, total / 2)
            away_xg = max(0.5, total / 2)

            score = predict_score(home_xg, away_xg)

            odd = 1.80  # tu peux changer ou connecter API cotes

            # FILTRE ULTRA PRO
            if prob > 0.72 and total > 2.5 and is_value(prob, odd):

                msg = f"""
💎 VIP ELITE 💎
⚽ {home} vs {away}
🎯 Score: {score[0]} - {score[1]}
📊 Probabilité: {round(prob*100,2)}%
🔥 VALUE BET
"""
                send_telegram(msg)

                results.append({
                    "match": f"{home} vs {away}",
                    "score": f"{score[0]}-{score[1]}",
                    "prob": round(prob*100,2)
                })

        except:
            continue

# ================= AFFICHAGE =================
if not results:
    st.error("❌ Aucun match VIP aujourd’hui")
else:
    st.success(f"🔥 {len(results)} MATCHS ELITE")

    for r in results:
        st.markdown(f"""
### ⚽ {r['match']}
- 🎯 Score : **{r['score']}**
- 📊 Probabilité : **{r['prob']}%**
""")

# ================= BANKROLL =================
if results:
    stake = bankroll * 0.02
    st.sidebar.write(f"💡 Mise PRO : {int(stake)} FCFA")
