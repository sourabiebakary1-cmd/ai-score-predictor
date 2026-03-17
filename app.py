import streamlit as st
import requests
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta

st.set_page_config(page_title="BAKARY AI DIEU", layout="wide")

# STYLE
st.markdown("""
<style>
html, body {font-size:18px; color:white;}
.stApp {background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);}
.card {background: rgba(0,0,0,0.5); padding:15px; border-radius:12px; margin-bottom:12px;}
.bar {height:10px; background:#333; border-radius:10px;}
</style>
""", unsafe_allow_html=True)

st.title("⚽ BAKARY AI DIEU 🧠🔥")

API_KEY = "289e8418878e48c598507cf2b72338f5"
headers = {"X-Auth-Token": API_KEY}

mise = st.sidebar.number_input("💰 Mise", value=100)
filtre = st.sidebar.selectbox("Filtre", ["Tous","SAFE","PIÈGE"])

# SAFE API
def safe_request(url, params=None):
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

# FORME + FORCE
def team_strength(team_id):
    data = safe_request(f"https://api.football-data.org/v4/teams/{team_id}/matches")
    if not data:
        return 1,1

    matches = data.get("matches", [])[:10]

    goals_for = 0
    goals_against = 0
    points = 0
    count = 0

    for m in matches:
        try:
            if m["score"]["fullTime"]["home"] is None:
                continue

            if m["homeTeam"]["id"] == team_id:
                gf = m["score"]["fullTime"]["home"]
                ga = m["score"]["fullTime"]["away"]
            else:
                gf = m["score"]["fullTime"]["away"]
                ga = m["score"]["fullTime"]["home"]

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
        return 1,1

    attack = goals_for / count
    defense = goals_against / count
    form = points / (count*3)

    return attack + form, defense

# MATCHES
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

                h_id = m["homeTeam"]["id"]
                a_id = m["awayTeam"]["id"]

                att_h, def_h = team_strength(h_id)
                att_a, def_a = team_strength(a_id)

                # IA MULTI FACTEURS
                xg_home = (att_h + def_a)/2 + 0.5
                xg_away = (att_a + def_h)/2

                matrix = np.outer(
                    [poisson.pmf(i, xg_home) for i in range(5)],
                    [poisson.pmf(j, xg_away) for j in range(5)]
                )

                scores = []
                for i in range(5):
                    for j in range(5):
                        scores.append((f"{i}-{j}", matrix[i][j]))

                top_scores = sorted(scores, key=lambda x: x[1], reverse=True)[:3]
                score_txt = ", ".join([f"{s[0]} ({int(s[1]*100)}%)" for s in top_scores])

                # CONFIANCE IA
                avantage = xg_home - xg_away
                confiance = int(60 + (avantage * 20))

                if confiance > 85:
                    confiance = 85
                if confiance < 40:
                    confiance = 40

                # BADGE
                if confiance >= 75:
                    badge = "💎 SAFE"
                elif abs(avantage) < 0.3:
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

    return results

data = get_matches()

# AFFICHAGE
for m in data:

    if "SAFE" in m["badge"]:
        color = "green"
    elif "PIÈGE" in m["badge"]:
        color = "red"
    else:
        color = "orange"

    st.markdown(f"""
    <div class="card">
    <b>⚽ {m['match']}</b><br><br>

    🎯 {m['score']}<br><br>

    🏷️ <span style="color:{color}">{m['badge']}</span><br><br>

    📊 {m['confiance']}%

    <div class="bar">
        <div style="width:{m['confiance']}%; height:10px; background:{color}; border-radius:10px;"></div>
    </div>
    </div>
    """, unsafe_allow_html=True)

# 💰 BANKROLL INTELLIGENTE
st.subheader("💰 Gestion Bankroll")

safe_matches = [m for m in data if "SAFE" in m["badge"]][:3]

if safe_matches:
    mise_safe = mise * 0.3
    cote = round(1.5 ** len(safe_matches),2)
    gain = mise_safe * cote

    for m in safe_matches:
        st.write(m["match"])

    st.success(f"Mise conseillée: {mise_safe}")
    st.success(f"Cote: {cote}")
    st.success(f"Gain potentiel: {gain}")

else:
    st.warning("Pas assez de matchs SAFE")
st.subheader("📡 MATCHS LIVE")

def get_live_matches():
    data = safe_request("https://api.football-data.org/v4/matches")

    live_list = []

    if not data:
        return live_list

    for m in data.get("matches", []):
        try:
            if m["status"] == "IN_PLAY":

                home = m["homeTeam"]["name"]
                away = m["awayTeam"]["name"]

                minute = m["minute"] if "minute" in m else 0

                score_home = m["score"]["fullTime"]["home"] or 0
                score_away = m["score"]["fullTime"]["away"] or 0

                # 🔥 IA LIVE
                total_goals = score_home + score_away

                if minute > 60 and total_goals < 2:
                    prediction = "⚽ BUT BIENTÔT"
                    color = "orange"
                elif total_goals >= 2:
                    prediction = "🔥 OVER 2.5"
                    color = "green"
                else:
                    prediction = "⚠️ CALME"
                    color = "red"

                live_list.append({
                    "match": f"{home} vs {away}",
                    "score": f"{score_home} - {score_away}",
                    "minute": minute,
                    "prediction": prediction,
                    "color": color
                })

        except:
            continue

    return live_list


live_data = get_live_matches()

for m in live_data:
    st.markdown(f"""
    <div class="card">
    ⚽ {m['match']}<br><br>
    ⏱️ {m['minute']}'<br><br>
    📊 {m['score']}<br><br>
    <b style="color:{m['color']}">{m['prediction']}</b>
    </div>
    """, unsafe_allow_html=True)
