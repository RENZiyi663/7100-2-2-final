"""
信度效度分析
Reliability and Validity Analysis of Survey Data
"""
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
from scipy.stats import pearsonr, spearmanr
import matplotlib.pyplot as plt
from sklearn.decomposition import FactorAnalysis
from sklearn.preprocessing import StandardScaler

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

BASE = Path(__file__).resolve().parents[1]
DATA_FILE = BASE / "Data" / "7100_2.xlsx"
OUT_DIR = BASE / "Output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =============== 数据读取与预处理 ===============

df = pd.read_excel(DATA_FILE)

# 去掉前两行（标题行和空行），从第3行开始数据
df = df.iloc[2:].reset_index(drop=True)

# 定义量表 - 使用列索引而不是完整列名
scale_indices = {
    "意图量表_Intention": [33, 34, 35],  # 我预计、我想要、我打算
    "AI评价量表_AI_Evaluation": [40, 41, 42, 43, 44],  # AI聊天机器人5项
    "健康关注量表_Health_Consciousness": [45, 46, 47, 48, 49, 50]  # 健康看法6项
}

# 将索引转换为实际列名
scales = {}
for scale_name, indices in scale_indices.items():
    scales[scale_name] = [df.columns[i] for i in indices]

# =============== 信度分析函数 ===============

def cronbach_alpha(df_items: pd.DataFrame) -> float:
    """计算Cronbach's Alpha系数"""
    d = df_items.dropna()
    k = d.shape[1]
    if k < 2 or len(d) < 2:
        return np.nan
    item_vars = d.var(axis=0, ddof=1)
    total_var = d.sum(axis=1).var(ddof=1)
    if total_var == 0:
        return np.nan
    return (k / (k - 1)) * (1 - item_vars.sum() / total_var)

def item_total_correlation(df_items: pd.DataFrame) -> pd.DataFrame:
    """计算项-总相关系数"""
    rows = []
    d = df_items.dropna()
    for c in df_items.columns:
        item_scores = d[c].astype(float)
        total_scores = d.drop(columns=[c]).astype(float).mean(axis=1)
        corr, pval = pearsonr(item_scores, total_scores)
        rows.append({
            "Item": c.replace('以下是一些关于您对自己健康看法的陈述。请根据实际情况，选择最能描述您的选项- ', '').replace('根据刚刚阅读的运动健康计划，请根据您的真实想法，评价以下每句话与您情况的符合 程度-', '').replace('根据刚刚阅读的运动健 康计划，请根据您的真实想法，评价以下每句话与您情况的符合程度-', '')[:30],
            "Item-Total Correlation": corr,
            "P-value": pval
        })
    return pd.DataFrame(rows)

def split_half_reliability(df_items: pd.DataFrame) -> dict:
    """计算分半信度"""
    d = df_items.dropna().astype(float)
    if len(d) < 3:
        return {"Spearman-Brown": np.nan, "Guttman": np.nan}
    
    n_cols = d.shape[1]
    # 奇偶分组
    half1 = d.iloc[:, :n_cols//2].sum(axis=1)
    half2 = d.iloc[:, n_cols//2:].sum(axis=1)
    
    r_half, _ = pearsonr(half1, half2)
    # Spearman-Brown校正公式
    sb = 2 * r_half / (1 + r_half) if r_half >= 0 else np.nan
    
    return {
        "Half Correlation": r_half,
        "Spearman-Brown": sb
    }

def composite_reliability(df_items: pd.DataFrame) -> dict:
    """计算组合信度(CR)和平均方差提取(AVE)"""
    d = df_items.dropna().astype(float)
    
    if len(d) < 5:
        return {"CR": np.nan, "AVE": np.nan, "n_samples": len(d)}
    
    # 使用相关系数矩阵计算
    corr_matrix = d.corr()
    
    # 简化计算：使用因子负荷估计
    # CR = (∑λ)² / [(∑λ)² + ∑(1-λ²)]
    # 这里使用项-总相关作为λ的估计
    
    loadings = []
    for col in d.columns:
        item_scores = d[col]
        total_scores = d.drop(columns=[col]).mean(axis=1)
        loading, _ = pearsonr(item_scores, total_scores)
        loadings.append(loading)
    
    loadings = np.array(loadings)
    sum_loadings = np.sum(loadings)
    sum_sq_loadings = np.sum(loadings ** 2)
    
    # CR = (∑λ)² / [(∑λ)² + k - ∑λ²]
    k = len(loadings)
    cr = (sum_sq_loadings) / (sum_sq_loadings + (k - sum_loadings))
    
    # AVE = ∑λ² / k
    ave = sum_sq_loadings / k
    
    return {
        "CR": cr,
        "AVE": ave,
        "Mean Loading": np.mean(loadings),
        "n_samples": len(d)
    }

def internal_consistency_report(df_items: pd.DataFrame, scale_name: str) -> dict:
    """生成内部一致性报告"""
    # 数值转换
    df_numeric = df_items.copy()
    for col in df_numeric.columns:
        df_numeric[col] = pd.to_numeric(df_numeric[col], errors='coerce')
    
    # 去掉全为NaN的行和列
    df_numeric = df_numeric.dropna(how='all', axis=0).dropna(how='all', axis=1)
    
    n_valid = df_numeric.dropna().shape[0]
    n_items = df_numeric.shape[1]
    
    if n_valid < 3 or n_items < 2:
        return {
            "Scale": scale_name,
            "n_items": n_items,
            "n_samples": n_valid,
            "Status": "Sample size or items too small"
        }
    
    report = {
        "Scale": scale_name,
        "n_items": n_items,
        "n_samples": n_valid,
        "Cronbach_Alpha": cronbach_alpha(df_numeric),
    }
    
    # 分半信度
    split_half_result = split_half_reliability(df_numeric)
    report.update(split_half_result)
    
    # 组合信度
    cr_result = composite_reliability(df_numeric)
    report.update(cr_result)
    
    return report

# =============== 效度分析函数 ===============

def exploratory_factor_analysis(df_items: pd.DataFrame, n_factors: int = None) -> dict:
    """探索性因数分析"""
    df_numeric = df_items.copy()
    for col in df_numeric.columns:
        df_numeric[col] = pd.to_numeric(df_numeric[col], errors='coerce')
    
    df_numeric = df_numeric.dropna()
    
    if len(df_numeric) < 5 or df_numeric.shape[1] < 2:
        return {"Status": "Insufficient data for EFA"}
    
    # 标准化
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df_numeric)
    
    # 自动确定因子数或使用指定的
    if n_factors is None:
        n_factors = min(3, df_numeric.shape[1] - 1)
    
    n_factors = min(n_factors, df_numeric.shape[1])
    
    # 因数分析
    fa = FactorAnalysis(n_components=n_factors, random_state=42, max_iter=1000)
    loadings = fa.fit_transform(df_scaled)
    
    # 获取因子负荷
    factor_loadings = pd.DataFrame(
        fa.components_.T,
        columns=[f"Factor_{i+1}" for i in range(n_factors)],
        index=df_numeric.columns
    )
    
    return {
        "n_factors": n_factors,
        "loadings": factor_loadings,
        "variance_explained": np.sum(np.var(loadings, axis=0)),
        "n_samples": len(df_numeric)
    }

def kmo_bartlett(df_items: pd.DataFrame) -> dict:
    """KMO和Bartlett球形检验"""
    from scipy.stats import chi2
    
    df_numeric = df_items.copy()
    for col in df_numeric.columns:
        df_numeric[col] = pd.to_numeric(df_numeric[col], errors='coerce')
    
    df_numeric = df_numeric.dropna()
    
    if len(df_numeric) < 5:
        return {"Status": "Insufficient data"}
    
    corr_matrix = df_numeric.corr()
    
    # KMO (Kaiser-Meyer-Olkin)
    n_vars = corr_matrix.shape[0]
    
    # 相关系数矩阵的平方
    r_sq = corr_matrix ** 2
    
    # 计算KMO
    sum_r_sq = r_sq.sum().sum() - np.trace(r_sq)
    
    # 逆矩阵
    try:
        inv_corr = np.linalg.inv(corr_matrix)
        partial_corr_sq = (inv_corr ** 2).sum().sum() - np.trace(inv_corr ** 2)
        kmo = sum_r_sq / (sum_r_sq + partial_corr_sq)
    except:
        kmo = np.nan
    
    # Bartlett球形检验
    n = len(df_numeric)
    det_r = np.linalg.det(corr_matrix)
    chi2_val = -(n - 1 - (2 * n_vars + 5) / 6) * np.log(det_r)
    df = (n_vars * (n_vars - 1)) / 2
    pval = 1 - chi2.cdf(chi2_val, df)
    
    return {
        "KMO": kmo,
        "Bartlett_Chi2": chi2_val,
        "Bartlett_df": df,
        "Bartlett_pvalue": pval
    }

# =============== 主分析流程 ===============

def main():
    print("=" * 80)
    print("信度效度分析报告")
    print("=" * 80)
    
    results = {}
    
    # 为每个量表进行分析
    for scale_name, col_list in scales.items():
        print(f"\n{'='*80}")
        print(f"量表: {scale_name}")
        print(f"{'='*80}")
        
        # 提取该量表的数据
        df_scale = df[col_list].copy()
        
        # 转换为数值
        for col in df_scale.columns:
            df_scale[col] = pd.to_numeric(df_scale[col], errors='coerce')
        
        print(f"\n【基本统计】")
        print(f"项目数: {len(col_list)}")
        print(f"有效样本数: {df_scale.dropna().shape[0]}")
        print(f"缺失数据: {df_scale.isna().sum().sum()}")
        
        # ===== 信度分析 =====
        print(f"\n【信度分析】")
        
        reliability = internal_consistency_report(df_scale, scale_name)
        
        print(f"Cronbach's Alpha: {reliability.get('Cronbach_Alpha', np.nan):.4f}")
        print(f"分半信度 (Spearman-Brown): {reliability.get('Spearman-Brown', np.nan):.4f}")
        print(f"复合信度 (CR): {reliability.get('CR', np.nan):.4f}")
        print(f"平均方差提取 (AVE): {reliability.get('AVE', np.nan):.4f}")
        print(f"平均因子负荷: {reliability.get('Mean Loading', np.nan):.4f}")
        
        # 项-总相关
        print(f"\n【项-总相关】")
        item_corr = item_total_correlation(df_scale)
        print(item_corr.to_string(index=False))
        
        # ===== 效度分析 =====
        print(f"\n【效度分析 - KMO和Bartlett检验】")
        
        kmo_bartlett_result = kmo_bartlett(df_scale)
        print(f"KMO值: {kmo_bartlett_result.get('KMO', np.nan):.4f}")
        print(f"Bartlett检验χ²: {kmo_bartlett_result.get('Bartlett_Chi2', np.nan):.4f}")
        print(f"Bartlett检验p值: {kmo_bartlett_result.get('Bartlett_pvalue', np.nan):.4e}")
        
        # 探索性因数分析
        print(f"\n【探索性因数分析】")
        efa_result = exploratory_factor_analysis(df_scale, n_factors=min(3, len(col_list)-1))
        
        if "loadings" in efa_result:
            print(f"建议因子数: {efa_result['n_factors']}")
            print(f"解释方差: {efa_result['variance_explained']:.4f}")
            print(f"\n因子负荷矩阵:")
            print(efa_result['loadings'].to_string())
        else:
            print(f"Status: {efa_result.get('Status', 'Unknown error')}")
        
        results[scale_name] = {
            'reliability': reliability,
            'item_corr': item_corr,
            'kmo_bartlett': kmo_bartlett_result,
            'efa': efa_result
        }
    
    # ===== 生成总结表格 =====
    print(f"\n{'='*80}")
    print("总结表格 - 信度系数")
    print(f"{'='*80}\n")
    
    summary_data = []
    for scale_name, res in results.items():
        reliability = res['reliability']
        summary_data.append({
            '量表': scale_name.split('_')[1],
            'Cronbach\'s α': f"{reliability.get('Cronbach_Alpha', np.nan):.4f}",
            'Spearman-Brown': f"{reliability.get('Spearman-Brown', np.nan):.4f}",
            '复合信度CR': f"{reliability.get('CR', np.nan):.4f}",
            'AVE': f"{reliability.get('AVE', np.nan):.4f}",
            '样本数': reliability.get('n_samples', 'N/A')
        })
    
    summary_df = pd.DataFrame(summary_data)
    print(summary_df.to_string(index=False))
    
    # 保存结果
    output_file = OUT_DIR / "reliability_validity_results.xlsx"
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        summary_df.to_excel(writer, sheet_name='信度总结', index=False)
        
        for scale_name, res in results.items():
            sheet_name = scale_name.split('_')[1][:25]  # 限制sheet名长度
            res['item_corr'].to_excel(writer, sheet_name=f"{sheet_name}_项相关", index=False)
            
            if 'loadings' in res['efa']:
                res['efa']['loadings'].to_excel(writer, sheet_name=f"{sheet_name}_EFA")
    
    print(f"\n✓ 分析结果已保存到: {output_file}")
    
    return results

if __name__ == "__main__":
    main()
