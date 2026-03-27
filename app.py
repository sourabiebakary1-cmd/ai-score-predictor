import streamlit as st
import math
import os
import csv

# ===== CONFIG =====
st.set_page_config(page_title="FC 25 Predictor PRO", layout="centered")

st.title("⚽ 1xBet - FC 25 Champions League")
st.subheader("Prédicteur + Auto-Apprentissage")

FILE = "data.csv"

# ===== CRÉER FICHIER SI N'EXISTE PAS =====
if not os.path.exists(FILE):
    with open(FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["home", "away", "hg", "ag"])

# ===== INPUT =====
st.header("📥 Entrée des données")

team_home = st.text_input("🏠 Équipe A")
team_away = st.text_input("✈️ Équipe B")

odd_home = st.number_input("📊 Cote A", min_value=1.01, step=0.01)
odd_draw = st.number_input("📊 Cote Nul", min_value=1.01, step=0.01)
odd_away = st.number_input("📊 Cote B", min_value=1.01, step=0.01)

# ===== APPRENTISSAGE (MOYENNE DES BUTS) =====
def learn_goals():
    total_goals = 0
    count = 0
    with open(FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_goals += int(row["hg"]) + int(row["ag"])
            count += 1
    return total_goals / count if count > 0 else 2.5

# ===== PRÉDICTION =====
if st.button("🚀 Lancer la prédiction"):

    p_home = 1 / odd_home
    p_draw = 1 / odd_draw
    p_away = 1 / odd_away

    total = p_home + p_draw + p_away
    p_home /= total
    p_draw /= total
    p_away /= total

    st.header("📊 Probabilités")
    st.write(f"{team_home} : {p_home*100:.2f}%")
    st.write(f"Nul : {p_draw*100:.2f}%")
    st.write(f"{team_away} : {p_away*100:.2f}%")

    # ===== AUTO LEARNING =====
    avg_goals = learn_goals()

    lambda_home = avg_goals * (p_home + 0.5 * p_draw)
    lambda_away = avg_goals * (p_away + 0.5 * p_draw)

    st.header("⚙️ Buts attendus")
    st.write(f"{team_home} : {lambda_home:.2f}")
    st.write(f"{team_away} : {lambda_away:.2f}")

    def poisson(k, lam):
        return (lam ** k * math.exp(-lam)) / math.factorial(k)

    scores = []
    for i in range(7):
        for j in range(7):
            prob = poisson(i, lambda_home) * poisson(j, lambda_away)
            scores.append(((i, j), prob))

    scores.sort(key=lambda x: x[1], reverse=True)

    st.header("🔥 Top 5 scores")
    for rank, ((i, j), prob) in enumerate(scores[:5], start=1):
        st.write(f"{rank}. {team_home} {i}-{j} {team_away} ({prob*100:.2f}%)")

# ===== AJOUT RÉSULTAT (APPRENTISSAGE) =====
st.markdown("---")
st.header("🧠 Ajouter résultat (apprentissage)")

hg = st.number_input("Buts équipe A", min_value=0, step=1)
ag = st.number_input("Buts équipe B", min_value=0, step=1)

if st.button("💾 Enregistrer le match"):
    with open(FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([team_home, team_away, hg, ag])

    st.success("✅ Match enregistré ! Le robot apprend...")
