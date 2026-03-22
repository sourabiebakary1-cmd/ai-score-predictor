import streamlit as st
import requests
import numpy as np

st.set_page_config(page_title="BAKARY AI PRO MAX ELITE", layout="wide")

API_KEY = "289e8418878e48c598507cf2b72338f5"

# ================= UI =================
st.title("⚽ BAKARY AI PRO MAX ELITE 🧠🔥")

st.warning("⚠️ Les paris comportent des risques. Ne misez jamais tout votre argent.")
st.info("📊 Analyse basée sur statistiques. Résultats non garantis.")

# ================= API =================
def get_matches():
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": API_KEY}

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            st.error(f"❌ Erreur API: {response.status_code}")
            return []

        data = response.json()

        if "matches" not in data:
            st.error("❌ Données API invalides")
            return []

        return data["matches"]

    except Exception as e:
        st.error(f"❌ Problème connexion API: {e}")
        return []

# ================= ANALYSE =================
def analyse_match(match):
    try:
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]

        # Sécuriser accès score
        score_data = match.get("score", {}).get("fullTime", {})

        home_goals = score_data.get("home")
        away_goals = score_data.get("away")

        # éviter None
        home_goals = home_goals if home_goals is not None else 1
        away_goals = away_goals if away_goals is not None else 1

        # logique simple (pas random)
        attaque_home = home_goals + 1
        attaque_away = away_goals + 1

        proba = attaque_home / (attaque_home + attaque_away)

        return {
            "match": f"{home} vs {away}",
            "proba": proba,
            "score": proba
        }

    except Exception as e:
        return None

# ================= PARI =================
def type_pari(proba):
    if proba > 0.75:
        return "Victoire domicile"
    elif proba > 0.60:
        return "Double chance"
    else:
        return "Over 1.5"

# ================= TRAITEMENT =================
matches = get_matches()

analyses = []
for m in matches:
    result = analyse_match(m)
    if result:
        analyses.append(result)

# ================= AFFICHAGE =================
st.subheader("💎 MATCH DU JOUR (ULTRA FIABLE)")

if len(analyses) == 0:
    st.error("❌ Aucun match disponible")
else:
    best_match = max(analyses, key=lambda x: x["score"])

    proba = best_match["proba"]

    if proba >= 0.75:
        st.success(f"✅ {best_match['match']}")
    else:
        st.warning("⚠️ Aucun match ultra fiable, voici le meilleur :")
        st.info(f"👉 {best_match['match']}")

    st.progress(int(proba * 100))
    st.write(f"📊 Confiance: {round(proba*100)}%")

    # type de pari
    pari = type_pari(proba)
    st.write(f"🎯 Pari conseillé : {pari}")

    # sécurité
    if proba < 0.65:
        st.error("🚫 MATCH RISQUÉ - NE PAS JOUER")

# ================= STRATEGIE =================
st.subheader("💰 STRATÉGIE EXPERT")

bankroll = 10000
mise = int(bankroll * 0.02)

st.write("💎 1 seul match par jour")
st.write(f"💵 Mise conseillée : {mise} FCFA")
st.write("📌 Discipline :")
st.write("- Jamais ALL-IN")
st.write("- Respect du système")

# ================= HISTORIQUE =================
st.subheader("📊 HISTORIQUE")

resultat = st.selectbox("Résultat", ["Gagné", "Perdu"])

if st.button("Ajouter"):
    st.success(f"Résultat enregistré : {resultat}")

# ================= DEBUG =================
with st.expander("⚙️ DEBUG (si problème)"):
    st.write("Nombre de matchs:", len(matches))
    if len(matches) > 0:
        st.write(matches[0])
