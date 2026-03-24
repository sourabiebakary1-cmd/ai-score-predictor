import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="BAKARY AI PRO", layout="wide")

DATA_FILE = "data.csv"

# ================= STYLE PRO =================
st.markdown("""
<style>
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
    st.info("💡 Ajoute tes matchs + résultats pour activer une vraie IA")

# ================= MATCHS IA =================
elif menu == "⚽ Matchs IA":
    st.title("⚽ Matchs & Prédictions IA")

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        st.warning("⚠️ Aucun match ajouté")
    else:
        st.dataframe(df)

        st.subheader("🔮 Analyse intelligente")

        predictions = []

        # ================= IA BASEE SUR RESULTATS =================
        team_stats = {}

        for _, row in df.iterrows():
            home = row["team_home"]
            away = row["team_away"]
            result = str(row["result"]).strip()

            if home not in team_stats:
                team_stats[home] = 1
            if away not in team_stats:
                team_stats[away] = 1

            if result == "1":
                team_stats[home] += 3
            elif result == "2":
                team_stats[away] += 3
            elif result == "X":
                team_stats[home] += 1
                team_stats[away] += 1

        # ================= PREDICTION =================
        for _, row in df.iterrows():
            home = row["team_home"]
            away = row["team_away"]

            score_home = team_stats.get(home, 1)
            score_away = team_stats.get(away, 1)

            total = score_home + score_away

            prob_home = int((score_home / total) * 100)
            prob_away = int((score_away / total) * 100)

            if prob_home > prob_away:
                pred = "1"
                text = f"✅ {home} gagne ({prob_home}%)"
            elif prob_home < prob_away:
                pred = "2"
                text = f"✅ {away} gagne ({prob_away}%)"
            else:
                pred = "X"
                text = "⚖️ Match nul (50%)"

            predictions.append(pred)

            st.success(f"{home} vs {away} → {text}")

        st.session_state["predictions"] = predictions

# ================= COUPON =================
elif menu == "🎟 Coupon":
    st.title("🎟 Coupon automatique")

    if "predictions" in st.session_state:
        preds = st.session_state["predictions"]

        st.subheader("💰 Ton coupon")

        for i, p in enumerate(preds):
            st.write(f"Match {i+1} → {p}")

        st.success("🔥 Coupon prêt !")
    else:
        st.warning("⚠️ Génère d'abord les prédictions")

# ================= AJOUTER =================
elif menu == "➕ Ajouter":
    st.title("➕ Ajouter un match")

    col1, col2 = st.columns(2)

    with col1:
        home = st.text_input("Équipe domicile")

    with col2:
        away = st.text_input("Équipe extérieur")

    result = st.selectbox("Résultat (optionnel)", ["", "1", "X", "2"])

    if st.button("Ajouter le match"):
        if home and away:
            new_data = pd.DataFrame([{
                "match": f"{home} vs {away}",
                "team_home": home,
                "team_away": away,
                "bet": "",
                "result": result
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

    if st.button("🗑 Réinitialiser données"):
        os.remove(DATA_FILE)
        st.success("Données supprimées, recharge la page")
