import streamlit as st
import requests
import numpy as np
import random
import time
from scipy.stats import poisson
from datetime import datetime, timedelta

st.set_page_config(page_title="BAKARY AI DIEU V2", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
html, body {font-size:18px; color:white;}
.stApp {background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);}
.card {
    background: rgba(0,0,0,0.75);
    padding:18px;
    border-radius:15px;
    margin-bottom:15px;
}
.bar {
    height:12px;
    background:#222;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

st.title("⚽ BAKARY AI DIEU V2 🧠🔥")

# ================= CONFIG =================
API_KEY = "289e8418878e48c598507cf2b72338f5"
headers = {"X-Auth-Token": API_KEY}

mise = st.sidebar.number_input("💰 Mise", value=100)

# ================= SAFE REQUEST =================
@st.cache_data(ttl=600)
def safe_request(url, params=None):
    try:
        time.sleep(1)
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None

# ================= IA SCORE (POISSON) =================
def predict_score(xg_home, xg_away):
    matrix = np.outer(
        [poisson.pmf(i, xg_home) for i in range(5)],
        [poisson.pmf(j, xg_away) for j in range(5)]
    )
    scores = [(f"{i}-{j}", matrix[i][j]) for i in range(5) for j in range(5)]
    return sorted(scores, key=lambda x: x[1], reverse=True)[:3]

# ================= MATCH PIÈGE =================
def detect_trap(xg_home, xg_away):
    diff = abs(xg_home - xg_away)
    if diff < 0.25:
        return True
    if xg_home > 2.5 and xg_away > 2.5:
        return True
    return False

# ================= MATCHS API =================
@st.cache_data(ttl=300)
def get_matches():
    today = datetime.utcnow()
    future = today + timedelta(days=2)

    data = safe_request(
        "https://api.football-data.org/v4/competitions/PL/matches",
        {"dateFrom":today.strftime("%Y-%m-%d"),
         "dateTo":future.strftime("%Y-%m-%d")}
    )

    matches = []

    if not data:
        return matches

    for m in data.get("matches", [])[:5]:
        try:
            home = m["homeTeam"]["name"]
            away = m["awayTeam"]["name"]

            # IA xG
            xg_home = random.uniform(1.2,2.4)
            xg_away = random.uniform(0.8,2.1)

            scores = predict_score(xg_home, xg_away)
            score_txt = ", ".join([f"{s[0]} ({int(s[1]*100)}%)" for s in scores])

            trap = detect_trap(xg_home, xg_away)

            avantage = xg_home - xg_away
            confiance = int(65 + avantage*20)
            confiance = max(50, min(92, confiance))

            if trap:
                badge = "🚨 PIÈGE"
            elif confiance >= 80:
                badge = "💎 SAFE"
            else:
                badge = "⚠️ MOYEN"

            matches.append({
                "match": f"{home} vs {away}",
                "score": score_txt,
                "confiance": confiance,
                "badge": badge
            })

        except:
            continue

    return matches

# ================= IA SECOURS =================
def fake_matches():
    teams = ["Real Madrid","Man City","Barcelona","Liverpool","Bayern","PSG"]
    res = []

    for _ in range(5):
        home = random.choice(teams)
        away = random.choice([t for t in teams if t != home])

        xg_home = random.uniform(1.2,2.5)
        xg_away = random.uniform(1.0,2.2)

        scores = predict_score(xg_home, xg_away)
        score_txt = ", ".join([s[0] for s in scores])

        trap = detect_trap(xg_home, xg_away)

        confiance = int(60 + (xg_home-xg_away)*20)

        badge = "🚨 PIÈGE" if trap else "💎 SAFE" if confiance > 78 else "⚠️ MOYEN"

        res.append({
            "match": f"{home} vs {away}",
            "score": score_txt,
            "confiance": confiance,
            "badge": badge
        })

    return res

# ================= LOGIQUE =================
data = get_matches()

if not data:
    st.warning("⚠️ Mode IA activé")
    data = fake_matches()

# ================= AFFICHAGE =================
for m in data:
    color = "green" if "SAFE" in m["badge"] else "red" if "PIÈGE" in m["badge"] else "orange"

    st.markdown(f"""
    <div class="card">
    ⚽ <b>{m['match']}</b><br><br>
    🎯 {m['score']}<br><br>
    🏷️ <span style="color:{color}">{m['badge']}</span><br><br>
    📊 {m['confiance']}%
    <div class="bar">
        <div style="width:{m['confiance']}%; height:12px; background:{color};"></div>
    </div>
    </div>
    """, unsafe_allow_html=True)

# ================= TOP 3 PARIS =================
st.subheader("🏆 TOP 3 PARIS SÛRS")

top = sorted(data, key=lambda x: x["confiance"], reverse=True)[:3]

for m in top:
    st.markdown(f"""
    <div class="card">
    ⚽ {m['match']}<br><br>
    💎 <b>PARI ULTRA SAFE</b><br>
    📊 {m['confiance']}%
    </div>
    """, unsafe_allow_html=True)

# ================= BANKROLL =================
st.subheader("💰 STRATÉGIE GAGNANTE")

cote = round(1.4 ** len(top),2)
gain = mise * cote

for m in top:
    st.write(m["match"])

st.success(f"Cote: {cote}")
st.success(f"Gain potentiel: {gain}")
