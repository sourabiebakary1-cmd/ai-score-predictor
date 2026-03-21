import streamlit as st
import requests
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="BAKARY AI PRO MAX (JOUEUR)", layout="wide")

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

st.title("⚽ BAKARY AI PRO MAX 🧠🔥")

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

    points = 0
    for m in data["matches"]:
        if m["score"]["winner"] == "HOME_TEAM":
            if m["homeTeam"]["id"] == team_id:
                points += 3
        elif m["score"]["winner"] == "AWAY_TEAM":
            if m["awayTeam"]["id"] == team_id:
                points += 3
        else:
            points += 1
    return points

# ================= H2H =================
@st.cache_data(ttl=600)
def get_h2h(team1_id, team2_id):
    data = safe_request(f"https://api.football-data.org/v4/teams/{team1_id}/matches?status=FINISHED&limit=10")
    if not data or "matches" not in data:
        return 0

    score = 0
    for m in data["matches"]:
        if (m["homeTeam"]["id"] == team1_id and m["awayTeam"]["id"] == team2_id) or \
           (m["homeTeam"]["id"] == team2_id and m["awayTeam"]["id"] == team1_id):

            if m["score"]["winner"] == "HOME_TEAM":
                if m["homeTeam"]["id"] == team1_id:
                    score += 1
                else:
                    score -= 1
            elif m["score"]["winner"] == "AWAY_TEAM":
                if m["awayTeam"]["id"] == team1_id:
                    score += 1
                else:
                    score -= 1
    return score

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

        form_home = get_form(h["id"])
        form_away = get_form(a["id"])
        h2h = get_h2h(h["id"], a["id"])

        league_avg = 1.4

        xg1 = (h["gf"]/38) * (a["ga"]/38) / league_avg
        xg2 = (a["gf"]/38) * (h["ga"]/38) / league_avg

        # 🔥 bonus forme
        if form_home > form_away:
            xg1 *= 1.2
        elif form_away > form_home:
            xg2 *= 1.2

        # 🔥 bonus H2H
        if h2h > 0:
            xg1 *= 1.1
        elif h2h < 0:
            xg2 *= 1.1

        # domicile
        xg1 *= 1.15

        xg1 = max(0.6, min(3.2, xg1))
        xg2 = max(0.6, min(3.2, xg2))

        scores = predict(xg1, xg2)

        total = xg1 + xg2
        diff = abs(xg1 - xg2)

        # 🎯 PICKS
        if diff > 1.0:
            pick = "🏆 HOME WIN" if xg1 > xg2 else "🏆 AWAY WIN"
        elif diff > 0.5:
            pick = "🔒 1X" if xg1 > xg2 else "🔒 X2"
        elif total >= 3:
            pick = "🔥 OVER 2.5"
        elif total <= 2:
            pick = "❄️ UNDER 2.5"
        else:
            pick = "⚽ BTTS"

        confiance = int(60 + diff * 40 + (form_home - form_away)*2 + h2h*3)
        confiance = max(55, min(90, confiance))

        if diff < 0.3:
            badge = "🚨 À ÉVITER"
        elif confiance >= 82:
            badge = "💎 TRÈS FORT"
        elif confiance >= 72:
            badge = "✅ BON"
        else:
            badge = "⚠️ RISQUÉ"

        return {
            "match": f"{home} vs {away}",
            "score": ", ".join([s[0] for s in scores]),
            "pick": pick,
            "conf": confiance,
            "badge": badge
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

# ================= AFFICHAGE =================
st.subheader("🎯 MEILLEURS MATCHS DU JOUR")

for m in results[:5]:
    st.markdown(f"""
    <div class="card">
    ⚽ {m['match']}<br><br>
    🎯 {m['score']}<br><br>
    📊 {m['pick']}<br><br>
    🏷️ {m['badge']}<br><br>
    📈 {m['conf']}%
    </div>
    """, unsafe_allow_html=True)

# ================= STRATEGIE =================
st.subheader("💰 STRATÉGIE")

mise = int(bankroll * 0.03)

st.info(f"""
👉 Priorité : 🔒 Double chance + 🏆 Victoire  
👉 Joue seulement : 💎 TRÈS FORT / ✅ BON  
👉 Évite : ⚠️ RISQUÉ / 🚨 À ÉVITER  

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
