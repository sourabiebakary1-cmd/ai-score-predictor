import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import os

st.set_page_config(page_title="BAKARY AI PRO MAX", layout="wide")

st.title("🤖 BAKARY AI - AUTO APPRENTISSAGE")

FILE = "data.csv"

# 📂 Charger ou créer base de données
if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=["Team1", "Team2", "Score1", "Score2"])

# 💾 Sauvegarder
def save_data(df):
    df.to_csv(FILE, index=False)

# 📊 Calcul stats équipes
def compute_stats(df):
    teams = pd.unique(df[['Team1', 'Team2']].values.ravel())
    stats = {}
    
    for team in teams:
        matches_home = df[df["Team1"] == team]
        matches_away = df[df["Team2"] == team]
        
        goals_scored = matches_home["Score1"].sum() + matches_away["Score2"].sum()
        goals_conceded = matches_home["Score2"].sum() + matches_away["Score1"].sum()
        
        games = len(matches_home) + len(matches_away)
        
        if games > 0:
            stats[team] = {
                "attack": goals_scored / games,
                "defense": goals_conceded / games
            }
    
    return stats

team_stats = compute_stats(df)

# 🔮 Prédiction IA
def predict(team1, team2):
    if team1 not in team_stats or team2 not in team_stats:
        return None
    
    a1 = team_stats[team1]["attack"]
    d1 = team_stats[team1]["defense"]
    
    a2 = team_stats[team2]["attack"]
    d2 = team_stats[team2]["defense"]
    
    lambda1 = a1 * d2
    lambda2 = a2 * d1
    
    # Score probable
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
    
    # 🎯 Over
    over = "OVER 8.5 🔥" if total > 8 else "UNDER ⚠️"
    
    # 🤝 BTTS
    btts = "OUI ✅" if lambda1 > 1 and lambda2 > 1 else "NON ❌"
    
    # 🏆 Winner
    if lambda1 > lambda2:
        winner = team1
    elif lambda2 > lambda1:
        winner = team2
    else:
        winner = "NUL"
    
    # 💰 Confiance
    confidence = min(100, int((total / 10) * 100))
    
    return {
        "score": f"{best_score[0]} - {best_score[1]}",
        "over": over,
        "btts": btts,
        "winner": winner,
        "confidence": confidence
    }

# ➕ Ajouter match (APPRENTISSAGE)
st.subheader("➕ Ajouter un match (apprentissage)")

team1_add = st.text_input("Equipe 1")
team2_add = st.text_input("Equipe 2")
score1_add = st.number_input("Score 1", 0, 20)
score2_add = st.number_input("Score 2", 0, 20)

if st.button("Enregistrer le match"):
    new_row = {
        "Team1": team1_add,
        "Team2": team2_add,
        "Score1": score1_add,
        "Score2": score2_add
    }
    
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_data(df)
    
    st.success("✅ Match enregistré - IA améliorée !")

# 🔮 Prédiction
st.subheader("🔮 Prédire un match")

teams = list(team_stats.keys())

if len(teams) > 1:
    team1 = st.selectbox("Equipe 1", teams)
    team2 = st.selectbox("Equipe 2", teams)
    
    if st.button("Lancer IA"):
        result = predict(team1, team2)
        
        if result:
            st.success(f"📊 Score : {result['score']}")
            st.info(result["over"])
            st.info(f"BTTS : {result['btts']}")
            st.success(f"🏆 {result['winner']}")
            
            # Confiance
            if result["confidence"] > 70:
                st.success(f"💰 TRÈS FIABLE ({result['confidence']}%)")
            elif result["confidence"] > 50:
                st.warning(f"⚠️ MOYEN ({result['confidence']}%)")
            else:
                st.error(f"❌ RISQUÉ ({result['confidence']}%)")
        else:
            st.warning("Pas assez de données")

# 📋 Historique
st.subheader("📋 Historique des matchs")
st.dataframe(df)
