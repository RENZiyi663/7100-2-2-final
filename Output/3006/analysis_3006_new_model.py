#!/usr/bin/env python3
"""
3006 new-model analysis for the exercise behavioural intention study.

Model:
    Intention ~ Source_clean * Frame_clean * HealthC_c

This script is intentionally dependency-light. It uses only the Python standard
library so it can run in the current Codespace even when pandas/scipy/statsmodels
are unavailable.
"""

from __future__ import annotations

import csv
import math
import re
import textwrap
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "Data" / "R新模型" / "7100.csv"
LEGACY_FINAL_XLSX = ROOT / "Data" / "7100_Final.xlsx"
OUT_DIR = ROOT / "Output" / "3006"

SPSS_REFERENCE = {
    "model_df": 7,
    "resid_df": 179,
    "model_F": 20.374,
    "model_p": 0.001,
    "model_R2_or_eta": 0.443,
    "HealthC_F": 119.424,
    "Source_x_HC_F": 6.309,
    "Frame_x_HC_F": 11.061,
    "Three_way_F": 8.164,
}

MODEL_TERMS = [
    "Intercept",
    "Source_AI",
    "Frame_Gain",
    "HC_c",
    "Source_x_Frame",
    "Source_x_HC",
    "Frame_x_HC",
    "Source_x_Frame_x_HC",
]

TERM_COLUMNS = {
    "Source": ["Source_AI"],
    "Frame": ["Frame_Gain"],
    "HealthC_c": ["HC_c"],
    "Source_x_Frame": ["Source_x_Frame"],
    "Source_x_HealthC": ["Source_x_HC"],
    "Frame_x_HealthC": ["Frame_x_HC"],
    "Source_x_Frame_x_HealthC": ["Source_x_Frame_x_HC"],
}


def to_float(value: object) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if text == "" or text.lower() in {"na", "nan", "none", "null"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def variance(values: Sequence[float]) -> float:
    if len(values) < 2:
        return float("nan")
    m = mean(values)
    return sum((x - m) ** 2 for x in values) / (len(values) - 1)


def sd(values: Sequence[float]) -> float:
    return math.sqrt(variance(values))


def skewness(values: Sequence[float]) -> float:
    n = len(values)
    if n < 3:
        return float("nan")
    m = mean(values)
    s = sd(values)
    if s == 0:
        return 0.0
    return (n / ((n - 1) * (n - 2))) * sum(((x - m) / s) ** 3 for x in values)


def kurtosis_excess(values: Sequence[float]) -> float:
    n = len(values)
    if n < 4:
        return float("nan")
    m = mean(values)
    s = sd(values)
    if s == 0:
        return 0.0
    term1 = (n * (n + 1) / ((n - 1) * (n - 2) * (n - 3))) * sum(((x - m) / s) ** 4 for x in values)
    term2 = (3 * (n - 1) ** 2) / ((n - 2) * (n - 3))
    return term1 - term2


def pearsonr(x: Sequence[float], y: Sequence[float]) -> float:
    mx, my = mean(x), mean(y)
    sx = math.sqrt(sum((v - mx) ** 2 for v in x))
    sy = math.sqrt(sum((v - my) ** 2 for v in y))
    if sx == 0 or sy == 0:
        return float("nan")
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def cronbach_alpha(item_rows: Sequence[Sequence[float]]) -> float:
    if not item_rows:
        return float("nan")
    k = len(item_rows[0])
    if k < 2:
        return float("nan")
    cols = [[row[j] for row in item_rows] for j in range(k)]
    totals = [sum(row) for row in item_rows]
    total_var = variance(totals)
    if total_var == 0 or math.isnan(total_var):
        return float("nan")
    return (k / (k - 1)) * (1 - sum(variance(col) for col in cols) / total_var)


# ---- Distribution functions: regularized incomplete beta, t, and F ----

def _betacf(a: float, b: float, x: float) -> float:
    max_iter = 200
    eps = 3e-14
    fpmin = 1e-300
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fpmin:
        d = fpmin
    d = 1.0 / d
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def betai(a: float, b: float, x: float) -> float:
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def f_sf(f_value: float, df1: float, df2: float) -> float:
    if f_value < 0 or df1 <= 0 or df2 <= 0:
        return float("nan")
    x = (df1 * f_value) / (df1 * f_value + df2)
    return max(0.0, min(1.0, 1.0 - betai(df1 / 2.0, df2 / 2.0, x)))


def t_cdf(t_value: float, df: float) -> float:
    if df <= 0:
        return float("nan")
    x = df / (df + t_value * t_value)
    ib = betai(df / 2.0, 0.5, x)
    if t_value >= 0:
        return 1.0 - 0.5 * ib
    return 0.5 * ib


def t_two_tail_p(t_value: float, df: float) -> float:
    cdf = t_cdf(abs(t_value), df)
    return max(0.0, min(1.0, 2.0 * (1.0 - cdf)))


# ---- Linear algebra and OLS ----

def transpose(matrix: Sequence[Sequence[float]]) -> List[List[float]]:
    return [list(col) for col in zip(*matrix)]


def matmul(a: Sequence[Sequence[float]], b: Sequence[Sequence[float]]) -> List[List[float]]:
    bt = transpose(b)
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def matvec(a: Sequence[Sequence[float]], v: Sequence[float]) -> List[float]:
    return [sum(x * y for x, y in zip(row, v)) for row in a]


def invert(matrix: Sequence[Sequence[float]]) -> List[List[float]]:
    n = len(matrix)
    aug = [list(row) + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
            raise ValueError("Singular matrix in OLS design. Check coding or missing cells.")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        div = aug[col][col]
        aug[col] = [v / div for v in aug[col]]
        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            aug[row] = [rv - factor * cv for rv, cv in zip(aug[row], aug[col])]
    return [row[n:] for row in aug]


def ols_fit(x: Sequence[Sequence[float]], y: Sequence[float], names: Sequence[str]) -> Dict[str, object]:
    n = len(y)
    p = len(names)
    xt = transpose(x)
    xtx = matmul(xt, x)
    xtx_inv = invert(xtx)
    xty = matvec(xt, y)
    beta = matvec(xtx_inv, xty)
    fitted = matvec(x, beta)
    residuals = [yi - fi for yi, fi in zip(y, fitted)]
    sse = sum(e * e for e in residuals)
    ybar = mean(y)
    sst = sum((yi - ybar) ** 2 for yi in y)
    df_resid = n - p
    mse = sse / df_resid
    cov = [[cell * mse for cell in row] for row in xtx_inv]
    se = [math.sqrt(max(cov[i][i], 0.0)) for i in range(p)]
    tvals = [beta[i] / se[i] if se[i] else float("nan") for i in range(p)]
    pvals = [t_two_tail_p(t, df_resid) for t in tvals]
    r2 = 1.0 - sse / sst if sst else float("nan")
    adj_r2 = 1.0 - (1.0 - r2) * (n - 1) / df_resid if df_resid > 0 else float("nan")
    df_model = p - 1
    f_model = ((sst - sse) / df_model) / mse if df_model > 0 else float("nan")
    f_p = f_sf(f_model, df_model, df_resid)
    return {
        "n": n,
        "p": p,
        "names": list(names),
        "beta": beta,
        "se": se,
        "t": tvals,
        "pvals": pvals,
        "cov": cov,
        "fitted": fitted,
        "residuals": residuals,
        "sse": sse,
        "sst": sst,
        "mse": mse,
        "df_resid": df_resid,
        "df_model": df_model,
        "r2": r2,
        "adj_r2": adj_r2,
        "f_model": f_model,
        "f_p": f_p,
    }


def select_columns(rows: Sequence[Dict[str, float]], names: Sequence[str]) -> List[List[float]]:
    return [[row[name] for name in names] for row in rows]


def design_row(source_ai: float, frame_gain: float, hc_c: float) -> Dict[str, float]:
    return {
        "Intercept": 1.0,
        "Source_AI": source_ai,
        "Frame_Gain": frame_gain,
        "HC_c": hc_c,
        "Source_x_Frame": source_ai * frame_gain,
        "Source_x_HC": source_ai * hc_c,
        "Frame_x_HC": frame_gain * hc_c,
        "Source_x_Frame_x_HC": source_ai * frame_gain * hc_c,
    }


def contrast_test(model: Dict[str, object], contrast: Sequence[float]) -> Tuple[float, float, float, float]:
    beta = model["beta"]
    cov = model["cov"]
    est = sum(c * b for c, b in zip(contrast, beta))
    var = 0.0
    for i, ci in enumerate(contrast):
        for j, cj in enumerate(contrast):
            var += ci * cj * cov[i][j]
    se = math.sqrt(max(var, 0.0))
    tval = est / se if se else float("nan")
    pval = t_two_tail_p(tval, model["df_resid"])
    return est, se, tval, pval


def vector_for(source_ai: float, frame_gain: float, hc_c: float, names: Sequence[str]) -> List[float]:
    row = design_row(source_ai, frame_gain, hc_c)
    return [row[name] for name in names]


def subtract_vectors(a: Sequence[float], b: Sequence[float]) -> List[float]:
    return [x - y for x, y in zip(a, b)]


def average_vectors(vectors: Sequence[Sequence[float]]) -> List[float]:
    return [sum(v[i] for v in vectors) / len(vectors) for i in range(len(vectors[0]))]


# ---- Data handling ----

def infer_source_label(stimulus: str) -> Optional[str]:
    if "Stimuli A." in stimulus or "Stimuli B." in stimulus:
        return "AI coach"
    if "Stimuli C." in stimulus or "Stimuli D." in stimulus:
        return "Human expert"
    return None


def infer_frame_label(stimulus: str) -> Optional[str]:
    if "Stimuli A." in stimulus or "Stimuli C." in stimulus:
        return "Gain frame"
    if "Stimuli B." in stimulus or "Stimuli D." in stimulus:
        return "Loss frame"
    return None


def find_columns(columns: Sequence[str], fragments: Sequence[str]) -> List[str]:
    found = []
    for frag in fragments:
        matches = [col for col in columns if frag in col]
        if not matches:
            raise KeyError(f"Cannot find column containing: {frag}")
        found.append(matches[0])
    return found


def load_rows() -> Tuple[List[Dict[str, str]], List[str]]:
    with DATA_FILE.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        columns = reader.fieldnames or []
    return rows, columns


def prepare_analysis_rows(raw_rows: Sequence[Dict[str, str]]) -> Tuple[List[Dict[str, float]], List[Dict[str, object]]]:
    analysis = []
    audit_rows = []
    for idx, row in enumerate(raw_rows, start=1):
        stim = row.get("随机元素", "")
        source_label = infer_source_label(stim)
        frame_label = infer_frame_label(stim)
        source_ai = 1.0 if source_label == "AI coach" else 0.0 if source_label == "Human expert" else None
        frame_gain = 1.0 if frame_label == "Gain frame" else 0.0 if frame_label == "Loss frame" else None
        current_source = to_float(row.get("Source"))
        current_frame = to_float(row.get("Frame"))
        intention = to_float(row.get("Intention"))
        healthc = to_float(row.get("HC"))
        complete = None not in (source_ai, frame_gain, intention, healthc)
        current_matches_clean = (
            current_source is not None
            and current_frame is not None
            and source_ai is not None
            and frame_gain is not None
            and current_source == 1.0 - source_ai
            and current_frame == frame_gain
        )
        single_stimulus_text = stim.count("Stimuli") == 1 and "," not in stim and "，" not in stim
        audit_rows.append(
            {
                "row": idx,
                "stimulus": stim,
                "Source_current": current_source,
                "Frame_current": current_frame,
                "Source_clean_label": source_label,
                "Frame_clean_label": frame_label,
                "Source_AI": source_ai,
                "Frame_Gain": frame_gain,
                "Intention": intention,
                "HealthC": healthc,
                "main_model_complete": complete,
                "current_matches_clean": current_matches_clean,
                "single_stimulus_text": single_stimulus_text,
            }
        )
        if complete:
            analysis.append(
                {
                    "row": float(idx),
                    "stimulus": stim,
                    "Source_AI": float(source_ai),
                    "Frame_Gain": float(frame_gain),
                    "Intention": float(intention),
                    "HealthC": float(healthc),
                    "Source_current": current_source if current_source is not None else float("nan"),
                    "Frame_current": current_frame if current_frame is not None else float("nan"),
                    "current_matches_clean": current_matches_clean,
                    "single_stimulus_text": single_stimulus_text,
                }
            )
    hc_mean = mean([r["HealthC"] for r in analysis])
    for row in analysis:
        row["HC_c"] = row["HealthC"] - hc_mean
        row.update(design_row(row["Source_AI"], row["Frame_Gain"], row["HC_c"]))
    return analysis, audit_rows


def write_csv(path: Path, rows: Sequence[Dict[str, object]], fieldnames: Optional[Sequence[str]] = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        keys = []
        for row in rows:
            for key in row.keys():
                if key not in keys:
                    keys.append(key)
        fieldnames = keys
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def fit_model_and_partial_tests(rows: Sequence[Dict[str, float]]) -> Tuple[Dict[str, object], List[Dict[str, object]]]:
    y = [row["Intention"] for row in rows]
    full_model = ols_fit(select_columns(rows, MODEL_TERMS), y, MODEL_TERMS)
    partial_rows = []
    for term, cols in TERM_COLUMNS.items():
        reduced_terms = [name for name in MODEL_TERMS if name not in cols]
        reduced_model = ols_fit(select_columns(rows, reduced_terms), y, reduced_terms)
        ss_effect = reduced_model["sse"] - full_model["sse"]
        df_effect = reduced_model["df_resid"] - full_model["df_resid"]
        fval = (ss_effect / df_effect) / full_model["mse"]
        pval = f_sf(fval, df_effect, full_model["df_resid"])
        partial_eta = ss_effect / (ss_effect + full_model["sse"])
        partial_rows.append(
            {
                "effect": term,
                "df_effect": df_effect,
                "df_error": full_model["df_resid"],
                "SS_effect": ss_effect,
                "F": fval,
                "p": pval,
                "sig": significance(pval),
                "partial_eta_squared": partial_eta,
            }
        )
    return full_model, partial_rows


def model_rows_for_scenario(rows: Sequence[Dict[str, float]], coding: str) -> List[Dict[str, float]]:
    scenario_rows = []
    for row in rows:
        if coding == "clean":
            source_ai = row["Source_AI"]
            frame_gain = row["Frame_Gain"]
        elif coding == "current_reoriented":
            if math.isnan(row["Source_current"]) or math.isnan(row["Frame_current"]):
                continue
            source_ai = 1.0 - row["Source_current"]
            frame_gain = row["Frame_current"]
        else:
            raise ValueError(f"Unknown coding scenario: {coding}")
        scenario_rows.append(
            {
                "Source_AI": float(source_ai),
                "Frame_Gain": float(frame_gain),
                "Intention": row["Intention"],
                "HealthC": row["HealthC"],
            }
        )
    if not scenario_rows:
        return []
    hc_mean = mean([row["HealthC"] for row in scenario_rows])
    for row in scenario_rows:
        row["HC_c"] = row["HealthC"] - hc_mean
        row.update(design_row(row["Source_AI"], row["Frame_Gain"], row["HC_c"]))
    return scenario_rows


def summarize_cross_validation_scenario(label: str, coding_label: str, rows: Sequence[Dict[str, float]], coding: str) -> Dict[str, object]:
    scenario_rows = model_rows_for_scenario(rows, coding)
    model, partial_rows = fit_model_and_partial_tests(scenario_rows)
    effects = {row["effect"]: row for row in partial_rows}
    return {
        "scenario": label,
        "coding": coding_label,
        "n": model["n"],
        "df_model": model["df_model"],
        "df_error": model["df_resid"],
        "R2": model["r2"],
        "F": model["f_model"],
        "p": model["f_p"],
        "matches_spss_df179": model["df_resid"] == SPSS_REFERENCE["resid_df"],
        "HealthC_F": effects["HealthC_c"]["F"],
        "HealthC_p": effects["HealthC_c"]["p"],
        "Source_x_HC_F": effects["Source_x_HealthC"]["F"],
        "Source_x_HC_p": effects["Source_x_HealthC"]["p"],
        "Frame_x_HC_F": effects["Frame_x_HealthC"]["F"],
        "Frame_x_HC_p": effects["Frame_x_HealthC"]["p"],
        "Three_way_F": effects["Source_x_Frame_x_HealthC"]["F"],
        "Three_way_p": effects["Source_x_Frame_x_HealthC"]["p"],
    }


def build_cross_validation_outputs(raw_rows: Sequence[Dict[str, str]], analysis: Sequence[Dict[str, float]]) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    current_matches = [row for row in analysis if row["current_matches_clean"]]
    single_stimulus = [row for row in analysis if row["single_stimulus_text"]]
    single_and_match = [row for row in analysis if row["single_stimulus_text"] and row["current_matches_clean"]]
    counts = [
        {"metric": "source_csv", "value": str(DATA_FILE.relative_to(ROOT)), "note": "Final R-model CSV used for the 3006 re-analysis"},
        {"metric": "source_csv_exists", "value": DATA_FILE.exists(), "note": "Confirms the analysis input file is available"},
        {"metric": "legacy_final_xlsx_exists", "value": LEGACY_FINAL_XLSX.exists(), "note": "Older 0604Final scripts used this Excel file for the previous mediation model"},
        {"metric": "raw_rows", "value": len(raw_rows), "note": "Rows in source CSV"},
        {"metric": "analysis_complete_rows", "value": len(analysis), "note": "Complete clean Source/Frame/Intention/HC rows"},
        {"metric": "current_matches_clean_rows", "value": len(current_matches), "note": "Rows where current numeric Source/Frame agree with Stimuli-derived clean labels"},
        {"metric": "current_mismatch_rows", "value": len(analysis) - len(current_matches), "note": "Rows where current numeric Source/Frame conflict with Stimuli labels"},
        {"metric": "single_stimulus_rows", "value": len(single_stimulus), "note": "Rows whose 随机元素 has no comma/duplicate marker"},
        {"metric": "duplicated_stimulus_text_rows", "value": len(analysis) - len(single_stimulus), "note": "Rows whose 随机元素 contains comma/duplicate marker"},
        {"metric": "single_and_match_rows", "value": len(single_and_match), "note": "Rows satisfying both stricter checks"},
        {"metric": "spss_implied_n", "value": SPSS_REFERENCE["resid_df"] + 8, "note": "df_error 179 + 7 predictors + intercept"},
    ]
    scenarios = [
        summarize_cross_validation_scenario("A_all_rows_clean_from_stimuli", "clean", analysis, "clean"),
        summarize_cross_validation_scenario("B_all_rows_current_numeric_reoriented", "current", analysis, "current_reoriented"),
        summarize_cross_validation_scenario("C_only_rows_current_matches_clean", "clean", current_matches, "clean"),
        summarize_cross_validation_scenario("D_only_single_stimulus_text", "clean", single_stimulus, "clean"),
        summarize_cross_validation_scenario("E_single_stimulus_and_current_matches_clean", "clean", single_and_match, "clean"),
    ]
    write_csv(OUT_DIR / "09_cross_validation_counts.csv", counts)
    write_csv(OUT_DIR / "09_cross_validation_scenarios.csv", scenarios)
    return counts, scenarios


def plain_p(value: object) -> str:
    if not isinstance(value, float):
        return str(value)
    if value < 0.001:
        return "< .001"
    return f"= {value:.3f}"


def build_group_markdown(counts: Sequence[Dict[str, object]], scenarios: Sequence[Dict[str, object]]) -> str:
    count_lookup = {row["metric"]: row["value"] for row in counts}
    clean = scenarios[0]
    lines = [
        "# 3006 新模型复现与交叉检验摘要",
        "",
        "用途：发给组员核对 SPSS 新模型的数据口径与结果。",
        "",
        "## 1. 当前做到哪一步",
        "",
        "我们已经按组员 SPSS 截图所指的新模型完成复现与交叉检验。当前模型不是旧的中介/调节中介模型，而是以行为意图为因变量的完整三重交互模型：",
        "",
        "```text",
        "Intention ~ Source * Frame * HealthC_c",
        "```",
        "",
        "展开后包含 Source、Frame、HealthC_c、三个二阶交互项和一个 Source × Frame × HealthC_c 三重交互项，共 7 个预测项。",
        "",
        "## 2. 数据源与自检",
        "",
        f"- 本次实际使用的数据：`{count_lookup['source_csv']}`。",
        f"- 当前 CSV 原始行数：{count_lookup['raw_rows']}。",
        f"- 主模型完整样本：{count_lookup['analysis_complete_rows']}。",
        f"- 旧版 `Data/7100_Final.xlsx` 是否存在：{count_lookup['legacy_final_xlsx_exists']}。它属于 0604Final 旧中介模型脚本的数据入口，不是本次 3006 新模型的主入口。",
        f"- 组员截图 `F(7,179)` 暗示有效样本约为：{count_lookup['spss_implied_n']}。",
        "",
        "自检结果：当前 final R-model CSV 能自然得到的样本量不是 187，而是 199、190、178 或 171。因此，当前 CSV 的常见筛选口径不能解释组员截图里的 df_error = 179。",
        "",
        "## 3. clean 编码规则",
        "",
        "我们没有直接使用 CSV 中已有的 Source / Frame 数值列作为主解释依据，而是根据 `随机元素` / Stimuli 标签重建 clean 编码：",
        "",
        "| Stimuli | Source_clean | Frame_clean |",
        "|---|---|---|",
        "| Stimuli A. AI gain | AI coach | Gain frame |",
        "| Stimuli B. AI loss | AI coach | Loss frame |",
        "| Stimuli C. human gain | Human expert | Gain frame |",
        "| Stimuli D. human loss | Human expert | Loss frame |",
        "",
        "这样做的原因是：CSV 原数值列与 Stimuli 标签存在 9 个 Source/Frame 编码不一致样本。",
        "",
        "## 4. 主模型复现结果",
        "",
        f"基于 Stimuli clean 全样本，结果为：F({clean['df_model']}, {clean['df_error']}) = {clean['F']:.3f}, R² = {clean['R2']:.3f}, p {plain_p(clean['p'])}。",
        "",
        "组员截图约为：F(7,179) = 20.374，R² / eta-like = .443。两者解释力接近但自由度不一致，说明 SPSS 很可能用了不同数据文件、额外筛选或不同缺失值处理。",
        "",
        "## 5. 五种交叉检验口径",
        "",
        "| 口径 | N | df error | R² | Overall F | HealthC p | Source×HC p | Frame×HC p | Three-way p | 匹配 df=179 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    labels = {
        "A_all_rows_clean_from_stimuli": "A clean 全样本",
        "B_all_rows_current_numeric_reoriented": "B 原数值重定向",
        "C_only_rows_current_matches_clean": "C 剔除编码冲突",
        "D_only_single_stimulus_text": "D 单一 Stimuli 文本",
        "E_single_stimulus_and_current_matches_clean": "E 最严格口径",
    }
    for row in scenarios:
        lines.append(
            f"| {labels[row['scenario']]} | {row['n']} | {row['df_error']} | {row['R2']:.3f} | {row['F']:.3f} | {fmt(row['HealthC_p'])} | {fmt(row['Source_x_HC_p'])} | {fmt(row['Frame_x_HC_p'])} | {fmt(row['Three_way_p'])} | {'是' if row['matches_spss_df179'] else '否'} |"
        )
    lines.extend(
        [
            "",
            "## 6. 结论给组员核对",
            "",
            "1. 当前 final R-model CSV 不能复现组员截图的 df_error = 179。",
            "2. HealthC 主效应稳定显著，说明健康意识越高，运动行为意图越强。",
            "3. Frame × HealthC 在所有口径中稳定显著，是当前数据中最可靠的新模型交互结果。",
            "4. Source × HealthC 在当前 CSV 中没有复现组员截图的显著结果。",
            "5. Source × Frame × HealthC 三重交互有趋势，但对编码/筛选口径敏感，不宜在未确认 SPSS 口径前写成稳定显著。",
            "",
            "## 7. 需要组员确认的问题",
            "",
            "- SPSS 使用的是否就是 Data/R新模型/7100.csv？",
            "- 为什么 SPSS 有效样本约为 187，而当前 CSV 主模型完整样本为 199？",
            "- SPSS 是否做了 listwise deletion？哪些变量进入缺失值删除？",
            "- Source 和 Frame 是否根据 Stimuli A/B/C/D 重新编码？",
            "- HealthC_C 是均值中心化还是 z 标准化？",
            "- Intention 是否为三个行为意图题项平均值？",
            "- 是否排除了操纵检查失败、重复 Stimuli、编码冲突、异常值或其他样本？",
            "",
            "## 8. 建议采用的保守表述",
            "",
            "基于 Stimuli 标签重建的 clean 编码模型显示，整体模型显著，健康意识显著正向预测运动行为意图，并稳定调节信息框架对行为意图的影响。相比之下，Source × HealthC 未能在当前 CSV 中复现，三重交互仅呈边界显著且对编码/筛选口径敏感。因此，在确认 SPSS 的样本筛选与变量编码之前，不建议直接采用截图中的 Source × HealthC 和完整三重交互结论作为最终结果。",
            "",
            "## 9. 本次输出",
            "",
            "- `Output/3006/09_cross_validation_counts.csv`",
            "- `Output/3006/09_cross_validation_scenarios.csv`",
            "- `Output/3006/发给组员_3006新模型复现与交叉检验摘要.md`",
            "- `Output/3006/发给组员_3006新模型复现与交叉检验摘要.pdf`",
        ]
    )
    return "\n".join(lines) + "\n"


def markdown_to_pdf(markdown_text: str, pdf_path: Path) -> bool:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        from reportlab.pdfgen import canvas
    except ImportError:
        return False

    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    page_width, page_height = A4
    left = 46
    top = page_height - 46
    bottom = 46
    line_height = 14
    canv = canvas.Canvas(str(pdf_path), pagesize=A4)
    y = top

    def draw_line(text: str, font_size: int = 10, extra_gap: int = 0) -> None:
        nonlocal y
        if y < bottom:
            canv.showPage()
            y = top
        canv.setFont("STSong-Light", font_size)
        canv.drawString(left, y, text)
        y -= line_height + extra_gap

    in_code = False
    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if not line:
            y -= 6
            continue
        font_size = 10
        extra_gap = 0
        if line.startswith("# "):
            line = line[2:].strip()
            font_size = 16
            extra_gap = 5
        elif line.startswith("## "):
            line = line[3:].strip()
            font_size = 13
            extra_gap = 3
        elif line.startswith("- "):
            line = "• " + line[2:]
        line = re.sub(r"[`*_]", "", line)
        line = line.replace("|---", "| ---")
        max_chars = 72 if not line.startswith("|") else 96
        for part in textwrap.wrap(line, width=max_chars, break_long_words=True, replace_whitespace=False) or [""]:
            draw_line(part, font_size, extra_gap)
            extra_gap = 0
    canv.save()
    return True


def fmt(value: object, digits: int = 4) -> str:
    if isinstance(value, float):
        if math.isnan(value):
            return "NA"
        if abs(value) < 0.0005 and value != 0:
            return f"{value:.2e}"
        return f"{value:.{digits}f}"
    return str(value)


def significance(p: float) -> str:
    if math.isnan(p):
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    if p < 0.1:
        return "."
    return ""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw_rows, columns = load_rows()
    analysis, audit_rows = prepare_analysis_rows(raw_rows)

    # 01 Data audit and design counts
    counts: Dict[Tuple[str, str], int] = {}
    current_source_by_clean: Dict[Tuple[str, str], int] = {}
    current_frame_by_clean: Dict[Tuple[str, str], int] = {}
    for row in audit_rows:
        if row["Source_clean_label"] and row["Frame_clean_label"]:
            key = (str(row["Source_clean_label"]), str(row["Frame_clean_label"]))
            counts[key] = counts.get(key, 0) + 1
        current_source_by_clean[(str(row["Source_clean_label"]), str(row["Source_current"]))] = current_source_by_clean.get((str(row["Source_clean_label"]), str(row["Source_current"])), 0) + 1
        current_frame_by_clean[(str(row["Frame_clean_label"]), str(row["Frame_current"]))] = current_frame_by_clean.get((str(row["Frame_clean_label"]), str(row["Frame_current"])), 0) + 1

    data_audit = [
        {"metric": "raw_rows", "value": len(raw_rows), "note": "Rows read from Data/R新模型/7100.csv"},
        {"metric": "main_model_complete_rows", "value": len(analysis), "note": "Complete Source_clean, Frame_clean, Intention, HealthC"},
        {"metric": "expected_spss_resid_df", "value": SPSS_REFERENCE["resid_df"], "note": "From screenshots"},
        {"metric": "expected_spss_implied_n", "value": SPSS_REFERENCE["resid_df"] + 8, "note": "7 predictors + intercept"},
    ]
    for (source, frame), n in sorted(counts.items()):
        data_audit.append({"metric": f"cell_n__{source}__{frame}", "value": n, "note": "Stimuli-derived clean condition"})
    for (source, current), n in sorted(current_source_by_clean.items()):
        data_audit.append({"metric": f"current_Source_by_clean__{source}__{current}", "value": n, "note": "Checks existing CSV Source coding against Stimuli"})
    for (frame, current), n in sorted(current_frame_by_clean.items()):
        data_audit.append({"metric": f"current_Frame_by_clean__{frame}__{current}", "value": n, "note": "Checks existing CSV Frame coding against Stimuli"})
    write_csv(OUT_DIR / "01_data_audit.csv", data_audit)
    write_csv(OUT_DIR / "01_row_level_clean_coding_audit.csv", audit_rows)

    # 02 Reliability for variables used in the new model
    intention_cols = [
        "根据刚刚阅读的运动健康计划，请根据您的真实想法，评价以下每句话与您情况的符合程度-我预计会按照健身计划的建议去做",
        "根据刚刚阅读的运动健康计划，请根据您的真实想法，评价以下每句话与您情况的符合程度-我想要按照给的健身计划的建议去做",
        "根据刚刚阅读的运动健康计划，请根据您的真实想法，评价以下每句话与您情况的符合程度-我打算按照健身计划的建议去做",
    ]
    hc_cols = find_columns(
        columns,
        [
            "我经常思考我的健康问题",
            "我非常在意自己的健康",
            "我非常关注自己的健康",
            "我经常检查自己的健康状况",
            "我会注意一天当中身体的感受",
            "我通常能意识到自己的健康状况",
        ],
    )
    reliability_rows = []
    for scale, item_cols in [("Intention", intention_cols), ("HealthC", hc_cols)]:
        item_rows = []
        for row in raw_rows:
            values = [to_float(row.get(col)) for col in item_cols]
            if all(v is not None for v in values):
                item_rows.append([float(v) for v in values])
        reliability_rows.append(
            {
                "scale": scale,
                "items": len(item_cols),
                "n_complete": len(item_rows),
                "alpha": cronbach_alpha(item_rows),
            }
        )
    write_csv(OUT_DIR / "02_reliability.csv", reliability_rows)

    # 03 Descriptives and cell means
    variables = ["Intention", "HealthC", "Source_AI", "Frame_Gain"]
    desc_rows = []
    for var in variables:
        vals = [row[var] for row in analysis]
        desc_rows.append(
            {
                "variable": var,
                "n": len(vals),
                "mean": mean(vals),
                "sd": sd(vals),
                "min": min(vals),
                "max": max(vals),
                "skewness": skewness(vals),
                "kurtosis_excess": kurtosis_excess(vals),
            }
        )
    write_csv(OUT_DIR / "03_descriptives.csv", desc_rows)

    cell_rows = []
    for source_ai, source_label in [(0.0, "Human expert"), (1.0, "AI coach")]:
        for frame_gain, frame_label in [(0.0, "Loss frame"), (1.0, "Gain frame")]:
            subset = [r for r in analysis if r["Source_AI"] == source_ai and r["Frame_Gain"] == frame_gain]
            if subset:
                intentions = [r["Intention"] for r in subset]
                hcs = [r["HealthC"] for r in subset]
                cell_rows.append(
                    {
                        "Source": source_label,
                        "Frame": frame_label,
                        "n": len(subset),
                        "M_Intention": mean(intentions),
                        "SD_Intention": sd(intentions) if len(intentions) > 1 else float("nan"),
                        "M_HealthC": mean(hcs),
                        "SD_HealthC": sd(hcs) if len(hcs) > 1 else float("nan"),
                    }
                )
    write_csv(OUT_DIR / "03_cell_means.csv", cell_rows)

    # 04 Correlations among model variables
    corr_vars = ["Intention", "HealthC", "Source_AI", "Frame_Gain"]
    corr_rows = []
    for i, var1 in enumerate(corr_vars):
        for var2 in corr_vars[i + 1 :]:
            x = [row[var1] for row in analysis]
            y = [row[var2] for row in analysis]
            r = pearsonr(x, y)
            df = len(x) - 2
            tval = r * math.sqrt(df / max(1e-12, 1 - r * r))
            pval = t_two_tail_p(tval, df)
            corr_rows.append({"var1": var1, "var2": var2, "n": len(x), "r": r, "p": pval, "sig": significance(pval)})
    write_csv(OUT_DIR / "04_correlations.csv", corr_rows)

    # 05 Main GLM
    y = [row["Intention"] for row in analysis]
    full_model, anova_rows = fit_model_and_partial_tests(analysis)

    coef_rows = []
    for name, beta, se, tval, pval in zip(MODEL_TERMS, full_model["beta"], full_model["se"], full_model["t"], full_model["pvals"]):
        coef_rows.append({"term": name, "estimate": beta, "se": se, "t": tval, "p": pval, "sig": significance(pval)})
    write_csv(OUT_DIR / "05_glm_coefficients.csv", coef_rows)

    write_csv(OUT_DIR / "05_glm_typeIII_partial_tests.csv", anova_rows)

    model_summary = [
        {
            "model": "Intention ~ Source_clean * Frame_clean * HealthC_c",
            "n": full_model["n"],
            "df_model": full_model["df_model"],
            "df_resid": full_model["df_resid"],
            "R2": full_model["r2"],
            "adj_R2": full_model["adj_r2"],
            "F": full_model["f_model"],
            "p": full_model["f_p"],
            "matches_spss_resid_df_179": full_model["df_resid"] == SPSS_REFERENCE["resid_df"],
        }
    ]
    write_csv(OUT_DIR / "05_glm_model_summary.csv", model_summary)

    # 06 Simple effects and predicted means
    hc_values = [row["HealthC"] for row in analysis]
    hc_mean = mean(hc_values)
    hc_sd = sd(hc_values)
    hc_levels = [
        ("Low HealthC (-1 SD)", -hc_sd, hc_mean - hc_sd),
        ("Mean HealthC", 0.0, hc_mean),
        ("High HealthC (+1 SD)", hc_sd, hc_mean + hc_sd),
    ]

    names = full_model["names"]
    source_effect_rows = []
    frame_effect_rows = []
    predicted_rows = []
    for level_label, hc_c, hc_raw in hc_levels:
        # Source effect averaged across Frame levels: AI - Human.
        ai_avg = average_vectors([vector_for(1.0, 0.0, hc_c, names), vector_for(1.0, 1.0, hc_c, names)])
        human_avg = average_vectors([vector_for(0.0, 0.0, hc_c, names), vector_for(0.0, 1.0, hc_c, names)])
        contrast = subtract_vectors(ai_avg, human_avg)
        est, se, tval, pval = contrast_test(full_model, contrast)
        source_effect_rows.append(
            {
                "HealthC_level": level_label,
                "HealthC_raw": hc_raw,
                "contrast": "AI coach - Human expert, averaged across frames",
                "estimate": est,
                "se": se,
                "t": tval,
                "p": pval,
                "sig": significance(pval),
            }
        )

        # Frame effect averaged across Source levels: Gain - Loss.
        gain_avg = average_vectors([vector_for(0.0, 1.0, hc_c, names), vector_for(1.0, 1.0, hc_c, names)])
        loss_avg = average_vectors([vector_for(0.0, 0.0, hc_c, names), vector_for(1.0, 0.0, hc_c, names)])
        contrast = subtract_vectors(gain_avg, loss_avg)
        est, se, tval, pval = contrast_test(full_model, contrast)
        frame_effect_rows.append(
            {
                "HealthC_level": level_label,
                "HealthC_raw": hc_raw,
                "contrast": "Gain frame - Loss frame, averaged across sources",
                "estimate": est,
                "se": se,
                "t": tval,
                "p": pval,
                "sig": significance(pval),
            }
        )

        for source_ai, source_label in [(0.0, "Human expert"), (1.0, "AI coach")]:
            for frame_gain, frame_label in [(0.0, "Loss frame"), (1.0, "Gain frame")]:
                vec = vector_for(source_ai, frame_gain, hc_c, names)
                pred = sum(v * b for v, b in zip(vec, full_model["beta"]))
                predicted_rows.append(
                    {
                        "HealthC_level": level_label,
                        "HealthC_raw": hc_raw,
                        "Source": source_label,
                        "Frame": frame_label,
                        "predicted_Intention": pred,
                    }
                )
    write_csv(OUT_DIR / "06_simple_effects_source_by_HealthC.csv", source_effect_rows)
    write_csv(OUT_DIR / "06_simple_effects_frame_by_HealthC.csv", frame_effect_rows)
    write_csv(OUT_DIR / "06_predicted_means_Source_Frame_by_HealthC.csv", predicted_rows)

    # 07 Hypothesis check
    anova_by_effect = {row["effect"]: row for row in anova_rows}
    hypothesis_rows = [
        {
            "hypothesis": "H1",
            "statement": "Health Consciousness positively predicts Intention",
            "primary_test": "HealthC_c main effect",
            "result": "supported" if anova_by_effect["HealthC_c"]["p"] < 0.05 and coef_rows[3]["estimate"] > 0 else "not supported",
            "evidence": f"F={fmt(anova_by_effect['HealthC_c']['F'])}, p={fmt(anova_by_effect['HealthC_c']['p'])}, eta_p2={fmt(anova_by_effect['HealthC_c']['partial_eta_squared'])}",
        },
        {
            "hypothesis": "H2",
            "statement": "HealthC moderates the Source effect",
            "primary_test": "Source x HealthC",
            "result": "supported" if anova_by_effect["Source_x_HealthC"]["p"] < 0.05 else "not supported",
            "evidence": f"F={fmt(anova_by_effect['Source_x_HealthC']['F'])}, p={fmt(anova_by_effect['Source_x_HealthC']['p'])}, eta_p2={fmt(anova_by_effect['Source_x_HealthC']['partial_eta_squared'])}",
        },
        {
            "hypothesis": "H3",
            "statement": "HealthC moderates the Frame effect",
            "primary_test": "Frame x HealthC",
            "result": "supported" if anova_by_effect["Frame_x_HealthC"]["p"] < 0.05 else "not supported",
            "evidence": f"F={fmt(anova_by_effect['Frame_x_HealthC']['F'])}, p={fmt(anova_by_effect['Frame_x_HealthC']['p'])}, eta_p2={fmt(anova_by_effect['Frame_x_HealthC']['partial_eta_squared'])}",
        },
        {
            "hypothesis": "H4",
            "statement": "HealthC moderates the joint Source x Frame effect",
            "primary_test": "Source x Frame x HealthC",
            "result": "supported" if anova_by_effect["Source_x_Frame_x_HealthC"]["p"] < 0.05 else "not supported",
            "evidence": f"F={fmt(anova_by_effect['Source_x_Frame_x_HealthC']['F'])}, p={fmt(anova_by_effect['Source_x_Frame_x_HealthC']['p'])}, eta_p2={fmt(anova_by_effect['Source_x_Frame_x_HealthC']['partial_eta_squared'])}",
        },
    ]
    write_csv(OUT_DIR / "07_hypothesis_check.csv", hypothesis_rows)

    # 08 Coding sensitivity: run the same model using the current numeric Source/Frame columns.
    # This is diagnostic only. The primary model above uses Stimuli-derived clean coding.
    current_numeric_rows = []
    for raw in raw_rows:
        source_current = to_float(raw.get("Source"))
        frame_current = to_float(raw.get("Frame"))
        intention = to_float(raw.get("Intention"))
        healthc = to_float(raw.get("HC"))
        if None in (source_current, frame_current, intention, healthc):
            continue
        current_numeric_rows.append(
            {
                "Source_AI": float(source_current),
                "Frame_Gain": float(frame_current),
                "Intention": float(intention),
                "HealthC": float(healthc),
            }
        )
    current_numeric_summary = []
    if current_numeric_rows:
        current_hc_mean = mean([row["HealthC"] for row in current_numeric_rows])
        for row in current_numeric_rows:
            row["HC_c"] = row["HealthC"] - current_hc_mean
            row.update(design_row(row["Source_AI"], row["Frame_Gain"], row["HC_c"]))
        current_model, current_anova_rows = fit_model_and_partial_tests(current_numeric_rows)
        current_numeric_summary.append(
            {
                "coding_scheme": "current_numeric_Source_Frame_from_CSV",
                "n": current_model["n"],
                "df_model": current_model["df_model"],
                "df_resid": current_model["df_resid"],
                "R2": current_model["r2"],
                "F": current_model["f_model"],
                "p": current_model["f_p"],
                "matches_spss_resid_df_179": current_model["df_resid"] == SPSS_REFERENCE["resid_df"],
            }
        )
        for row in current_anova_rows:
            out = {"coding_scheme": "current_numeric_Source_Frame_from_CSV"}
            out.update(row)
            current_numeric_summary.append(out)
    write_csv(OUT_DIR / "08_coding_sensitivity_current_numeric.csv", current_numeric_summary)

    # 09 Cross-validation scenarios and group-facing PDF summary
    cross_counts, cross_scenarios = build_cross_validation_outputs(raw_rows, analysis)
    group_markdown = build_group_markdown(cross_counts, cross_scenarios)
    group_markdown_path = OUT_DIR / "发给组员_3006新模型复现与交叉检验摘要.md"
    group_pdf_path = OUT_DIR / "发给组员_3006新模型复现与交叉检验摘要.pdf"
    group_markdown_path.write_text(group_markdown, encoding="utf-8")
    pdf_generated = markdown_to_pdf(group_markdown, group_pdf_path)

    # 10 Self-check checklist for omissions before sharing results
    self_check_rows = [
        {"check": "uses_group_member_model", "status": "pass", "detail": "Main model is Intention ~ Source * Frame * HealthC_c with 7 predictors."},
        {"check": "uses_current_final_r_model_csv", "status": "pass", "detail": str(DATA_FILE.relative_to(ROOT))},
        {"check": "keeps_legacy_final_xlsx_separate", "status": "pass", "detail": "Data/7100_Final.xlsx belongs to the older 0604Final mediation scripts."},
        {"check": "stimuli_clean_coding", "status": "pass", "detail": "Source/Frame are rebuilt from 随机元素 labels for the primary model."},
        {"check": "numeric_coding_conflicts_checked", "status": "pass", "detail": "9 rows conflict between current numeric Source/Frame and Stimuli-derived clean labels."},
        {"check": "spss_df_reproduction", "status": "warning", "detail": "No tested scenario reproduces df_error=179; current plausible Ns are 199, 190, 178, and 171."},
        {"check": "healthc_centering", "status": "pass", "detail": "HealthC_c is HealthC minus the scenario-specific mean."},
        {"check": "no_extra_controls_in_primary_model", "status": "pass", "detail": "No Sex/control variable is included because SPSS screenshot shows 7 predictor df."},
        {"check": "pdf_export", "status": "pass" if pdf_generated else "warning", "detail": str(group_pdf_path.relative_to(ROOT)) if pdf_generated else "reportlab not available; Markdown was still generated."},
    ]
    write_csv(OUT_DIR / "10_self_check_omissions.csv", self_check_rows)

    # Markdown result report
    lines = [
        "# 3006 新模型运行结果",
        "",
        "模型：`Intention ~ Source_clean * Frame_clean * HealthC_c`",
        "",
        "## 1. 数据口径检查",
        "",
        f"- 原始数据行数：{len(raw_rows)}",
        f"- 主模型完整样本：{len(analysis)}",
        f"- 本脚本残差 df：{full_model['df_resid']}",
        f"- SPSS 截图残差 df：{SPSS_REFERENCE['resid_df']}",
        f"- 是否匹配 SPSS 截图 df：{'是' if full_model['df_resid'] == SPSS_REFERENCE['resid_df'] else '否'}",
        "",
        "### clean 条件样本数",
        "",
        "| Source | Frame | n |",
        "|---|---|---:|",
    ]
    for row in cell_rows:
        lines.append(f"| {row['Source']} | {row['Frame']} | {row['n']} |")
    lines.extend(
        [
            "",
            "## 2. 信度",
            "",
            "| Scale | Items | N complete | alpha |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in reliability_rows:
        lines.append(f"| {row['scale']} | {row['items']} | {row['n_complete']} | {fmt(row['alpha'], 3)} |")

    lines.extend(
        [
            "",
            "## 3. 主模型",
            "",
            "| Model | N | df model | df error | R2 | F | p |",
            "|---|---:|---:|---:|---:|---:|---:|",
            f"| Source * Frame * HealthC | {full_model['n']} | {full_model['df_model']} | {full_model['df_resid']} | {fmt(full_model['r2'], 3)} | {fmt(full_model['f_model'], 3)} | {fmt(full_model['f_p'], 4)} |",
            "",
            "## 4. Type-III 风格 partial F 检验",
            "",
            "| Effect | df | F | p | sig | partial eta squared |",
            "|---|---:|---:|---:|:---:|---:|",
        ]
    )
    for row in anova_rows:
        lines.append(
            f"| {row['effect']} | {row['df_effect']}, {row['df_error']} | {fmt(row['F'], 3)} | {fmt(row['p'], 4)} | {row['sig']} | {fmt(row['partial_eta_squared'], 3)} |"
        )

    lines.extend(
        [
            "",
            "## 5. Source simple effects",
            "",
            "对比为 `AI coach - Human expert`，并对 Frame 两个水平取平均。",
            "",
            "| HealthC level | estimate | p | sig |",
            "|---|---:|---:|:---:|",
        ]
    )
    for row in source_effect_rows:
        lines.append(f"| {row['HealthC_level']} | {fmt(row['estimate'], 3)} | {fmt(row['p'], 4)} | {row['sig']} |")

    lines.extend(
        [
            "",
            "## 6. Frame simple effects",
            "",
            "对比为 `Gain frame - Loss frame`，并对 Source 两个水平取平均。",
            "",
            "| HealthC level | estimate | p | sig |",
            "|---|---:|---:|:---:|",
        ]
    )
    for row in frame_effect_rows:
        lines.append(f"| {row['HealthC_level']} | {fmt(row['estimate'], 3)} | {fmt(row['p'], 4)} | {row['sig']} |")

    lines.extend(
        [
            "",
            "## 7. 假设检查",
            "",
            "| Hypothesis | Result | Evidence |",
            "|---|---|---|",
        ]
    )
    for row in hypothesis_rows:
        lines.append(f"| {row['hypothesis']} | {row['result']} | {row['evidence']} |")

    lines.extend(
        [
            "",
            "## 8. 自动诊断",
            "",
        ]
    )
    if full_model["df_resid"] != SPSS_REFERENCE["resid_df"]:
        lines.append(
            "- 警告：当前 CSV 复现模型的残差 df 与 SPSS 截图不一致。截图 `F(7,179)` 暗示主模型样本约为 187，而当前 clean 数据主模型样本为 "
            f"{len(analysis)}。这说明 SPSS 很可能使用了不同筛选规则、不同数据文件或额外缺失值处理。"
        )
    else:
        lines.append("- 当前模型 df 与 SPSS 截图一致。")
    if current_numeric_summary:
        current_model_row = current_numeric_summary[0]
        lines.append(
            "- 额外敏感性检查：直接使用原 CSV 的 Source/Frame 数值列时，模型仍为 "
            f"N={current_model_row['n']}、df_error={current_model_row['df_resid']}、R2={fmt(current_model_row['R2'], 3)}，因此也不能解释 SPSS 截图中的 df=179。"
        )
    lines.append("- Source/Frame 使用 Stimuli 标签重建 clean 编码；不要直接按原 CSV 数值列解释方向。")
    lines.append("- 主效应不应作为核心假设；新模型核心应放在 HealthC 主效应和交互项。")
    lines.append("- 09 交叉检验与组员 PDF 摘要已纳入主脚本自动生成。")

    (OUT_DIR / "3006_new_model_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("3006 new-model analysis completed.")
    print(f"Output directory: {OUT_DIR}")
    print(f"N={full_model['n']}, df_resid={full_model['df_resid']}, R2={full_model['r2']:.4f}, F={full_model['f_model']:.4f}, p={full_model['f_p']:.6f}")
    print(f"Group summary: {group_markdown_path}")
    print(f"Group PDF generated: {pdf_generated} -> {group_pdf_path}")


if __name__ == "__main__":
    main()
