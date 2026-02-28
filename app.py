import streamlit as st
import random

st.set_page_config(page_title="AI Score Predictor", page_icon="⚽", layout="centered")

st.markdown("""
<style>
body {background-color: #0e1117;}
.stTextInput>div>div>input {
    background-color: #1c1f26;
    color: white;
    border-radius: 10px;
}
.stButton>button {
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-size: 18px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;color:white;'>⚽ AI Score Predictor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:gray;'>EA Sports FC 25 - Top 3 Scores Probables</p>", unsafe_allow_html=True)

team1 = st.text_input("Entrez le nom de l'équipe 1")
team2 = st.text_input("Entrez le nom de l'équipe 2")

def generate_realistic_score():
    base_scores = [(1,0),(0,1),(1,1),(2,1),(1,2),(2,0),(0,2),(2,2),(3,1),(1,3)]
    return random.choice(base_scores)

if st.button("🚀 Prédire le score"):
    if team1 and team2:
        st.markdown("## 🔥 Top 3 Scores Probables")

        scores = set()
        while len(scores) < 3:
            scores.add(generate_realistic_score())

        for score in scores:
            st.markdown(
                f"""
                <div style="
                background-color:#1c1f26;
                padding:20px;
                border-radius:15px;
                margin-bottom:15px;
                text-align:center;
                font-size:22px;
                color:white;">
                {team1} {score[0]} - {score[1]} {team2}
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.warning("⚠️ Veuillez entrer les deux équipes")
