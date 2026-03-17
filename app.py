import streamlit as st
import requests
import pandas as pd
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta

st.set_page_config(page_title="BAKARY AI ULTIME", layout="wide")

# STYLE
st.markdown("""
<style>
html, body {font-size:18px; color:white;}
.stApp {background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);}
.card {background: rgba(0,0,0,0.5); padding:15px; border-radius:12px; margin-bottom:12px;}
.bar {height:10px; background:#333; border-radius:10px;}
img {width:40px;}
</style>
""", unsafe_allow_html=True)

st.title("⚽ BAKARY AI ULTIME 🚀🔥")

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

# FORME
def team_form(team_id):
    data = safe_request(f"https://api.football-data.org/v4/teams/{team_id}/matches")
    if not data:
        return 1

    matches = data.get("matches", [])[:5]
    score = 0

    for m in matches:
        try:
            if m["score"]["winner"] == "HOME_TEAM" and m["homeTeam"]["id"] == team_id:
                score += 1
            elif m["score"]["winner"] == "AWAY_TEAM" and m["awayTeam"]["id"] == team_id:
                score += 1
        except:
            continue

    return score / max(len(matches),1)

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

                form_home = team_form(h_id)
                form_away = team_form(a_id)

                # IA BOOST
                xg_home = 1.5 + form_home + 0.3
                xg_away = 1.2 + form_away

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

                confiance = int((form_home + form_away)*50)

                # BADGE
                if confiance > 70:
                    badge = "💎 SAFE"
                elif abs(form_home - form_away) < 0.2:
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

# TICKET
st.subheader("🎟️ Ticket automatique")

safe_matches = [m for m in data if "SAFE" in m["badge"]][:3]

if safe_matches:
    cote = round(1.5 ** len(safe_matches),2)
    gain = mise * cote

    for m in safe_matches:
        st.write(m["match"])

    st.success(f"Cote: {cote}")
    st.success(f"Gain potentiel: {gain}")

else:
    st.warning("Pas assez de matchs SAFE")
