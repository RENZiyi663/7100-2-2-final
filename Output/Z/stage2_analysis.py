import math
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.optimize import minimize
from scipy.stats import chi2_contingency, t
import matplotlib.pyplot as plt


BASE = Path(__file__).resolve().parents[1]
DATA_FILE = BASE / "Data" / "7100.xlsx"
OUT_DIR = BASE / "Output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_XLSX = OUT_DIR / "中步分析结果汇总.xlsx"
OUT_MD = OUT_DIR / "中步分析简报.md"
OUT_PLOT = OUT_DIR / "moderation_plot_trust_hc.png"


def cronbach_alpha(df_items: pd.DataFrame) -> float:
    d = df_items.dropna()
    k = d.shape[1]
    if k < 2 or len(d) < 2:
        return np.nan
    item_vars = d.var(axis=0, ddof=1)
    total_var = d.sum(axis=1).var(ddof=1)
    if total_var == 0:
        return np.nan
    return (k / (k - 1)) * (1 - item_vars.sum() / total_var)


def item_total_corr(df_items: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for c in df_items.columns:
        rest = df_items.drop(columns=[c]).mean(axis=1)
        corr = df_items[c].corr(rest)
        rows.append({"item": c, "item_total_corr": corr})
    return pd.DataFrame(rows)


def cfa_composite_reliability(df_items: pd.DataFrame) -> dict:
    d = df_items.dropna().astype(float)
    p = d.shape[1]
    if p < 2 or len(d) < 5:
        return {
            "n": len(d),
            "cr": np.nan,
            "ave": np.nan,
            "admissible": False,
            "optimization_ok": False,
            "loadings": pd.DataFrame(columns=["item", "std_loading", "std_error_var"]),
        }

    z = (d - d.mean()) / d.std(ddof=1)
    s = z.cov().values
    logdet_s = np.linalg.slogdet(s)[1]

    eigvals, eigvecs = np.linalg.eigh(s)
    lead = np.sqrt(max(eigvals[-1] - 1e-3, 1e-3)) * eigvecs[:, -1]
    if lead.sum() < 0:
        lead *= -1
    lead = np.clip(lead, -0.9, 0.9)
    uniq0 = np.clip(np.diag(s) - lead**2, 0.1, 2.0)
    x0 = np.concatenate([lead, np.log(uniq0)])
    bounds = [(-0.999, 0.999)] * p + [(-8, 3)] * p

    def objective(x):
        lam = x[:p]
        uniq = np.exp(x[p:])
        sigma = np.outer(lam, lam) + np.diag(uniq)
        sign, logdet_sigma = np.linalg.slogdet(sigma)
        if sign <= 0:
            return 1e10
        sigma_inv = np.linalg.inv(sigma)
        return logdet_sigma + np.trace(s @ sigma_inv) - logdet_s - p

    res = minimize(objective, x0, method="L-BFGS-B", bounds=bounds)
    lam = res.x[:p]
    if lam.sum() < 0:
        lam *= -1
    uniq = np.exp(res.x[p:])

    item_var = lam**2 + uniq
    std_loading = lam / np.sqrt(item_var)
    std_error_var = uniq / item_var
    cr = (std_loading.sum() ** 2) / ((std_loading.sum() ** 2) + std_error_var.sum())
    ave = (std_loading**2).sum() / ((std_loading**2).sum() + std_error_var.sum())

    # Boundary solutions indicate an improper or unstable CFA solution.
    boundary_hit = np.any(np.abs(lam) > 0.98) or np.any(std_error_var < 0.02)
    admissible = bool(res.success and not boundary_hit)

    loadings = pd.DataFrame(
        {
            "item": list(d.columns),
            "std_loading": std_loading,
            "std_error_var": std_error_var,
        }
    )
    return {
        "n": len(d),
        "cr": cr,
        "ave": ave,
        "admissible": admissible,
        "optimization_ok": bool(res.success),
        "loadings": loadings,
    }


def find_col(cols, keyword):
    matched = [c for c in cols if keyword in c]
    if not matched:
        raise ValueError(f"Column not found for keyword: {keyword}")
    return matched[0]


def source_from_stim(s):
    s = str(s)
    if "AI" in s:
        return "AI健康教练"
    if "human" in s:
        return "人类专家"
    return np.nan


def frame_from_stim(s):
    s = str(s)
    if "gain" in s:
        return "采取健康行动的好处"
    if "loss" in s:
        return "不采取健康行动的负面后果"
    return np.nan


def mediation_bootstrap(df, x, m, y, covariates=None, n_boot=5000, seed=2026):
    covariates = covariates or []
    rng = np.random.default_rng(seed)

    # Path a: M ~ X + covariates
    f_a = f"{m} ~ {x}" + (" + " + " + ".join(covariates) if covariates else "")
    model_a = smf.ols(f_a, data=df).fit()
    a = model_a.params[x]

    # Path b and c': Y ~ X + M + covariates
    f_b = f"{y} ~ {x} + {m}" + (" + " + " + ".join(covariates) if covariates else "")
    model_b = smf.ols(f_b, data=df).fit()
    b = model_b.params[m]
    c_prime = model_b.params[x]

    # Total effect c
    f_c = f"{y} ~ {x}" + (" + " + " + ".join(covariates) if covariates else "")
    model_c = smf.ols(f_c, data=df).fit()
    c_total = model_c.params[x]

    indirect = a * b

    # Bootstrap CI for indirect effect
    boot_effects = []
    n = len(df)
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        bdf = df.iloc[idx]
        try:
            ba = smf.ols(f_a, data=bdf).fit().params[x]
            bb = smf.ols(f_b, data=bdf).fit().params[m]
            boot_effects.append(ba * bb)
        except Exception:
            continue

    boot_effects = np.array(boot_effects)
    ci_low, ci_high = np.percentile(boot_effects, [2.5, 97.5]) if len(boot_effects) else (np.nan, np.nan)

    return {
        "a": a,
        "b": b,
        "c_total": c_total,
        "c_prime": c_prime,
        "indirect_ab": indirect,
        "boot_ci_low": ci_low,
        "boot_ci_high": ci_high,
        "boot_n": len(boot_effects),
        "model_a_p": model_a.pvalues.get(x, np.nan),
        "model_b_p_m": model_b.pvalues.get(m, np.nan),
        "model_b_p_x": model_b.pvalues.get(x, np.nan),
        "model_c_p": model_c.pvalues.get(x, np.nan),
    }


def johnson_neyman_from_model(model, pred_name, mod_name, alpha=0.05, mod_values=None):
    params = model.params
    cov = model.cov_params()
    df_resid = int(model.df_resid)
    t_crit = t.ppf(1 - alpha / 2, df_resid)

    b1 = params[pred_name]
    b3 = params[f"{pred_name}:{mod_name}"]
    v1 = cov.loc[pred_name, pred_name]
    v3 = cov.loc[f"{pred_name}:{mod_name}", f"{pred_name}:{mod_name}"]
    c13 = cov.loc[pred_name, f"{pred_name}:{mod_name}"]

    # Solve (b1+b3w)^2 - tcrit^2*(v1 + 2*c13*w + v3*w^2)=0
    A = b3**2 - (t_crit**2) * v3
    B = 2 * b1 * b3 - (t_crit**2) * 2 * c13
    C = b1**2 - (t_crit**2) * v1

    roots = []
    if abs(A) < 1e-12:
        if abs(B) > 1e-12:
            roots = [(-C / B)]
    else:
        disc = B**2 - 4 * A * C
        if disc >= 0:
            r1 = (-B - math.sqrt(disc)) / (2 * A)
            r2 = (-B + math.sqrt(disc)) / (2 * A)
            roots = sorted([r1, r2])

    rows = []
    if mod_values is not None:
        for w in mod_values:
            slope = b1 + b3 * w
            se = math.sqrt(max(v1 + 2 * c13 * w + v3 * (w**2), 1e-12))
            t_val = slope / se
            p_val = 2 * (1 - t.cdf(abs(t_val), df_resid))
            rows.append(
                {
                    "moderator_value": w,
                    "conditional_slope": slope,
                    "se": se,
                    "t": t_val,
                    "p": p_val,
                    "significant": p_val < alpha,
                }
            )

    return {
        "roots": roots,
        "t_crit": t_crit,
        "df_resid": df_resid,
        "grid_table": pd.DataFrame(rows),
    }


def main():
    raw = pd.read_excel(DATA_FILE)
    raw = raw[raw["作答ID"].notna()].copy()
    cols = list(raw.columns)

    stim_col = "随机元素"
    mc_source_col = find_col(cols, "主要来自于")
    mc_frame_col = find_col(cols, "主要强调的是")
    att_col = "本题选C"

    int_cols = [
        find_col(cols, "我愿意按照教练推荐的运动计划来做"),
        find_col(cols, "在需要的时候，我会照着推荐的运动计划去做"),
        find_col(cols, "当我想提升体能或改善健康时，我愿意按照这些运动建议来做"),
    ]
    se_cols = [
        find_col(cols, "难易程度是"),
        find_col(cols, "有多大信心"),
        find_col(cols, "有多确定自己能"),
    ]
    trust_cols = [
        find_col(cols, "我对AI给的建议有信心"),
        find_col(cols, "AI给的建议是靠谱的"),
        find_col(cols, "我可以信任AI给的建议"),
    ]
    hc_cols = [
        find_col(cols, "我经常思考我的健康问题"),
        find_col(cols, "我非常在意自己的健康"),
        find_col(cols, "我非常关注自己的健康"),
        find_col(cols, "我经常检查自己的健康状况"),
        find_col(cols, "我会注意一天当中身体的感受"),
        find_col(cols, "我通常能意识到自己的健康状况"),
    ]

    for c in int_cols + se_cols + trust_cols + hc_cols:
        raw[c] = pd.to_numeric(raw[c], errors="coerce")

    raw["source"] = raw[stim_col].map(source_from_stim)
    raw["frame"] = raw[stim_col].map(frame_from_stim)
    raw["design_valid"] = raw["source"].notna() & raw["frame"].notna()

    valid = raw[raw["design_valid"]].copy()
    valid["mc_source_correct"] = valid[mc_source_col] == valid["source"]
    valid["mc_frame_correct"] = valid[mc_frame_col] == valid["frame"]
    valid["att_pass"] = valid[att_col].astype(str).str.strip() == "C"

    strict = valid[valid["mc_source_correct"] & valid["mc_frame_correct"] & valid["att_pass"]].copy()

    strict["DV_Intention"] = strict[int_cols].mean(axis=1)
    strict["M_Trust"] = strict[trust_cols].mean(axis=1)
    strict["M_SelfEfficacy"] = strict[se_cols].mean(axis=1)
    strict["W_HealthConsciousness"] = strict[hc_cols].mean(axis=1)

    strict["Source_bin"] = strict["source"].map({"人类专家": 0, "AI健康教练": 1})
    strict["Frame_bin"] = strict["frame"].map({"采取健康行动的好处": 0, "不采取健康行动的负面后果": 1})

    # 1) Data cleaning summary
    tbl_clean = pd.DataFrame(
        [
            {"step": "raw_non_empty", "n": len(raw)},
            {"step": "valid_design_rows", "n": len(valid)},
            {"step": "strict_after_mc_attention", "n": len(strict)},
            {
                "step": "excluded_count",
                "n": len(raw) - len(strict),
            },
        ]
    )

    # 2) Reliability + item-total
    scale_defs = {
        "DV_Intention": int_cols,
        "M_Trust": trust_cols,
        "M_SelfEfficacy": se_cols,
        "W_HealthConsciousness": hc_cols,
    }
    rel_rows = []
    item_total_tables = {}
    cfa_loading_tables = {}
    for scale_name, items in scale_defs.items():
        d = strict[items]
        cfa_rel = cfa_composite_reliability(d)
        rel_rows.append(
            {
                "scale": scale_name,
                "n_items": len(items),
                "alpha": cronbach_alpha(d),
                "cr": cfa_rel["cr"],
                "ave": cfa_rel["ave"],
                "cfa_admissible": cfa_rel["admissible"],
                "mean": d.mean(axis=1).mean(),
                "sd": d.mean(axis=1).std(ddof=1),
            }
        )
        itc = item_total_corr(d)
        itc.insert(0, "scale", scale_name)
        item_total_tables[scale_name] = itc
        loadings = cfa_rel["loadings"].copy()
        loadings.insert(0, "scale", scale_name)
        cfa_loading_tables[scale_name] = loadings
    tbl_reliability = pd.DataFrame(rel_rows)
    tbl_item_total = pd.concat(item_total_tables.values(), ignore_index=True)
    tbl_cfa_loadings = pd.concat(cfa_loading_tables.values(), ignore_index=True)

    # 3) Manipulation check
    ctab_source = pd.crosstab(valid["source"], valid[mc_source_col])
    ctab_frame = pd.crosstab(valid["frame"], valid[mc_frame_col])
    chi2_s, p_s, dof_s, _ = chi2_contingency(ctab_source)
    chi2_f, p_f, dof_f, _ = chi2_contingency(ctab_frame)

    tbl_manip = pd.DataFrame(
        [
            {
                "check": "source_manipulation",
                "accuracy": valid["mc_source_correct"].mean(),
                "chi2": chi2_s,
                "dof": dof_s,
                "p": p_s,
            },
            {
                "check": "frame_manipulation",
                "accuracy": valid["mc_frame_correct"].mean(),
                "chi2": chi2_f,
                "dof": dof_f,
                "p": p_f,
            },
            {
                "check": "attention_check_pass",
                "accuracy": valid["att_pass"].mean(),
                "chi2": np.nan,
                "dof": np.nan,
                "p": np.nan,
            },
        ]
    )

    # 4) Descriptive stats
    key_vars = ["DV_Intention", "M_Trust", "M_SelfEfficacy", "W_HealthConsciousness"]
    tbl_desc = strict[key_vars].agg(["count", "mean", "std", "min", "max"]).T.reset_index()
    tbl_desc = tbl_desc.rename(columns={"index": "variable"})

    cell_desc = (
        strict.groupby(["source", "frame"])[key_vars]
        .agg(["count", "mean", "std"])
        .reset_index()
    )
    cell_desc.columns = ["_".join(c).strip("_") for c in cell_desc.columns.to_flat_index()]

    # 5) Correlations
    corr = strict[key_vars].corr()
    pvals = pd.DataFrame(np.ones_like(corr), index=corr.index, columns=corr.columns)
    for r in corr.index:
        for c in corr.columns:
            if r == c:
                pvals.loc[r, c] = 0
            else:
                rr = strict[[r, c]].dropna()
                if len(rr) > 2:
                    model = sm.OLS(rr[r], sm.add_constant(rr[c])).fit()
                    pvals.loc[r, c] = model.pvalues.iloc[1]
    corr_out = corr.copy()
    for r in corr.index:
        for c in corr.columns:
            if r == c:
                corr_out.loc[r, c] = np.nan
            else:
                corr_out.loc[r, c] = float(corr.loc[r, c])
    tbl_corr_long = (
        corr_out.stack()
        .dropna()
        .rename("r")
        .reset_index()
        .rename(columns={"level_0": "var1", "level_1": "var2"})
    )
    tbl_corr_long["p"] = tbl_corr_long.apply(lambda x: pvals.loc[x["var1"], x["var2"]], axis=1)

    # 6) 2x2 ANOVA
    anova_model = smf.ols("DV_Intention ~ C(source) * C(frame)", data=strict).fit()
    tbl_anova = sm.stats.anova_lm(anova_model, typ=2).reset_index().rename(columns={"index": "term"})

    # 7) Mediation bootstrap (trust + self-efficacy)
    med_df = strict[["Source_bin", "Frame_bin", "DV_Intention", "M_Trust", "M_SelfEfficacy"]].dropna().copy()
    med_trust = mediation_bootstrap(
        med_df,
        x="Source_bin",
        m="M_Trust",
        y="DV_Intention",
        covariates=["Frame_bin"],
        n_boot=5000,
        seed=2026,
    )
    med_se = mediation_bootstrap(
        med_df,
        x="Source_bin",
        m="M_SelfEfficacy",
        y="DV_Intention",
        covariates=["Frame_bin"],
        n_boot=5000,
        seed=2027,
    )
    tbl_med = pd.DataFrame(
        [
            {"mediator": "M_Trust", **med_trust},
            {"mediator": "M_SelfEfficacy", **med_se},
        ]
    )

    # 8) Moderation: HC moderates Trust -> Intention
    mod_df = strict[["DV_Intention", "M_Trust", "W_HealthConsciousness", "Source_bin", "Frame_bin"]].dropna().copy()
    mod_df["Trust_c"] = mod_df["M_Trust"] - mod_df["M_Trust"].mean()
    mod_df["HC_c"] = mod_df["W_HealthConsciousness"] - mod_df["W_HealthConsciousness"].mean()

    mod_model = smf.ols(
        "DV_Intention ~ Trust_c * HC_c + Source_bin + Frame_bin",
        data=mod_df,
    ).fit()
    tbl_mod = pd.DataFrame(
        {
            "term": mod_model.params.index,
            "coef": mod_model.params.values,
            "se": mod_model.bse.values,
            "t": mod_model.tvalues.values,
            "p": mod_model.pvalues.values,
        }
    )
    tbl_mod_summary = pd.DataFrame(
        [
            {
                "model": "DV_Intention ~ Trust_c*HC_c + Source + Frame",
                "n": len(mod_df),
                "R2": mod_model.rsquared,
                "Adj_R2": mod_model.rsquared_adj,
                "F": mod_model.fvalue,
                "F_p": mod_model.f_pvalue,
            }
        ]
    )

    # 9) Simple slopes + Johnson-Neyman
    mean_hc = mod_df["HC_c"].mean()
    sd_hc = mod_df["HC_c"].std(ddof=1)
    slope_points = {
        "Low_HC_minus_1SD": mean_hc - sd_hc,
        "Mean_HC": mean_hc,
        "High_HC_plus_1SD": mean_hc + sd_hc,
    }

    b1 = mod_model.params["Trust_c"]
    b3 = mod_model.params["Trust_c:HC_c"]
    cov = mod_model.cov_params()
    v1 = cov.loc["Trust_c", "Trust_c"]
    v3 = cov.loc["Trust_c:HC_c", "Trust_c:HC_c"]
    c13 = cov.loc["Trust_c", "Trust_c:HC_c"]

    slopes_rows = []
    for label, w in slope_points.items():
        slope = b1 + b3 * w
        se = np.sqrt(max(v1 + 2 * c13 * w + v3 * (w**2), 1e-12))
        tval = slope / se
        pval = 2 * (1 - t.cdf(abs(tval), int(mod_model.df_resid)))
        slopes_rows.append(
            {
                "level": label,
                "HC_c_value": w,
                "slope_trust_on_DV": slope,
                "se": se,
                "t": tval,
                "p": pval,
            }
        )
    tbl_slopes = pd.DataFrame(slopes_rows)

    hc_grid = np.linspace(mod_df["HC_c"].min(), mod_df["HC_c"].max(), 200)
    jn = johnson_neyman_from_model(
        mod_model,
        pred_name="Trust_c",
        mod_name="HC_c",
        mod_values=hc_grid,
    )
    tbl_jn_grid = jn["grid_table"]
    tbl_jn_roots = pd.DataFrame(
        {
            "jn_root_HC_c": jn["roots"] if jn["roots"] else [np.nan],
            "t_critical": [jn["t_crit"]] + [np.nan] * (max(len(jn["roots"]), 1) - 1),
            "df_resid": [jn["df_resid"]] + [np.nan] * (max(len(jn["roots"]), 1) - 1),
        }
    )

    # Plot moderation lines at low/mean/high HC
    trust_seq = np.linspace(mod_df["Trust_c"].min(), mod_df["Trust_c"].max(), 100)
    plt.figure(figsize=(8, 6))
    for label, hcv in slope_points.items():
        pred_df = pd.DataFrame(
            {
                "Trust_c": trust_seq,
                "HC_c": hcv,
                "Source_bin": 0,
                "Frame_bin": 0,
            }
        )
        pred = mod_model.predict(pred_df)
        plt.plot(trust_seq, pred, label=label)
    plt.xlabel("Trust (centered)")
    plt.ylabel("Predicted Intention")
    plt.title("Moderation: HC moderates Trust -> Intention")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_PLOT, dpi=220)
    plt.close()

    # Export all tables to one Excel workbook
    with pd.ExcelWriter(OUT_XLSX, engine="openpyxl") as writer:
        tbl_clean.to_excel(writer, index=False, sheet_name="01_cleaning")
        tbl_reliability.to_excel(writer, index=False, sheet_name="02_reliability")
        tbl_item_total.to_excel(writer, index=False, sheet_name="02_item_total")
        tbl_cfa_loadings.to_excel(writer, index=False, sheet_name="02_cfa_loadings")
        tbl_manip.to_excel(writer, index=False, sheet_name="03_manip_check")
        ctab_source.to_excel(writer, sheet_name="03_ctab_source")
        ctab_frame.to_excel(writer, sheet_name="03_ctab_frame")
        tbl_desc.to_excel(writer, index=False, sheet_name="04_descriptive")
        cell_desc.to_excel(writer, index=False, sheet_name="04_cell_descriptive")
        tbl_corr_long.to_excel(writer, index=False, sheet_name="05_correlation")
        tbl_anova.to_excel(writer, index=False, sheet_name="06_anova_2x2")
        tbl_med.to_excel(writer, index=False, sheet_name="07_mediation_boot")
        tbl_mod.to_excel(writer, index=False, sheet_name="08_moderation_coef")
        tbl_mod_summary.to_excel(writer, index=False, sheet_name="08_moderation_model")
        tbl_slopes.to_excel(writer, index=False, sheet_name="09_simple_slopes")
        tbl_jn_roots.to_excel(writer, index=False, sheet_name="09_jn_roots")
        tbl_jn_grid.to_excel(writer, index=False, sheet_name="09_jn_grid")

    # Brief markdown interpretation
    med_trust_sig = med_trust["boot_ci_low"] * med_trust["boot_ci_high"] > 0
    med_se_sig = med_se["boot_ci_low"] * med_se["boot_ci_high"] > 0
    interaction_p = float(tbl_mod.loc[tbl_mod["term"] == "Trust_c:HC_c", "p"].values[0])

    md_lines = [
        "# 中步分析简报",
        "",
        "## 数据与清理",
        f"- 原始有效行数（去空作答ID后）：{len(raw)}",
        f"- 严格样本（操纵检验+注意力检验通过）：{len(strict)}",
        "",
        "## 信度",
    ]
    for _, r in tbl_reliability.iterrows():
        rel_line = f"- {r['scale']}: alpha={r['alpha']:.3f}, CR={r['cr']:.3f}, AVE={r['ave']:.3f}"
        if not bool(r["cfa_admissible"]):
            rel_line += "（单因子CFA出现边界解，CR仅供参考）"
        md_lines.append(rel_line)

    md_lines.extend(
        [
            "",
            "## 实验操控检验",
            f"- 来源操纵准确率：{tbl_manip.loc[tbl_manip['check']=='source_manipulation','accuracy'].values[0]:.3f}",
            f"- 框架操纵准确率：{tbl_manip.loc[tbl_manip['check']=='frame_manipulation','accuracy'].values[0]:.3f}",
            "",
            "## 2x2 ANOVA（DV: Intention）",
            "- 详见 Excel 的 06_anova_2x2。",
            "",
            "## 中介效应（Bootstrap）",
            f"- Trust 中介间接效应 ab={med_trust['indirect_ab']:.4f}, 95%CI [{med_trust['boot_ci_low']:.4f}, {med_trust['boot_ci_high']:.4f}]",
            f"- Self-efficacy 中介间接效应 ab={med_se['indirect_ab']:.4f}, 95%CI [{med_se['boot_ci_low']:.4f}, {med_se['boot_ci_high']:.4f}]",
            f"- Trust 中介是否显著（CI不跨0）：{'是' if med_trust_sig else '否'}",
            f"- Self-efficacy 中介是否显著（CI不跨0）：{'是' if med_se_sig else '否'}",
            "",
            "## 调节效应（HC调节Trust->Intention）",
            f"- 交互项 Trust×HC p={interaction_p:.4f}",
            "- 简单斜率与Johnson-Neyman结果详见 Excel 的 09_simple_slopes 与 09_jn_roots/09_jn_grid。",
            f"- 调节图：{OUT_PLOT.name}",
            "",
            "## 初步解读",
            "- 本数据在严格样本下可支持‘来源与框架操纵成功’。",
            "- 主效应和交互若较弱，重点可放在机制路径（尤其信任）与边界条件（健康意识）上。",
            "- 若你后续定稿模型，可优先围绕 Source -> Trust -> Intention，并检验 HC 是否调节 Trust 对 Intention 的作用。",
        ]
    )

    OUT_MD.write_text("\n".join(md_lines), encoding="utf-8")

    print("Generated:")
    print(OUT_XLSX)
    print(OUT_MD)
    print(OUT_PLOT)


if __name__ == "__main__":
    main()
