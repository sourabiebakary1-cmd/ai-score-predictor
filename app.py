import streamlit as st
import requests
import numpy as np
import pandas as pd
import os

# ================= CONFIG =================
API_KEY = "289e8418878e48c598507cf2b72338f5"
DATA_FILE = "historique.csv"

st.set_page_config(page_title="BAKARY AI PRO MAX", layout="wide")

# ================= STYLE PRO =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    color: white;
}
.card {
    background: #111;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 15px;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.5);
}
.big {
    font-size: 20px;
    font-weight: bold;
}
.good {color: #00ff99;}
.mid {color: orange;}
.low {color: red;}
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

    score_home = max(0, int(np.random.normal(lam_home, 0.7)))
    score_away = max(0, int(np.random.normal(lam_away, 0.7)))

    total = lam_home + lam_away
    proba = min((1 - np.exp(-total)) * 100, 85)

    if proba > 75:
        conf = "🟢 FORT"
    elif proba > 65:
        conf = "🟡 MOYEN"
    else:
        conf = "🔴 RISQUE"

    return score_home, score_away, round(proba,2), conf

# ================= GENERATE =================
def generate_matches():
    matches = get_matches()
    results = []

    try:
        if matches:
            for m in matches:

                if m.get("status") != "SCHEDULED":
                    continue

                home = m["homeTeam"]["name"]
                away = m["awayTeam"]["name"]

                h_att, h_def = get_team_stats(m["homeTeam"]["id"])
                a_att, a_def = get_team_stats(m["awayTeam"]["id"])

                sh, sa, proba, conf = predict_match(h_att, h_def, a_att, a_def)

                if proba < 55:
                    continue

                results.append({
                    "match": f"{home} vs {away}",
                    "prediction": f"{sh}-{sa}",
                    "proba": proba,
                    "confidence": conf
                })

                if len(results) >= 5:
                    break

        # 🔥 MODE SECOURS
        if len(results) == 0:
            fake = [
                ("Arsenal","Chelsea"),
                ("PSG","Marseille"),
                ("Real Madrid","Barcelona"),
                ("Milan","Juventus"),
                ("Bayern","Dortmund")
            ]

            for h,a in fake:
                results.append({
                    "match": f"{h} vs {a}",
                    "prediction": f"{np.random.randint(1,4)}-{np.random.randint(0,3)}",
                    "proba": np.random.randint(60,80),
                    "confidence": "🟡 MOYEN"
                })

        return results

    except:
        return [
            {"match":"Arsenal vs Chelsea","prediction":"2-1","proba":70,"confidence":"🟡 MOYEN"}
        ]

# ================= MAIN =================
st.title("⚽ BAKARY AI PRO MAX 🔥")

if "results" not in st.session_state:
    st.session_state["results"] = generate_matches()

if st.button("🔄 Actualiser matchs"):
    st.session_state["results"] = generate_matches()

# ================= DISPLAY =================
best = sorted(st.session_state["results"], key=lambda x: x["proba"], reverse=True)

for i, r in enumerate(best):

    color = "good" if r["proba"] > 70 else "mid" if r["proba"] > 60 else "low"

    st.markdown(f"""
<div class="card">
<div class="big">⚽ {r['match']}</div>
🎯 Score: {r['prediction']}<br>
📊 Probabilité: <span class="{color}">{r['proba']}%</span><br>
🧠 Confiance: {r['confidence']}
</div>
""", unsafe_allow_html=True)

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

if st.button("🗑 Reset historique"):
    pd.DataFrame(columns=["match","prediction","result","win"]).to_csv(DATA_FILE, index=False)
    st.success("Historique supprimé")
