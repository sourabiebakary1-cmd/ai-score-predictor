if st.button("🚀 Analyser le match"):

    result = analyse_match(team1, team2)

    if result is None:
        st.error("Equipe non trouvée")

    else:

        if "top_scores" in result:
            st.subheader("🔥 Top 3 Scores Probables")
            for score in result["top_scores"]:
                st.write(f"{team1} {score[0]} - {score[1]} {team2}")

        if "home_win" in result:
            st.subheader("📊 Probabilités 1X2")
            st.write(f"Victoire {team1} : {round(result['home_win']*100,1)}%")
            st.write(f"Match nul : {round(result['draw']*100,1)}%")
            st.write(f"Victoire {team2} : {round(result['away_win']*100,1)}%")

        if "over_25" in result:
            st.subheader("⚽ Marchés supplémentaires")
            st.write(f"Over 2.5 buts : {round(result['over_25']*100,1)}%")
            st.write(f"BTTS : {round(result['btts']*100,1)}%")
