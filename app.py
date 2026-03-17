import streamlit as st
import requests
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta

st.set_page_config(page_title="BAKARY AI DIEU PRO MAX", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
html, body {font-size:20px; color:white;}
.stApp {background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);}
.card {
    background: rgba(0,0,0,0.6);
    padding:18px;
    border-radius:15px;
    margin-bottom:15px;
    box-shadow: 0 0 10px rgba(0,0,0,0.5);
}
.bar {
    height:12px;
    background:#222;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

st.title("⚽ BAKARY AI DIEU PRO MAX 🧠🔥")

# ================= API =================
API_KEY = "289e8418878e48c598507cf2b72338f5"

if not API_KEY:
    st.error("❌ Clé API manquante")
    st.stop()

headers = {"X-Auth-Token": API_KEY}

# ================= SIDEBAR =================
mise = st.sidebar.number_input("💰 Mise", value=100)
filtre = st.sidebar.selectbox("Filtre", ["Tous","SAFE","PIÈGE"])

# ================= SAFE REQUEST =================
@st.cache_data(ttl=300)
def safe_request(url, params=None):
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)

        if r.status_code == 200:
            return r.json()

        elif r.status_code == 403:
            st.error("❌ Clé API invalide ou limite atteinte")
            return None

        elif r.status_code == 429:
            st.warning("⚠️ Trop de requêtes API")
            return None

        return None

    except:
        return None

# ================= FORCE ÉQUIPE =================
@st.cache_data(ttl=600)
def team_strength(team_id):
    data = safe_request(f"https://api.football-data.org/v4/teams/{team_id}/matches")

    if not data:
        return 1.2, 1.2

    matches = data.get("matches", [])[:10]

    gf, ga, pts, count = 0,0,0,0

    for m in matches:
        try:
            score = m.get("score", {}).get("fullTime", {})
            if score.get("home") is None:
                continue

            if m["homeTeam"]["id"] == team_id:
                g_for = score.get("home",0)
                g_against = score.get("away",0)
            else:
                g_for = score.get("away",0)
                g_against = score.get("home",0)

            gf += g_for
            ga += g_against

            if g_for > g_against:
                pts += 3
            elif g_for == g_against:
                pts += 1

            count += 1
        except:
            continue

    if count == 0:
        return 1.2, 1.2

    attack = gf / count
    defense = ga / count
    form = pts / (count*3)

    return attack + form, defense

# ================= MATCHS =================
@st.cache_data(ttl=300)
def get_matches():
    leagues = ["PL","PD","SA"]
    today = datetime.utcnow()
    future = today + timedelta(days=3)

    results = []

    for league in leagues:
        data = safe_request(
            f"https://api.football-data.org/v4/competitions/{league}/matches",
            {"dateFrom":today.strftime("%Y-%m-%d"),"dateTo":future.strftime("%Y-%m-%d")}
        )

        if not data:
            continue

        for m in data.get("matches", []):
            try:
                home = m["homeTeam"]["name"]
                away = m["awayTeam"]["name"]

                att_h, def_h = team_strength(m["homeTeam"]["id"])
                att_a, def_a = team_strength(m["awayTeam"]["id"])

                xg_home = max(0.5, (att_h + def_a)/2 + 0.3)
                xg_away = max(0.3, (att_a + def_h)/2)

                matrix = np.outer(
                    [poisson.pmf(i, xg_home) for i in range(5)],
                    [poisson.pmf(j, xg_away) for j in range(5)]
                )

                scores = [(f"{i}-{j}", matrix[i][j]) for i in range(5) for j in range(5)]
                top_scores = sorted(scores, key=lambda x: x[1], reverse=True)[:3]

                score_txt = ", ".join([f"{s[0]} ({int(s[1]*100)}%)" for s in top_scores])

                avantage = xg_home - xg_away
                confiance = int(65 + (avantage * 25))
                confiance = max(45, min(90, confiance))

                if confiance >= 85:
                    badge = "💎 ULTRA SAFE"
                elif confiance >= 78:
                    badge = "💎 SAFE"
                elif abs(avantage) < 0.25:
                    badge = "🚨 PIÈGE"
                else:
                    badge = "⚠️ MOYEN"

                if filtre == "SAFE" and "SAFE" not in badge:
                    continue
                if filtre == "PIÈGE" and badge != "🚨 PIÈGE":
                    continue

                results.append({
                    "match": f"{home} vs {away}",
                    "score": score_txt,
                    "confiance": confiance,
                    "badge": badge
                })

            except:
                continue

    if not results:
        results.append({
            "match": "Aucun match",
            "score": "Erreur API",
            "confiance": 50,
            "badge": "⚠️"
        })

    return results

data = get_matches()

# ================= IA GLOBAL =================
st.subheader("📊 IA GLOBAL")

moyenne = int(np.mean([m["confiance"] for m in data]))

if moyenne >= 75:
    st.success(f"🔥 IA FORTE ({moyenne}%)")
elif moyenne >= 60:
    st.warning(f"⚠️ IA MOYENNE ({moyenne}%)")
else:
    st.error(f"🚫 IA FAIBLE ({moyenne}%)")

# ================= PARI DU JOUR =================
st.subheader("🧠 PARI DU JOUR")

best = sorted(data, key=lambda x: x["confiance"], reverse=True)[0]

st.markdown(f"""
<div class="card">
🏆 {best['match']}<br><br>
🔥 {best['confiance']}%<br><br>
💎 <b>MEILLEUR PARI</b>
</div>
""", unsafe_allow_html=True)

# ================= AFFICHAGE =================
for m in data:
    color = "green" if "SAFE" in m["badge"] else "red" if "PIÈGE" in m["badge"] else "orange"

    st.markdown(f"""
    <div class="card">
    ⚽ {m['match']}<br><br>
    🎯 {m['score']}<br><br>
    🏷️ {m['badge']}<br><br>
    📊 {m['confiance']}%
    <div class="bar">
        <div style="width:{m['confiance']}%; height:12px; background:{color}; border-radius:10px;"></div>
    </div>
    </div>
    """, unsafe_allow_html=True)
