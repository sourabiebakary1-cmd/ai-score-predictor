import streamlit as st
import numpy as np
import pandas as pd
import os
import random
import datetime
import requests

# ================= CONFIG =================
DATA_FILE = "historique.csv"

# 🔥 REMPLACE PAR TON LIEN FIREBASE
FIREBASE_URL = "https://TON-PROJET.firebaseio.com/users.json"

st.set_page_config(page_title="BAKARY AI VIP 🔥", layout="wide")
st.set_option('client.showErrorDetails', False)

# ================= 🔐 VIP FIREBASE =================
def check_vip(code):
    try:
        res = requests.get(FIREBASE_URL)
        data = res.json()

        if not data or code not in data:
            return False, "⛔ Code invalide"

        expiry = datetime.datetime.strptime(data[code]["expiry"], "%Y-%m-%d")

        if datetime.datetime.now() > expiry:
            return False, "❌ Abonnement expiré"

        return True, "✅ Accès VIP activé 🔥"

    except:
        return False, "⚠️ Erreur connexion serveur"

code = st.text_input("🔐 Entrer votre code VIP", type="password")

valid, message = check_vip(code)

if not valid:
    st.warning(message)
    st.stop()

st.success(message)

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

def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except:
        return pd.DataFrame(columns=["match","prediction","result","win"])

# ================= BANKROLL =================
if "bankroll" not in st.session_state:
    st.session_state["bankroll"] = 10000

def bet_strategy(proba):
    if proba > 80:
        return 0.08
    elif proba > 70:
        return 0.05
    else:
        return 0.02

# ================= IA =================
def get_form_boost():
    df = load_data()
    if len(df) < 10:
        return 0
    try:
        rate = df["win"].sum() / len(df)
        return max(min((rate - 0.5) * 15, 8), -8)
    except:
        return 0

def xgboost_predict():
    try:
        form = get_form_boost()

        xg_home = np.clip(random.uniform(0.8, 2.2) + form/30, 0.5, 3)
        xg_away = np.clip(random.uniform(0.7, 2.0), 0.5, 3)

        score_home = min(int(np.random.poisson(xg_home)), 4)
        score_away = min(int(np.random.poisson(xg_away)), 4)

        total = score_home + score_away

        proba = np.clip(((xg_home + xg_away)/4)*100 + form, 55, 85)

        btts = "OUI" if score_home > 0 and score_away > 0 else "NON"
        over = "OUI" if total >= 3 else "NON"

        if proba > 78:
            conf = "🟢 IA FORTE"
        elif proba > 68:
            conf = "🟡 IA MOYENNE"
        else:
            conf = "🔴 IA RISQUE"

        return score_home, score_away, round(proba,2), conf, btts, over

    except:
        return 1,1,60,"🔴 ERREUR","NON","NON"

def is_trap(proba, sh, sa):
    return proba > 80 and (sh >= 4 or sa >= 4)

# ================= MATCHS =================
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
            "score_home": sh,
            "score_away": sa,
            "proba": proba,
            "confidence": conf,
            "btts": btts,
            "over": over
        })

    return results

# ================= MAIN =================
st.title("⚽ BAKARY AI VIP 🤖💰")
st.subheader(f"💰 Bankroll: {st.session_state['bankroll']} FCFA")

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

    if is_trap(r["proba"], r["score_home"], r["score_away"]):
        st.warning("⚠️ MATCH RISQUÉ")

    mise = int(st.session_state["bankroll"] * bet_strategy(r["proba"]))
    st.write(f"💸 Mise conseillée: {mise} FCFA")

    if st.button(f"💾 Sauvegarder {i}", key=f"s{i}"):
        df = load_data()
        new = {
            "match": r["match"],
            "prediction": r["prediction"],
            "result": "",
            "win": random.choice([0,1])
        }
        df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success("✅ Sauvegardé")

# ================= HISTORIQUE =================
st.subheader("📊 Historique")

df = load_data()
st.dataframe(df)

if not df.empty:
    rate = (df["win"].sum()/len(df))*100
    st.write(f"📈 Performance: {round(rate,2)}%")
