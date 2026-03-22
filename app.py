import streamlit as st
import requests
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="BAKARY AI PRO MAX ELITE V2", layout="wide")

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
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>⚽ BAKARY AI PRO MAX V2 🧠🔥</h1>", unsafe_allow_html=True)

# API_KEY = "289e8418878e48c598507cf2b72338f5"
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
    comps = ["PL","PD"]
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

# ================= FORME =================
@st.cache_data(ttl=600)
def get_form(team_id):
    data = safe_request(f"https://api.football-data.org/v4/teams/{team_id}/matches?status=FINISHED&limit=5")
    if not data or "matches" not in data:
        return 0

    pts = 0
    for m in data["matches"]:
        if m["score"]["winner"] == "HOME_TEAM" and m["homeTeam"]["id"] == team_id:
            pts += 3
        elif m["score"]["winner"] == "AWAY_TEAM" and m["awayTeam"]["id"] == team_id:
            pts += 3
        else:
            pts += 1
    return pts

# ================= POISSON =================
def predict_goals(xg1, xg2):
    matrix = np.outer(
        [poisson.pmf(i, xg1) for i in range(5)],
        [poisson.pmf(j, xg2) for j in range(5)]
    )
    return matrix

# ================= IA PRO =================
def analyse(home, away, stats):
    try:
        h = stats.get(home)
        a = stats.get(away)
        if not h or not a:
            return None

        form_home = get_form(h["id"])
        form_away = get_form(a["id"])

        xg1 = (h["gf"]/38) * (a["ga"]/38)
        xg2 = (a["gf"]/38) * (h["ga"]/38)

        if form_home > form_away:
            xg1 *= 1.2
        else:
            xg2 *= 1.2

        xg1 = max(0.6, min(3.5, xg1))
        xg2 = max(0.6, min(3.5, xg2))

        total = xg1 + xg2
        diff = abs(xg1 - xg2)

        # ================= SCORE =================
        score = 0
        if total > 2.5: score += 1
        if total > 3: score += 1
        if diff > 0.6: score += 1
        if abs(form_home - form_away) >= 2: score += 1

        # ================= PROBA =================
        matrix = predict_goals(xg1, xg2)

        prob_over15 = 1 - sum(matrix[i][j] for i in range(2) for j in range(2))
        prob_over25 = 1 - sum(matrix[i][j] for i in range(3) for j in range(3))
        prob_over35 = 1 - sum(matrix[i][j] for i in range(4) for j in range(4))

        prob_btts = 1 - (matrix[0].sum() + matrix[:,0].sum() - matrix[0][0])

        # ================= PICKS =================
        if prob_over25 > 0.65:
            pick = "🔥 OVER 2.5"
        elif diff > 0.8:
            pick = "🏆 WIN"
        else:
            pick = "🔒 DOUBLE CHANCE"

        btts = "OUI" if prob_btts > 0.55 else "NON"

        confiance = int(60 + score * 8 + prob_over25 * 20)
        confiance = min(92, confiance)

        if score < 2:
            return None

        return {
            "match": f"{home} vs {away}",
            "score": f"{round(xg1)}-{round(xg2)}",
            "pick": pick,
            "btts": btts,
            "over15": round(prob_over15*100),
            "over25": round(prob_over25*100),
            "over35": round(prob_over35*100),
            "conf": confiance
        }

    except:
        return None

# ================= MATCHS =================
@st.cache_data(ttl=300)
def get_matches(date):
    comps = ["PL","PD"]
    matches = []
    for c in comps:
        data = safe_request(f"https://api.football-data.org/v4/competitions/{c}/matches?dateFrom={date}&dateTo={date}")
        if data and "matches" in data:
            for m in data["matches"]:
                if m["status"] in ["SCHEDULED","TIMED"]:
                    matches.append(m)
    return matches

# ================= RUN =================
stats = get_stats()
matches = get_matches(date_str)

results = []
for m in matches:
    r = analyse(m["homeTeam"]["name"], m["awayTeam"]["name"], stats)
    if r:
        results.append(r)

results = sorted(results, key=lambda x: x["conf"], reverse=True)

# ================= FILTRE ANTI PERTE =================
if len(results) < 2:
    st.error("🚫 JOUR DANGEREUX → NE PAS PARIER")
    st.stop()

# ================= TOP 3 =================
st.subheader("🔥 TOP 3 MATCHS")

for r in results[:3]:
    st.markdown(f"""
    <div class="card">
    ⚽ {r['match']}<br><br>
    🎯 Score : {r['score']}<br><br>
    📊 {r['pick']}<br><br>
    ⚽ BTTS : {r['btts']}<br><br>
    🔢 Over1.5 : {r['over15']}%<br>
    🔢 Over2.5 : {r['over25']}%<br>
    🔢 Over3.5 : {r['over35']}%<br><br>
    📈 Confiance : {r['conf']}%
    </div>
    """, unsafe_allow_html=True)

# ================= STRATEGIE =================
st.subheader("💰 STRATÉGIE PRO")

mise = int(bankroll * 0.02)

st.info(f"""
💵 Mise : {mise} FCFA  

🎯 Jouer 1 à 2 matchs max  
🚫 Stop si perte  
""")
