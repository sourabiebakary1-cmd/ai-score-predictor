import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime, timedelta
import json
import requests

# ================= CONFIG =================
DATA_FILE = "historique.csv"
CODES_FILE = "codes.json"
OWNER_NUMBER = "22607093407"
ADMIN_PASSWORD = "bakary2026VIP"
API_KEY = "TA_CLE_API_ICI"

st.set_page_config(page_title="BAKARY AI PRO MAX", layout="wide")

# ================= FILES =================
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["match","prediction","result","win"]).to_csv(DATA_FILE, index=False)

if not os.path.exists(CODES_FILE):
    with open(CODES_FILE, "w") as f:
        json.dump({}, f)

def load_codes():
    with open(CODES_FILE, "r") as f:
        return json.load(f)

def save_codes(c):
    with open(CODES_FILE, "w") as f:
        json.dump(c, f, indent=4)

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

    # GENERATE
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

    # DASHBOARD
    st.sidebar.subheader("📊 Stats")
    total = len(codes)
    used = len([c for c in codes if codes[c]["used"]])
    st.sidebar.write(f"Total: {total}")
    st.sidebar.write(f"Utilisés: {used}")

    # CLIENT LIST
    st.subheader("📋 LISTE CLIENTS")
    clients = []
    for c in codes:
        if codes[c]["used"]:
            clients.append({
                "Code": c,
                "Numéro": codes[c].get("numero",""),
                "Date": codes[c].get("date",""),
                "Durée": codes[c]["days"]
            })
    st.dataframe(pd.DataFrame(clients))

# ================= PAIEMENT =================
def paiement():
    st.title("💰 ACCÈS VIP")

    message = "Bonjour, j'ai payé pour BAKARY AI. ID : "
    link = f"https://wa.me/{OWNER_NUMBER}?text={message}"

    st.markdown(f"[📞 Envoyer preuve WhatsApp]({link})")

    num = st.text_input("Numéro")
    trans = st.text_input("Transaction ID")
    code = st.text_input("Code VIP", type="password")

    if st.button("Activer"):
        if not num or not trans or not code:
            st.warning("Remplis tout")
            return

        codes = load_codes()

        if code in codes and not codes[code]["used"]:
            days = codes[code]["days"]

            codes[code]["used"] = True
            codes[code]["numero"] = num
            codes[code]["date"] = str(datetime.now())

            save_codes(codes)

            st.session_state.auth = True
            st.session_state.expire = datetime.now() + timedelta(days=days)

            st.success("VIP activé")
        else:
            st.error("Code invalide")

# 🔒 BLOQUAGE
if not st.session_state.auth:
    paiement()
    st.stop()

# 🔒 EXPIRATION
if datetime.now() > st.session_state.expire:
    st.error("Expiré")
    st.session_state.auth = False
    st.stop()

# ================= API MATCHS =================
def get_matches():
    url = "https://v3.football.api-sports.io/fixtures?next=5"
    headers = {"x-apisports-key": API_KEY}

    try:
        res = requests.get(url, headers=headers).json()
        matches = []

        for m in res["response"]:
            home = m["teams"]["home"]["name"]
            away = m["teams"]["away"]["name"]

            proba = random.randint(60,90)
            matches.append(f"{home} vs {away} | {proba}%")

        return matches
    except:
        return ["Erreur API"]

# ================= APP =================
st.title("⚽ BAKARY AI PRO MAX 🔥")

for m in get_matches():
    st.success(m)
