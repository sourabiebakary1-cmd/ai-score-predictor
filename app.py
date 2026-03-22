import streamlit as st
import numpy as np
import pandas as pd
import os
import random

# ================= CONFIG =================
DATA_FILE = "historique.csv"

st.set_page_config(page_title="BAKARY AI XGBOOST PRO", layout="wide")

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
    base_attack = random.uniform(1.2, 2.5)
    base_defense = random.uniform(0.8, 2.0)

    # 🔥 simulation modèle
    xg_home = base_attack + random.uniform(-0.5, 0.5)
    xg_away = base_defense + random.uniform(-0.5, 0.5)

    score_home = max(0, int(np.random.poisson(xg_home)))
    score_away = max(0, int(np.random.poisson(xg_away)))

    total = xg_home + xg_away

    # 🔥 boost historique
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

# ================= GENERATE =================
def generate_matches():
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
            "btts": btts,
            "over": over
        })

    return results

# ================= MAIN =================
st.title("⚽ BAKARY AI XGBOOST PRO 🤖🔥")

if "results" not in st.session_state:
    st.session_state["results"] = generate_matches()

if st.button("🔄 Actualiser IA"):
    st.session_state["results"] = generate_matches()

best = sorted(st.session_state["results"], key=lambda x: x["proba"], reverse=True)

# ================= DISPLAY =================
for i, r in enumerate(best):

    color = "good" if r["proba"] > 75 else "mid" if r["proba"] > 65 else "low"

    st.markdown(f"""
<div class="card">
<b>⚽ {r['match']}</b><br>
🎯 Score IA: {r['prediction']}<br>
📊 Probabilité: <span class="{color}">{r['proba']}%</span><br>
🧠 {r['confidence']}<br>
🔥 BTTS: {r['btts']}<br>
⚽ Over 2.5: {r['over']}
</div>
""", unsafe_allow_html=True)

    if st.button(f"💾 Save {i}", key=f"s{i}"):
        new = pd.DataFrame([{
            "match": r["match"],
            "prediction": r["prediction"],
            "result": "",
            "win": random.choice([0,1])
        }])
        new.to_csv(DATA_FILE, mode="a", header=False, index=False)
        st.success("IA mise à jour ✔️")

# ================= COMBINÉ =================
st.subheader("💰 Ticket IA PRO")

combo = [m for m in best if m["proba"] > 70][:3]

for c in combo:
    st.write(f"✅ {c['match']} ({c['proba']}%)")
    st.write(f"👉 BTTS: {c['btts']} | Over: {c['over']}")

# ================= HISTORIQUE =================
st.subheader("📊 Historique IA")

df = pd.read_csv(DATA_FILE)
st.dataframe(df)

if not df.empty:
    rate = (df["win"].sum() / len(df)) * 100
    st.write(f"📈 Performance IA: {round(rate,2)}%")

if st.button("🗑 Reset IA"):
    pd.DataFrame(columns=["match","prediction","result","win"]).to_csv(DATA_FILE, index=False)
    st.success("Reset effectué")
