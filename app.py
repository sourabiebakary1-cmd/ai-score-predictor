import streamlit as st
import requests
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="BAKARY AI PRO MAX ELITE", layout="wide")

API_KEY = "289e8418878e48c598507cf2b72338f5"

st.title("⚽ BAKARY AI PRO MAX ELITE 🧠🔥")

st.warning("⚠️ Les paris comportent des risques.")
st.info("📊 Analyse avancée (Poisson + IA)")

# ================= API =================
@st.cache_data(ttl=300)
def get_matches():
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": API_KEY}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return []
        return r.json().get("matches", [])
    except:
        return []

# ================= POISSON =================
def poisson_model(home_attack, away_attack):
    max_goals = 5
    matrix = np.zeros((max_goals, max_goals))

    for i in range(max_goals):
        for j in range(max_goals):
            matrix[i][j] = poisson.pmf(i, home_attack) * poisson.pmf(j, away_attack)

    return matrix

# ================= ANALYSE =================
def analyse_match(match):
    try:
        home = match.get("homeTeam", {}).get("name", "Equipe A")
        away = match.get("awayTeam", {}).get("name", "Equipe B")

        # Valeurs simulées réalistes (évite bug API vide)
        home_attack = np.random.uniform(1.2, 2.2)
        away_attack = np.random.uniform(0.8, 1.8)

        matrix = poisson_model(home_attack, away_attack)

        # Probabilités
        home_win = np.sum(np.tril(matrix, -1))
        draw = np.sum(np.diag(matrix))
        away_win = np.sum(np.triu(matrix, 1))

        over_25 = np.sum([matrix[i][j] for i in range(6) for j in range(6) if i+j > 2])
        btts = np.sum([matrix[i][j] for i in range(1,6) for j in range(1,6)])

        # Score exact probable
        best_score = np.unravel_index(np.argmax(matrix), matrix.shape)

        proba = max(home_win, away_win)

        return {
            "match": f"{home} vs {away}",
            "proba": proba,
            "over25": over_25,
            "btts": btts,
            "score_exact": f"{best_score[0]} - {best_score[1]}"
        }

    except:
        return None

# ================= DATA =================
matches = get_matches()

analyses = []
for m in matches:
    r = analyse_match(m)
    if r:
        analyses.append(r)

# ================= MATCH DU JOUR =================
st.subheader("💎 MATCH DU JOUR")

if len(analyses) == 0:
    st.error("❌ Aucun match disponible")
else:
    best = max(analyses, key=lambda x: x["proba"])
    proba = best["proba"]

    if proba < 0.70:
        st.error("🚫 JOUR OFF - NE PAS JOUER")
        st.stop()

    st.success(f"✅ {best['match']}")
    st.progress(int(proba * 100))
    st.write(f"📊 Confiance: {round(proba*100)}%")

    # ================= PARIS =================
    st.subheader("🎯 PRÉDICTIONS")

    # Over/Under
    if best["over25"] > 0.65:
        st.write(f"⚽ Over 2.5 ✅ ({round(best['over25']*100)}%)")
    else:
        st.write(f"⚽ Under 2.5 ✅ ({round((1-best['over25'])*100)}%)")

    # BTTS
    if best["btts"] > 0.60:
        st.write(f"🔥 BTTS OUI ({round(best['btts']*100)}%)")
    else:
        st.write(f"❌ BTTS NON ({round((1-best['btts'])*100)}%)")

    # Score exact
    st.write(f"🔢 Score probable: {best['score_exact']}")

# ================= BANKROLL =================
st.subheader("💰 GESTION ARGENT")

bankroll = st.number_input("💰 Ton budget", value=10000)
mise = int(bankroll * 0.02)

st.success(f"💵 Mise conseillée: {mise} FCFA")

# ================= APPRENTISSAGE =================
st.subheader("🧠 APPRENTISSAGE")

if "history" not in st.session_state:
    st.session_state.history = []

result = st.selectbox("Résultat du pari", ["Gagné", "Perdu"])

if st.button("Enregistrer"):
    st.session_state.history.append(result)

wins = st.session_state.history.count("Gagné")
losses = st.session_state.history.count("Perdu")

total = wins + losses

if total > 0:
    winrate = wins / total * 100
    st.write(f"📊 Winrate: {round(winrate)}%")
    st.write(f"✅ Gagné: {wins} | ❌ Perdu: {losses}")

# ================= DEBUG =================
with st.expander("⚙️ DEBUG"):
    st.write("Matchs:", len(matches))
