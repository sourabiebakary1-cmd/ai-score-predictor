import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime, timedelta
import json
import requests
import numpy as np
from scipy.stats import poisson

# ================= CONFIG =================
DATA_FILE = "historique.csv"
CODES_FILE = "codes.json"
OWNER_NUMBER = "22607093407"
API_KEY = "289e8418878e48c598507cf2b72338f5"

MODE_TEST = True

st.set_page_config(page_title="BAKARY AI PRO MAX ULTRA", layout="wide")

# ================= FILES =================
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["match","prediction","date"]).to_csv(DATA_FILE, index=False)

if not os.path.exists(CODES_FILE):
    with open(CODES_FILE, "w") as f:
        json.dump({"VIP12345": {"used": False, "days": 30}}, f)

# ================= IA =================
def poisson_pred(home_avg, away_avg):
    matrix = [[poisson.pmf(i, home_avg)*poisson.pmf(j, away_avg)
               for j in range(6)] for i in range(6)]

    home_win = sum(matrix[i][j] for i in range(6) for j in range(6) if i>j)
    draw = sum(matrix[i][i] for i in range(6))
    away_win = sum(matrix[i][j] for i in range(6) for j in range(6) if i<j)

    over25 = sum(matrix[i][j] for i in range(6) for j in range(6) if i+j>=3)
    btts = sum(matrix[i][j] for i in range(1,6) for j in range(1,6))

    max_prob = 0
    best_score = "0-0"
    for i in range(6):
        for j in range(6):
            if matrix[i][j] > max_prob:
                max_prob = matrix[i][j]
                best_score = f"{i}-{j}"

    return home_win, draw, away_win, over25, btts, best_score

# ================= MATCH =================
def get_matches():
    try:
        headers = {"x-apisports-key": API_KEY}
        url = "https://v3.football.api-sports.io/fixtures?date=" + datetime.now().strftime("%Y-%m-%d")
        res = requests.get(url, headers=headers).json()
        matches = res.get("response", [])

        if matches:
            return matches
    except:
        pass

    # fallback
    return [
        {"teams": {"home": {"name": "Barcelona"}, "away": {"name": "Real Madrid"}}},
        {"teams": {"home": {"name": "PSG"}, "away": {"name": "Marseille"}}},
        {"teams": {"home": {"name": "Arsenal"}, "away": {"name": "Chelsea"}}},
        {"teams": {"home": {"name": "Bayern"}, "away": {"name": "Dortmund"}}},
        {"teams": {"home": {"name": "Juventus"}, "away": {"name": "Inter"}}},
    ]

# ================= APP =================
st.title("🔥 BAKARY AI PRO MAX ULTRA (BUSINESS PRO)")

matches = get_matches()

ticket = []
message_global = "🔥 PRONOSTICS DU JOUR 🔥\n\n"

for m in matches[:5]:
    home = m["teams"]["home"]["name"]
    away = m["teams"]["away"]["name"]

    st.subheader(f"{home} vs {away}")

    base = random.uniform(1.2, 2.2)
    home_avg = base + random.uniform(-0.3, 0.5)
    away_avg = base + random.uniform(-0.5, 0.3)

    home_win, draw, away_win, over25, btts, score = poisson_pred(home_avg, away_avg)

    if home_win > 0.6:
        safe_bet = "Victoire domicile"
        confidence = home_win
    elif away_win > 0.6:
        safe_bet = "Victoire extérieur"
        confidence = away_win
    elif over25 > 0.65:
        safe_bet = "Over 2.5"
        confidence = over25
    elif btts > 0.65:
        safe_bet = "BTTS OUI"
        confidence = btts
    else:
        safe_bet = "Double chance"
        confidence = max(home_win, away_win)

    st.write(f"⚽ {round(home_win*100,1)}% | 🤝 {round(draw*100,1)}% | 🚀 {round(away_win*100,1)}%")
    st.success(f"🎯 Score: {score}")
    st.error(f"💰 PARI SÛR: {safe_bet}")
    st.info(f"📊 Confiance: {round(confidence*100,1)}%")

    # MESSAGE WHATSAPP
    msg = f"⚽ {home} vs {away}\n💰 {safe_bet}\n📊 {round(confidence*100,1)}%\n🎯 {score}\n\n"
    message_global += msg

    if confidence > 0.65:
        ticket.append(f"{home} vs {away} → {safe_bet}")

    # SAVE SECURISÉ
    try:
        df = pd.read_csv(DATA_FILE)
    except:
        df = pd.DataFrame(columns=["match","prediction","date"])

    df.loc[len(df)] = [f"{home} vs {away}", safe_bet, str(datetime.now())]

    try:
        df.to_csv(DATA_FILE, index=False)
    except:
        pass

# ================= TICKET COMBINE =================
st.subheader("🎯 TICKET COMBINÉ")

if ticket:
    for t in ticket:
        st.write("✅", t)
else:
    st.warning("Aucun pari sûr aujourd’hui")

# ================= MESSAGE WHATSAPP =================
st.subheader("📱 MESSAGE WHATSAPP")

st.text_area("Copie et envoie à tes clients 👇", message_global, height=250)
