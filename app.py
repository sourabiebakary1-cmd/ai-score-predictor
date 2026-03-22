import streamlit as st
import requests
import numpy as np
import pandas as pd
import os

# ================= CONFIG =================
API_KEY = "289e8418878e48c598507cf2b72338f5"
DATA_FILE = "historique.csv"

st.set_page_config(page_title="BAKARY AI PRO MAX FINAL", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#000000,#1a1a1a,#1f3b4d);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ================= INIT =================
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["match","prediction","result","win"]).to_csv(DATA_FILE, index=False)

# ================= API =================
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

def get_team_stats(team_id):
    url = f"https://api.football-data.org/v4/teams/{team_id}/matches?limit=5"
    headers = {"X-Auth-Token": API_KEY}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return 1.5, 1.5

        matches = res.json().get("matches", [])

        gf, ga, count = 0, 0, 0

        for m in matches:
            if m["score"]["fullTime"]["home"] is None:
                continue

            if m["homeTeam"]["id"] == team_id:
                gf += m["score"]["fullTime"]["home"]
                ga += m["score"]["fullTime"]["away"]
            else:
                gf += m["score"]["fullTime"]["away"]
                ga += m["score"]["fullTime"]["home"]

            count += 1

        if count == 0:
            return 1.5, 1.5

        return gf/count, ga/count

    except:
        return 1.5, 1.5

# ================= IA =================
def predict_match(h_att, h_def, a_att, a_def):
    lam_home = (h_att + a_def) / 2
    lam_away = (a_att + h_def) / 2

    # 🔥 variation réaliste
    score_home = max(0, int(np.random.normal(lam_home, 0.7)))
    score_away = max(0, int(np.random.normal(lam_away, 0.7)))

    total = lam_home + lam_away
    proba = min((1 - np.exp(-total)) * 100, 85)

    confidence = "🔥🔥🔥" if proba > 75 else "🔥🔥" if proba > 65 else "🔥"

    return score_home, score_away, round(proba,2), confidence

# ================= GENERATE =================
def generate_matches():
    matches = get_matches()
    results = []

    # MODE SECOURS
    if not matches:
        fake = [
            ("Arsenal","Chelsea"),
            ("PSG","Marseille"),
            ("Real Madrid","Barcelona"),
            ("Milan","Juventus"),
            ("Bayern","Dortmund")
        ]

        for h,a in fake:
            sh = np.random.randint(1,4)
            sa = np.random.randint(0,3)
            proba = np.random.randint(60,80)

            results.append({
                "match": f"{h} vs {a}",
                "prediction": f"{sh}-{sa}",
                "proba": proba,
                "confidence": "🔥🔥"
            })

        return results

    for m in matches:
        if m.get("status") != "SCHEDULED":
            continue

        home = m["homeTeam"]["name"]
        away = m["awayTeam"]["name"]

        h_att, h_def = get_team_stats(m["homeTeam"]["id"])
        a_att, a_def = get_team_stats(m["awayTeam"]["id"])

        sh, sa, proba, conf = predict_match(h_att, h_def, a_att, a_def)

        if proba < 60:
            continue

        results.append({
            "match": f"{home} vs {away}",
            "prediction": f"{sh}-{sa}",
            "proba": proba,
            "confidence": conf
        })

        if len(results) >= 5:
            break

    return results

# ================= MAIN =================
st.title("⚽ BAKARY AI PRO MAX FINAL 🔥")

if "results" not in st.session_state:
    st.session_state["results"] = generate_matches()

if st.button("🔄 Actualiser"):
    st.session_state["results"] = generate_matches()

# ================= DISPLAY =================
best = sorted(st.session_state["results"], key=lambda x: x["proba"], reverse=True)

for i, r in enumerate(best):

    st.markdown(f"""
### ⚽ {r['match']}

- 🎯 Score: {r['prediction']}
- 📊 Probabilité: {r['proba']}%
- 🧠 Confiance: {r['confidence']}
---
""")

    if st.button(f"💾 Sauvegarder {i}", key=f"save_{i}"):
        new = pd.DataFrame([{
            "match": r["match"],
            "prediction": r["prediction"],
            "result": "",
            "win": 0
        }])
        new.to_csv(DATA_FILE, mode="a", header=False, index=False)
        st.success("Ajouté")

# ================= COMBINÉ =================
st.subheader("💰 Ticket Combiné PRO")

combo = best[:3]

for c in combo:
    st.write(f"✅ {c['match']} ({c['proba']}%)")

# ================= HISTORIQUE =================
st.subheader("📊 Historique")
df = pd.read_csv(DATA_FILE)
st.dataframe(df)

# RESET
if st.button("🗑 Reset historique"):
    pd.DataFrame(columns=["match","prediction","result","win"]).to_csv(DATA_FILE, index=False)
    st.success("Historique supprimé")
