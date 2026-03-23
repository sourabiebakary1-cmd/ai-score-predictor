import streamlit as st
import pandas as pd
import os
from scipy.stats import poisson
import urllib.parse

st.set_page_config(page_title="BAKARY AI GOD MODE", layout="wide")

DATA_FILE = "data.csv"

# ================= FILE =================
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["match","team_home","team_away","bet","result"]).to_csv(DATA_FILE, index=False)

def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except:
        return pd.DataFrame(columns=["match","team_home","team_away","bet","result"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# ================= STYLE =================
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#0f2027,#203a43,#2c5364); color:white;}
.block {background:#111;padding:15px;border-radius:15px;margin-bottom:10px;}
.good {color:#00ffcc;}
.bad {color:#ff4d4d;}
.warn {color:#ffaa00;}
</style>
""", unsafe_allow_html=True)

st.title("🔥 BAKARY AI GOD MODE 😈💎")

# ================= BASE =================
teams = {
    "Real Madrid": (2.0,1.0),"Barcelona": (1.9,1.1),"Man City": (2.2,0.9),
    "Liverpool": (1.8,1.2),"PSG": (2.1,1.1),"Arsenal": (1.7,1.2),
    "Chelsea": (1.5,1.3),"Bayern": (2.3,1.0),"Dortmund": (1.9,1.4)
}

data = load_data()

# ================= BOOST GLOBAL =================
win_rate = 0.5
if len(data) > 0:
    win_rate = (data["result"] == "WIN").mean()

global_boost = 1 + (win_rate - 0.5)
st.info(f"🌍 Boost IA: {round(global_boost,2)}")

# ================= IA AUTO-CORRECTION =================
bet_history = data.groupby("bet")["result"].apply(list).to_dict()

def adjust_prob(bet, prob):
    if bet in bet_history and len(bet_history[bet]) > 5:
        wins = bet_history[bet].count("WIN")
        rate = wins / len(bet_history[bet])
        return prob * (1 + (rate - 0.5))
    return prob

# ================= TEAM LEARNING =================
team_stats = {}

for _, row in data.iterrows():
    for t in [row["team_home"], row["team_away"]]:
        if t not in team_stats:
            team_stats[t] = {"attack":1,"defense":1,"win":0,"total":0}

        team_stats[t]["total"] += 1

        if row["result"] == "WIN":
            team_stats[t]["win"] += 1
            team_stats[t]["attack"] += 0.05
        else:
            team_stats[t]["defense"] += 0.05

def get_boost(team):
    if team in team_stats and team_stats[team]["total"] > 2:
        atk = team_stats[team]["attack"]
        dfc = team_stats[team]["defense"]
        wr = team_stats[team]["win"]/team_stats[team]["total"]
        return atk*(1+(wr-0.5)), dfc
    return 1,1

# ================= IA =================
def analyse(home, away):

    hf, ha = teams.get(home, (1.5,1.5))
    af, aa = teams.get(away, (1.5,1.5))

    bh_atk, bh_def = get_boost(home)
    ba_atk, ba_def = get_boost(away)

    home_avg = ((hf*bh_atk)+(aa*ba_def))/2
    away_avg = ((af*ba_atk)+(ha*bh_def))/2

    matrix = [[poisson.pmf(i, home_avg)*poisson.pmf(j, away_avg)
               for j in range(6)] for i in range(6)]

    hw = sum(matrix[i][j] for i in range(6) for j in range(6) if i>j)
    aw = sum(matrix[i][j] for i in range(6) for j in range(6) if i<j)
    draw = sum(matrix[i][j] for i in range(6) for j in range(6) if i==j)

    over15 = sum(matrix[i][j] for i in range(6) for j in range(6) if i+j>=2)
    over25 = sum(matrix[i][j] for i in range(6) for j in range(6) if i+j>=3)
    btts = sum(matrix[i][j] for i in range(1,6) for j in range(1,6))

    # 🔥 IA correction appliquée
    options = {
        "Over 1.5": adjust_prob("Over 1.5", over15),
        "Over 2.5": adjust_prob("Over 2.5", over25),
        "BTTS OUI": adjust_prob("BTTS OUI", btts),
        "Victoire Domicile": adjust_prob("Victoire Domicile", hw),
        "Victoire Extérieur": adjust_prob("Victoire Extérieur", aw)
    }

    best = max(options, key=options.get)

    conf = min(options[best]*global_boost,0.95)
    conf_percent = round(conf*100,1)

    diff = abs(hw-aw)

    if diff < 0.07:
        risk = "GROS PIÈGE"
    elif draw > 0.32:
        risk = "MATCH BLOQUÉ"
    elif conf_percent > 78:
        risk = "ULTRA FIABLE"
    elif conf_percent > 68:
        risk = "FIABLE"
    else:
        risk = "RISQUÉ"

    return best, conf_percent, risk

# ================= INPUT =================
st.sidebar.title("⚙️ AJOUT MATCH")

matchs = []
for i in range(4):
    home = st.sidebar.text_input(f"Domicile {i+1}", key=f"h{i}")
    away = st.sidebar.text_input(f"Extérieur {i+1}", key=f"a{i}")

    if home and away:
        matchs.append((home, away))

# ================= ANALYSE =================
results = []

for home, away in matchs:

    bet, conf, risk = analyse(home, away)

    # 🔥 ANTI PERTE
    if conf < 65 or "PIÈGE" in risk or "RISQUÉ" in risk:
        st.error(f"❌ {home} vs {away} BLOQUÉ (risque)")
        continue

    # 🔥 BANKROLL
    if conf > 80:
        stake = "5%"
    elif conf > 70:
        stake = "3%"
    else:
        stake = "1%"

    color = "good" if "FIABLE" in risk else "warn"

    st.markdown(f"""
    <div class="block">
    <h3>{home} vs {away}</h3>
    💰 {bet}<br>
    📊 {conf}%<br>
    📦 Mise: {stake}<br>
    ⚠️ <span class="{color}">{risk}</span>
    </div>
    """, unsafe_allow_html=True)

    results.append((home, away, bet, risk, conf))

# ================= PARI DU JOUR =================
st.markdown("## 🤖 PARI DU JOUR")

best_day = None
best_score = 0

for r in results:
    if r[4] > best_score:
        best_score = r[4]
        best_day = r

if best_day:
    st.success(f"🔥 {best_day[0]} vs {best_day[1]} → {best_day[2]} ({best_day[4]}%)")
else:
    st.warning("❌ Aucun bon pari")

# ================= SAVE =================
st.markdown("## ✅ ENREGISTRER")

for i, r in enumerate(results):
    res = st.selectbox(f"{r[0]} vs {r[1]}", ["WIN","LOSS"], key=f"res{i}")

    if st.button(f"Sauver {i}", key=f"btn{i}"):
        new = pd.DataFrame([{
            "match": f"{r[0]} vs {r[1]}",
            "team_home": r[0],
            "team_away": r[1],
            "bet": r[2],
            "result": res
        }])
        data = pd.concat([data, new], ignore_index=True)
        save_data(data)
        st.success("✅ Sauvegardé")
