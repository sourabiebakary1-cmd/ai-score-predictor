import streamlit as st
import requests
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="BAKARY AI PRO MAX VIP", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    color: white;
}
.card {
    background: rgba(0,0,0,0.9);
    padding:20px;
    border-radius:18px;
    margin-bottom:18px;
}
.free {
    background: linear-gradient(90deg,#ff512f,#dd2476);
    padding:20px;
    border-radius:18px;
    margin-bottom:20px;
    text-align:center;
    font-size:20px;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>⚽ BAKARY AI PRO MAX VIP 💎🔥</h1>", unsafe_allow_html=True)

# 🔐 TA CLÉ API (INCLUSE)
API_KEY = "289e8418878e48c598507cf2b72338f5"
headers = {"X-Auth-Token": API_KEY}

# ================= SIDEBAR =================
bankroll = st.sidebar.number_input("💼 Bankroll", value=10000)

choix = st.sidebar.selectbox("📅 Date", ["Aujourd'hui", "Demain"])
selected_date = datetime.utcnow() if choix == "Aujourd'hui" else datetime.utcnow() + timedelta(days=1)
date_str = selected_date.strftime("%Y-%m-%d")

# ================= API =================
@st.cache_data(ttl=600)
def safe_request(url):
    try:
        time.sleep(1)
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None

# ================= STATS =================
@st.cache_data(ttl=600)
def get_stats():
    comps = ["PL","PD","SA","BL1","FL1"]
    teams = {}
    for c in comps:
        data = safe_request(f"https://api.football-data.org/v4/competitions/{c}/standings")
        if data and "standings" in data:
            for t in data["standings"][0]["table"]:
                teams[t["team"]["name"].strip()] = {
                    "gf": t["goalsFor"],
                    "ga": t["goalsAgainst"],
                    "id": t["team"]["id"]
                }
    return teams

# ================= MATCHS =================
@st.cache_data(ttl=300)
def get_matches(date):
    comps = ["PL","PD","SA","BL1","FL1"]
    matches = []

    for c in comps:
        data = safe_request(f"https://api.football-data.org/v4/competitions/{c}/matches?dateFrom={date}&dateTo={date}")
        if data and "matches" in data:
            for m in data["matches"]:
                if m["status"] in ["SCHEDULED","TIMED"]:
                    matches.append(m)

    # fallback demain
    if len(matches) == 0:
        tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
        for c in comps:
            data = safe_request(f"https://api.football-data.org/v4/competitions/{c}/matches?dateFrom={tomorrow}&dateTo={tomorrow}")
            if data and "matches" in data:
                for m in data["matches"]:
                    if m["status"] in ["SCHEDULED","TIMED"]:
                        matches.append(m)

    return matches

# ================= IA =================
def predict(xg1, xg2):
    matrix = np.outer(
        [poisson.pmf(i, xg1) for i in range(5)],
        [poisson.pmf(j, xg2) for j in range(5)]
    )
    scores = [(f"{i}-{j}", matrix[i][j]) for i in range(5) for j in range(5)]
    return sorted(scores, key=lambda x: x[1], reverse=True)[:3]

def analyse(home, away, stats):
    try:
        h = stats.get(home)
        a = stats.get(away)
        if not h or not a:
            return None

        league_avg = 1.4

        xg1 = (h["gf"]/38) * (a["ga"]/38) / league_avg
        xg2 = (a["gf"]/38) * (h["ga"]/38) / league_avg

        xg1 *= 1.15

        xg1 = max(0.6, min(3.2, xg1))
        xg2 = max(0.6, min(3.2, xg2))

        total = xg1 + xg2

        # 🔥 uniquement OVER
        if total < 2.2:
            return None

        scores = predict(xg1, xg2)

        confiance = int(65 + total * 8)
        confiance = max(70, min(90, confiance))

        return {
            "match": f"{home} vs {away}",
            "score": ", ".join([s[0] for s in scores]),
            "conf": confiance
        }

    except:
        return None

# ================= RUN =================
stats = get_stats()
matches = get_matches(date_str)

results = []
for m in matches:
    r = analyse(m["homeTeam"]["name"], m["awayTeam"]["name"], stats)
    if r:
        results.append(r)

results = sorted(results, key=lambda x: x["conf"], reverse=True)

# ================= 🎁 MATCH GRATUIT =================
st.subheader("🎁 MATCH GRATUIT DU JOUR")

if len(results) > 0:
    free = results[0]
    st.markdown(f"""
    <div class="free">
    🔥 {free['match']} <br><br>
    🎯 OVER 2.5 <br><br>
    📈 Confiance {free['conf']}%
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("Aucun match disponible")

# ================= 🔥 TOP 3 =================
st.subheader("🔥 TOP 3 OVER 2.5")

top_matches = results[:3]

if len(top_matches) == 0:
    st.warning("Aucun bon match aujourd’hui")
else:
    for m in top_matches:
        st.markdown(f"""
        <div class="card">
        ⚽ {m['match']}<br><br>
        🎯 {m['score']}<br><br>
        🔥 OVER 2.5<br><br>
        💎 Confiance {m['conf']}%
        </div>
        """, unsafe_allow_html=True)

# ================= 💰 STRATÉGIE AUTO =================
st.subheader("💰 STRATÉGIE INTELLIGENTE")

mise = int(bankroll * 0.05)

st.success(f"""
👉 Mise automatique : {mise} FCFA  
👉 Joue uniquement OVER 2.5  
👉 Prends 1 à 2 matchs max  
👉 Priorité : 💎 Confiance élevée  
""")

# ================= 📈 SUIVI =================
st.subheader("📈 SUIVI GAINS")

if "gain_total" not in st.session_state:
    st.session_state["gain_total"] = 0

gain = st.number_input("Gain du jour (+ ou -)", value=0)

if st.button("Valider gain"):
    st.session_state["gain_total"] += gain

st.success(f"Total : {st.session_state['gain_total']} FCFA")
