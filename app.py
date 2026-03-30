import streamlit as st
import math
import os
import csv
from datetime import datetime
from collections import defaultdict, Counter
import numpy as np

# Try to import scipy; if missing, we'll provide fallback (no Dixon-Coles MLE)
try:
    from scipy.optimize import minimize
    SCIPY_AVAILABLE = True
except Exception:
    SCIPY_AVAILABLE = False

# ===== CONFIG =====
st.set_page_config(page_title="FC 25 Predictor PRO (Dixon-Coles)", layout="centered")
st.title("⚽ FC 25 Predictor PRO — Dixon‑Coles intégré")
st.subheader("Poisson + Dixon‑Coles (MLE) — améliore corrélations faibles scores")

FILE = "data.csv"
PRED_LOG = "predictions_log.csv"

# ===== CSV HEADER =====
HEADER = ["date", "home", "away", "hg", "ag", "odd_home", "odd_draw", "odd_away"]
PRED_HEADER = ["date", "home", "away", "lambda_home", "lambda_away",
               "model_pH", "model_pD", "model_pA",
               "bm_pH", "bm_pD", "bm_pA",
               "final_pH", "final_pD", "final_pA"]

# ===== CREATE FILES IF MISSING =====
if not os.path.exists(FILE):
    with open(FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
if not os.path.exists(PRED_LOG):
    with open(PRED_LOG, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(PRED_HEADER)

# ===== INPUT =====
st.header("📥 Entrée des données")
team_home = st.text_input("🏠 Équipe A").strip()
team_away = st.text_input("✈️ Équipe B").strip()

col1, col2, col3 = st.columns(3)
with col1:
    odd_home = st.number_input("📊 Cote A", min_value=1.01, step=0.01, value=1.50, format="%.2f")
with col2:
    odd_draw = st.number_input("📊 Cote Nul", min_value=1.01, step=0.01, value=3.50, format="%.2f")
with col3:
    odd_away = st.number_input("📊 Cote B", min_value=1.01, step=0.01, value=5.00, format="%.2f")

blend = st.slider("Blending ratio (modèle vs cotes) — 0=model, 1=cotes", 0.0, 1.0, 0.2)
home_adv_slider = st.slider("Home advantage factor (initial)", 1.00, 1.20, 1.07, 0.01)
reg = st.slider("Regularization strength (reg) for simple model", 0.1, 20.0, 1.0, 0.1)

# ===== UTIL =====
def safe_float(x, default=None):
    try:
        return float(x)
    except Exception:
        return default

def poisson_pmf(k, lam):
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    if k < 0:
        return 0.0
    try:
        return (lam ** k) * math.exp(-lam) / math.factorial(k)
    except (OverflowError, ValueError):
        return 0.0

# ===== READ MATCHES =====
def read_matches():
    matches = []
    if not os.path.exists(FILE):
        return matches
    with open(FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                matches.append({
                    "date": row.get("date", ""),
                    "home": row.get("home", "").strip(),
                    "away": row.get("away", "").strip(),
                    "hg": int(row.get("hg") or 0),
                    "ag": int(row.get("ag") or 0),
                    "odd_home": safe_float(row.get("odd_home")),
                    "odd_draw": safe_float(row.get("odd_draw")),
                    "odd_away": safe_float(row.get("odd_away")),
                })
            except Exception:
                continue
    return matches

# ===== SIMPLE LEARNING (fallback) =====
def learn_team_strengths_simple(matches, reg=1.0):
    team_attack = defaultdict(float)
    team_defense = defaultdict(float)
    team_count = Counter()

    total_home_goals = 0
    total_away_goals = 0
    n_matches = 0

    for m in matches:
        h = m["home"]; a = m["away"]
        hg = m["hg"]; ag = m["ag"]
        total_home_goals += hg
        total_away_goals += ag
        n_matches += 1
        team_attack[h] += hg
        team_defense[h] += ag
        team_attack[a] += ag
        team_defense[a] += hg
        team_count[h] += 1
        team_count[a] += 1

    if n_matches == 0:
        return {}, {}, 1.25, 1.25

    mean_home = total_home_goals / n_matches
    mean_away = total_away_goals / n_matches
    league_mean = (mean_home + mean_away) / 2

    attack_rate = {}
    defense_rate = {}
    for t in team_count:
        played = team_count.get(t, 0)
        if played == 0:
            attack_rate[t] = league_mean
            defense_rate[t] = league_mean
        else:
            att = team_attack.get(t, 0) / played
            defc = team_defense.get(t, 0) / played
            attack_rate[t] = (att * played + reg * league_mean) / (played + reg)
            defense_rate[t] = (defc * played + reg * league_mean) / (played + reg)

    return attack_rate, defense_rate, mean_home, mean_away

# ===== DIXON-COLLES LIKELIHOOD & PREDICTION =====
def dc_tau(x, y, rho):
    # Dixon-Coles correction tau for small scores (0/1)
    # tau(x,y) as in Dixon-Coles paper:
    if x == 0 and y == 0:
        return 1 - (rho)
    if x == 0 and y == 1:
        return 1 + (rho)
    if x == 1 and y == 0:
        return 1 + (rho)
    if x == 1 and y == 1:
        return 1 - (rho)
    return 1.0

def dc_log_likelihood(params, matches, team_index, base_home_mean):
    # params: [log_attack_1..log_attack_T, log_def_1..log_def_T, log_home_adv, rho]
    # We store log of attack/def to ensure positivity; base scaling handled via base_home_mean
    T = len(team_index)
    # param partition
    log_att = params[:T]
    log_def = params[T:2*T]
    log_home = params[2*T]
    rho = params[2*T + 1]
    # clamp rho to a reasonable interval in likelihood? We'll penalize large |rho|
    ll = 0.0
    eps = 1e-12
    for m in matches:
        h = m["home"]; a = m["away"]
        hg = m["hg"]; ag = m["ag"]
        ih = team_index[h]; ia = team_index[a]
        att_h = math.exp(log_att[ih])
        def_h = math.exp(log_def[ih])
        att_a = math.exp(log_att[ia])
        def_a = math.exp(log_def[ia]]
)
        # expected goals (lambdas)
        lambda_h = att_h * def_a / base_home_mean * mean_home_glob * math.exp(log_home)
        lambda_a = att_a * def_h / base_home_mean * mean_away_glob
        # compute Poisson probs
        # direct pmf
        ph = poisson_pmf(hg, lambda_h)
        pa = poisson_pmf(ag, lambda_a)
        tau = dc_tau(hg, ag, rho)
        prob = max(eps, ph * pa * tau)
        ll += math.log(prob)
    # Negative log-likelihood (for minimizer)
    # Add small L2 penalty on rho and log parameters to regularize
    reg_penalty = 1e-3 * (rho**2 + sum(x*x for x in params))
    return -ll + reg_penalty

# We'll implement a wrapper that builds team index and runs minimize
def estimate_dixon_coles(matches, init_home_adv=1.07):
    # Build team index
    teams = sorted({m["home"] for m in matches} | {m["away"] for m in matches})
    T = len(teams)
    team_index = {t: i for i, t in enumerate(teams)}

    # compute global means used for scaling
    total_home = sum(m["hg"] for m in matches)
    total_away = sum(m["ag"] for m in matches)
    n_matches = len(matches)
    global_mean_home = total_home / n_matches if n_matches else 1.25
    global_mean_away = total_away / n_matches if n_matches else 1.25
    base_home_mean = (global_mean_home + global_mean_away) / 2

    # store global for use in likelihood via closure (we set as globals)
    global mean_home_glob, mean_away_glob
    mean_home_glob = global_mean_home
    mean_away_glob = global_mean_away

    # initial params: log attack = log(league_mean), log_def similar, log_home = log(init_home_adv), rho=0
    init_log_att = [math.log(base_home_mean) for _ in range(T)]
    init_log_def = [math.log(base_home_mean) for _ in range(T)]
    init_log_home = math.log(init_home_adv)
    init_rho = 0.0

    x0 = np.array(init_log_att + init_log_def + [init_log_home, init_rho])

    # bounds: no bounds on logs, but rho we may keep between -0.9 and 0.9 via constraint
    bounds = [(None, None)] * (2*T + 1) + [(-0.99, 0.99)]

    # minimize negative log-likelihood
    res = minimize(lambda x: dc_log_likelihood(x, matches, team_index, base_home_mean),
                   x0, method="L-BFGS-B", bounds=bounds,
                   options={"maxiter": 1000})

    if not res.success:
        st.warning(f"Optimisation Dixon-Coles a convergé avec message: {res.message}")

    params = res.x
    log_att = params[:T]
    log_def = params[T:2*T]
    log_home = params[2*T]
    rho = params[2*T + 1]

    attack = {teams[i]: math.exp(log_att[i]) for i in range(T)}
    defense = {teams[i]: math.exp(log_def[i]) for i in range(T)}
    home_adv = math.exp(log_home)

    return attack, defense, global_mean_home, global_mean_away, home_adv, rho

# ===== EVALUATION HELPERS =====
def score_from_result(hg, ag):
    if hg > ag: return "H"
    if hg == ag: return "D"
    return "A"

def compute_issue_probs_from_scores(score_probs):
    pH = sum(p for (i,j),p in score_probs.items() if i>j)
    pD = sum(p for (i,j),p in score_probs.items() if i==j)
    pA = sum(p for (i,j),p in score_probs.items() if i<j)
    return pH, pD, pA

# ===== PREDICTION HELPERS USING DIXON-COLLES =====
def score_grid_probs_dc(lambda_h, lambda_a, rho, max_score=6):
    probs = {}
    total = 0.0
    for i in range(max_score+1):
        for j in range(max_score+1):
            p = poisson_pmf(i, lambda_h) * poisson_pmf(j, lambda_a) * dc_tau(i, j, rho)
            probs[(i,j)] = max(0.0, p)
            total += probs[(i,j)]
    if total > 0:
        for k in probs:
            probs[k] /= total
    return probs

# ===== MAIN UI: estimation button and usage =====
st.markdown("---")
st.write("Utilisez le bouton ci‑dessous pour estimer les paramètres Dixon‑Coles (requires scipy).")
col_est1, col_est2 = st.columns([1,4])
with col_est1:
    if st.button("🔬 Estimer Dixon‑Coles (MLE)"):
        matches = read_matches()
        if not matches:
            st.info("Aucun match dans l'historique pour estimer.")
        else:
            if not SCIPY_AVAILABLE:
                st.error("scipy n'est pas installé. Installez via 'pip install scipy' puis relancez.")
            else:
                with st.spinner("Optimisation en cours (peut prendre quelques secondes)..."):
                    try:
                        attack_dc, defense_dc, mh, ma, home_adv_est, rho_est = estimate_dixon_coles(matches, init_home_adv=home_adv_slider)
                        st.success("Paramètres estimés.")
                        st.write(f"Home advantage (est) : {home_adv_est:.3f}")
                        st.write(f"Rho (Dixon‑Coles) : {rho_est:.4f}")
                        st.write("Extrait attaque/defense (quelques équipes) :")
                        sample = list(attack_dc.keys())[:10]
                        for t in sample:
                            st.write(f"{t} — att: {attack_dc[t]:.3f}, def: {defense_dc[t]:.3f}")
                        # save estimated params to a file for reuse
                        try:
                            np.savez("dc_params.npz", teams=np.array(list(attack_dc.keys())), 
                                     attack=np.array([attack_dc[t] for t in attack_dc]),
                                     defense=np.array([defense_dc[t] for t in attack_dc]),
                                     home_adv=home_adv_est, rho=rho_est, mean_home=mh, mean_away=ma)
                            st.info("Paramètres sauvegardés dans dc_params.npz")
                        except Exception as e:
                            st.warning(f"Impossible de sauvegarder paramètres : {e}")
                    except Exception as e:
                        st.error(f"Erreur pendant l'estimation : {e}")

with col_est2:
    st.write("Si estimation lente, réduisez la taille de l'historique ou utilisez données récentes seulement.")

# ===== LOAD DC PARAMS IF EXIST =====
DC_PARAMS = None
if os.path.exists("dc_params.npz"):
    try:
        z = np.load("dc_params.npz", allow_pickle=True)
        teams_arr = [t.decode() if isinstance(t, bytes) else t for t in z["teams"]]
        attack_dc = {teams_arr[i]: float(z["attack"][i]) for i in range(len(teams_arr))}
        defense_dc = {teams_arr[i]: float(z["defense"][i]) for i in range(len(teams_arr))}
        home_adv_dc = float(z["home_adv"])
        rho_dc = float(z["rho"])
        mean_home_dc = float(z["mean_home"])
        mean_away_dc = float(z["mean_away"])
        DC_PARAMS = (attack_dc, defense_dc, mean_home_dc, mean_away_dc, home_adv_dc, rho_dc)
    except Exception:
        DC_PARAMS = None

# ===== PREDICTION SECTION (uses DC params if present, else simple model) =====
st.markdown("---")
if st.button("🚀 Lancer la prédiction"):
    if not team_home or not team_away:
        st.error("Veuillez renseigner les deux équipes.")
    else:
        matches = read_matches()
        use_dc = DC_PARAMS is not None
        if use_dc:
            attack_rate, defense_rate, mean_home, mean_away, home_adv, rho = DC_PARAMS
            st.write("Utilisation des paramètres Dixon‑Coles estimés.")
        else:
            attack_rate, defense_rate, mean_home, mean_away = learn_team_strengths_simple(matches, reg=reg)
            home_adv = home_adv_slider
            rho = 0.0  # no DC correction

        if team_home not in attack_rate:
            st.info(f"Attention : peu ou pas de données historiques pour {team_home}.")
        if team_away not in attack_rate:
            st.info(f"Attention : peu ou pas de données historiques pour {team_away}.")

        # compute lambdas using rates
        base = (mean_home + mean_away) / 2
        att_home = attack_rate.get(team_home, base)
        def_home = defense_rate.get(team_home, base)
        att_away = attack_rate.get(team_away, base)
        def_away = defense_rate.get(team_away, base)

        lambda_h = att_home * def_away / base * mean_home * home_adv
        lambda_a = att_away * def_home / base * mean_away
        lambda_h = max(0.05, min(lambda_h, 6.0))
        lambda_a = max(0.05, min(lambda_a, 6.0))

        # score grid using DC correction if rho != 0
        max_score = st.slider("Nombre max de buts à considérer par équipe", 3, 8, 6)
        if rho != 0.0:
            score_probs = score_grid_probs_dc(lambda_h, lambda_a, rho, max_score=max_score)
        else:
            score_probs = {}
            for i in range(max_score+1):
                for j in range(max_score+1):
                    score_probs[(i,j)] = poisson_pmf(i, lambda_h) * poisson_pmf(j, lambda_a)
            total = sum(score_probs.values())
            if total > 0:
                for k in score_probs:
                    score_probs[k] /= total

        model_pH, model_pD, model_pA = compute_issue_probs_from_scores(score_probs)

        ph = 1.0/odd_home; pd = 1.0/odd_draw; pa = 1.0/odd_away
        tot = ph+pd+pa if (ph+pd+pa) > 0 else 1.0
        bm_pH = ph/tot; bm_pD = pd/tot; bm_pA = pa/tot

        final_pH = (1-blend)*model_pH + blend*bm_pH
        final_pD = (1-blend)*model_pD + blend*bm_pD
        final_pA = (1-blend)*model_pA + blend*bm_pA

        st.header("📊 Probabilités (issue)")
        st.write(f"{team_home} : modèle {model_pH*100:.2f}%  | bookmaker {bm_pH*100:.2f}%  | final {final_pH*100:.2f}%")
        st.write(f"Nul : modèle {model_pD*100:.2f}%  | bookmaker {bm_pD*100:.2f}%  | final {final_pD*100:.2f}%")
        st.write(f"{team_away} : modèle {model_pA*100:.2f}%  | bookmaker {bm_pA*100:.2f}%  | final {final_pA*100:.2f}%")

        st.header("⚙️ Buts attendus (lambdas)")
        st.write(f"{team_home} : {lambda_h:.2f}")
        st.write(f"{team_away} : {lambda_a:.2f}")
        if rho != 0.0:
            st.write(f"Dixon‑Coles rho : {rho:.4f}")

        top = sorted(score_probs.items(), key=lambda x: x[1], reverse=True)[:10]
        st.header("🔥 Top scores (modèle)")
        for rank, ((i,j), prob) in enumerate(top, start=1):
            st.write(f"{rank}. {team_home} {i}-{j} {team_away} ({prob*100:.3f}%)")

        # Log prediction
        try:
            with open(PRED_LOG, "a", newline="", encoding="utf-8") as pf:
                pwriter = csv.writer(pf)
                pwriter.writerow([
                    datetime.utcnow().isoformat(),
                    team_home,
                    team_away,
                    f"{lambda_h:.3f}",
                    f"{lambda_a:.3f}",
                    f"{model_pH:.4f}",
                    f"{model_pD:.4f}",
                    f"{model_pA:.4f}",
                    f"{bm_pH:.4f}",
                    f"{bm_pD:.4f}",
                    f"{bm_pA:.4f}",
                    f"{final_pH:.4f}",
                    f"{final_pD:.4f}",
                    f"{final_pA:.4f}",
                ])
        except Exception as e:
            st.warning(f"Impossible d'écrire le log de prédiction: {e}")

# ===== RECORD RESULT =====
st.markdown("---")
st.header("🧠 Ajouter résultat (apprentissage)")
hg = st.number_input("Buts équipe A", min_value=0, step=1, key="hg2")
ag = st.number_input("Buts équipe B", min_value=0, step=1, key="ag2")

col_save1, col_save2 = st.columns([3,1])
with col_save1:
    if st.button("💾 Enregistrer le match"):
        if not team_home or not team_away:
            st.error("Pour enregistrer: renseignez les équipes.")
        else:
            try:
                with open(FILE, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        datetime.utcnow().isoformat(),
                        team_home,
                        team_away,
                        int(hg),
                        int(ag),
                        f"{odd_home:.2f}",
                        f"{odd_draw:.2f}",
                        f"{odd_away:.2f}",
                    ])
                st.success("✅ Match enregistré !")
            except Exception as e:
                st.error(f"Erreur lors de l'enregistrement: {e}")

with col_save2:
    if st.button("⚠️ Réinitialiser données (supprimer CSV)"):
        if os.path.exists(FILE):
            os.remove(FILE)
            with open(FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(HEADER)
            st.success("✅ Données réinitialisées.")
        else:
            st.info("Aucun fichier à supprimer.")

# ===== EVALUATION SECTION =====
st.markdown("---")
if st.button("📈 Évaluer le modèle sur l'historique"):
    matches = read_matches()
    if not matches:
        st.info("Pas de matches enregistrés pour évaluation.")
    else:
        # decide which params to use
        if DC_PARAMS is not None:
            attack_rate, defense_rate, mean_home, mean_away, home_adv_dc, rho_dc = DC_PARAMS
            use_dc_eval = True
        else:
            attack_rate, defense_rate, mean_home, mean_away = learn_team_strengths_simple(matches, reg=reg)
            home_adv_dc = home_adv_slider
            rho_dc = 0.0
            use_dc_eval = False

        max_score_eval = 6
        logprob_sum = 0.0
        issue_ll = 0.0
        brier_sum = 0.0
        n = 0
        exact_prob_sum = 0.0
        for m in matches:
            att_h = attack_rate.get(m["home"], (mean_home + mean_away)/2)
            def_h = defense_rate.get(m["home"], (mean_home + mean_away)/2)
            att_a = attack_rate.get(m["away"], (mean_home + mean_away)/2)
            def_a = defense_rate.get(m["away"], (mean_home + mean_away)/2)
            lambda_h = att_h * def_a / ((mean_home + mean_away)/2) * mean_home * home_adv_dc
            lambda_a = att_a * def_h / ((mean_home + mean_away)/2) * mean_away
            lambda_h = max(0.05, min(lambda_h, 6.0))
            lambda_a = max(0.05, min(lambda_a, 6.0))
            if rho_dc != 0.0:
                probs = score_grid_probs_dc(lambda_h, lambda_a, rho_dc, max_score=max_score_eval)
            else:
                probs = {}
                for i in range(max_score_eval+1):
                    for j in range(max_score_eval+1):
                        probs[(i,j)] = poisson_pmf(i, lambda_h) * poisson_pmf(j, lambda_a)
                total = s
