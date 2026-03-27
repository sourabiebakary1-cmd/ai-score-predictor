import streamlit as st

st.set_page_config(page_title="BAKARY AI PRO", layout="wide")

st.title("🤖 BAKARY AI - VERSION SIMPLE")

# Entrées
team_a = st.text_input("Equipe A")
team_b = st.text_input("Equipe B")

cote_a = st.number_input("Cote A", value=1.5)
cote_draw = st.number_input("Cote Nul", value=3.5)
cote_b = st.number_input("Cote B", value=2.5)

if st.button("PRÉDIRE"):

    # Convertir cotes en probabilités
    p_a = 1 / cote_a
    p_draw = 1 / cote_draw
    p_b = 1 / cote_b

    total = p_a + p_draw + p_b

    p_a /= total
    p_draw /= total
    p_b /= total

    st.subheader("📊 Probabilités")
    st.write(f"{team_a} : {round(p_a*100,2)}%")
    st.write(f"Nul : {round(p_draw*100,2)}%")
    st.write(f"{team_b} : {round(p_b*100,2)}%")

    # Décision intelligente
    max_proba = max(p_a, p_b, p_draw)

    if max_proba < 0.5:
        decision = "⚠️ PAS DE PARI"
    elif p_a == max_proba:
        decision = f"✅ PARIER sur {team_a}"
    elif p_b == max_proba:
        decision = f"✅ PARIER sur {team_b}"
    else:
        decision = "🤝 MATCH NUL"

    st.subheader("🎯 Décision")
    st.success(decision)

    # Analyse buts simple
    st.subheader("⚽ Analyse Buts")

    if p_a > 0.4 and p_b > 0.4:
        st.write("👉 BTTS OUI")
    else:
        st.write("👉 BTTS NON")

    if (p_a + p_b) > 0.75:
        st.write("👉 OVER 2.5")
    else:
        st.write("👉 UNDER 2.5")
