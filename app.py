import streamlit as st
import requests
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta
import time

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

# ================= VIP =================
vip = st.sidebar.selectbox("🔐 Accès", ["Gratuit", "VIP"])

if vip == "VIP":
    st.success("💎 Mode VIP activé")
else:
    st.warning("🔒 Mode gratuit (accès limité)")

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
        time.sleep(1)
        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code == 200:
            return r.json()
        elif r.status_code == 403:
            st.error("❌ Clé API invalide")
        elif r.status_code == 429:
            st.warning("⚠️ Limite API atteinte → attends 1 min")
    except:
        st.warning("⚠️ Erreur API")

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
                    "ga": t["goalsAgainst"]
                }
    return teams

# ================= MATCHS =================
@st.cache_data(ttl=300)
def get_matches(date):
    comps = ["PL","PD"]
    matches = []

    for c in comps:
        data = safe_request(f"https://api.football-data.org/v4/competitions/{c}/matches?dateFrom={date}&dateTo={date}")
        if data and "matches" in data:
            for m in data["matches"]:
                if m["status"] in ["SCHEDULED","TIMED","LIVE","IN_PLAY"]:
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
        home = home.strip()
        away = away.strip()

        h = stats.get(home, {"gf":38,"ga":38})
        a = stats.get(away, {"gf":38,"ga":38})

        league_avg = 1.4

        xg1 = (h["gf"]/38) * (a["ga"]/38) / league_avg
        xg2 = (a["gf"]/38) * (h["ga"]/38) / league_avg

        xg1 *= 1.15

        xg1 = max(0.6, min(3.5, xg1))
        xg2 = max(0.6, min(3.5, xg2))

        scores = predict(xg1, xg2)

        total = xg1 + xg2
        diff = abs(xg1 - xg2)

        if total >= 3:
            pick = "🔥 OVER 2.5"
        elif xg1 > xg2 + 0.4:
            pick = "🏠 HOME"
        elif xg2 > xg1 + 0.4:
            pick = "✈️ AWAY"
        else:
            pick = "⚽ BTTS"

        # 🔥 NOUVELLE CONFIANCE
        confiance = int(60 + diff * 50 + (total/3)*10)

        if h["gf"] > a["ga"]:
            confiance += 5

        confiance = max(55, min(92, confiance))

        if diff < 0.3:
            badge = "🚨 PIÈGE"
        elif confiance >= 85:
            badge = "💎 ULTRA SAFE"
        elif confiance >= 75:
            badge = "💎 SAFE"
        elif confiance >= 65:
            badge = "⚠️ MOYEN"
        else:
            badge = "❌ RISQUÉ"

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

if not stats:
    st.error("❌ API stats indisponibles")
    st.stop()

matches = get_matches(date_str)

if not matches:
    next_day = (selected_date + timedelta(days=1)).strftime("%Y-%m-%d")
    matches = get_matches(next_day)
    st.warning(f"⚠️ Aucun match aujourd'hui → demain ({next_day})")

results = []
for m in matches:
    r = analyse(m["homeTeam"]["name"], m["awayTeam"]["name"], stats)
    if r:
        results.append(r)

results = sorted(results, key=lambda x: x["conf"], reverse=True)

# ================= VIP LIMIT =================
if vip == "Gratuit":
    st.subheader("💎 TOP 1 MATCH GRATUIT")
    for m in results[:1]:
        st.success(f"{m['match']} → {m['pick']} ({m['conf']}%)")
    st.error("🔒 Passe en VIP pour voir tous les matchs")
else:
    st.subheader(f"💎 TOP 3 MATCHS ({date_str})")
    for m in results[:3]:
        st.success(f"{m['match']} → {m['pick']} ({m['conf']}%)")

# ================= AFFICHAGE =================
def show(title, data):
    st.subheader(title)
    for m in data:
        st.markdown(f"""
        <div class="card">
        ⚽ {m['match']}<br><br>
        🎯 {m['score']}<br><br>
        📊 {m['pick']}<br><br>
        🏷️ {m['badge']}<br><br>
        📈 {m['conf']}%
        </div>
        """, unsafe_allow_html=True)

ultra = [r for r in results if "ULTRA" in r["badge"]]
safe = [r for r in results if "SAFE" in r["badge"] and "ULTRA" not in r["badge"]]
moyen = [r for r in results if "MOYEN" in r["badge"]]

show("💎 ULTRA SAFE", ultra)
show("💎 SAFE", safe)
show("⚠️ MOYEN", moyen)

# ================= WHATSAPP =================
st.subheader("💰 ACCÈS VIP")
st.markdown("""
📲 Contact WhatsApp  
👉 https://wa.me/22666267681  

💎 Prix :
- 1 jour : 1000 FCFA
- 1 semaine : 5000 FCFA
- 1 mois : 15000 FCFA
""")

# ================= GAINS =================
st.subheader("📈 SUIVI GAINS")

if "gain_total" not in st.session_state:
    st.session_state["gain_total"] = 0

gain = st.number_input("Entrer gain du jour (+ ou -)", value=0)

if st.button("Valider gain"):
    st.session_state["gain_total"] += gain

st.success(f"💰 Total gains : {st.session_state['gain_total']} FCFA")
