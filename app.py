import streamlit as st
import requests
from datetime import datetime
from scipy.stats import poisson
import urllib.parse

# ================= CONFIG =================
API_KEY = "289e8418878e48c598507cf2b72338f5"

st.set_page_config(page_title="BAKARY AI", layout="wide")

# ================= STYLE PRO =================
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

h1 {
    text-align: center;
    font-size: 40px;
}

h2, h3 {
    color: #00ffcc;
}

.block {
    background-color: #111;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 10px;
    box-shadow: 0px 0px 10px rgba(0,255,200,0.3);
}

.stButton>button {
    background: linear-gradient(45deg,#00ffcc,#00ccff);
    color: black;
    border-radius: 10px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# ================= LOGO =================
try:
    st.image("logo.png", width=120)
except:
    st.warning("Ajoute logo.png dans le dossier")

st.title("🔥 BAKARY AI PRO")

# ================= MENU =================
menu = st.sidebar.radio("📱 MENU", ["🏠 Accueil", "🎯 Pronostics", "📲 WhatsApp"])

# ================= POISSON =================
def poisson_pred(home_avg, away_avg):
    matrix = [[poisson.pmf(i, home_avg)*poisson.pmf(j, away_avg)
               for j in range(6)] for i in range(6)]

    over25 = sum(matrix[i][j] for i in range(6) for j in range(6) if i+j>=3)

    best_score = "0-0"
    max_prob = 0

    for i in range(6):
        for j in range(6):
            if matrix[i][j] > max_prob:
                max_prob = matrix[i][j]
                best_score = f"{i}-{j}"

    return over25, best_score

# ================= API =================
def get_matches():
    try:
        url = "https://v3.football.api-sports.io/fixtures?date=" + datetime.now().strftime("%Y-%m-%d")
        headers = {"x-apisports-key": API_KEY}
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code == 200:
            return res.json()["response"]
    except:
        st.warning("⚠️ Mode offline")

    return []

# ================= ACCUEIL =================
if menu == "🏠 Accueil":
    st.markdown("## 💎 Bienvenue")
    st.success("Application IA de pronostics football")
    st.info("Analyse intelligente + Match Ultra sûr 🔥")

# ================= PRONOSTICS =================
elif menu == "🎯 Pronostics":

    st.markdown("## 🎯 MATCHS DU JOUR")

    matches = get_matches()
    message = "🔥 PRONOSTICS 🔥\n\n"

    best_match = None
    best_conf = 0

    for m in matches[:5]:

        try:
            home = m["teams"]["home"]["name"]
            away = m["teams"]["away"]["name"]
        except:
            continue

        home_avg = 1.6
        away_avg = 1.2

        prob, score = poisson_pred(home_avg, away_avg)
        conf = round(prob * 100, 1)

        if conf < 65:
            continue

        st.markdown(f"""
        <div class="block">
        <h3>{home} vs {away}</h3>
        🎯 Score probable: {score}<br>
        📊 Confiance: {conf}%<br>
        💰 Pari: Over 2.5
        </div>
        """, unsafe_allow_html=True)

        message += f"{home} vs {away} → Over 2.5 ({conf}%)\n\n"

        if conf > best_conf:
            best_conf = conf
            best_match = f"{home} vs {away} ({conf}%)"

    st.markdown("## 💎 MATCH ULTRA SÛR")

    if best_match:
        st.success(best_match)
    else:
        st.warning("Aucun match fiable")

# ================= WHATSAPP =================
elif menu == "📲 WhatsApp":

    st.markdown("## 📲 ENVOYER PRONOSTICS")

    message = "🔥 PRONOSTICS BAKARY AI 🔥"

    encoded = urllib.parse.quote(message)
    link = f"https://wa.me/?text={encoded}"

    st.markdown(f"[📤 Envoyer WhatsApp]({link})")
    st.text_area("Message", message)
