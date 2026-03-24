import streamlit as st
import pandas as pd
import os
from scipy.stats import poisson

st.set_page_config(page_title="BAKARY AI PRO", layout="wide")

DATA_FILE = "data.csv"

# ================= STYLE PRO =================
st.markdown("""
<style>
body {background-color: #0e1117;}
.stApp {background-color: #0e1117; color: white;}
h1, h2, h3 {color: #00ffcc;}
</style>
""", unsafe_allow_html=True)

# ================= INIT DATA =================
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=[
        "match", "team_home", "team_away", "bet", "result"
    ]).to_csv(DATA_FILE, index=False)

# ================= MENU =================
menu = st.sidebar.radio("📊 MENU", [
    "🏠 Accueil", "⚽ Matchs IA", "🎟 Coupon", "➕ Ajouter", "📊 Stats"
])

# ================= ACCUEIL =================
if menu == "🏠 Accueil":
    st.title("🔥 BAKARY AI PRO")
    st.subheader("Robot intelligent de prédiction football")

    st.info("💡 Ajoute tes matchs et laisse l'IA analyser")

# ================= MATCHS IA =================
elif menu == "⚽ Matchs IA":
    st.title("⚽ Matchs & Prédictions")

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        st.warning("⚠️ Aucun match ajouté")
    else:
        st.dataframe(df)

        st.subheader("🔮 Prédictions IA")

        predictions = []

        for i, row in df.iterrows():
            home = row["team_home"]
            away = row["team_away"]

            # IA améliorée (simulation + logique)
            home_goals = poisson.rvs(mu=1.6)
            away_goals = poisson.rvs(mu=1.2)

            if home_goals > away_goals:
                pred = "1"
                text = f"✅ {home} gagne"
            elif home_goals < away_goals:
                pred = "2"
                text = f"✅ {away} gagne"
            else:
                pred = "X"
                text = "⚖️ Match nul"

            predictions.append(pred)

            st.success(f"{home} vs {away} → {text}")

        # STOCKAGE PREDICTIONS
        st.session_state["predictions"] = predictions

# ================= COUPON =================
elif menu == "🎟 Coupon":
    st.title("🎟 Coupon automatique")

    if "predictions" in st.session_state:
        preds = st.session_state["predictions"]

        st.subheader("💰 Ton coupon généré")

        for i, p in enumerate(preds):
            st.write(f"Match {i+1} → {p}")

        st.success("🔥 Coupon prêt !")
    else:
        st.warning("⚠️ Va dans Matchs IA pour générer")

# ================= AJOUTER =================
elif menu == "➕ Ajouter":
    st.title("➕ Ajouter un match")

    col1, col2 = st.columns(2)

    with col1:
        home = st.text_input("Équipe domicile")

    with col2:
        away = st.text_input("Équipe extérieur")

    if st.button("Ajouter le match"):
        if home and away:
            new_data = pd.DataFrame([{
                "match": f"{home} vs {away}",
                "team_home": home,
                "team_away": away,
                "bet": "",
                "result": ""
            }])

            new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.success("✅ Match ajouté")
        else:
            st.error("❌ Remplis tous les champs")

# ================= STATS =================
elif menu == "📊 Stats":
    st.title("📊 Statistiques")

    df = pd.read_csv(DATA_FILE)

    st.metric("Nombre de matchs", len(df))

    if not df.empty:
        st.dataframe(df.tail(5))
