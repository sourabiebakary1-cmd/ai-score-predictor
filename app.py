import streamlit as st
import requests
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="BAKARY AI DIEU PRO MAX", layout="wide")

# ================= STYLE MOBILE PRO =================
st.markdown("""
<style>
html, body {
    font-size:18px;
    color:white;
}
h1 {
    font-size:26px !important;
}
.stApp {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
}
.card {
    background: rgba(0,0,0,0.7);
    padding:18px;
    border-radius:15px;
    margin-bottom:15px;
    box-shadow: 0 0 10px rgba(0,0,0,0.5);
    font-size:16px;
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
headers = {"X-Auth-Token": API_KEY}

# ================= SIDEBAR =================
mise = st.sidebar.number_input("💰 Mise", value=100)
filtre = st.sidebar.selectbox("Filtre", ["Tous","SAFE","PIÈGE"])

# ================= SAFE REQUEST ULTRA =================
@st.cache_data(ttl=600)
def safe_request(url, params=None):
    try:
        time.sleep(1.2)  # 🔥 évite trop de requêtes

        r = requests.get(url, headers=headers, params=params, timeout=10)

        if r.status_code == 200:
            return r.json()

        elif r.status_code == 403:
            st.error("❌ Clé API invalide ou bloquée")
            return None

        elif r.status_code == 429:
            st.warning("⚠️ Limite API atteinte → pause 60s")
            time.sleep(60)
            return None

        else:
            return None

    except:
        st.warning("⚠️ Erreur connexion API")
        return None

# ================= FORCE ÉQUIPE OPTIMISÉ =================
@st.cache_data(ttl=1800)
def team_strength(team_id):
    data = safe_request(f"https://api.football-data.org/v4/teams/{team_id}/matches")

    if not data:
        return 1.2, 1.2

    matches = data.get("matches", [])[:6]  # 🔥 réduit appels

    goals_for, goals_against, points, count = 0,0,0,0

    for m in matches:
        try:
            score = m.get("score", {}).get("fullTime", {})
            if score.get("home") is None:
                continue

            if m["homeTeam"]["id"] == team_id:
                gf = score.get("home",0)
                ga = score.get("away",0)
            else:
                gf = score.get("away",0)
                ga = score.get("home",0)

            goals_for += gf
            goals_against += ga

            if gf > ga:
                points += 3
            elif gf == ga:
                points += 1

            count += 1
        except:
            continue

    if count == 0:
        return 1.2, 1.2

    attack = goals_for / count
    defense = goals_against / count
    form = points / (count*3)

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

        for m in data.get("matches", [])[:6]:  # 🔥 limite matchs
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

                if confiance >= 78:
                    badge = "💎 SAFE"
                elif abs(avantage) < 0.25:
                    badge = "🚨 PIÈGE"
                else:
                    badge = "⚠️ MOYEN"

                if filtre == "SAFE" and badge != "💎 SAFE":
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
            "match": "Aucun match fiable",
            "score": "Données indisponibles",
            "confiance": 50,
            "badge": "⚠️ ATTENTE"
        })

    return results

data = get_matches()

# ================= AFFICHAGE =================
for m in data:
    color = "green" if "SAFE" in m["badge"] else "red" if "PIÈGE" in m["badge"] else "orange"

    st.markdown(f"""
    <div class="card">
    <b>⚽ {m['match']}</b><br><br>
    🎯 {m['score']}<br><br>
    🏷️ <span style="color:{color}">{m['badge']}</span><br><br>
    📊 {m['confiance']}%
    <div class="bar">
        <div style="width:{m['confiance']}%; height:12px; background:{color}; border-radius:10px;"></div>
    </div>
    </div>
    """, unsafe_allow_html=True)

# ================= TOP PARIS =================
st.subheader("🎯 TOP PARIS IA")

for m in data:
    if "SAFE" in m["badge"]:
        pari = "✅ Victoire probable"
    elif "PIÈGE" in m["badge"]:
        pari = "🚫 Éviter"
    else:
        pari = "⚠️ BTTS / Over 1.5"

    st.markdown(f"""
    <div class="card">
    ⚽ {m['match']}<br><br>
    🎯 <b>{pari}</b>
    </div>
    """, unsafe_allow_html=True)

# ================= BANKROLL =================
st.subheader("💰 Gestion Bankroll")

valid = [m for m in data if "SAFE" in m["badge"]]
if len(valid) < 2:
    valid = sorted(data, key=lambda x: x["confiance"], reverse=True)[:3]

cote = round(1.4 ** len(valid),2)
gain = mise * cote

for m in valid:
    st.write(m["match"])

st.success(f"Cote: {cote}")
st.success(f"Gain potentiel: {gain}")
