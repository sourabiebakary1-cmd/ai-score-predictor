import streamlit as st

st.title("🔥 BAKARY PREDICTOR PRO 🔥")

st.header("Entrer les statistiques des équipes")

# Equipe A
st.subheader("Equipe A")
a_scored = st.number_input("Moyenne buts marqués A", 0.0, 10.0, 3.0)
a_conceded = st.number_input("Moyenne buts encaissés A", 0.0, 10.0, 2.0)

# Equipe B
st.subheader("Equipe B")
b_scored = st.number_input("Moyenne buts marqués B", 0.0, 10.0, 3.0)
b_conceded = st.number_input("Moyenne buts encaissés B", 0.0, 10.0, 2.0)

if st.button("Analyser le match"):

    force_a = (a_scored + b_conceded) / 2
    force_b = (b_scored + a_conceded) / 2

    st.subheader("📊 Analyse intelligente")

    if force_a > force_b:
        st.success("Victoire probable : Equipe A")
        confiance = min((force_a - force_b) * 20, 95)
    elif force_b > force_a:
        st.success("Victoire probable : Equipe B")
        confiance = min((force_b - force_a) * 20, 95)
    else:
        st.warning("Match équilibré")
        confiance = 50

    st.write(f"Confiance : {round(confiance,1)} %")

    total = force_a + force_b

    if a_scored > 2 and b_scored > 2:
        st.info("BTTS : OUI probable")

    if total > 6:
        st.info("Over 5.5 probable")

    score1 = f"{round(force_a)} - {round(force_b)}"
    score2 = f"{round(force_a+1)} - {round(force_b)}"
    score3 = f"{round(force_a)} - {round(force_b+1)}"

    st.subheader("🎯 3 Scores Exact Probables")
    st.write(score1)
    st.write(score2)
    st.write(score3)
