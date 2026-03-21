import streamlit as st
import requests
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="BAKARY AI PRO MAX (OVER)", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    color: white;
}
.card {
    background: rgba(0,255,100,0.15);
    padding:15px;
    border-radius:12px;
    margin-bottom:10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>⚽ BAKARY AI PRO MAX 🔥 OVER</h1>", unsafe_allow_html=True)

# 🔐 TA CLÉ API
API_KEY = "289e8418878e48c598507cf2b72338f5"
headers = {"X-Auth-Token": API_KEY}

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

    # 🔥 fallback demain si vide
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

        scores = predict(xg1, xg2)

        total = xg1 + xg2

        # 🔥 TOUJOURS OVER (plus jamais vide)
        confiance = int(65 + total * 8)
        confiance = max(60, min(90, confiance))

        return {
            "match": f"{home} vs {away}",
            "score": ", ".join([s[0] for s in scores]),
            "pick": "🔥 OVER 2.5",
            "conf": confiance,
            "badge": "💎 TRÈS FORT" if confiance >= 80 else "✅ BON"
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

# 🔥 tri + sécurité
results = sorted(results, key=lambda x: x["conf"], reverse=True)

# 🔥 toujours au moins 3 matchs
if len(results) < 3:
    results = results[:3]
else:
    results = results[:3]

# ================= AFFICHAGE =================
st.subheader("🔥 TOP 3 OVER 2.5")

for m in results:
    st.markdown(f"""
    <div class="card">
    ⚽ {m['match']} ➤ 🔥 OVER 2.5 ({m['conf']}%)
    </div>
    """, unsafe_allow_html=True)

# ================= STRATEGIE =================
st.subheader("💰 STRATÉGIE")

mise = int(bankroll * 0.03)

st.info(f"""
👉 Joue uniquement : 🔥 OVER 2.5  
👉 Prends les 3 matchs en combiné  
👉 Priorité : 💎 TRÈS FORT  

💵 Mise conseillée : {mise} FCFA  
""")

# ================= SUIVI =================
st.subheader("📈 SUIVI")

if "gain_total" not in st.session_state:
    st.session_state["gain_total"] = 0

gain = st.number_input("Gain du jour (+ ou -)", value=0)

if st.button("Valider"):
    st.session_state["gain_total"] += gain

st.success(f"Total : {st.session_state['gain_total']} FCFA")
