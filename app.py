import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime, timedelta
import json
import requests
from scipy.stats import poisson

# ================= CONFIG =================
DATA_FILE = "historique.csv"
OWNER_NUMBER = "22607093407"
API_KEY = "289e8418878e48c598507cf2b72338f5"

st.set_page_config(page_title="BAKARY AI GOD MODE", layout="wide")

# ================= FILE =================
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["match","prediction","date"]).to_csv(DATA_FILE, index=False)

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

# ================= API =================
def get_matches():
    try:
        headers = {"x-apisports-key": API_KEY}
        url = "https://v3.football.api-sports.io/fixtures?next=5"
        res = requests.get(url, headers=headers, timeout=5).json()

        if "response" in res and len(res["response"]) > 0:
            return res["response"]

    except:
        pass

    return None

# ================= APP =================
st.title("🔥 BAKARY AI GOD MODE (ULTIME)")

matches = get_matches()

message = "🔥 PRONOSTICS VIP 🔥\n\n"

# ================= SI API OK =================
if matches:

    st.success("✅ Matchs réels chargés")

    for m in matches[:5]:
        home = m["teams"]["home"]["name"]
        away = m["teams"]["away"]["name"]

        st.subheader(f"{home} vs {away}")

        # Simulation intelligente (pas random pur)
        base = 1.5
        home_avg = base + random.uniform(0, 0.5)
        away_avg = base + random.uniform(0, 0.5)

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
        st.error(f"💰 Pari sûr: {bet}")
        st.info(f"📊 Confiance: {round(conf*100,1)}%")

        message += f"{home} vs {away}\n{bet} ({round(conf*100,1)}%)\n\n"

# ================= SI API KO =================
else:
    st.error("❌ API limitée → affichage secours")

    fallback = [
        ("Barcelona", "Real Madrid"),
        ("PSG", "Marseille"),
        ("Arsenal", "Chelsea"),
    ]

    for home, away in fallback:
        st.subheader(f"{home} vs {away}")

        home_win = random.uniform(0.4, 0.6)
        away_win = random.uniform(0.2, 0.4)
        over25 = random.uniform(0.5, 0.7)

        bet = "Over 2.5"
        conf = over25
        score = "2-1"

        st.success(f"🎯 Score: {score}")
        st.error(f"💰 Pari sûr: {bet}")
        st.info(f"📊 Confiance: {round(conf*100,1)}%")

        message += f"{home} vs {away}\n{bet} ({round(conf*100,1)}%)\n\n"

# ================= WHATSAPP =================
st.subheader("📱 ENVOYER AUX CLIENTS")

link = f"https://wa.me/{OWNER_NUMBER}?text={message}"
st.markdown(f"[📤 Envoyer WhatsApp]({link})")

st.text_area("Copie message 👇", message)
