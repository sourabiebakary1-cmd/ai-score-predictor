import streamlit as st
import requests
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta

st.set_page_config(page_title="BAKARY AI PRO MAX FINAL", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
html, body {font-size:20px; color:white;}
.stApp {background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);}
.card {
    background: rgba(0,0,0,0.9);
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

st.markdown("<h1 style='text-align:center;'>⚽ BAKARY AI PRO MAX FINAL 🧠🔥</h1>", unsafe_allow_html=True)

# ================= CONFIG =================
API_KEY = "289e8418878e48c598507cf2b72338f5"
headers = {"X-Auth-Token": API_KEY}

mise = st.sidebar.number_input("💰 Mise", min_value=1, value=100)
bankroll = st.sidebar.number_input("💼 Bankroll", value=10000)

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

# ================= STANDINGS MULTI =================
@st.cache_data(ttl=600)
def get_all_standings():
    competitions = ["CL", "PL", "PD", "SA", "BL1", "FL1"]
    teams = {}

    for comp in competitions:
        url = f"https://api.football-data.org/v4/competitions/{comp}/standings"
        data = safe_request(url)

        if data and "standings" in data:
            try:
                for t in data["standings"][0]["table"]:
                    teams[t["team"]["name"]] = {
                        "gf": t["goalsFor"],
                        "ga": t["goalsAgainst"]
                    }
            except:
                continue

    return teams

# ================= MATCHS MULTI =================
@st.cache_data(ttl=300)
def get_matches():
    today = datetime.utcnow()
    future = today + timedelta(days=5)

    competitions = ["CL", "PL", "PD", "SA", "BL1", "FL1"]

    matches = []

    for comp in competitions:
        url = f"https://api.football-data.org/v4/competitions/{comp}/matches?dateFrom={today.strftime('%Y-%m-%d')}&dateTo={future.strftime('%Y-%m-%d')}"
        data = safe_request(url)

        if data and "matches" in data:
            try:
                for m in data["matches"]:
                    if m["status"] in ["SCHEDULED", "TIMED", "LIVE", "IN_PLAY"]:
                        matches.append(m)
            except:
                continue

    return matches

# ================= IA =================
def predict_score(xg_home, xg_away):
    matrix = np.outer(
        [poisson.pmf(i, xg_home) for i in range(5)],
        [poisson.pmf(j, xg_away) for j in range(5)]
    )
    scores = [(f"{i}-{j}", matrix[i][j]) for i in range(5) for j in range(5)]
    return sorted(scores, key=lambda x: x[1], reverse=True)[:3]

def analyse(home, away, stats):
    try:
        if home in stats and away in stats:
            h = stats[home]
            a = stats[away]
            xg_home = (h["gf"]/12) - (a["ga"]/25)
            xg_away = (a["gf"]/12) - (h["ga"]/25)
        else:
            return None

        xg_home = max(0.6, min(3, xg_home))
        xg_away = max(0.6, min(3, xg_away))

        scores = predict_score(xg_home, xg_away)
        total = xg_home + xg_away

        if total > 2.8:
            analyse = "🔥 OVER 2.5"
        elif xg_home > xg_away:
            analyse = "🏠 Victoire Domicile"
        else:
            analyse = "✈️ Victoire Extérieur"

        diff = abs(xg_home - xg_away)
        confiance = int(55 + diff * 30)

        badge = "🚨 PIÈGE" if diff < 0.35 else "💎 SAFE" if confiance >= 75 else "⚠️ MOYEN"

        return {
            "score": ", ".join([s[0] for s in scores]),
            "analyse": analyse,
            "confiance": max(50, min(90, confiance)),
            "badge": badge
        }

    except:
        return None

# ================= LOGIQUE =================
stats = get_all_standings()
matches = get_matches()

if not matches:
    st.error("❌ Aucun match trouvé (API limitée)")
    st.warning("⛔ Essaye plus tard ou change API")
    st.stop()

st.success("📡 MATCHS DISPONIBLES (LIVE + FUTUR)")

results = []
seen = set()

for m in matches:
    try:
        home = m["homeTeam"]["name"]
        away = m["awayTeam"]["name"]

        key = home + away
        if home == away or key in seen:
            continue

        seen.add(key)

        res = analyse(home, away, stats)

        if res:
            results.append({
                "match": f"{home} vs {away}",
                **res
            })
    except:
        continue

if not results:
    st.error("❌ Aucun match exploitable IA")
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

# ================= STRAT =================
st.subheader("💰 STRATÉGIE")

top = [m for m in results if "PIÈGE" not in m["badge"]]
top = sorted(top, key=lambda x: x["confiance"], reverse=True)[:3]

if not top:
    st.warning("⚠️ Aucun bon pari aujourd’hui")
else:
    mise_conseillee = int(bankroll * 0.05)

    for m in top:
        st.success(f"{m['match']} → {m['analyse']} ({m['confiance']}%)")

    st.info(f"💰 Mise: {mise_conseillee}")
