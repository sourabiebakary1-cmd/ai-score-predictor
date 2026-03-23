import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import json
import requests
from scipy.stats import poisson

# ================= CONFIG =================
DATA_FILE = "historique.csv"
OWNER_NUMBER = "22607093407"
API_KEY = "289e8418878e48c598507cf2b72338f5"

st.set_page_config(page_title="BAKARY AI GOD MODE", layout="wide")

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
        url = "https://v3.football.api-sports.io/fixtures?next=10"
        res = requests.get(url, headers=headers, timeout=10).json()
        return res.get("response", [])
    except:
        return []

def get_form(team_id):
    try:
        headers = {"x-apisports-key": API_KEY}
        url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5"
        res = requests.get(url, headers=headers, timeout=10).json()["response"]

        points = 0
        for m in res:
            if m["teams"]["home"]["winner"]:
                points += 3
            elif m["teams"]["away"]["winner"]:
                points += 3
            else:
                points += 1

        return points / 15
    except:
        return 0.5

def get_h2h(home_id, away_id):
    try:
        headers = {"x-apisports-key": API_KEY}
        url = f"https://v3.football.api-sports.io/fixtures/headtohead?h2h={home_id}-{away_id}&last=5"
        res = requests.get(url, headers=headers, timeout=10).json()["response"]

        goals = 0
        for m in res:
            goals += m["goals"]["home"] + m["goals"]["away"]

        return goals / 5
    except:
        return 2.5

# ================= APP =================
st.title("🔥 BAKARY AI GOD MODE (ULTIME)")

matches = get_matches()

if not matches:
    st.error("❌ API limitée ou aucun match")
    st.stop()

message = "🔥 PRONOSTICS ULTRA FIABLE 🔥\n\n"
selected = []

# ================= ANALYSE =================
for m in matches:

    home = m["teams"]["home"]["name"]
    away = m["teams"]["away"]["name"]

    home_id = m["teams"]["home"]["id"]
    away_id = m["teams"]["away"]["id"]

    st.subheader(f"{home} vs {away}")

    form_home = get_form(home_id)
    form_away = get_form(away_id)
    h2h_goals = get_h2h(home_id, away_id)

    home_avg = 1.2 + form_home
    away_avg = 1.2 + form_away

    home_win, away_win, over25, score = poisson_pred(home_avg, away_avg)

    # 🎯 DECISION ULTRA
    if home_win > 0.65 and form_home > form_away:
        bet = "Victoire domicile"
        conf = home_win
    elif away_win > 0.65 and form_away > form_home:
        bet = "Victoire extérieur"
        conf = away_win
    elif over25 > 0.7 or h2h_goals > 2.5:
        bet = "Over 2.5"
        conf = over25
    else:
        continue  # 🔥 ignore mauvais match

    selected.append((home, away, bet, conf, score))

# ================= TOP 3 =================
selected = sorted(selected, key=lambda x: x[3], reverse=True)[:3]

if not selected:
    st.warning("⚠️ Aucun match fiable aujourd’hui")
    st.stop()

# ================= AFFICHAGE =================
for home, away, bet, conf, score in selected:

    st.success(f"{home} vs {away}")
    st.write(f"🎯 Score: {score}")
    st.write(f"💰 Pari: {bet}")
    st.write(f"📊 Confiance: {round(conf*100,1)}%")

    message += f"{home} vs {away}\n{bet} ({round(conf*100,1)}%)\n🎯 {score}\n\n"

# ================= WHATSAPP =================
st.subheader("📱 ENVOI CLIENT")

link = f"https://wa.me/?text={message}"
st.markdown(f"[📤 Envoyer WhatsApp]({link})")

st.text_area("Message", message, height=250)
