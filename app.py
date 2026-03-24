import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="BAKARY AI ULTIMATE", layout="wide")

DATA_FILE = "data.csv"

# ================= INIT =================
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=[
        "team_home","team_away","score_home","score_away","date"
    ]).to_csv(DATA_FILE, index=False)

if "coupon" not in st.session_state:
    st.session_state.coupon = []

st.title("🔥 BAKARY AI ULTIMATE")

menu = st.sidebar.radio("Menu", [
    "🏠 Accueil",
    "🤖 Matchs IA",
    "🎟️ Coupon",
    "➕ Ajouter",
    "📊 Stats"
])

# ================= FONCTIONS =================
def get_data(df, team):
    return df[(df["team_home"] == team) | (df["team_away"] == team)].tail(10)

def stats(df, team):
    buts, enc = [], []
    for _, r in df.iterrows():
        if r["team_home"] == team:
            buts.append(r["score_home"])
            enc.append(r["score_away"])
        elif r["team_away"] == team:
            buts.append(r["score_away"])
            enc.append(r["score_home"])
    if len(buts) == 0:
        return 5, 5
    return sum(buts)/len(buts), sum(enc)/len(enc)

def predict(t1, t2, df):
    d1 = get_data(df, t1)
    d2 = get_data(df, t2)

    a1, d1v = stats(d1, t1)
    a2, d2v = stats(d2, t2)

    s1 = (a1 + d2v) / 2
    s2 = (a2 + d1v) / 2
    total = s1 + s2
    conf = min(100, int((total/10)*100))

    return s1, s2, total, conf

# ================= ACCUEIL =================
if menu == "🏠 Accueil":
    st.subheader("📊 Dashboard")
    df = pd.read_csv(DATA_FILE)

    if len(df) > 0:
        df["total"] = df["score_home"] + df["score_away"]

        col1, col2, col3 = st.columns(3)
        col1.metric("Matchs", len(df))
        col2.metric("Moyenne buts", round(df["total"].mean(), 2))
        col3.metric("Over 6.5 %", round((df["total"] > 6).mean()*100, 2))
    else:
        st.warning("Pas de données")

# ================= MATCHS IA =================
elif menu == "🤖 Matchs IA":
    st.subheader("🤖 Générateur de matchs")

    df = pd.read_csv(DATA_FILE)
    teams = list(set(df["team_home"]).union(set(df["team_away"])))

    if len(teams) < 2:
        st.warning("Ajoute des matchs d'abord")
    else:
        for i in range(min(10, len(teams)//2)):
            t1 = teams[i]
            t2 = teams[-i-1]

            if t1 != t2:
                s1, s2, total, conf = predict(t1, t2, df)

                st.markdown(f"### {t1} 🆚 {t2}")
                st.write(f"🎯 {round(s1)} - {round(s2)} | 🔥 {round(total,2)} buts | 🧠 {conf}%")

                col1, col2, col3 = st.columns(3)

                if col1.button(f"OVER 5.5 {i}"):
                    st.session_state.coupon.append(f"{t1} vs {t2} - OVER 5.5")

                if col2.button(f"OVER 6.5 {i}"):
                    st.session_state.coupon.append(f"{t1} vs {t2} - OVER 6.5")

                if col3.button(f"BTTS {i}"):
                    st.session_state.coupon.append(f"{t1} vs {t2} - BTTS")

# ================= COUPON =================
elif menu == "🎟️ Coupon":
    st.subheader("🎟️ Mon Coupon")

    if len(st.session_state.coupon) == 0:
        st.warning("Aucun pari ajouté")
    else:
        for bet in st.session_state.coupon:
            st.write(f"✅ {bet}")

        st.success(f"Total paris : {len(st.session_state.coupon)}")

        if st.button("❌ Vider coupon"):
            st.session_state.coupon = []

# ================= AJOUT =================
elif menu == "➕ Ajouter":
    st.subheader("➕ Ajouter match")

    h = st.text_input("Equipe domicile")
    a = st.text_input("Equipe extérieur")
    sh = st.number_input("Score domicile", 0, 20)
    sa = st.number_input("Score extérieur", 0, 20)

    if st.button("Ajouter"):
        new = pd.DataFrame([[h, a, sh, sa, pd.Timestamp.now()]],
                           columns=["team_home","team_away","score_home","score_away","date"])
        new.to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.success("Match ajouté")

# ================= STATS =================
elif menu == "📊 Stats":
    st.subheader("📊 Statistiques")

    df = pd.read_csv(DATA_FILE)

    if len(df) > 0:
        df["total"] = df["score_home"] + df["score_away"]

        st.metric("Matchs", len(df))
        st.metric("Moyenne", round(df["total"].mean(), 2))
        st.line_chart(df["total"])
    else:
        st.warning("Pas de données")
