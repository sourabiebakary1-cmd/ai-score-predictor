import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from xgboost import XGBClassifier
from scipy.stats import poisson

st.set_page_config(page_title="BAKARY AI PRO MAX", layout="wide")

st.title("⚽ BAKARY AI PRO MAX 🔥🧠💰")

# ================= CONFIG =================
bankroll = st.sidebar.number_input("💰 Bankroll", value=10000)
date = st.sidebar.date_input("📅 Date", datetime.today())

# ================= DATASET =================
@st.cache_data
def create_dataset():
    np.random.seed(42)

    df = pd.DataFrame({
        "home_goals": np.random.randint(0, 4, 500),
        "away_goals": np.random.randint(0, 4, 500),
    })

    df["total"] = df["home_goals"] + df["away_goals"]
    df["over25"] = (df["total"] > 2).astype(int)

    st.write("📊 Dataset:", len(df))
    return df

df = create_dataset()

# ================= MODEL =================
@st.cache_resource
def train_model(df):
    X = df[["home_goals","away_goals","total"]]
    y = df["over25"]

    model = XGBClassifier(n_estimators=120)
    model.fit(X, y)

    return model

model = train_model(df)

# ================= MATCHS SIMULÉS =================
def get_matches():
    teams = [
        "Real Madrid", "Barcelona", "Arsenal", "Chelsea",
        "PSG", "Bayern", "Juventus", "Milan",
        "Liverpool", "Man City"
    ]

    matches = []

    for i in range(6):
        home = np.random.choice(teams)
        away = np.random.choice(teams)

        if home != away:
            matches.append({
                "teams": {
                    "home": {"name": home, "id": np.random.randint(1,100)},
                    "away": {"name": away, "id": np.random.randint(1,100)}
                }
            })

    return matches

# ================= FEATURES =================
def compute_features(home_id, away_id):
    h_for = (home_id % 3) + np.random.uniform(0.8, 1.5)
    a_for = (away_id % 3) + np.random.uniform(0.8, 1.5)
    total = h_for + a_for
    return h_for, a_for, total

# ================= SCORE =================
def predict_score(home_xg, away_xg):
    best = (0, 0)
    max_prob = 0

    for i in range(5):
        for j in range(5):
            prob = poisson.pmf(i, home_xg) * poisson.pmf(j, away_xg)
            if prob > max_prob:
                max_prob = prob
                best = (i, j)

    return best

# ================= ANALYSE =================
matches = get_matches()
results = []

for m in matches:
    try:
        home = m["teams"]["home"]["name"]
        away = m["teams"]["away"]["name"]

        home_id = m["teams"]["home"]["id"]
        away_id = m["teams"]["away"]["id"]

        h_for, a_for, total = compute_features(home_id, away_id)

        prob = model.predict_proba([[h_for, a_for, total]])[0][1]
        score = predict_score(h_for, a_for)

        if prob > 0.65 and total > 2.3:
            results.append({
                "match": f"{home} vs {away}",
                "score": f"{score[0]}-{score[1]}",
                "prob": round(prob*100,2),
                "btts": "OUI" if h_for > 1 and a_for > 1 else "NON",
                "over25": "OUI" if total > 2.5 else "NON"
            })

    except:
        continue

# ================= AFFICHAGE =================
if not results:
    st.warning("⚠️ Aucun match fort → Regénère")
else:
    st.success(f"🔥 {len(results)} MATCHS FIABLES")

    for r in results:
        st.markdown(f"""
### ⚽ {r['match']}
- 🎯 Score : **{r['score']}**
- 📊 Probabilité : **{r['prob']}%**
- 🔥 BTTS : **{r['btts']}**
- ⚽ Over 2.5 : **{r['over25']}**
""")

# ================= BANKROLL =================
if results:
    stake = bankroll * 0.03
    st.sidebar.write(f"💡 Mise conseillée : {int(stake)} FCFA")

# ================= UI PRO =================
if st.button("🔄 Générer nouveaux matchs"):
    st.rerun()

st.sidebar.markdown("### 🧠 Conseils PRO")
st.sidebar.write("✔ Jouer 2-3 matchs max")
st.sidebar.write("✔ Éviter les petites cotes")
st.sidebar.write("✔ Discipline = profit 💰")
