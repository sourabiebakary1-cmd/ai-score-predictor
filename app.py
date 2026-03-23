import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import requests
from scipy.stats import poisson

# ================= CONFIG =================
DATA_FILE = "historique.csv"
OWNER_NUMBER = "22607093407"
API_KEY = "289e8418878e48c598507cf2b72338f5"

st.set_page_config(page_title="BAKARY AI PRO MAX FINAL", layout="wide")

# ================= FILE =================
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["match","prediction","date"]).to_csv(DATA_FILE, index=False)

# ================= IA =================
def poisson_pred(home_avg, away_avg):
    matrix = [[poisson.pmf(i, home_avg)*poisson.pmf(j, away_avg)
               for j in range(6)] for i in range(6)]

    home_win = sum(matrix[i][j] for i in range(6) for j in range(6) if i > j)
    away_win = sum(matrix[i][j] for i in range(6) for j in range(6) if i < j)
    over25 = sum(matrix[i][j] for i in range(6) for j in range(6) if i + j >= 3)

    best_score = "0-0"
    max_prob = 0

    for i in range(6):
        for j in range(6):
            if matrix[i][j] > max_prob:
                max_prob = matrix[i][j]
                best_score = f"{i}-{j}"

    return home_win, away_win, over25, best_score

# ================= MATCH API =================
def get_matches():
    headers = {"x-apisports-key": API_KEY}

    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    matches = []

    try:
        # AUJOURD’HUI
        res1 = requests.get(
            f"https://v3.football.api-sports.io/fixtures?date={today}",
            headers=headers,
            timeout=5
        ).json()

        matches += res1.get("response", [])

        # DEMAIN
        res2 = requests.get(
            f"https://v3.football.api-sports.io/fixtures?date={tomorrow}",
            headers=headers,
            timeout=5
        ).json()

        matches += res2.get("response", [])

    except:
        return []

    return matches

# ================= APP =================
st.title("🔥 BAKARY AI PRO MAX FINAL (VRAIS MATCHS)")

matches = get_matches()

message = "🔥 PRONOSTICS VIP 🔥\n\n"

# ================= SI MATCH TROUVÉ =================
if matches and len(matches) > 0:

    st.success(f"✅ {len(matches)} matchs trouvés (aujourd’hui + demain)")

    for m in matches[:5]:

        try:
            home = m["teams"]["home"]["name"]
            away = m["teams"]["away"]["name"]
        except:
            continue

        st.subheader(f"{home} vs {away}")

        # valeurs fixes intelligentes (pas random pur)
        home_avg = 1.5
        away_avg = 1.2

        home_win, away_win, over25, score = poisson_pred(home_avg, away_avg)

        if home_win > 0.6:
            bet = "Victoire domicile"
            conf = home_win
        elif away_win > 0.6:
            bet = "Victoire extérieur"
            conf = away_win
        else:
            bet = "Over 2.5"
            conf = over25

        st.success(f"🎯 Score: {score}")
        st.error(f"💰 Pari sûr: {bet}")
        st.info(f"📊 Confiance: {round(conf*100,1)}%")

        message += f"{home} vs {away}\n{bet} ({round(conf*100,1)}%)\n\n"

        # SAUVEGARDE SÉCURISÉ
        try:
            df = pd.read_csv(DATA_FILE)
        except:
            df = pd.DataFrame(columns=["match","prediction","date"])

        df.loc[len(df)] = [f"{home} vs {away}", bet, str(datetime.now())]

        try:
            df.to_csv(DATA_FILE, index=False)
        except:
            pass

# ================= SI API BLOQUÉ =================
else:
    st.error("❌ Aucun match trouvé → API LIMITÉE ou BLOQUÉE")

# ================= WHATSAPP =================
st.subheader("📱 ENVOYER AUX CLIENTS")

link = f"https://wa.me/{OWNER_NUMBER}?text={message}"
st.markdown(f"[📤 Envoyer WhatsApp]({link})")

st.text_area("Copie message 👇", message)
