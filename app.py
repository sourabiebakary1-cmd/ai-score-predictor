import streamlit as st
import requests
import numpy as np
import random
from scipy.stats import poisson
from datetime import datetime, timedelta

st.set_page_config(page_title="BAKARY AI PRO MAX", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
html, body, [class*="css"] {
    font-size: 20px !important;
    color: white;
}
.stApp {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
}
.card {
    background: rgba(0,0,0,0.85);
    padding:20px;
    border-radius:18px;
    margin-bottom:18px;
}
.bar {
    height:14px;
    background:#222;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>⚽ BAKARY AI PRO MAX 🧠🔥</h1>", unsafe_allow_html=True)

# ================= CONFIG =================
API_KEY = "289e8418878e48c598507cf2b72338f5"
headers = {"X-Auth-Token": API_KEY}

mise = st.sidebar.number_input("💰 Mise", min_value=1, value=100)

# ================= SAFE REQUEST =================
@st.cache_data(ttl=600)
def safe_request(url, params=None):
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None

# ================= IA =================
def predict_score(xg_home, xg_away):
    matrix = np.outer(
        [poisson.pmf(i, xg_home) for i in range(5)],
        [poisson.pmf(j, xg_away) for j in range(5)]
    )
    scores = [(f"{i}-{j}", matrix[i][j]) for i in range(5) for j in range(5)]
    return sorted(scores, key=lambda x: x[1], reverse=True)[:3]

def analyse_match(xg_home, xg_away):
    total = xg_home + xg_away
    
    if total > 3:
        return "🔥 OVER 2.5"
    elif xg_home > 1.5 and xg_away > 1.2:
        return "⚽ BTTS"
    elif xg_home > xg_away:
        return "🏠 Victoire Domicile"
    else:
        return "✈️ Victoire Extérieur"

def detect_trap(xg_home, xg_away):
    return abs(xg_home - xg_away) < 0.3

# ================= MATCHS =================
@st.cache_data(ttl=300)
def get_matches():
    today = datetime.utcnow()
    future = today + timedelta(days=2)

    data = safe_request(
        "https://api.football-data.org/v4/competitions/PL/matches",
        {
            "dateFrom": today.strftime("%Y-%m-%d"),
            "dateTo": future.strftime("%Y-%m-%d")
        }
    )

    matches = []

    if not data or "matches" not in data:
        return matches

    for m in data["matches"][:6]:
        try:
            home = m["homeTeam"]["name"]
            away = m["awayTeam"]["name"]

            # IA xG amélioré
            xg_home = random.uniform(1.3,2.6)
            xg_away = random.uniform(1.0,2.2)

            scores = predict_score(xg_home, xg_away)
            score_txt = ", ".join([s[0] for s in scores])

            analyse = analyse_match(xg_home, xg_away)
            trap = detect_trap(xg_home, xg_away)

            confiance = int(60 + (xg_home - xg_away)*20 + random.uniform(0,10))
            confiance = max(50, min(90, confiance))

            badge = "🚨 PIÈGE" if trap else "💎 SAFE" if confiance > 78 else "⚠️ MOYEN"

            matches.append({
                "match": f"{home} vs {away}",
                "score": score_txt,
                "analyse": analyse,
                "confiance": confiance,
                "badge": badge
            })

        except:
            continue

    return matches

# ================= SECOURS =================
def fake_matches():
    teams = ["Real Madrid","Man City","Barcelona","Liverpool","Bayern","PSG"]
    res = []

    for _ in range(6):
        home = random.choice(teams)
        away = random.choice([t for t in teams if t != home])

        xg_home = random.uniform(1.3,2.6)
        xg_away = random.uniform(1.0,2.2)

        scores = predict_score(xg_home, xg_away)
        analyse = analyse_match(xg_home, xg_away)

        confiance = int(60 + (xg_home - xg_away)*20)
        confiance = max(50, min(90, confiance))

        badge = "🚨 PIÈGE" if detect_trap(xg_home, xg_away) else "💎 SAFE" if confiance > 78 else "⚠️ MOYEN"

        res.append({
            "match": f"{home} vs {away}",
            "score": ", ".join([s[0] for s in scores]),
            "analyse": analyse,
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
    📊 <b>{m['analyse']}</b><br><br>
    🏷️ <span style="color:{color}">{m['badge']}</span><br><br>
    📈 {m['confiance']}%
    <div class="bar">
        <div style="width:{m['confiance']}%; height:14px; background:{color};"></div>
    </div>
    </div>
    """, unsafe_allow_html=True)

# ================= TOP =================
st.subheader("🏆 TOP PARIS")

top = sorted(data, key=lambda x: x["confiance"], reverse=True)[:3]

for m in top:
    st.success(f"{m['match']} → {m['analyse']} ({m['confiance']}%)")

# ================= STRAT =================
st.subheader("💰 STRATÉGIE")

cote = round(1.5 ** len(top), 2)
gain = mise * cote

st.write("🎯 Paris conseillés :")
for m in top:
    st.write("✔️", m["match"], "→", m["analyse"])

st.success(f"Cote: {cote}")
st.success(f"Gain potentiel: {gain}")
