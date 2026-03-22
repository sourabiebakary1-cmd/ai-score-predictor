import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from xgboost import XGBClassifier
from scipy.stats import poisson

st.set_page_config(page_title="BAKARY AI AUTO PRO", layout="wide")

st.title("⚽ BAKARY AI AUTO PRO 🔥🧠")

# ================= CONFIG =================
bankroll = st.sidebar.number_input("💰 Bankroll", value=10000)
date = st.sidebar.date_input("📅 Date", datetime.today())

API_KEY = "289e8418878e48c598507cf2b72338f5"

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

# ================= AUTO DATASET =================
@st.cache_data
def create_dataset():
    all_data = []

    leagues = [39, 140]
    season = 2023

    for league in leagues:
        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
        params = {"league": league, "season": season}

        try:
            res = requests.get(url, headers=HEADERS, params=params)

            if res.status_code != 200:
                continue

            data = res.json().get("response", [])

            for match in data:
                try:
                    if match["fixture"]["status"]["short"] != "FT":
                        continue

                    home_goals = match["goals"]["home"]
                    away_goals = match["goals"]["away"]

                    total = home_goals + away_goals

                    over25 = 1 if total > 2 else 0

                    all_data.append([
                        home_goals,
                        away_goals,
                        total,
                        over25
                    ])
                except:
                    continue
        except:
            continue

    df = pd.DataFrame(all_data, columns=[
        "home_goals","away_goals","total","over25"
    ])

    return df

df = create_dataset()

# ================= MODEL =================
@st.cache_resource
def train_model(df):
    X = df[["home_goals","away_goals","total"]]
    y = df["over25"]

    model = XGBClassifier(n_estimators=120)
    model.fit(X, y)

    return model

model = train_model(df)

# ================= API MATCH =================
def get_matches():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    params = {"date": date.strftime('%Y-%m-%d')}

    try:
        res = requests.get(url, headers=HEADERS, params=params)

        if res.status_code != 200:
            return []

        return res.json().get("response", [])
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

# ================= FEATURES =================
def compute_features(stats_home, stats_away):
    try:
        h_for = float(stats_home["goals"]["for"]["average"]["total"])
        a_for = float(stats_away["goals"]["for"]["average"]["total"])

        total = h_for + a_for

        return h_for, a_for, total
    except:
        return 1.2, 1.2, 2.4

# ================= SCORE =================
def predict_score(home_xg, away_xg):
    best = (0, 0)
    max_prob = 0

    for i in range(5):
        for j in range(5):
            prob = poisson.pmf(i, home_xg) * poisson.pmf(j, away_xg)
            if prob > max_prob:
                max_prob = prob
                best = (i, j)

    return best

# ================= ANALYSE =================
matches = get_matches()
results = []

if not matches:
    st.warning("🚫 Aucun match aujourd’hui")
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

            h_for, a_for, total = compute_features(stats_home, stats_away)

            prob = model.predict_proba([[h_for, a_for, total]])[0][1]

            score = predict_score(h_for, a_for)

            if prob > 0.70 and total > 2.4:
                results.append({
                    "match": f"{home} vs {away}",
                    "score": f"{score[0]}-{score[1]}",
                    "prob": round(prob*100,2)
                })

        except:
            continue

# ================= AFFICHAGE =================
if not results:
    st.error("❌ Aucun match fiable")
else:
    st.success(f"🔥 {len(results)} MATCHS AUTO")

    for r in results:
        st.markdown(f"""
### ⚽ {r['match']}
- 🎯 Score : **{r['score']}**
- 📊 Probabilité : **{r['prob']}%**
""")

# ================= BANKROLL =================
if results:
    stake = bankroll * 0.02
    st.sidebar.write(f"💡 Mise : {int(stake)} FCFA")
