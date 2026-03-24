import streamlit as st
import pandas as pd
import os
from PIL import Image
import pytesseract
import re

st.set_page_config(page_title="BAKARY AI AUTO", layout="wide")

DATA_FILE = "data.csv"

# ================= INIT =================
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=[
        "team_home","team_away","score_home","score_away","date"
    ]).to_csv(DATA_FILE, index=False)

if "coupon" not in st.session_state:
    st.session_state.coupon = []

st.title("🔥 BAKARY AI AUTO (Image Scanner)")

menu = st.sidebar.radio("Menu", [
    "📸 Import Image",
    "🤖 Matchs IA",
    "🎟️ Coupon",
    "➕ Ajouter",
    "📊 Stats"
])

# ================= IA =================
def extract_matches(text):
    matches = []
    
    # Exemple : Braga 8 : 14 Anderlecht
    pattern = r"([A-Za-z\s]+)\s(\d+)\s[:]\s(\d+)\s([A-Za-z\s]+)"
    
    results = re.findall(pattern, text)

    for r in results:
        home = r[0].strip()
        score_home = int(r[1])
        score_away = int(r[2])
        away = r[3].strip()

        matches.append([home, away, score_home, score_away])

    return matches

# ================= IMPORT IMAGE =================
if menu == "📸 Import Image":
    st.subheader("📸 Scanner les matchs")

    uploaded_file = st.file_uploader("Upload image", type=["png","jpg","jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Image chargée")

        text = pytesseract.image_to_string(image)

        st.write("🔍 Texte détecté :")
        st.text(text)

        matches = extract_matches(text)

        if matches:
            df = pd.DataFrame(matches, columns=[
                "team_home","team_away","score_home","score_away"
            ])
            df["date"] = pd.Timestamp.now()

            df.to_csv(DATA_FILE, mode='a', header=False, index=False)

            st.success(f"✅ {len(matches)} matchs ajoutés automatiquement !")
            st.dataframe(df)
        else:
            st.warning("⚠️ Aucun match détecté")

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

# ================= MATCHS IA =================
elif menu == "🤖 Matchs IA":
    st.subheader("🤖 Générateur")

    df = pd.read_csv(DATA_FILE)
    teams = list(set(df["team_home"]).union(set(df["team_away"])))

    if len(teams) < 2:
        st.warning("Ajoute des matchs")
    else:
        for i in range(min(10, len(teams)//2)):
            t1 = teams[i]
            t2 = teams[-i-1]

            if t1 != t2:
                s1,s2,total,conf = predict(t1,t2,df)

                st.markdown(f"### {t1} vs {t2}")
                st.write(f"{round(s1)} - {round(s2)} | {round(total,2)} buts | {conf}%")

                col1,col2,col3 = st.columns(3)

                if col1.button(f"O5 {i}"):
                    st.session_state.coupon.append(f"{t1}-{t2} OVER 5.5")

                if col2.button(f"O6 {i}"):
                    st.session_state.coupon.append(f"{t1}-{t2} OVER 6.5")

                if col3.button(f"BTTS {i}"):
                    st.session_state.coupon.append(f"{t1}-{t2} BTTS")

# ================= COUPON =================
elif menu == "🎟️ Coupon":
    st.subheader("🎟️ Coupon")

    if len(st.session_state.coupon) == 0:
        st.warning("Vide")
    else:
        for b in st.session_state.coupon:
            st.write("✅", b)

        if st.button("Vider"):
            st.session_state.coupon = []

# ================= AJOUT =================
elif menu == "➕ Ajouter":
    st.subheader("Ajouter match")

    h = st.text_input("Home")
    a = st.text_input("Away")
    sh = st.number_input("Score H",0,20)
    sa = st.number_input("Score A",0,20)

    if st.button("Ajouter"):
        new = pd.DataFrame([[h,a,sh,sa,pd.Timestamp.now()]],
                           columns=["team_home","team_away","score_home","score_away","date"])
        new.to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.success("Ajouté")

# ================= STATS =================
elif menu == "📊 Stats":
    df = pd.read_csv(DATA_FILE)

    if len(df)>0:
        df["total"] = df["score_home"]+df["score_away"]
        st.metric("Matchs", len(df))
        st.metric("Moyenne", round(df["total"].mean(),2))
    else:
        st.warning("Pas de data")
