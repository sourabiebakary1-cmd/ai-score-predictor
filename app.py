import streamlit as st

st.set_page_config(page_title="BAKARY AI PRO MAX", layout="wide")

st.title("🤖 BAKARY AI PRO MAX - INTELLIGENT")

# ===== INPUT =====
team_a = st.text_input("Equipe A")
team_b = st.text_input("Equipe B")

cote_a = st.number_input("Cote A", value=2.0)
cote_draw = st.number_input("Cote Nul", value=3.2)
cote_b = st.number_input("Cote B", value=2.0)

type_match = st.selectbox("Type de match", ["FIFA", "REEL"])

# ===== CALCUL =====
if st.button("ANALYSER"):

    p_a = 1 / cote_a
    p_draw = 1 / cote_draw
    p_b = 1 / cote_b

    total = p_a + p_draw + p_b

    p_a /= total
    p_draw /= total
    p_b /= total

    st.subheader("📊 Probabilités")
    st.write(f"{team_a}: {round(p_a*100,2)}%")
    st.write(f"Nul: {round(p_draw*100,2)}%")
    st.write(f"{team_b}: {round(p_b*100,2)}%")

    max_proba = max(p_a, p_b, p_draw)

    # ===== DETECTION MATCH =====
    ecart = abs(p_a - p_b)

    if ecart < 0.1:
        type_game = "ÉQUILIBRÉ"
    elif p_a > p_b:
        type_game = "FAVORI " + team_a
    else:
        type_game = "FAVORI " + team_b

    st.subheader("🧠 Type de match")
    st.info(type_game)

    # ===== ANALYSE BUTS =====
    btts = False
    over25 = False

    if p_a > 0.35 and p_b > 0.35:
        btts = True

    if (p_a + p_b) > 0.75:
        over25 = True

    st.subheader("⚽ Analyse Buts")

    if btts:
        st.write("✔️ BTTS OUI")
    else:
        st.write("❌ BTTS NON")

    if over25:
        st.write("✔️ OVER 2.5")
    else:
        st.write("❌ UNDER 2.5")

    # ===== DECISION INTELLIGENTE =====
    st.subheader("🎯 Décision Finale")

    decision = "⚠️ PAS DE PARI"

    # CAS FIFA
    if type_match == "FIFA":
        if btts and over25:
            decision = "🔥 PARIER OVER 2.5"
        elif btts:
            decision = "✅ PARIER BTTS"
        else:
            decision = "⚠️ PAS DE PARI"

    # CAS MATCH REEL
    else:
        if max_proba < 0.5:
            decision = "⚠️ PAS DE PARI"
        elif type_game.startswith("FAVORI"):
            decision = "✅ DOUBLE CHANCE"
        elif btts and over25:
            decision = "🔥 OVER 2.5"
        else:
            decision = "⚠️ PAS DE PARI"

    st.success(decision)

    # ===== SCORE ESTIMATION =====
    st.subheader("📈 Score estimé")

    goals_a = round(p_a * 3)
    goals_b = round(p_b * 3)

    st.write(f"Score probable: {goals_a} - {goals_b}")
