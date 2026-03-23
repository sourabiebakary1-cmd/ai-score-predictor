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

    if st.sidebar.button("🎟 Générer Code 7j"):
        code = "VIP" + str(random.randint(10000,99999))
        codes[code] = {"used": False, "days": 7}
        save_codes(codes)
        st.sidebar.success(code)

    if st.sidebar.button("🎟 Générer Code 30j"):
        code = "VIP" + str(random.randint(10000,99999))
        codes[code] = {"used": False, "days": 30}
        save_codes(codes)
        st.sidebar.success(code)

    st.sidebar.subheader("📊 Clients")
    clients = []
    for c in codes:
        if codes[c].get("used"):
            clients.append({
                "Code": c,
                "Date": codes[c].get("date",""),
                "Durée": codes[c]["days"]
            })
    st.dataframe(pd.DataFrame(clients))

# ================= PAIEMENT =================
def paiement():
    st.title("💰 ACCÈS VIP")

    st.write("💳 Paiement : Orange Money / Moov / Telecel")
    st.write("📞 Numéro :", OWNER_NUMBER)

    link = f"https://wa.me/{OWNER_NUMBER}?text=Bonjour j'ai payé pour BAKARY AI"
    st.markdown(f"[📲 Envoyer preuve WhatsApp]({link})")

    code = st.text_input("Code VIP", type="password")

    if st.button("Activer"):
        codes = load_codes()

        if code in codes and not codes[code]["used"]:
            codes[code]["used"] = True
            codes[code]["date"] = str(datetime.now())
            save_codes(codes)

            st.session_state.auth = True
            st.session_state.expire = datetime.now() + timedelta(days=codes[code]["days"])

            st.success("✅ VIP activé")
        else:
            st.error("❌ Code invalide")

# ================= BLOQUAGE =================
if not st.session_state.auth:
    paiement()
    st.stop()

if st.session_state.expire and datetime.now() > st.session_state.expire:
    st.error("⛔ Abonnement expiré")
    st.session_state.auth = False
    st.stop()

# ================= IA =================
def poisson_pred(home_avg, away_avg):
    matrix = [[poisson.pmf(i, home_avg)*poisson.pmf(j, away_avg)
               for j in range(6)] for i in range(6)]

    home_win = sum(matrix[i][j] for i in range(6) for j in range(6) if i>j)
    away_win = sum(matrix[i][j] for i in range(6) for j in range(6) if i<j)
    over25 = sum(matrix[i][j] for i in range(6) for j in range(6) if i+j>=3)

    best_score = "0-0"
    max_prob = 0
    for i in range(6):
        for j in range(6):
            if matrix[i][j] > max_prob:
                max_prob = matrix[i][j]
                best_score = f"{i}-{j}"

    return home_win, away_win, over25, best_score

# ================= MATCH =================
def get_matches():
    try:
        headers = {"x-apisports-key": API_KEY}
        url = "https://v3.football.api-sports.io/fixtures?date=" + datetime.now().strftime("%Y-%m-%d")
        res = requests.get(url, headers=headers, timeout=5).json()
        matches = res.get("response", [])
        if matches:
            return matches
    except:
        pass

    return [
        {"teams": {"home": {"name": "Barcelona"}, "away": {"name": "Real Madrid"}}},
        {"teams": {"home": {"name": "PSG"}, "away": {"name": "Marseille"}}},
        {"teams": {"home": {"name": "Arsenal"}, "away": {"name": "Chelsea"}}},
    ]

# ================= APP =================
st.title("🔥 BAKARY AI PRO MAX (VIP)")

matches = get_matches()

message = "🔥 PRONOSTICS VIP 🔥\n\n"

for m in matches[:3]:
    home = m["teams"]["home"]["name"]
    away = m["teams"]["away"]["name"]

    st.subheader(f"{home} vs {away}")

    base = random.uniform(1.2, 2.2)
    home_avg = base + random.uniform(-0.3, 0.5)
    away_avg = base + random.uniform(-0.5, 0.3)

    home_win, away_win, over25, score = poisson_pred(home_avg, away_avg)

    if home_win > 0.6:
        bet = "Victoire domicile"
        conf = home_win
    elif away_win > 0.6:
        bet = "Victoire extérieur"
        conf = away_win
    else:
        bet = "Over 2.5"
        conf = over25

    st.success(f"🎯 Score: {score}")
    st.error(f"💰 Pari: {bet}")
    st.info(f"📊 Confiance: {round(conf*100,1)}%")

    message += f"{home} vs {away}\n{bet} ({round(conf*100,1)}%)\n\n"

# ================= WHATSAPP =================
st.subheader("📱 ENVOYER AUX CLIENTS")

link = f"https://wa.me/?text={message}"
st.markdown(f"[📤 Envoyer sur WhatsApp]({link})")

st.text_area("Copie message 👇", message)
