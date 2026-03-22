import streamlit as st
import requests
import numpy as np
import pandas as pd
from scipy.stats import poisson
import os

# ================= CONFIG =================
API_KEY = "289e8418878e48c598507cf2b72338f5"
DATA_FILE = "historique.csv"

st.set_page_config(page_title="BAKARY AI GOD MODE", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#000000,#1a1a1a,#2c5364);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ================= INIT FILE =================
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["match","prediction","result","win"]).to_csv(DATA_FILE, index=False)

df = pd.read_csv(DATA_FILE)

# ================= FUNCTIONS =================

def get_matches():
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": API_KEY}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return []
        data = res.json()
        return data.get("matches", [])
    except:
        return []

# -------- LEARNING --------
def learning_adjustment(df):
    if len(df) < 10:
        return 1.0
    win_rate = df["win"].mean()
    if win_rate > 0.6:
        return 1.1
    elif win_rate < 0.4:
        return 0.9
    return 1.0

# -------- POISSON --------
def predict_score(lam_home, lam_away):
    home = np.argmax([poisson.pmf(i, lam_home) for i in range(6)])
    away = np.argmax([poisson.pmf(i, lam_away) for i in range(6)])
    return home, away

# -------- PROBA --------
def calcul_proba(lam_home, lam_away, adjust):
    total = (lam_home + lam_away) * adjust
    proba = 1 - np.exp(-total)
    return min(proba * 100, 85)

# -------- FILTRE --------
def filtre_match(lh, la):
    if lh + la < 2.3:
        return False
    if abs(lh - la) > 1.8:
        return False
    return True

# -------- BTTS --------
def btts(lh, la):
    return "OUI" if lh > 1 and la > 1 else "NON"

# -------- OVER --------
def over25(lh, la):
    return "OUI" if lh + la > 2.6 else "NON"

# -------- CONFIDENCE --------
def confidence(p):
    if p > 75:
        return "🔥🔥🔥"
    elif p > 65:
        return "🔥🔥"
    return "🔥"

# ================= SIDEBAR =================
st.sidebar.title("💰 Bankroll")

bankroll = st.sidebar.number_input("Montant", value=10000)
mise = int(bankroll * 0.02)

st.sidebar.write(f"Mise conseillée: {mise} FCFA")

if len(df) > 0:
    winrate = round(df["win"].mean() * 100, 2)
    st.sidebar.write(f"Winrate: {winrate}%")

# ================= MAIN =================
st.title("⚽ BAKARY AI – GOD MODE 🔥")

adjust = learning_adjustment(df)

if st.button("🚀 Générer matchs fiables"):

    matches = get_matches()

    if not matches:
        st.error("❌ API bloquée ou limite atteinte")
    else:
        results = []

        for match in matches:

            if match.get("status") != "SCHEDULED":
                continue

            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]

            # simulation stable
            lam_home = np.random.uniform(1.0, 2.3)
            lam_away = np.random.uniform(0.9, 2.1)

            if not filtre_match(lam_home, lam_away):
                continue

            sh, sa = predict_score(lam_home, lam_away)
            proba = calcul_proba(lam_home, lam_away, adjust)

            results.append({
                "match": f"{home} vs {away}",
                "score": f"{sh}-{sa}",
                "proba": round(proba,2),
                "btts": btts(lam_home, lam_away),
                "over": over25(lam_home, lam_away)
            })

            if len(results) >= 5:
                break

        # STOCKAGE SESSION
        st.session_state["results"] = results

# ================= DISPLAY =================
if "results" in st.session_state:

    for i, r in enumerate(st.session_state["results"]):

        st.markdown(f"""
### ⚽ {r['match']}

- 🎯 Score: {r['score']}
- 📊 Probabilité: {r['proba']}%
- 🧠 Confiance: {confidence(r['proba'])}
- 🔥 BTTS: {r['btts']}
- ⚽ Over 2.5: {r['over']}
---
""")

        if st.button(f"✅ Valider {i}", key=f"val_{i}"):

            new = pd.DataFrame([{
                "match": r["match"],
                "prediction": r["score"],
                "result": "",
                "win": 0
            }])

            new.to_csv(DATA_FILE, mode="a", header=False, index=False)
            st.success("Ajouté à l'historique")

# ================= HISTORIQUE =================
st.subheader("📊 Historique")
df = pd.read_csv(DATA_FILE)
st.dataframe(df)

# RESET
if st.button("🗑 Reset historique"):
    pd.DataFrame(columns=["match","prediction","result","win"]).to_csv(DATA_FILE, index=False)
    st.success("Historique réinitialisé")
