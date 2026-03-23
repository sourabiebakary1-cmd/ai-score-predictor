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
OWNER_NUMBER = "22607093407"  # ton numéro OK
ADMIN_PASSWORD = "bakary2026VIP"
API_KEY = "289e8418878e48c598507cf2b72338f5"

MODE_TEST = True  # 🔥 IMPORTANT (mets False après)

st.set_page_config(page_title="BAKARY AI PRO MAX ULTRA", layout="wide")

# ================= FILES =================
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["match","prediction","date"]).to_csv(DATA_FILE, index=False)

if not os.path.exists(CODES_FILE):
    with open(CODES_FILE, "w") as f:
        json.dump({"VIP12345": {"used": False, "days": 30}}, f)

def load_codes():
    return json.load(open(CODES_FILE))

def save_codes(c):
    json.dump(c, open(CODES_FILE, "w"), indent=4)

# ================= SESSION =================
if "auth" not in st.session_state:
    st.session_state.auth = False

if "expire" not in st.session_state:
    st.session_state.expire = None

# ================= VIP =================
def paiement():
    st.title("💰 ACCÈS VIP")

    link = f"https://wa.me/{OWNER_NUMBER}?text=Bonjour j'ai payé pour BAKARY AI"
    st.markdown(f"[📞 Envoyer preuve WhatsApp]({link})")

    num = st.text_input("Numéro")
    code = st.text_input("Code VIP", type="password")

    if st.button("Activer"):
        codes = load_codes()

        if code in codes and not codes[code]["used"]:
            codes[code]["used"] = True
            save_codes(codes)

            st.session_state.auth = True
            st.session_state.expire = datetime.now() + timedelta(days=codes[code]["days"])

            st.success("VIP activé 🔥")
        else:
            st.error("Code invalide ❌")

# 🔓 MODE TEST (très important)
if MODE_TEST:
    st.session_state.auth = True

if not st.session_state.auth:
    paiement()
    st.stop()

if st.session_state.expire and datetime.now() > st.session_state.expire:
    st.error("Accès expiré ❌")
    st.session_state.auth = False
    st.stop()

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

# ================= STATS =================
def get_team_stats(team_id, league_id):
    url = f"https://v3.football.api-sports.io/teams/statistics?league={league_id}&season=2023&team={team_id}"
    headers = {"x-apisports-key": API_KEY}

    try:
        res = requests.get(url, headers=headers).json()
        data = res.get("response", {})

        scored = data["goals"]["for"]["total"]["home"] / max(1, data["fixtures"]["played"]["home"])
        conceded = data["goals"]["against"]["total"]["away"] / max(1, data["fixtures"]["played"]["away"])

        return scored, conceded
    except:
        return 1.3, 1.3

# ================= MATCH =================
def get_matches():
    url = "https://v3.football.api-sports.io/fixtures?next=5"
    headers = {"x-apisports-key": API_KEY}

    try:
        res = requests.get(url, headers=headers).json()
        return res.get("response", [])
    except:
        return []

# ================= APP =================
st.title("🔥 BAKARY AI PRO MAX ULTRA (PARI SÛR)")

matches = get_matches()

if not matches:
    st.error("❌ Aucun match trouvé (clé API ou limite atteinte)")
    st.stop()

for m in matches:
    home = m["teams"]["home"]["name"]
    away = m["teams"]["away"]["name"]

    home_id = m["teams"]["home"]["id"]
    away_id = m["teams"]["away"]["id"]
    league_id = m["league"]["id"]

    st.subheader(f"{home} vs {away}")

    home_avg, _ = get_team_stats(home_id, league_id)
    _, away_avg = get_team_stats(away_id, league_id)

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
        safe_bet = "Match risqué ⚠️"
        confidence = max(home_win, away_win, over25, btts)

    st.write(f"🏠 {round(home_win*100,1)}% | 🤝 {round(draw*100,1)}% | 🚀 {round(away_win*100,1)}%")
    st.write(f"⚽ Over2.5: {round(over25*100,1)}% | 🔥 BTTS: {round(btts*100,1)}%")

    st.success(f"🎯 Score probable: {score}")
    st.error(f"💰 PARI SÛR: {safe_bet}")
    st.info(f"📊 Confiance: {round(confidence*100,1)}%")

    df = pd.read_csv(DATA_FILE)
    df.loc[len(df)] = [f"{home} vs {away}", safe_bet, str(datetime.now())]
    df.to_csv(DATA_FILE, index=False)
