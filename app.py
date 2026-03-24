import streamlit as st
import pandas as pd
import os
from scipy.stats import poisson
import urllib.parse

st.set_page_config(page_title="BAKARY AI ULTIMATE", layout="wide")

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

st.title("🔥 BAKARY AI ULTIMATE 🤖💎")

# ================= BASE =================
teams = {
    "Real Madrid": (2.0,1.0),"Barcelona": (1.9,1.1),"Man City": (2.2,0.9),
    "Liverpool": (1.8,1.2),"PSG": (2.1,1.1),"Arsenal": (1.7,1.2),
    "Chelsea": (1.5,1.3),"Bayern": (2.3,1.0),"Dortmund": (1.9,1.4)
}

# ================= DATA =================
data = load_data()

win_rate = 0.5
if len(data) > 0:
    win_rate = (data["result"] == "WIN").mean()

global_boost = 1 + (win_rate - 0.5)
st.info(f"🌍 Boost global: {round(global_boost,2)}")

# ================= TEAM LEARNING =================
team_stats = {}

for _, row in data.iterrows():
    for t in [row["team_home"], row["team_away"]]:
        if t not in team_stats:
            team_stats[t] = {"win":0,"total":0}
        team_stats[t]["total"] += 1
        if row["result"] == "WIN":
            team_stats[t]["win"] += 1

def team_boost(team):
    if team in team_stats and team_stats[team]["total"] > 2:
        rate = team_stats[team]["win"] / team_stats[team]["total"]
        return 1 + (rate - 0.5)
    return 1

# ================= MATCH FACILE =================
def is_easy_match(home, away):
    hf, ha = teams.get(home, (1.5,1.5))
    af, aa = teams.get(away, (1.5,1.5))

    if hf > 1.8 and aa > 1.3:
        return True
    if af > 1.8 and ha > 1.3:
        return True

    return False

# ================= IA =================
def analyse(home, away):

    hf, ha = teams.get(home, (1.5,1.5))
    af, aa = teams.get(away, (1.5,1.5))

    bh = team_boost(home)
    ba = team_boost(away)

    home_avg = ((hf + aa)/2)*bh
    away_avg = ((af + ha)/2)*ba

    matrix = [[poisson.pmf(i, home_avg)*poisson.pmf(j, away_avg)
               for j in range(6)] for i in range(6)]

    hw = sum(matrix[i][j] for i in range(6) for j in range(6) if i>j)
    aw = sum(matrix[i][j] for i in range(6) for j in range(6) if i<j)
    draw = sum(matrix[i][j] for i in range(6) for j in range(6) if i==j)

    over15 = sum(matrix[i][j] for i in range(6) for j in range(6) if i+j>=2)
    over25 = sum(matrix[i][j] for i in range(6) for j in range(6) if i+j>=3)

    options = {
        "Over 1.5": over15,
        "Over 2.5": over25,
        "Victoire Domicile": hw,
        "Victoire Extérieur": aw
    }

    best = max(options, key=options.get)
    conf = options[best] * global_boost
    conf_percent = round(conf*100,1)

    diff = abs(hw - aw)

    if diff < 0.1:
        risk = "PIÈGE ÉLEVÉ"
    elif draw > 0.28:
        risk = "MATCH BLOQUÉ"
    elif conf_percent > 70:
        risk = "FIABLE"
    elif conf_percent > 60:
        risk = "MOYEN"
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
safe_matches = []

for home, away in matchs:

    bet, conf, risk = analyse(home, away)

    if risk == "PIÈGE ÉLEVÉ":
        color = "bad"
    elif risk == "FIABLE":
        color = "good"
    else:
        color = "warn"

    st.markdown(f"""
    <div class="block">
    <h3>{home} vs {away}</h3>
    💰 {bet}<br>
    📊 {conf}%<br>
    ⚠️ <span class="{color}">{risk}</span>
    </div>
    """, unsafe_allow_html=True)

    results.append((home, away, bet, risk, conf))

    if risk == "FIABLE":
        safe_matches.append((home, away, bet, conf))

# ================= ULTRA SAFE =================
st.markdown("## 💎 MATCH ULTRA SÛR")

if safe_matches:
    best = max(safe_matches, key=lambda x: x[3])
    st.success(f"{best[0]} vs {best[1]} → {best[2]} ({best[3]}%)")
else:
    st.warning("Aucun match sûr")

# ================= PARI SÛR DIRECT =================
st.markdown("## 🎯 PARI SÛR DIRECT")

best_safe = None
best_score = 0

for home, away, bet, risk, conf in results:
    if risk == "FIABLE" and is_easy_match(home, away):
        if conf > best_score:
            best_score = conf
            best_safe = (home, away, bet, conf)

if best_safe:
    st.success(f"🔥 PARI SÛR: {best_safe[0]} vs {best_safe[1]} → {best_safe[2]} ({best_safe[3]}%)")
else:
    st.warning("❌ Aucun pari sûr aujourd'hui")

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

# ================= STATS =================
st.markdown("## 📊 STATS")

if len(data) > 0:
    win = (data["result"] == "WIN").sum()
    loss = (data["result"] == "LOSS").sum()
    total = win + loss
    rate = round(win/total*100,1) if total > 0 else 0

    st.success(f"Win: {win}")
    st.error(f"Loss: {loss}")
    st.info(f"Taux: {rate}%")
else:
    st.warning("Pas de données")

# ================= WHATSAPP =================
message = "🔥 BAKARY AI ULTIMATE 🔥\n\n"
for r in results:
    message += f"{r[0]} vs {r[1]} → {r[2]} ({r[3]})\n"

encoded = urllib.parse.quote(message)
link = f"https://wa.me/?text={encoded}"

st.markdown(f"[📲 Envoyer WhatsApp]({link})")
st.text_area("Message", message)
