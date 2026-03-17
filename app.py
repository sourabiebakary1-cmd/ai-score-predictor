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

# ================= DATE =================
choix = st.sidebar.selectbox("📅 Choisir la date", ["Aujourd'hui", "Demain"])

selected_date = datetime.utcnow() if choix == "Aujourd'hui" else datetime.utcnow() + timedelta(days=1)
date_str = selected_date.strftime("%Y-%m-%d")

# ================= SAFE API =================
@st.cache_data(ttl=600)
def safe_request(url):
    try:
        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code == 200:
            return r.json()

        elif r.status_code == 403:
            st.error("❌ Clé API invalide")
        elif r.status_code == 429:
            st.warning("⚠️ Limite API atteinte")

    except requests.exceptions.Timeout:
        st.warning("⚠️ Timeout API")
    except requests.exceptions.RequestException:
        st.warning("⚠️ Erreur connexion API")

    return None

# ================= STATS =================
@st.cache_data(ttl=600)
def get_stats():
    comps = ["PL","PD","SA","BL1","FL1"]
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
                continue
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
    try:
        h = stats.get(home, {"gf":1.5,"ga":1.5})
        a = stats.get(away, {"gf":1.5,"ga":1.5})

        xg1 = max(0.8, min(3, (h["gf"]/10)-(a["ga"]/20)))
        xg2 = max(0.8, min(3, (a["gf"]/10)-(h["ga"]/20)))

        scores = predict(xg1,xg2)
        total = xg1 + xg2
        diff = abs(xg1-xg2)

        if total > 2.7:
            pick = "🔥 OVER 2.5"
        elif xg1 > xg2:
            pick = "🏠 HOME"
        else:
            pick = "✈️ AWAY"

        confiance = int(55 + diff*35)

        if diff < 0.3:
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

    except:
        return None

# ================= RUN =================
stats = get_stats()

if not stats:
    st.error("❌ API stats indisponibles")
    st.stop()

matches = get_matches(date_str)

# 🔥 AUTO DEMAIN
if not matches:
    next_day = (selected_date + timedelta(days=1)).strftime("%Y-%m-%d")
    matches = get_matches(next_day)
    st.warning(f"⚠️ Aucun match aujourd'hui → demain ({next_day})")

if not matches:
    st.error("❌ Aucun match disponible")
    st.stop()

results = []
for m in matches:
    r = analyse(m["homeTeam"]["name"], m["awayTeam"]["name"], stats)
    if r:
        results.append(r)

if not results:
    st.warning("⚠️ Aucun match analysé")
    st.stop()

# ================= FILTRE =================
safe = [r for r in results if r["conf"] >= 70 and "PIÈGE" not in r["badge"]]
moyen = [r for r in results if 60 <= r["conf"] < 70]

if not safe:
    st.warning("⚠️ Aucun SAFE → affichage complet")
    safe = results

# ================= AFFICHAGE =================
st.subheader(f"💎 TOP 3 MATCHS ({date_str})")

for m in safe[:3]:
    st.success(f"{m['match']} → {m['pick']} ({m['conf']}%)")

st.subheader("💎 MATCHS SAFE")

for m in safe:
    st.markdown(f"""
    <div class="card">
    ⚽ {m['match']}<br><br>
    🎯 {m['score']}<br><br>
    📊 {m['pick']}<br><br>
    🏷️ {m['badge']}<br><br>
    📈 {m['conf']}%
    </div>
    """, unsafe_allow_html=True)

st.subheader("⚠️ MATCHS MOYENS")

for m in moyen:
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
st.subheader("💰 STRATÉGIE PRO")
mise_auto = int(bankroll * 0.05)
st.info(f"💵 Mise conseillée : {mise_auto}")
