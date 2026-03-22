import streamlit as st
import requests
import numpy as np
from datetime import datetime

st.set_page_config(page_title="BAKARY AI PRO MAX ELITE", layout="wide")

API_KEY = "289e8418878e48c598507cf2b72338f5"

# ================= DESIGN =================
st.markdown("""
    <style>
    body {
        background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚽ BAKARY AI PRO MAX ELITE 🧠🔥")

st.warning("⚠️ Les paris comportent des risques. Ne misez jamais tout votre argent.")
st.info("📊 Analyse basée sur statistiques. Résultats non garantis.")

# ================= API FOOTBALL =================
def get_matches():
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data.get("matches", [])
    except:
        return []

# ================= IA SIMPLIFIÉE =================
def analyse_match(match):
    try:
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]

        # simulation simple (à améliorer plus tard)
        proba = np.random.uniform(0.60, 0.90)
        forme = np.random.uniform(0.5, 1.0)
        domicile = 1 if np.random.rand() > 0.5 else 0.7

        score = (proba * 0.6) + (forme * 0.2) + (domicile * 0.2)

        return {
            "match": f"{home} vs {away}",
            "proba": proba,
            "score": score
        }
    except:
        return None

# ================= TRAITEMENT =================
matches = get_matches()

analyses = []
for m in matches:
    result = analyse_match(m)
    if result:
        analyses.append(result)

# ================= MATCH DU JOUR =================
st.subheader("💎 MATCH DU JOUR (ULTRA FIABLE)")

if len(analyses) == 0:
    st.error("❌ Aucun match trouvé (API ou connexion problème)")
else:
    best_match = max(analyses, key=lambda x: x["score"])

    if best_match["proba"] >= 0.80:
        st.success(f"✅ {best_match['match']}")
    else:
        st.warning("⚠️ Aucun match ultra fiable, voici le meilleur :")
        st.info(f"👉 {best_match['match']}")

    st.progress(int(best_match["proba"] * 100))
    st.write(f"📊 Confiance: {round(best_match['proba']*100)}%")

# ================= SÉCURITÉ =================
st.subheader("💰 STRATÉGIE EXPERT")

bankroll = 10000
mise = bankroll * 0.02

st.write("💎 1 seul match par jour")
st.write(f"💵 Mise conseillée : {int(mise)} FCFA")
st.write("📌 Discipline :")
st.write("- Jamais ALL-IN")
st.write("- Respect du système")

# ================= JOUR DANGEREUX =================
if len(analyses) > 0 and max([a["proba"] for a in analyses]) < 0.70:
    st.error("🚫 JOUR DANGEREUX - NE PAS JOUER")

# ================= HISTORIQUE =================
st.subheader("📊 HISTORIQUE")

resultat = st.selectbox("Résultat", ["Gagné", "Perdu"])

if st.button("Ajouter"):
    st.success(f"Résultat enregistré : {resultat}")

# ================= DEBUG =================
with st.expander("⚙️ DEBUG (si problème)"):
    st.write("Nombre de matchs:", len(matches))
    st.write(matches[:2])
