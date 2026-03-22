import streamlit as st
import requests
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="BAKARY AI PRO MAX ELITE", layout="wide")

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
.safe {color: #00ffcc;}
.risk {color: orange;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>⚽ BAKARY AI PRO MAX ELITE 🧠🔥</h1>", unsafe_allow_html=True)

# API_KEY = "289e8418878e48c598507cf2b72338f5"
API_KEY = "TA_CLE_API_ICI"
headers = {"X-Auth-Token": API_KEY}

bankroll = st.sidebar.number_input("💼 Bankroll", value=10000)

choix = st.sidebar.selectbox("📅 Date", ["Aujourd'hui", "Demain"])
selected_date = datetime.utcnow() if choix == "Aujourd'hui" else datetime.utcnow() + timedelta(days=1)
date_str = selected_date.strftime("%Y-%m-%d")

# ⚠️ MESSAGES PRO
st.warning("⚠️ Les paris comportent des risques. Ne misez jamais tout votre argent.")
st.info("📊 BAKARY AI : Analyse basée sur données statistiques avancées. Résultats non garantis.")

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

# ================= IA =================
def predict(xg1, xg2):
    matrix = np.outer(
        [poisson.pmf(i, xg1) for i in range(5)],
        [poisson.pmf(j, xg2) for j in range(5)]
    )
    scores = [(f"{i}-{j}", matrix[i][j]) for i in range(5) for j in range(5)]
    return sorted(scores, key=lambda x: x[1], reverse=True)

def analyse(home, away, stats):
    try:
        h = stats.get(home)
        a = stats.get(away)
        if not h or not a:
            return None

        form_home = get_form(h["id"])
        form_away = get_form(a["id"])

        league_avg = 1.4

        xg1 = (h["gf"]/38) * (a["ga"]/38) / league_avg
        xg2 = (a["gf"]/38) * (h["ga"]/38) / league_avg

        # BOOST FORME
        if form_home > form_away:
            xg1 *= 1.2
        elif form_away > form_home:
            xg2 *= 1.2

        # BOOST OFFENSIF
        if h["gf"] > a["ga"]:
            xg1 *= 1.1
        if a["gf"] > h["ga"]:
            xg2 *= 1.1

        xg1 = max(0.6, min(3.2, xg1))
        xg2 = max(0.6, min(3.2, xg2))

        total = xg1 + xg2
        diff = abs(xg1 - xg2)

        # 🔥 FILTRES EXPERT
        if total < 2.2:
            return None
        if diff < 0.3:
            return None
        if abs(form_home - form_away) < 2:
            return None
        if xg1 < 1.0 or xg2 < 0.8:
            return None
        if h["ga"] < 20 and a["ga"] < 20:
            return None

        scores = predict(xg1, xg2)
        main_score = scores[0][0]

        # 🎯 PICKS
        if total >= 3.0 and (xg1 > 1.2 and xg2 > 1.0):
            pick = "🔥 OVER 2.5"
        elif diff > 0.8:
            pick = "🏆 HOME WIN" if xg1 > xg2 else "🏆 AWAY WIN"
        else:
            pick = "🔒 DOUBLE CHANCE"

        # 📊 CONFIANCE EXPERT
        confiance = int(50 + (total * 7) + (diff * 30))
        confiance = max(60, min(90, confiance))

        # 🏷️ FILTRE ÉLITE FINAL
        if not (confiance >= 78 and total > 2.5 and diff > 0.5):
            return None

        badge = "💎 MATCH ULTRA FIABLE"
        risk = "FAIBLE"
        color = "safe"

        return {
            "match": f"{home} vs {away}",
            "score": main_score,
            "pick": pick,
            "conf": confiance,
            "badge": badge,
            "risk": risk,
            "color": color
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

# ================= MATCH DU JOUR =================
st.subheader("💎 MATCH DU JOUR (ULTRA FIABLE)")

if len(results) > 0:
    best = results[0]
    st.markdown(f"""
    <div class="card">
    🏆 MEILLEUR CHOIX<br><br>
    ⚽ {best['match']}<br><br>
    🎯 Score probable : {best['score']}<br><br>
    📊 {best['pick']}<br><br>
    🏷️ {best['badge']}<br><br>
    ⚠️ Risque : <span class="{best['color']}">{best['risk']}</span><br><br>
    📈 Confiance : {best['conf']}%
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("❌ Aucun match fiable aujourd’hui")

# ================= STRATEGIE =================
st.subheader("💰 STRATÉGIE EXPERT")

mise = int(bankroll * 0.02)

st.info(f"""
💎 1 seul match par jour  

💵 Mise conseillée : {mise} FCFA  

📌 Discipline :
- Jamais all-in
- Respect du système
""")

# ================= HISTORIQUE =================
st.subheader("📊 HISTORIQUE")

if "history" not in st.session_state:
    st.session_state["history"] = []

result_input = st.selectbox("Résultat", ["Gagné", "Perdu"])

if st.button("Ajouter résultat"):
    st.session_state["history"].append(result_input)

wins = st.session_state["history"].count("Gagné")
total = len(st.session_state["history"])

if total > 0:
    rate = int((wins/total)*100)
    st.success(f"Taux de réussite : {rate}% ({wins}/{total})")
