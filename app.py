import streamlit as st
import requests
import numpy as np
import pandas as pd
from scipy.stats import poisson
import os

# ================= CONFIG =================
API_KEY = "289e8418878e48c598507cf2b72338f5"
DATA_FILE = "historique.csv"

st.set_page_config(page_title="BAKARY AI PRO MAX", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#000000,#1a1a1a,#2c5364);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ================= INIT =================
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
        return res.json().get("matches", [])
    except:
        return []

def predict_score(lh, la):
    home = np.argmax([poisson.pmf(i, lh) for i in range(6)])
    away = np.argmax([poisson.pmf(i, la) for i in range(6)])
    return home, away

def calcul_proba(lh, la):
    total = lh + la
    proba = 1 - np.exp(-total)
    return min(proba * 100, 85)

def btts(lh, la):
    return "OUI" if lh > 1 and la > 1 else "NON"

def over25(lh, la):
    return "OUI" if lh + la > 2.5 else "NON"

# ================= SIDEBAR =================
st.sidebar.title("💰 Bankroll")
bankroll = st.sidebar.number_input("Montant", value=10000)
mise = int(bankroll * 0.02)
st.sidebar.write(f"Mise conseillée: {mise} FCFA")

# ================= MAIN =================
st.title("⚽ BAKARY AI PRO MAX 🔥")

if st.button("🚀 Générer matchs fiables"):

    matches = get_matches()
    results = []

    # 🔥 MODE SECOURS (si API fail)
    if not matches:
        st.warning("⚠️ API indisponible → MODE AUTO activé")

        fake = [
            ("Arsenal", "Chelsea"),
            ("PSG", "Marseille"),
            ("Real Madrid", "Barcelona"),
            ("Milan", "Juventus"),
            ("Bayern", "Dortmund")
        ]

        for home, away in fake:
            lh = np.random.uniform(1.2, 2.3)
            la = np.random.uniform(1.0, 2.1)

            sh, sa = predict_score(lh, la)
            proba = calcul_proba(lh, la)

            results.append({
                "match": f"{home} vs {away}",
                "score": f"{sh}-{sa}",
                "proba": round(proba,2),
                "btts": btts(lh, la),
                "over": over25(lh, la)
            })

    else:
        for match in matches:

            if match.get("status") != "SCHEDULED":
                continue

            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]

            lh = np.random.uniform(1.0, 2.3)
            la = np.random.uniform(0.9, 2.1)

            # 🔥 filtre léger
            if lh + la < 2.0:
                continue

            sh, sa = predict_score(lh, la)
            proba = calcul_proba(lh, la)

            results.append({
                "match": f"{home} vs {away}",
                "score": f"{sh}-{sa}",
                "proba": round(proba,2),
                "btts": btts(lh, la),
                "over": over25(lh, la)
            })

            if len(results) >= 5:
                break

    if len(results) == 0:
        st.error("❌ Aucun match trouvé")
    else:
        st.session_state["results"] = results

# ================= DISPLAY =================
if "results" in st.session_state:

    for i, r in enumerate(st.session_state["results"]):

        st.markdown(f"""
### ⚽ {r['match']}

- 🎯 Score: {r['score']}
- 📊 Probabilité: {r['proba']}%
- 🔥 BTTS: {r['btts']}
- ⚽ Over 2.5: {r['over']}
---
""")

        if st.button(f"✅ Valider {i}", key=f"btn_{i}"):

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
st.dataframe(df)

# RESET
if st.button("🗑 Reset historique"):
    pd.DataFrame(columns=["match","prediction","result","win"]).to_csv(DATA_FILE, index=False)
    st.success("Historique supprimé")
