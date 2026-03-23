import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="BAKARY AI PRO MAX (OVER)", layout="wide")

API_KEY = "TA_CLE_API"

st.title("🔥 BAKARY AI PRO MAX (OVER 2.5 ONLY)")

today = datetime.now().strftime("%Y-%m-%d")

url = f"https://v3.football.api-sports.io/fixtures?date={today}"

headers = {
    "x-apisports-key": API_KEY
}

# ================= STYLE =================
st.markdown("""
<style>
.card {
    background: #0e1117;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 10px;
}
.safe {color: #00ff99;}
.danger {color: red;}
</style>
""", unsafe_allow_html=True)

# ================= FETCH =================
try:
    res = requests.get(url, headers=headers)
    data = res.json()
    matches = data.get("response", [])

    if not matches:
        st.warning("⚠️ Aucun match aujourd’hui ou API limitée")
    else:
        st.success(f"✅ {len(matches)} matchs trouvés")

        safe_matches = []

        for match in matches:

            if match["fixture"]["status"]["short"] != "NS":
                continue

            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]
            league = match["league"]["name"]

            # ================= IA OVER =================
            # (simulation intelligente sans random)
            goals_avg = 2.8  # moyenne générale football

            if "Premier League" in league:
                confidence = 75
            elif "La Liga" in league:
                confidence = 72
            elif "Serie A" in league:
                confidence = 70
            else:
                confidence = 65

            # filtrage
            if confidence >= 70:
                safe_matches.append((home, away, confidence))

        # ================= AFFICHAGE =================
        st.markdown("## 💎 TOP MATCHS OVER")

        if not safe_matches:
            st.warning("❌ Aucun match fiable aujourd’hui")
        else:
            for m in safe_matches[:5]:
                st.markdown(f"""
                <div class="card">
                ⚽ {m[0]} vs {m[1]}<br>
                🔥 OVER 2.5<br>
                📊 Confiance : <span class="safe">{m[2]}%</span>
                </div>
                """, unsafe_allow_html=True)

# ================= WHATSAPP =================
            st.markdown("## 📲 ENVOYER AUX CLIENTS")

            msg = "🔥 PRONOSTICS OVER 2.5 🔥\n\n"

            for m in safe_matches[:3]:
                msg += f"{m[0]} vs {m[1]} → OVER 2.5 ({m[2]}%)\n"

            st.text_area("Copie message", msg)

except:
    st.error("❌ Problème API - Vérifie ta clé")
