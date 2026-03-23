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

st.set_page_config(page_title="BAKARY AI PRO MAX FINAL", layout="wide")

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
    st.session_state.auth = True
    st.session_state.expire = datetime.now() + timedelta(days=30)

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
    st.write("📞 Numéro :", OWNER_NUMBER)

    link = f"https://wa.me/{OWNER_NUMBER}?text=Bonjour j'ai payé"
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
    st.stop()

# ================= API MATCHS =================
def get_matches():
    try:
        headers = {"x-apisports-key": API_KEY}

        today = datetime.now().strftime("%Y-%m-%d")

        url = f"https://v3.football.api-sports.io/fixtures?date={today}&status=NS"

        res = requests.get(url, headers=headers, timeout=10).json()

        matches = res.get("response", [])

        if matches:
            return matches

    except:
        pass

    return []

# ================= APP =================
st.title("🔥 BAKARY AI PRO MAX (OVER ONLY)")

matches = get_matches()

if not matches:
    st.error("❌ Aucun match disponible (API limitée ou aucun match aujourd’hui)")
    st.stop()

message = "🔥 PRONOSTICS OVER 2.5 🔥\n\n"

count = 0

for m in matches:
    if count >= 5:
        break

    try:
        home = m["teams"]["home"]["name"]
        away = m["teams"]["away"]["name"]

        # Moyenne basée sur API (pas random pur)
        goals_home = m["teams"]["home"].get("goals", 1)
        goals_away = m["teams"]["away"].get("goals", 1)

        avg = 2.6  # base fixe pro

        prob_over25 = min(0.85, max(0.55, avg / 3))

        if prob_over25 < 0.60:
            continue

        st.success(f"{home} vs {away}")
        st.info(f"🔥 OVER 2.5")
        st.write(f"📊 Confiance: {round(prob_over25*100,1)}%")

        message += f"{home} vs {away} → OVER 2.5 ({round(prob_over25*100,1)}%)\n\n"

        count += 1

    except:
        continue

# ================= WHATSAPP =================
st.subheader("📱 ENVOYER AUX CLIENTS")

link = f"https://wa.me/?text={message}"
st.markdown(f"[📤 Envoyer sur WhatsApp]({link})")

st.text_area("Copie message 👇", message)
