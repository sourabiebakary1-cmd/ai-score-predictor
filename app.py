import streamlit as st
import requests
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="BAKARY AI RÉELLE PRO", layout="wide")

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

st.markdown("<h1 style='text-align:center;'>⚽ BAKARY AI IA RÉELLE PRO 🧠🔥</h1>", unsafe_allow_html=True)

# ================= CONFIG =================
API_KEY = "289e8418878e48c598507cf2b72338f5"
headers = {"X-Auth-Token": API_KEY}

mise = st.sidebar.number_input("💰 Mise", min_value=1, value=100)

# ================= SAFE REQUEST =================
@st.cache_data(ttl=600)
def safe_request(url):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            return None
    except:
        return None

# ================= STATS =================
@st.cache_data(ttl=600)
def get_standings():
    data = safe_request("https://api.football-data.org/v4/competitions/PL/standings")
    
    teams = {}
    if data and "standings" in data:
        for t in data["standings"][0]["table"]:
            teams[t["team"]["name"]] = {
                "points": t["points"],
                "gf": t["goalsFor"],
                "ga": t["goalsAgainst"]
            }
    return teams

# ================= MATCHS MONDE =================
@st.cache_data(ttl=300)
def get_matches():
    today = datetime.utcnow()
    future = today + timedelta(days=3)

    url = f"https://api.football-data.org/v4/matches?dateFrom={today.strftime('%Y-%m-%d')}&dateTo={future.strftime('%Y-%m-%d')}"
    data = safe_request(url)

    if not data or "matches" not in data:
        return []

    return data["matches"][:10]

# ================= IA =================
def predict_score(xg_home, xg_away):
    matrix = np.outer(
        [poisson.pmf(i, xg_home) for i in range(5)],
        [poisson.pmf(j, xg_away) for j in range(5)]
    )
    scores = [(f"{i}-{j}", matrix[i][j]) for i in range(5) for j in range(5)]
    return sorted(scores, key=lambda x: x[1], reverse=True)[:3]

def analyse_real(home, away, stats):
    if home not in stats or away not in stats:
        # fallback si équipe inconnue
        xg_home = random.uniform(1.2, 2.2)
        xg_away = random.uniform(0.8, 2.0)
    else:
        h = stats[home]
        a = stats[away]

        xg_home = (h["gf"] / 10) - (a["ga"] / 20)
        xg_away = (a["gf"] / 10) - (h["ga"] / 20)

    xg_home = max(0.5, min(3, xg_home))
    xg_away = max(0.5, min(3, xg_away))

    scores = predict_score(xg_home, xg_away)

    total = xg_home + xg_away

    if total > 2.8:
        analyse = "🔥 OVER 2.5"
    elif xg_home > xg_away:
        analyse = "🏠 Victoire Domicile"
    else:
        analyse = "✈️ Victoire Extérieur"

    diff = abs(xg_home - xg_away)
    confiance = int(60 + diff * 25)

    badge = "🚨 PIÈGE" if diff < 0.3 else "💎 SAFE" if confiance > 75 else "⚠️ MOYEN"

    return {
        "score": ", ".join([s[0] for s in scores]),
        "analyse": analyse,
        "confiance": max(50, min(90, confiance)),
        "badge": badge
    }

# ================= FALLBACK MATCHS =================
def fake_matches():
    teams = ["Real Madrid","Man City","Barcelona","Liverpool","Bayern","PSG"]
    res = []

    for _ in range(5):
        home = random.choice(teams)
        away = random.choice([t for t in teams if t != home])

        res.append({
            "homeTeam": {"name": home},
            "awayTeam": {"name": away}
        })
    return res

# ================= LOGIQUE =================
stats = get_standings()
matches = get_matches()

# 🔥 SI API VIDE → FAKE
if not matches:
    st.warning("⚠️ API vide → Mode secours activé")
    matches = fake_matches()

results = []

for m in matches:
    try:
        home = m["homeTeam"]["name"]
        away = m["awayTeam"]["name"]

        res = analyse_real(home, away, stats)

        if res:
            results.append({
                "match": f"{home} vs {away}",
                **res
            })
    except:
        continue

# ================= SI RIEN =================
if not results:
    st.error("❌ Aucun match exploitable")
    st.stop()

# ================= AFFICHAGE =================
for m in results:
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

top = sorted(results, key=lambda x: x["confiance"], reverse=True)[:3]

for m in top:
    st.success(f"{m['match']} → {m['analyse']} ({m['confiance']}%)")

# ================= STRAT =================
st.subheader("💰 STRATÉGIE")

cote = round(1.5 ** len(top), 2)
gain = mise * cote

for m in top:
    st.write("✔️", m["match"], "→", m["analyse"])

st.success(f"Cote: {cote}")
st.success(f"Gain potentiel: {gain}")
