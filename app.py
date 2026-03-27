import streamlit as st
import math
import os
import csv
from datetime import datetime
from collections import defaultdict

# ===== CONFIG =====
st.set_page_config(page_title="FC 25 Predictor PRO", layout="centered")
st.title("⚽ 1xBet - FC 25 Champions League")
st.subheader("Prédicteur + Auto-Apprentissage")

FILE = "data.csv"

# ===== CRÉER FICHIER SI N'EXISTE PAS =====
if not os.path.exists(FILE):
    with open(FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "home", "away", "hg", "ag", "odd_home", "odd_draw", "odd_away"])

# ===== INPUT =====
st.header("📥 Entrée des données")
team_home = st.text_input("🏠 Équipe A").strip()
team_away = st.text_input("✈️ Équipe B").strip()

col1, col2, col3 = st.columns(3)
with col1:
    odd_home = st.number_input("📊 Cote A", min_value=1.01, step=0.01, value=1.50, format="%.2f")
with col2:
    odd_draw = st.number_input("📊 Cote Nul", min_value=1.01, step=0.01, value=3.50, format="%.2f")
with col3:
    odd_away = st.number_input("📊 Cote B", min_value=1.01, step=0.01, value=5.00, format="%.2f")

# ===== APPRENTISSAGE (MOYENNE DES BUTS) =====
def read_matches():
    matches = []
    if not os.path.exists(FILE):
        return matches
    with open(FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                matches.append({
                    "date": row.get("date", ""),
                    "home": row.get("home", ""),
                    "away": row.get("away", ""),
                    "hg": int(row.get("hg", 0)),
                    "ag": int(row.get("ag", 0)),
                    "odd_home": float(row.get("odd_home")) if row.get("odd_home") else None,
                    "odd_draw": float(row.get("odd_draw")) if row.get("odd_draw") else None,
                    "odd_away": float(row.get("odd_away")) if row.get("odd_away") else None,
                })
            except Exception:
                continue
    return matches

def learn_avg_goals_per_team():
    matches = read_matches()
    if not matches:
        return 1.25, 1.25
    home_goals_total = 0
    away_goals_total = 0
    n_home = 0
    n_away = 0
    for m in matches:
        home_goals_total += m["hg"]
        away_goals_total += m["ag"]
        n_home += 1
        n_away += 1
    avg_home = home_goals_total / n_home if n_home else 1.25
    avg_away = away_goals_total / n_away if n_away else 1.25
    return avg_home, avg_away

# ===== PRÉDICTION =====
def poisson(k, lam):
    return (lam ** k * math.exp(-lam)) / math.factorial(k)

st.markdown("---")
if st.button("🚀 Lancer la prédiction"):
    if not team_home or not team_away:
        st.error("Veuillez renseigner les deux équipes avant de lancer la prédiction.")
    else:
        p_home = 1.0 / odd_home
        p_draw = 1.0 / odd_draw
        p_away = 1.0 / odd_away
        total = p_home + p_draw + p_away
        p_home /= total
        p_draw /= total
        p_away /= total

        st.header("📊 Probabilités (implicites)")
        st.write(f"{team_home} : {p_home*100:.2f}%")
        st.write(f"Nul : {p_draw*100:.2f}%")
        st.write(f"{team_away} : {p_away*100:.2f}%")

        avg_home, avg_away = learn_avg_goals_per_team()
        total_avg = avg_home + avg_away
        if total_avg <= 0:
            total_avg = 2.5

        lambda_home = total_avg * (p_home + 0.5 * p_draw) * (avg_home / (avg_home + avg_away + 1e-9))
        lambda_away = total_avg * (p_away + 0.5 * p_draw) * (avg_away / (avg_home + avg_away + 1e-9))

        st.header("⚙️ Buts attendus")
        st.write(f"{team_home} : {lambda_home:.2f}")
        st.write(f"{team_away} : {lambda_away:.2f}")

        max_score = st.slider("Nombre max de buts à considérer par équipe", 3, 8, 6)
        scores = []
        for i in range(max_score + 1):
            for j in range(max_score + 1):
                prob = poisson(i, lambda_home) * poisson(j, lambda_away)
                scores.append(((i, j), prob))
        scores.sort(key=lambda x: x[1], reverse=True)

        st.header("🔥 Top scores")
        for rank, ((i, j), prob) in enumerate(scores[:10], start=1):
            st.write(f"{rank}. {team_home} {i}-{j} {team_away} ({prob*100:.3f}%)")

# ===== AJOUT RÉSULTAT =====
st.markdown("---")
st.header("🧠 Ajouter résultat (apprentissage)")
hg = st.number_input("Buts équipe A", min_value=0, step=1, key="hg")
ag = st.number_input("Buts équipe B", min_value=0, step=1, key="ag")

col_save1, col_save2 = st.columns([3,1])
with col_save1:
    if st.button("💾 Enregistrer le match"):
        if not team_home or not team_away:
            st.error("Pour enregistrer un match, renseignez d'abord les deux équipes.")
        else:
            with open(FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.utcnow().isoformat(),
                    team_home,
                    team_away,
                    int(hg),
                    int(ag),
                    f"{odd_home:.2f}",
                    f"{odd_draw:.2f}",
                    f"{odd_away:.2f}",
                ])
            st.success("✅ Match enregistré ! Le robot apprend...")

with col_save2:
    if st.button("⚠️ Réinitialiser données (supprimer CSV)"):
        if os.path.exists(FILE):
            os.remove(FILE)
            with open(FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["date", "home", "away", "hg", "ag", "odd_home", "odd_draw", "odd_away"])
            st.success("✅ Données réinitialisées.")
        else:
            st.info("Aucun fichier à supprimer.")
