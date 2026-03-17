import streamlit as st
import requests
import pandas as pd
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta

st.set_page_config(page_title="BAKARY AI FOOTBALL PRO MAX", layout="wide")

# 🎨 STYLE PRO MAX
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
.block {
    background: rgba(255,255,255,0.05);
    padding: 10px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("⚽ BAKARY AI FOOTBALL PRO MAX 🚀🔥")

API_KEY = "289e8418878e48c598507cf2b72338f5"
headers = {"X-Auth-Token": API_KEY}

# -------- SIDEBAR --------
st.sidebar.title("⚙️ Paramètres PRO")

mise = st.sidebar.number_input("💰 Mise", value=100)

menu = st.sidebar.radio("Menu", [
    "Analyse IA 🧠",
    "Top Safe 💎",
    "Score Exact 🎯",
    "Matchs Pièges 🚨",
    "Ticket PRO 🎟️",
    "Bankroll 💰"
])

# -------- STATS ÉQUIPE --------
@st.cache_data(ttl=600)
def get_team_stats(team_id):
    try:
        url = f"https://api.football-data.org/v4/teams/{team_id}/matches"
        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code != 200:
            return 1.5, 1.2

        data = r.json()
        matches = data.get("matches", [])[:10]

        gf = ga = c = 0

        for m in matches:
            if m["score"]["fullTime"]["home"] is None:
                continue

            if m["homeTeam"]["id"] == team_id:
                gf += m["score"]["fullTime"]["home"]
                ga += m["score"]["fullTime"]["away"]
            else:
                gf += m["score"]["fullTime"]["away"]
                ga += m["score"]["fullTime"]["home"]

            c += 1

        if c == 0:
            return 1.5, 1.2

        return gf/c, ga/c

    except:
        return 1.5, 1.2

# -------- MATCHES --------
@st.cache_data(ttl=300)
def get_matches():

    leagues = ["PL","PD","BL1","SA","FL1"]
    today = datetime.utcnow()
    future = today + timedelta(days=5)

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

            for m in r.json().get("matches", []):

                home = m["homeTeam"]["name"]
                away = m["awayTeam"]["name"]

                h_id = m["homeTeam"]["id"]
                a_id = m["awayTeam"]["id"]

                h_att, h_def = get_team_stats(h_id)
                a_att, a_def = get_team_stats(a_id)

                attack_home = (h_att + a_def)/2 + 0.4
                attack_away = (a_att + h_def)/2

                # POISSON MATRIX
                home_probs = [poisson.pmf(i, attack_home) for i in range(6)]
                away_probs = [poisson.pmf(i, attack_away) for i in range(6)]
                matrix = np.outer(home_probs, away_probs)

                home_win = draw = away_win = 0
                over25 = btts = 0
                best_score = ""
                best_prob = 0

                for i in range(6):
                    for j in range(6):
                        p = matrix[i][j]

                        if i > j:
                            home_win += p
                        elif i == j:
                            draw += p
                        else:
                            away_win += p

                        if p > best_prob:
                            best_prob = p
                            best_score = f"{i}-{j}"

                        if i+j > 2:
                            over25 += p
                        if i>0 and j>0:
                            btts += p

                prob_home = int(home_win*100)
                prob_away = int(away_win*100)

                # 🎯 IA CHOIX PARI
                if prob_home > 65:
                    bet = "🏆 Victoire Domicile"
                elif prob_away > 65:
                    bet = "🏆 Victoire Extérieur"
                elif over25 > 0.7:
                    bet = "🔥 Over 2.5"
                elif btts > 0.65:
                    bet = "🔥 BTTS"
                else:
                    bet = "⚠️ Risqué"

                # 🚨 PIÈGE
                if abs(prob_home - prob_away) < 10:
                    danger = "🚨 Piège"
                elif prob_home > 70 or prob_away > 70:
                    danger = "💎 Ultra Safe"
                else:
                    danger = "⚠️ Moyen"

                confiance = int((prob_home + over25*100 + btts*100)/3)

                matches.append({
                    "Match": f"{home} vs {away}",
                    "Pari": bet,
                    "Score": best_score,
                    "Confiance": confiance,
                    "Danger": danger
                })

        except:
            continue

    if len(matches) == 0:
        matches.append({
            "Match": "API OFFLINE",
            "Pari": "Réessaie",
            "Score": "-",
            "Confiance": 0,
            "Danger": "🚨"
        })

    return pd.DataFrame(matches)

df = get_matches()

# -------- BANKROLL --------
def bankroll(mise, confiance):
    if confiance > 75:
        return mise * 0.3
    elif confiance > 60:
        return mise * 0.2
    else:
        return mise * 0.1

# -------- UI --------
if df.empty:
    st.warning("Aucun match")
else:

    if menu == "Analyse IA 🧠":
        st.dataframe(df)

    elif menu == "Top Safe 💎":
        st.table(df[df["Danger"]=="💎 Ultra Safe"].sort_values(by="Confiance", ascending=False))

    elif menu == "Score Exact 🎯":
        st.table(df[["Match","Score","Confiance"]].sort_values(by="Confiance", ascending=False))

    elif menu == "Matchs Pièges 🚨":
        st.table(df[df["Danger"]=="🚨 Piège"])

    elif menu == "Ticket PRO 🎟️":
        ticket = df[df["Danger"]=="💎 Ultra Safe"].head(3)
        st.table(ticket)
        cote = round(np.random.uniform(2.5,5.0),2)
        st.success(f"Cote totale: {cote}")
        st.success(f"Gain: {mise * cote}")

    elif menu == "Bankroll 💰":
        st.subheader("Gestion intelligente")
        for _, row in df.head(5).iterrows():
            mise_calc = bankroll(mise, row["Confiance"])
            st.write(f"{row['Match']} → Mise conseillée: {round(mise_calc,2)}")
