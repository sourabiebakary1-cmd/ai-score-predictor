import streamlit as st
import numpy as np
import pandas as pd
import os
import random

# ================= CONFIG =================
DATA_FILE = "historique.csv"

st.set_page_config(page_title="BAKARY AI XGBOOST PRO", layout="wide")

# 🔒 cacher erreurs Streamlit
st.set_option('client.showErrorDetails', False)

# ================= STYLE =================
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
}
.good {color: #00ff99;}
.mid {color: orange;}
.low {color: red;}
</style>
""", unsafe_allow_html=True)

# ================= INIT =================
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["match","prediction","result","win"]).to_csv(DATA_FILE, index=False)

# ================= IA LEARNING =================
def get_form_boost():
    try:
        df = pd.read_csv(DATA_FILE)

        if len(df) < 5:
            return 0

        wins = df["win"].sum()
        rate = wins / len(df)

        return (rate - 0.5) * 30
    except:
        return 0

# ================= XGBOOST SIMULATION =================
def xgboost_predict():
    try:
        base_attack = random.uniform(1.2, 2.5)
        base_defense = random.uniform(0.8, 2.0)

        xg_home = base_attack + random.uniform(-0.5, 0.5)
        xg_away = base_defense + random.uniform(-0.5, 0.5)

        score_home = max(0, int(np.random.poisson(xg_home)))
        score_away = max(0, int(np.random.poisson(xg_away)))

        total = xg_home + xg_away
        boost = get_form_boost()

        proba = min((total * 20) + boost, 90)

        btts = "OUI" if score_home > 0 and score_away > 0 else "NON"
        over = "OUI" if total > 2.5 else "NON"

        if proba > 80:
            conf = "🟢 IA FORTE"
        elif proba > 70:
            conf = "🟡 IA MOYENNE"
        else:
            conf = "🔴 IA RISQUE"

        return score_home, score_away, round(proba,2), conf, btts, over

    except:
        return 1, 1, 60, "🔴 ERREUR", "NON", "NON"

# ================= GENERATE =================
def generate_matches():
    try:
        teams = [
            ("Arsenal","Chelsea"),
            ("PSG","Marseille"),
            ("Real Madrid","Barcelona"),
            ("Milan","Juventus"),
            ("Bayern","Dortmund")
        ]

        results = []

        for h,a in teams:
            sh, sa, proba, conf, btts, over = xgboost_predict()

            results.append({
                "match": f"{h} vs {a}",
                "prediction": f"{sh}-{sa}",
                "proba": proba,
                "confidence": conf,
                "btts": btts if btts else "NON",
                "over": over if over else "NON"
            })

        return results

    except:
        return [{
            "match":"Erreur vs Système",
            "prediction":"1-1",
            "proba":50,
            "confidence":"🔴 ERREUR",
            "btts":"NON",
            "over":"NON"
        }]

# ================= MAIN =================
st.title("⚽ BAKARY AI XGBOOST PRO 🤖🔥")

if "results" not in st.session_state:
    st.session_state["results"] = generate_matches()

if st.button("🔄 Actualiser IA"):
    st.session_state["results"] = generate_matches()

best = sorted(st.session_state["results"], key=lambda x: x.get("proba",0), reverse=True)

# ================= DISPLAY =================
for i, r in enumerate(best):

    proba = r.get("proba", 0)
    match = r.get("match", "Match inconnu")
    prediction = r.get("prediction", "0-0")
    confidence = r.get("confidence", "❓")
    btts = r.get("btts", "NON")
    over = r.get("over", "NON")

    color = "good" if proba > 75 else "mid" if proba > 65 else "low"

    st.markdown(f"""
<div class="card">
<b>⚽ {match}</b><br>
🎯 Score IA: {prediction}<br>
📊 Probabilité: <span class="{color}">{proba}%</span><br>
🧠 {confidence}<br>
🔥 BTTS: {btts}<br>
⚽ Over 2.5: {over}
</div>
""", unsafe_allow_html=True)

    if st.button(f"💾 Save {i}", key=f"s{i}"):
        try:
            new = pd.DataFrame([{
                "match": match,
                "prediction": prediction,
                "result": "",
                "win": random.choice([0,1])
            }])
            new.to_csv(DATA_FILE, mode="a", header=False, index=False)
            st.success("IA mise à jour ✔️")
        except:
            st.error("Erreur sauvegarde")

# ================= COMBINÉ =================
st.subheader("💰 Ticket IA PRO")

combo = [m for m in best if m.get("proba",0) > 70][:3]

for c in combo:
    st.write(f"✅ {c.get('match','?')} ({c.get('proba',0)}%)")
    st.write(f"👉 BTTS: {c.get('btts','NON')} | Over: {c.get('over','NON')}")

# ================= HISTORIQUE =================
st.subheader("📊 Historique IA")

try:
    df = pd.read_csv(DATA_FILE)
except:
    df = pd.DataFrame(columns=["match","prediction","result","win"])

st.dataframe(df)

if not df.empty:
    try:
        rate = (df["win"].sum() / len(df)) * 100
        st.write(f"📈 Performance IA: {round(rate,2)}%")
    except:
        st.write("Erreur calcul")

if st.button("🗑 Reset IA"):
    try:
        pd.DataFrame(columns=["match","prediction","result","win"]).to_csv(DATA_FILE, index=False)
        st.success("Reset effectué")
    except:
        st.error("Erreur reset")
