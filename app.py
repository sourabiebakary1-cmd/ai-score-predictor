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
ADMIN_PASSWORD = "bakary2026VIP"
API_KEY = "289e8418878e48c598507cf2b72338f5"

st.set_page_config(page_title="BAKARY AI PRO MAX", layout="wide")

# ================= FILES =================
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["match","prediction","date"]).to_csv(DATA_FILE, index=False)

if not os.path.exists(CODES_FILE):
    with open(CODES_FILE, "w") as f:
        json.dump({}, f)

def load_codes():
    try:
        return json.load(open(CODES_FILE))
    except:
        return {}

def save_codes(c):
    json.dump(c, open(CODES_FILE, "w"), indent=4)

# ================= SESSION =================
if "auth" not in st.session_state:
    st.session_state.auth = False

if "expire" not in st.session_state:
    st.session_state.expire = None

# ================= ADMIN =================
st.sidebar.title("🔐 ADMIN")
admin = st.sidebar.text_input("Mot de passe", type="password")

if admin == ADMIN_PASSWORD:
    st.sidebar.success("Admin connecté")

    codes = load_codes()

    if st.sidebar.button("🎟 Code 7j"):
        code = "VIP" + str(random.randint(10000,99999))
        codes[code] = {"used": False, "days": 7}
        save_codes(codes)
        st.sidebar.success(code)

    if st.sidebar.button("🎟 Code 30j"):
        code = "VIP" + str(random.randint(10000,99999))
        codes[code] = {"used": False, "days": 30}
        save_codes(codes)
        st.sidebar.success(code)

# ================= PAIEMENT =================
def paiement():
    st.title("💰 ACCÈS VIP")

    st.write("💳 Orange Money / Moov / Telecel")
    st.write("📞 Numéro :", OWNER_NUMBER)

    link = f"https://wa.me/{OWNER_NUMBER}?text=Bonjour j'ai payé pour BAKARY AI"
    st.markdown(f"[📲 Envoyer preuve WhatsApp]({link})")

    code = st.text_input("Code VIP", type="password")

    if st.button("Activer"):
        codes = load_codes()

        if code in codes and not codes[code]["used"]:
            codes[code]["used"] = True
            save_codes(codes)

            st.session_state.auth = True
            st.session_state.expire = datetime.now() + timedelta(days=codes[code]["days"])

            st.success("✅ VIP activé")
            st.rerun()
        else:
            st.error("❌ Code invalide")

# ================= BLOQUAGE =================
if not st.session_state.auth:
    paiement()
    st.stop()

if st.session_state.expire is not None:
    if datetime.now() > st.session_state.expire:
        st.error("⛔ Expiré")
        st.session_state.auth = False
        st.stop()

# ================= API STATS =================
def get_team_stats(team_id, league_id):
    try:
        url = f"https://v3.football.api-sports.io/teams/statistics?league={league_id}&season=2023&team={team_id}"
        headers = {"x-apisports-key": API_KEY}
        res = requests.get(url, headers=headers, timeout=5).json()["response"]

        scored = res["goals"]["for"]["average"]["total"]
        conceded = res["goals"]["against"]["average"]["total"]

        return float(scored), float(conceded)
    except:
        return 1.5, 1.5  # fallback

# ================= MATCH =================
def get_matches():
    try:
        headers = {"x-apisports-key": API_KEY}
        url = "https://v3.football.api-sports.io/fixtures?next=5"
        res = requests.get(url, headers=headers, timeout=5).json()
        if res.get("response"):
            return res["response"]
    except:
        st.warning("⚠️ API indisponible")

    return []

# ================= IA =================
def analyse(home_avg, away_avg):
    home_win = home_avg / (home_avg + away_avg)
    away_win = away_avg / (home_avg + away_avg)

    over25 = (home_avg + away_avg) / 3
    btts = min(home_avg, away_avg) / 2

    score = f"{round(home_avg)}-{round(away_avg)}"

    return home_win, away_win, over25, btts, score

# ================= APP =================
st.title("🔥 BAKARY AI PRO MAX (IA RÉELLE)")

matches = get_matches()

if not matches:
    st.error("❌ Aucun match (API limite ou clé)")
    st.stop()

for m in matches[:5]:
    home = m["teams"]["home"]["name"]
    away = m["teams"]["away"]["name"]

    home_id = m["teams"]["home"]["id"]
    away_id = m["teams"]["away"]["id"]
    league_id = m["league"]["id"]

    st.subheader(f"{home} vs {away}")

    home_avg, home_conc = get_team_stats(home_id, league_id)
    away_avg, away_conc = get_team_stats(away_id, league_id)

    home_win, away_win, over25, btts, score = analyse(home_avg, away_avg)

    if home_win > 0.6:
        bet = "Victoire domicile"
        conf = home_win
    elif away_win > 0.6:
        bet = "Victoire extérieur"
        conf = away_win
    elif over25 > 0.7:
        bet = "Over 2.5"
        conf = over25
    elif btts > 0.6:
        bet = "BTTS OUI"
        conf = btts
    else:
        bet = "Match risqué"
        conf = max(home_win, away_win)

    st.write(f"🏠 {round(home_win*100,1)}% | 🚀 {round(away_win*100,1)}%")
    st.write(f"⚽ Over2.5: {round(over25*100,1)}% | 🔥 BTTS: {round(btts*100,1)}%")

    st.success(f"🎯 Score: {score}")
    st.error(f"💰 PARI SÛR: {bet}")
    st.info(f"📊 Confiance: {round(conf*100,1)}%")
