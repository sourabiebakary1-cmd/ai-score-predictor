import streamlit as st
import requests
import pandas as pd
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="BAKARY AI FOOTBALL PRO V23", layout="wide")

# 🎨 STYLE PRO
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}
h1 {
    color: #00ffcc;
    text-align: center;
}
.stButton>button {
    background-color: #00ffcc;
    color: black;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("⚽ BAKARY AI FOOTBALL PRO V23 🚀")

API_KEY = "289e8418878e48c598507cf2b72338f5"
headers = {"X-Auth-Token": API_KEY}

# -------- SIDEBAR --------
st.sidebar.title("⚙️ Paramètres")

mise = st.sidebar.number_input("💰 Mise", value=100)
menu = st.sidebar.radio(
    "Menu",
    [
        "Pari Intelligent 🎯",
        "Top Safe 🔒",
        "Ticket Auto 🎟️",
        "Stop Loss 🛑",
        "Live Alert ⏱️"
    ]
)

# -------- STATS --------
@st.cache_data(ttl=600)
def get_team_stats(team_id):
    try:
        url = f"https://api.football-data.org/v4/teams/{team_id}/matches"
        params = {"limit": 10, "status": "FINISHED"}
        r = requests.get(url, headers=headers, params=params, timeout=10)

        if r.status_code != 200:
            return 1.5, 1.2

        data = r.json()
        matches = data.get("matches", [])

        goals_for = goals_against = count = 0

        for m in matches:
            if m["score"]["fullTime"]["home"] is None:
                continue

            if m["homeTeam"]["id"] == team_id:
                goals_for += m["score"]["fullTime"]["home"]
                goals_against += m["score"]["fullTime"]["away"]
            else:
                goals_for += m["score"]["fullTime"]["away"]
                goals_against += m["score"]["fullTime"]["home"]

            count += 1

        if count == 0:
            return 1.5, 1.2

        return goals_for/count, goals_against/count

    except:
        return 1.5, 1.2

# -------- MATCHES --------
@st.cache_data(ttl=300)
def get_matches():

    leagues = ["PL","PD","BL1","SA","FL1"]

    today = datetime.utcnow()
    future = today + timedelta(days=5)  # 🔥 augmenté

    matches = []

    for league in leagues:
        try:
            url = f"https://api.football-data.org/v4/competitions/{league}/matches"
            params = {
                "dateFrom": today.strftime("%Y-%m-%d"),
                "dateTo": future.strftime("%Y-%m-%d")
            }

            r = requests.get(url, headers=headers, params=params, timeout=10)

            if r.status_code != 200:
                continue

            data = r.json()

            for match in data.get("matches", []):

                home = match["homeTeam"]["name"]
                away = match["awayTeam"]["name"]

                home_id = match["homeTeam"]["id"]
                away_id = match["awayTeam"]["id"]

                home_attack, home_def = get_team_stats(home_id)
                away_attack, away_def = get_team_stats(away_id)

                attack_home = (home_attack + away_def)/2 + 0.3
                attack_away = (away_attack + home_def)/2

                home_probs = [poisson.pmf(i, attack_home) for i in range(6)]
                away_probs = [poisson.pmf(i, attack_away) for i in range(6)]

                matrix = np.outer(home_probs, away_probs)

                home_win = away_win = 0
                over25 = btts = 0

                for i in range(6):
                    for j in range(6):
                        p = matrix[i][j]

                        if i > j:
                            home_win += p
                        else:
                            away_win += p

                        if i+j > 2:
                            over25 += p
                        if i>0 and j>0:
                            btts += p

                prob_home = int(home_win*100)
                prob_away = int(away_win*100)

                if over25 > 0.65:
                    bet = "🔥 Over 2.5"
                elif btts > 0.60:
                    bet = "🔥 BTTS"
                else:
                    bet = "⚖️ Match risqué"

                diff = abs(prob_home - prob_away)

                if diff < 10:
                    danger = "🚨"
                elif diff < 20:
                    danger = "⚠️"
                else:
                    danger = "✅"

                matches.append({
                    "Match": f"{home} vs {away}",
                    "Pari": bet,
                    "Danger": danger
                })

        except:
            continue

    # 🔥 FALLBACK (évite écran vide)
    if len(matches) == 0:
        matches.append({
            "Match": "⚠️ API OFFLINE",
            "Pari": "Réessaie plus tard",
            "Danger": "🚨"
        })

    return pd.DataFrame(matches)

df = get_matches()

# -------- STOP LOSS --------
def stop_loss(df):
    safe = df[df["Danger"]=="✅"]

    if len(safe) < 2:
        return "🛑 STOP (Pas assez de matchs fiables)"

    return "✅ GO (Bon moment pour parier)"

# -------- TICKET --------
def ticket_auto(df, mise):
    df = df[df["Danger"]=="✅"].head(3)

    if df.empty:
        return df, 0, 0

    cote = round(np.random.uniform(2.5,4.5),2)
    gain = mise * cote

    return df, cote, gain

# -------- LIVE ALERT --------
def live_alert(df):
    alerts = []

    for _, row in df.iterrows():

        if "Over" in row["Pari"] and row["Danger"]=="✅":
            alerts.append(f"🔥 {row['Match']} → OVER conseillé")

        elif "BTTS" in row["Pari"] and row["Danger"]=="✅":
            alerts.append(f"🔥 {row['Match']} → BTTS conseillé")

    return alerts

# -------- UI --------
if df.empty:
    st.warning("⚠️ Aucun match disponible")
else:

    if menu == "Pari Intelligent 🎯":
        st.dataframe(df)

    elif menu == "Top Safe 🔒":
        st.table(df[df["Danger"]=="✅"])

    elif menu == "Stop Loss 🛑":
        st.success(stop_loss(df))

    elif menu == "Ticket Auto 🎟️":
        t, c, g = ticket_auto(df, mise)
        st.table(t)
        st.success(f"Cote: {c}")
        st.success(f"Gain: {g}")

    elif menu == "Live Alert ⏱️":

        st.subheader("🚨 Alertes en direct")

        alerts = live_alert(df)

        if alerts:
            for a in alerts:
                st.success(a)
        else:
            st.warning("Aucune alerte fiable")

        if st.button("🔄 Rafraîchir"):
            st.cache_data.clear()
            st.rerun()
