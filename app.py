import streamlit as st
import numpy as np
import pandas as pd
import os
import random
from datetime import datetime, timedelta
import json

# ================= CONFIG =================
DATA_FILE = "historique.csv"
CODES_FILE = "codes.json"
OWNER_NUMBER = "07000000"

# ================= INIT FILES =================
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["match","prediction","result","win"]).to_csv(DATA_FILE, index=False)

if not os.path.exists(CODES_FILE):
    with open(CODES_FILE, "w") as f:
        json.dump({
            "VIP123": {"BAKARY2026"},
            "VIP456": {"BAKARY2026"},
            "VIP789": {"BAKARY2026"}
        }, f)

# ================= LOAD DATA =================
def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except:
        return pd.DataFrame(columns=["match","prediction","result","win"])

def load_codes():
    try:
        with open(CODES_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_codes(codes):
    with open(CODES_FILE, "w") as f:
        json.dump(codes, f)

# ================= SESSION =================
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if "expire_date" not in st.session_state:
    st.session_state["expire_date"] = None

# ================= PAIEMENT =================
def paiement():
    st.title("💰 ACCÈS VIP ORANGE MONEY")

    st.info(f"📲 Envoie 2000 FCFA au : {OWNER_NUMBER}")

    numero = st.text_input("📱 Ton numéro")
    transaction = st.text_input("🧾 ID Transaction")
    code = st.text_input("🔑 Code VIP", type="password")

    if st.button("Valider paiement"):

        if not numero or not transaction or not code:
            st.warning("⚠️ Remplis tous les champs")
            return

        codes = load_codes()

        if code in codes and not codes[code]["used"]:
            codes[code]["used"] = True
            save_codes(codes)

            st.session_state["auth"] = True
            st.session_state["expire_date"] = datetime.now() + timedelta(days=30)

            st.success("✅ Accès activé")
        else:
            st.error("❌ Code invalide ou déjà utilisé")

# 🔒 BLOQUAGE
if not st.session_state["auth"]:
    paiement()
    st.stop()

# 🔒 EXPIRATION
if datetime.now() > st.session_state["expire_date"]:
    st.error("⛔ Abonnement expiré")
    st.stop()

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
        return 1,1,60,"ERREUR","NON","NON"

def is_trap_match(proba, sh, sa):
    return proba > 80 and (sh >= 4 or sa >= 4)

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

# ================= APP =================
st.title("⚽ BAKARY AI PRO MAX ULTIME 🔥")

if st.button("🔄 Actualiser IA"):
    st.session_state["results"] = generate_matches()

if "results" not in st.session_state:
    st.session_state["results"] = generate_matches()

best = sorted(st.session_state["results"], key=lambda x: x["proba"], reverse=True)

for r in best:
    st.write(f"⚽ {r['match']} | 🎯 {r['prediction']} | 📊 {r['proba']}% | {r['confidence']}")

# ================= HISTORIQUE =================
st.subheader("📊 Historique")
df = load_data()
st.dataframe(df)
