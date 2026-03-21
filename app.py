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

st.markdown("<h1 style='text-align:center;'>⚽ BAKARY AI PRO MAX 🧠🔥</h1>", unsafe_allow_html=True)

API_KEY = "TA_CLE_API_ICI"
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

        if form_home > form_away:
            xg1 *= 1.2
        elif form_away > form_home:
            xg2 *= 1.2

        if h2h > 0:
            xg1 *= 1.1
        elif h2h < 0:
            xg2 *= 1.1

        xg1 *= 1.15

        xg1 = max(0.6, min(3.2, xg1))
        xg2 = max(0.6, min(3.2, xg2))

        scores = predict(xg1, xg2)

        total = xg1 + xg2
        diff = abs(xg1 - xg2)

        # ✅ LOGIQUE CORRIGÉE
        if total >= 2.7:
            pick = "🔥 OVER 2.5"
        elif diff > 0.8:
            pick = "🏆 HOME WIN" if xg1 > xg2 else "🏆 AWAY WIN"
        elif diff > 0.4:
            pick = "🔒 1X" if xg1 > xg2 else "🔒 X2"
        else:
            pick = "⚽ BTTS"

        confiance = int(60 + (total * 5) + (diff * 20) + (form_home - form_away)*2)
        confiance = max(55, min(90, confiance))

        if confiance >= 80:
            badge = "💎 TRÈS FORT"
        elif confiance >= 70:
            badge = "✅ BON"
        elif confiance >= 60:
            badge = "⚠️ RISQUÉ"
        else:
            badge = "🚨 À ÉVITER"

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

if len(matches) == 0:
    st.error("❌ Aucun match trouvé aujourd’hui (vérifie API ou date)")

results = []
for m in matches:
    r = analyse(m["homeTeam"]["name"], m["awayTeam"]["name"], stats)
    if r:
        results.append(r)

results = sorted(results, key=lambda x: x["conf"], reverse=True)

# ================= AFFICHAGE =================
st.subheader("🎯 MEILLEURS MATCHS")

top_matches = [m for m in results if m["conf"] >= 70][:3]

if len(top_matches) == 0:
    st.warning("⚠️ Aucun match fiable aujourd’hui")
else:
    for m in top_matches:
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
👉 Priorité : 🔥 OVER 2.5  
👉 Sécurité : 🔒 DOUBLE CHANCE  
👉 Risqué : 🏆 VICTOIRE  

👉 Joue seulement : 💎 TRÈS FORT / ✅ BON  

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
