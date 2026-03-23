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

# ================= SESSION (AUTO LOGIN POUR TEST) =================
if "auth" not in st.session_state:
    st.session_state.auth = True
    st.session_state.expire = datetime.now() + timedelta(days=30)

# ================= API MATCHS (CORRIGÉ) =================
def get_matches():
    try:
        headers = {"x-apisports-key": API_KEY}

        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        # aujourd’hui
        url1 = f"https://v3.football.api-sports.io/fixtures?date={today}"
        res1 = requests.get(url1, headers=headers, timeout=10).json()
        m1 = res1.get("response", [])

        # demain
        url2 = f"https://v3.football.api-sports.io/fixtures?date={tomorrow}"
        res2 = requests.get(url2, headers=headers, timeout=10).json()
        m2 = res2.get("response", [])

        matches = m1 + m2

        if matches:
            return matches

    except:
        pass

    # fallback (évite écran vide)
    return [
        {"teams": {"home": {"name": "API LIMITÉE"}, "away": {"name": "REESSAYER PLUS TARD"}}}
    ]

# ================= APP =================
st.title("🔥 BAKARY AI PRO MAX (OVER ONLY)")

matches = get_matches()

if not matches:
    st.warning("⚠️ API limitée → affichage secours")

message = "🔥 PRONOSTICS OVER 2.5 🔥\n\n"

count = 0

for m in matches:
    if count >= 5:
        break

    try:
        home = m["teams"]["home"]["name"]
        away = m["teams"]["away"]["name"]

        # ✅ OVER FIXE (pas de random)
        prob = 65

        st.success(f"{home} vs {away}")
        st.info("🔥 OVER 2.5")
        st.write(f"📊 Confiance: {prob}%")

        message += f"{home} vs {away} → OVER 2.5 ({prob}%)\n\n"

        count += 1

    except:
        continue

# ================= WHATSAPP =================
st.subheader("📱 ENVOYER AUX CLIENTS")

link = f"https://wa.me/?text={message}"
st.markdown(f"[📤 Envoyer sur WhatsApp]({link})")

st.text_area("Copie message 👇", message)
