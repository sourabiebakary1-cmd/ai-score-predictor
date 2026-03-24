import streamlit as st
import pandas as pd
import os
from scipy.stats import poisson
import urllib.parse

st.set_page_config(page_title="BAKARY AI FINAL PRO MAX", layout="wide")

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

def reset_data():
    pd.DataFrame(columns=["match","team_home","team_away","bet","result"]).to_csv(DATA_FILE, index=False)

# ================= UI =================
st.title("🔥 BAKARY AI FINAL PRO MAX 🤖")

bankroll = st.sidebar.number_input("💰 Budget", value=10000)

# ================= DATA =================
data = load_data()
win_rate = (data["result"]=="WIN").mean() if len(data)>0 else 0.5
global_boost = 1 + (win_rate - 0.5)

# ================= BASE =================
teams = {
    "Real Madrid": (2.0,1.0),"Barcelona": (1.9,1.1),
    "Man City": (2.2,0.9),"Liverpool": (1.8,1.2),
    "PSG": (2.1,1.1),"Arsenal": (1.7,1.2),
    "Chelsea": (1.5,1.3),"Bayern": (2.3,1.0),
    "Dortmund": (1.9,1.4)
}

form = {
    "Real Madrid":0.8,"Barcelona":0.7,"Man City":0.9,
    "Liverpool":0.75,"PSG":0.85,"Arsenal":0.7,
    "Chelsea":0.6,"Bayern":0.9,"Dortmund":0.7
}

# ================= IA (NOUVEL ALGORITHME INTÉGRÉ) =================
def analyse(home, away):

    if home not in teams or away not in teams:
        return "❌ Données insuffisantes",0,"❌ ÉVITER",(0,0)

    hf, ha = teams[home]
    af, aa = teams[away]

    f1 = form.get(home,0.5)
    f2 = form.get(away,0.5)

    home_avg = ((hf+aa)/2)*(1+f1)
    away_avg = ((af+ha)/2)*(1+f2)

    matrix = [[poisson.pmf(i,home_avg)*poisson.pmf(j,away_avg)
               for j in range(6)] for i in range(6)]

    hw = sum(matrix[i][j] for i in range(6) for j in range(6) if i>j)
    aw = sum(matrix[i][j] for i in range(6) for j in range(6) if i<j)
    draw = sum(matrix[i][j] for i in range(6) for j in range(6) if i==j)

    total_goals = home_avg + away_avg

    over25 = sum(matrix[i][j] for i in range(6) for j in range(6) if i+j>=3)
    btts = sum(matrix[i][j] for i in range(1,6) for j in range(1,6))

    # Score exact
    best_score = max([(i,j,matrix[i][j]) for i in range(6) for j in range(6)], key=lambda x:x[2])

    # Score intelligent
    score = 0
    if abs(hw - aw) > 0.25:
        score += 2
    if draw < 0.25:
        score += 1
    if total_goals > 2.5:
        score += 1
    if over25 > 0.6:
        score += 1
    if btts > 0.55:
        score += 1

    options = {
        "Over 2.5": over25,
        "BTTS": btts,
        "Victoire Domicile": hw,
        "Victoire Extérieur": aw
    }

    best = max(options, key=options.get)
    conf = round(options[best] * global_boost * 100, 1)

    # Décision intelligente
    if abs(hw - aw) < 0.1:
        decision = "❌ PIÈGE"
    elif score >= 5 and conf > 75:
        decision = "💎 JOUER FORT"
    elif score >= 3 and conf > 65:
        decision = "✅ JOUER"
    else:
        decision = "❌ ÉVITER"

    return best, conf, decision, (best_score[0], best_score[1])

# ================= MISE =================
def stake(conf):
    if conf>80:
        return int(bankroll*0.1)
    elif conf>70:
        return int(bankroll*0.07)
    else:
        return int(bankroll*0.03)

# ================= INPUT =================
st.sidebar.title("⚙️ MATCHS")

matchs=[]
for i in range(5):
    h=st.sidebar.text_input(f"Home {i}",key=f"h{i}")
    a=st.sidebar.text_input(f"Away {i}",key=f"a{i}")
    if h and a:
        matchs.append((h,a))

# ================= ANALYSE =================
results=[]
for home,away in matchs:

    bet,conf,decision,score=analyse(home,away)
    mise=stake(conf)

    st.write(f"### {home} vs {away}")
    st.write(f"💰 {bet}")
    st.write(f"📊 {conf}%")
    st.write(f"🎯 {score[0]} - {score[1]}")
    st.write(f"🚀 {decision}")
    st.write(f"💵 Mise: {mise}")

    results.append((home,away,bet,conf))

# ================= BEST =================
st.write("## 💎 MEILLEUR MATCH")

safe=[r for r in results if r[3]>70]

if safe:
    best=max(safe,key=lambda x:x[3])
    st.success(f"{best[0]} vs {best[1]} → {best[2]} ({best[3]}%)")
else:
    st.warning("Aucun bon match")

# ================= RESET =================
if st.sidebar.button("RESET"):
    reset_data()
    st.success("Reset OK")

# ================= WHATSAPP =================
msg="BAKARY AI PRO MAX\n\n"
for r in results:
    msg+=f"{r[0]} vs {r[1]} → {r[2]} ({r[3]}%)\n"

link="https://wa.me/?text="+urllib.parse.quote(msg)

st.markdown(f"[Envoyer WhatsApp]({link})")
st.text_area("Message", msg)
