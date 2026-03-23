import streamlit as st
from datetime import datetime

st.set_page_config(page_title="BAKARY AI PRO MAX (OVER ONLY)", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    color: white;
}
.card {
    background: #0b0b0b;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ================= TITRE =================
st.title("⚽🔥 BAKARY AI PRO MAX (OVER ONLY)")

# ================= DATE =================
today = datetime.now().strftime("%Y-%m-%d")
st.info(f"📅 Matchs du jour : {today}")

# ================= MATCHS (MANUEL) =================
matches = [
    {"match": "Liverpool vs Chelsea", "confidence": 85},
    {"match": "Barcelona vs Real Madrid", "confidence": 82},
    {"match": "PSG vs Marseille", "confidence": 80},
]

# ================= TOP MATCHS =================
st.subheader("💎 TOP MATCHS")

for m in matches:
    st.markdown(f"""
    <div class="card">
        ⚽ {m['match']} <br><br>
        🔥 OVER 2.5 <br><br>
        📊 Confiance: {m['confidence']}%
    </div>
    """, unsafe_allow_html=True)

# ================= MESSAGE WHATSAPP =================
message = "🔥 PRONOSTICS OVER 2.5 🔥\n\n"

for m in matches:
    message += f"{m['match']} → OVER 2.5 ({m['confidence']}%)\n"

# ================= WHATSAPP =================
st.subheader("📲 ENVOYER AUX CLIENTS")

whatsapp_link = f"https://wa.me/22607093407?text={message}"
st.markdown(f"[📤 Envoyer sur WhatsApp]({whatsapp_link})")

# ================= COPIER MESSAGE =================
st.text_area("📋 Copier message", message)

# ================= VIP =================
st.subheader("💰 ACCÈS VIP")

code = st.text_input("Entrer code VIP")

if code == "1234":
    st.success("✅ Accès VIP activé")
else:
    st.warning("🔒 Accès limité")
