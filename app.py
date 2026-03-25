import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import os

st.set_page_config(page_title="BAKARY AI PRO MAX", layout="wide")

st.title("🤖 BAKARY AI - AUTO APPRENTISSAGE PRO")

FILE = "data.csv"

# 📂 Charger ou créer base
if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=["Team1", "Team2", "Score1", "Score2"])

# 💾 Sauvegarde
def save_data(df):
    df.to_csv(FILE, index=False)

# 📊 Calcul stats
def compute_stats(df):
    stats = {}
    
    if df.empty:
        return stats
    
    teams = pd.unique(df[['Team1', 'Team2']].values.ravel())
    
    for team in teams:
        if team == "" or pd.isna(team):
            continue
        
        matches_home = df[df["Team1"] == team]
        matches_away = df[df["Team2"] == team]
        
        games = len(matches_home) + len(matches_away)
        
        if games == 0:
            continue
        
        goals_scored = matches_home["Score1"].sum() + matches_away["Score2"].sum()
        goals_conceded = matches_home["Score2"].sum() + matches_away["Score1"].sum()
        
        stats[team] = {
            "attack": goals_scored / games,
            "defense": goals_conceded / games
        }
    
    return stats

# 🔄 Toujours recalculer
team_stats = compute_stats(df)

# 🔮 IA
def predict(team1, team2):
    if team1 not in team_stats or team2 not in team_stats:
        return None
    
    a1 = team_stats[team1]["attack"]
    d1 = team_stats[team1]["defense"]
    
    a2 = team_stats[team2]["attack"]
    d2 = team_stats[team2]["defense"]
    
    # Protection contre zéro
    lambda1 = max(0.1, a1 * d2)
    lambda2 = max(0.1, a2 * d1)
    
    max_goals = 10
    best_prob = 0
    best_score = (0, 0)
    
    for i in range(max_goals):
        for j in range(max_goals):
            prob = poisson.pmf(i, lambda1) * poisson.pmf(j, lambda2)
            if prob > best_prob:
                best_prob = prob
                best_score = (i, j)
    
    total = lambda1 + lambda2
    
    over = "OVER 8.5 🔥" if total > 8 else "UNDER ⚠️"
    btts = "OUI ✅" if lambda1 > 1 and lambda2 > 1 else "NON ❌"
    
    if lambda1 > lambda2:
        winner = team1
    elif lambda2 > lambda1:
        winner = team2
    else:
        winner = "NUL"
    
    confidence = min(100, int((total / 10) * 100))
    
    return {
        "score": f"{best_score[0]} - {best_score[1]}",
        "over": over,
        "btts": btts,
        "winner": winner,
        "confidence": confidence
    }

# ⚡ Charger données rapides
st.subheader("⚡ Charger données exemple")

if st.button("Charger matchs puissants"):
    sample = [
        {"Team1": "RedBull", "Team2": "Fenerbahce", "Score1": 9, "Score2": 6},
        {"Team1": "RedBull", "Team2": "Braga", "Score1": 12, "Score2": 8},
        {"Team1": "WestHam", "Team2": "Olympiacos", "Score1": 13, "Score2": 11},
        {"Team1": "Lille", "Team2": "Anderlecht", "Score1": 5, "Score2": 9},
        {"Team1": "Chelsea", "Team2": "Nice", "Score1": 6, "Score2": 6},
        {"Team1": "Villarreal", "Team2": "Eintracht", "Score1": 10, "Score2": 6},
        {"Team1": "Roma", "Team2": "Chelsea", "Score1": 7, "Score2": 4},
        {"Team1": "Celta", "Team2": "Anderlecht", "Score1": 6, "Score2": 14},
        {"Team1": "Nice", "Team2": "Villarreal", "Score1": 6, "Score2": 10},
    ]
    
    df = pd.concat([df, pd.DataFrame(sample)], ignore_index=True)
    save_data(df)
    st.success("🔥 Données ajoutées ! Recharge la page")

# ➕ Ajouter match
st.subheader("➕ Ajouter un match")

team1_add = st.text_input("Equipe 1")
team2_add = st.text_input("Equipe 2")
score1_add = st.number_input("Score 1", 0, 20)
score2_add = st.number_input("Score 2", 0, 20)

if st.button("Enregistrer"):
    if team1_add == "" or team2_add == "":
        st.error("❌ Mets les noms des équipes")
    elif score1_add == 0 and score2_add == 0:
        st.warning("⚠️ Evite 0-0 (inutile pour IA)")
    else:
        new_row = {
            "Team1": team1_add,
            "Team2": team2_add,
            "Score1": score1_add,
            "Score2": score2_add
        }
        
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(df)
        st.success("✅ Match ajouté ! Recharge la page")

# 🔮 Prédiction
st.subheader("🔮 Prédire un match")

teams = list(team_stats.keys())

if len(teams) < 2:
    st.warning("⚠️ Ajoute au moins 2 équipes")
else:
    team1 = st.selectbox("Equipe 1", teams)
    team2 = st.selectbox("Equipe 2", teams)
    
    if team1 == team2:
        st.warning("⚠️ Choisis 2 équipes différentes")
    else:
        if st.button("Lancer IA"):
            result = predict(team1, team2)
            
            if result:
                st.success(f"📊 Score : {result['score']}")
                st.info(result["over"])
                st.info(f"BTTS : {result['btts']}")
                st.success(f"🏆 {result['winner']}")
                
                if result["confidence"] > 70:
                    st.success(f"💰 TRÈS FIABLE ({result['confidence']}%)")
                elif result["confidence"] > 50:
                    st.warning(f"⚠️ MOYEN ({result['confidence']}%)")
                else:
                    st.error(f"❌ RISQUÉ ({result['confidence']}%)")

# 📋 Historique
st.subheader("📋 Historique")
st.dataframe(df)
