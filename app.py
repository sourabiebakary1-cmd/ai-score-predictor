import streamlit as st
import requests
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta

st.set_page_config(page_title="BAKARY AI PRO MAX ULTIME", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);}
.card {
    background: rgba(0,0,0,0.9);
    padding:20px;
    border-radius:18px;
    margin-bottom:18px;
}
</style>
""", unsafe_allow_html=True)

st.title("⚽ BAKARY AI PRO MAX ULTIME 🧠🔥")

# ================= CONFIG =================
API_KEY = "289e8418878e48c598507cf2b72338f5"
headers = {"X-Auth-Token": API_KEY}

mise = st.sidebar.number_input("💰 Mise", 1, value=100)
bankroll = st.sidebar.number_input("💼 Bankroll", value=10000)

# ================= SAFE API =================
@st.cache_data(ttl=600)
def safe_request(url):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None

# ================= DATA =================
@st.cache_data(ttl=600)
def get_stats():
    comps = ["CL","PL","PD","SA","BL1","FL1"]
    teams = {}

    for c in comps:
        data = safe_request(f"https://api.football-data.org/v4/competitions/{c}/standings")
        if data and "standings" in data:
            try:
                for t in data["standings"][0]["table"]:
                    teams[t["team"]["name"]] = {
                        "gf": t["goalsFor"],
                        "ga": t["goalsAgainst"]
                    }
            except:
                pass
    return teams

@st.cache_data(ttl=300)
def get_matches():
    today = datetime.utcnow()
    future = today + timedelta(days=5)

    comps = ["CL","PL","PD","SA","BL1","FL1"]
    matches = []

    for c in comps:
        data = safe_request(f"https://api.football-data.org/v4/competitions/{c}/matches?dateFrom={today.strftime('%Y-%m-%d')}&dateTo={future.strftime('%Y-%m-%d')}")
        if data and "matches" in data:
            for m in data["matches"]:
                if m["status"] in ["SCHEDULED","TIMED","LIVE","IN_PLAY"]:
                    matches.append(m)
    return matches

# ================= IA =================
def predict(xg1,xg2):
    matrix = np.outer(
        [poisson.pmf(i,xg1) for i in range(5)],
        [poisson.pmf(j,xg2) for j in range(5)]
    )
    scores = [(f"{i}-{j}",matrix[i][j]) for i in range(5) for j in range(5)]
    return sorted(scores,key=lambda x:x[1],reverse=True)[:3]

def analyse(home,away,stats):
    if home not in stats or away not in stats:
        return None

    h,a = stats[home], stats[away]

    xg1 = (h["gf"]/10)-(a["ga"]/20)
    xg2 = (a["gf"]/10)-(h["ga"]/20)

    xg1 = max(0.6,min(3,xg1))
    xg2 = max(0.6,min(3,xg2))

    scores = predict(xg1,xg2)
    total = xg1+xg2
    diff = abs(xg1-xg2)

    # ANALYSE
    if total > 2.7:
        pick = "🔥 OVER 2.5"
    elif xg1 > xg2:
        pick = "🏠 HOME"
    else:
        pick = "✈️ AWAY"

    # CONFIANCE
    confiance = int(55 + diff*35)

    # ANTI PIÈGE
    if diff < 0.35:
        badge = "🚨 PIÈGE"
    elif confiance >= 75:
        badge = "💎 SAFE"
    else:
        badge = "⚠️ MOYEN"

    return {
        "match": f"{home} vs {away}",
        "score": ", ".join([s[0] for s in scores]),
        "pick": pick,
        "conf": max(50,min(90,confiance)),
        "badge": badge
    }

# ================= RUN =================
stats = get_stats()
matches = get_matches()

if not matches:
    st.error("❌ Aucun match")
    st.stop()

results = []
for m in matches:
    try:
        r = analyse(m["homeTeam"]["name"], m["awayTeam"]["name"], stats)
        if r:
            results.append(r)
    except:
        pass

# ================= FILTRE =================
filtered = [r for r in results if not "PIÈGE" in r["badge"] and r["conf"] >= 70]

# ================= TOP 3 =================
top = sorted(filtered, key=lambda x:x["conf"], reverse=True)[:3]

# ================= AFFICHAGE =================
st.subheader("💎 TOP 3 ULTRA SAFE")

for m in top:
    st.success(f"{m['match']} → {m['pick']} ({m['conf']}%)")

st.subheader("📊 MATCHS SÉLECTIONNÉS")

for m in filtered:
    color = "green" if "SAFE" in m["badge"] else "orange"

    st.markdown(f"""
    <div class="card">
    ⚽ {m['match']}<br><br>
    🎯 {m['score']}<br><br>
    📊 {m['pick']}<br><br>
    🏷️ <span style="color:{color}">{m['badge']}</span><br><br>
    📈 {m['conf']}%
    </div>
    """, unsafe_allow_html=True)

# ================= STRAT =================
st.subheader("💰 STRATÉGIE PRO")

mise_auto = int(bankroll * 0.05)
st.info(f"💵 Mise conseillée : {mise_auto}")
