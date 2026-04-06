"""
中介调节模型分析 (Framework C - Moderated Mediation)
Health Consciousness 作为调节变量
"""

import pandas as pd
import numpy as np
from statsmodels.formula.api import ols
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 1. 数据加载与处理
# ============================================================================

df_raw = pd.read_excel('Data/7100_2.xlsx')

# 跳过元数据行，从第2行（index=2）开始读取实际数据
df = df_raw.iloc[2:].reset_index(drop=True)

# 初始化分析数据集
df_analysis = pd.DataFrame()

# 【关键编码1】Source变量（列29）: AI vs 人类专家
source_text = df.iloc[:, 28].astype(str)  # 列29，0-indexed为28
df_analysis['Source'] = (source_text == 'AI健康教练').astype(int)
# Source编码：AI健康教练=1, 人类专家=0

# 【关键编码2】Frame变量（列30）: 损失框架 vs 收益框架
frame_text = df.iloc[:, 29].astype(str)  # 列30，0-indexed为29
# 损失框架包含"负面"或"负面后果"；收益框架为"采取行动的好处"
df_analysis['Frame'] = frame_text.str.contains('负面|后果', na=False).astype(int)
# Frame编码：损失框架=1, 收益框架=0

# 交互项
df_analysis['SourcexFrame'] = df_analysis['Source'] * df_analysis['Frame']

# 【保序复合评分】各变量通过均值计算（先转换为数值）
intention_cols = df.iloc[:, [33, 34, 35]].apply(pd.to_numeric, errors='coerce')
df_analysis['Intention'] = intention_cols.mean(axis=1)  # 列33-35

se_cols = df.iloc[:, [36, 37, 38]].apply(pd.to_numeric, errors='coerce')
df_analysis['SelfEfficacy'] = se_cols.mean(axis=1)  # 列36-38

trust_cols = df.iloc[:, [40, 41, 42, 43, 44]].apply(pd.to_numeric, errors='coerce')
df_analysis['Trust'] = trust_cols.mean(axis=1)  # 列40-44

hc_cols = df.iloc[:, [45, 46, 47, 48, 49, 50]].apply(pd.to_numeric, errors='coerce')
df_analysis['HealthConsciousness'] = hc_cols.mean(axis=1)  # 列45-50

print(f"有效样本数: {len(df_analysis)}")
print(f"缺失值检查:\n{df_analysis.isnull().sum()}\n")

# ============================================================================
# 2. 标准化与中心化处理
# ============================================================================

# 二元变量（Source, Frame）不需要标准化（已是0/1）
# 对连续变量进行标准化
scaler = StandardScaler()
continuous_vars = ['Intention', 'Trust', 'SelfEfficacy', 'HealthConsciousness']

for col in continuous_vars:
    df_analysis[col] = scaler.fit_transform(df_analysis[[col]])

# 创建中心化版本（便于解释交互项）
df_analysis['HC_centered'] = df_analysis['HealthConsciousness'] - df_analysis['HealthConsciousness'].mean()
df_analysis['Trust_centered'] = df_analysis['Trust'] - df_analysis['Trust'].mean()
df_analysis['SE_centered'] = df_analysis['SelfEfficacy'] - df_analysis['SelfEfficacy'].mean()

# 交互项：Source×HC, Frame×HC, Interaction×HC
# （使用原始未中心化版本，以保持二元变量的解释性）
df_analysis['SourcexHC'] = df_analysis['Source'] * df_analysis['HC_centered']
df_analysis['FramexHC'] = df_analysis['Frame'] * df_analysis['HC_centered']
df_analysis['InteractionxHC'] = df_analysis['SourcexFrame'] * df_analysis['HC_centered']

# M→DV的调节交互
df_analysis['TrustxHC'] = df_analysis['Trust_centered'] * df_analysis['HC_centered']
df_analysis['SExHC'] = df_analysis['SE_centered'] * df_analysis['HC_centered']

print("=" * 80)
print("编码解释")
print("=" * 80)
print("""
【Source编码】
  1 = AI健康教练 (AI Coach)
  0 = 人类专家 (Human Expert)
  → 正向系数表示：AI相比人类的效应

【Frame编码】
  1 = 损失框架 (Loss Frame) - "不采取健康行动的负面后果"
  0 = 收益框架 (Gain Frame) - "采取行动的好处"
  → 正向系数表示：损失框架相比收益框架的效应

【变量关系】
Source（信息来源）和Frame（框架类型）如何通过心理机制（Trust信任、
Self-efficacy自我效能）影响Intention（行为意图），以及这些路径如何被
Health Consciousness（健康意识）所调节。
""")

# ============================================================================
# 3. 核心回归：框架Framework B（基准）
# ============================================================================

print("\n" + "=" * 80)
print("【框架B-基准】总效应与先行路径（无调节）")
print("=" * 80)

# 模型1：直接效应
model_1 = ols('Intention ~ Source + Frame + SourcexFrame', data=df_analysis).fit()
print("\n【模型1】总效应 (Direct Effect - c pathway)")
print(model_1.summary().tables[1])
print(f"R² = {model_1.rsquared:.4f}, F = {model_1.fvalue:.4f}, p = {model_1.f_pvalue:.6f}")

# 模型2A：Trust先行路径
model_2a = ols('Trust ~ Source + Frame + SourcexFrame', data=df_analysis).fit()
print("\n【模型2A】信任路径 (Trust a-pathways, 无调节)")
print(model_2a.summary().tables[1])

# 模型2B：SE先行路径
model_2b = ols('SelfEfficacy ~ Source + Frame + SourcexFrame', data=df_analysis).fit()
print("\n【模型2B】效能路径 (SE a-pathways, 无调节)")
print(model_2b.summary().tables[1])

# 模型3：完整中介
model_3 = ols('Intention ~ Source + Frame + SourcexFrame + Trust + SelfEfficacy', 
              data=df_analysis).fit()
print("\n【模型3】完整中介模型 (Complete Mediation, 无调节)")
print(model_3.summary().tables[1])
print(f"R² = {model_3.rsquared:.4f}, F = {model_3.fvalue:.4f}, p = {model_3.f_pvalue:.6f}")

# ============================================================================
# 4. 核心分析：框架C（调节中介）- b路径调节
# ============================================================================

print("\n\n" + "=" * 80)
print("【框架C-调节中介】b路径调节 (HC调节中介→结果关系)")
print("=" * 80)

# 模型C1：完整调节中介模型（M→DV路径中加入HC调节）
model_c1 = ols(
    'Intention ~ Source + Frame + SourcexFrame + Trust + SelfEfficacy + '
    'HealthConsciousness + TrustxHC + SExHC',
    data=df_analysis
).fit()

print("\n【模型C1】M→DV b路径的HC调节")
print(model_c1.summary().tables[1])
print(f"R² = {model_c1.rsquared:.4f}, Adj R² = {model_c1.rsquared_adj:.4f}")
print(f"F = {model_c1.fvalue:.4f}, p = {model_c1.f_pvalue:.6f}")

# ============================================================================
# 5. 核心分析：框架C（调节中介）- a路径调节
# ============================================================================

print("\n" + "=" * 80)
print("【框架C-调节中介】a路径调节 (HC调节独立变量→中介关系)")
print("=" * 80)

# 模型C2A：Source/Frame → Trust，加入HC调节
model_c2a = ols(
    'Trust ~ Source + Frame + SourcexFrame + HealthConsciousness + '
    'SourcexHC + FramexHC + InteractionxHC',
    data=df_analysis
).fit()

print("\n【模型C2A】IV→Trust a路径的HC调节")
print(model_c2a.summary().tables[1])

# 模型C2B：Source/Frame → SE，加入HC调节
model_c2b = ols(
    'SelfEfficacy ~ Source + Frame + SourcexFrame + HealthConsciousness + '
    'SourcexHC + FramexHC + InteractionxHC',
    data=df_analysis
).fit()

print("\n【模型C2B】IV→SE a路径的HC调节")
print(model_c2b.summary().tables[1])

# ============================================================================
# 6. 完整调节中介模型（同时调节a路径和b路径）
# ============================================================================

print("\n\n" + "=" * 80)
print("【框架C-完整】同时调节a路径与b路径")
print("=" * 80)

# 先重估包含a路径调节的中介值
df_pred_c2a = pd.DataFrame({
    'Source': df_analysis['Source'],
    'Frame': df_analysis['Frame'],
    'SourcexFrame': df_analysis['SourcexFrame'],
    'HealthConsciousness': df_analysis['HealthConsciousness'],
    'SourcexHC': df_analysis['SourcexHC'],
    'FramexHC': df_analysis['FramexHC'],
    'InteractionxHC': df_analysis['InteractionxHC']
})

df_analysis['Trust_pred_c2a'] = model_c2a.predict(df_pred_c2a)
df_analysis['Trust_pred_c2a_centered'] = df_analysis['Trust_pred_c2a'] - df_analysis['Trust_pred_c2a'].mean()

df_pred_c2b = pd.DataFrame({
    'Source': df_analysis['Source'],
    'Frame': df_analysis['Frame'],
    'SourcexFrame': df_analysis['SourcexFrame'],
    'HealthConsciousness': df_analysis['HealthConsciousness'],
    'SourcexHC': df_analysis['SourcexHC'],
    'FramexHC': df_analysis['FramexHC'],
    'InteractionxHC': df_analysis['InteractionxHC']
})

df_analysis['SE_pred_c2b'] = model_c2b.predict(df_pred_c2b)
df_analysis['SE_pred_c2b_centered'] = df_analysis['SE_pred_c2b'] - df_analysis['SE_pred_c2b'].mean()

# 在包含调节中介的完整模型中，基于a路径调节的预测中介
model_c_full = ols(
    'Intention ~ Source + Frame + SourcexFrame + HealthConsciousness + '
    'SourcexHC + FramexHC + InteractionxHC + '
    'Trust_pred_c2a + SelfEfficacy + '
    'Trust_pred_c2a:HealthConsciousness + SelfEfficacy:HealthConsciousness',
    data=df_analysis
).fit()

print("\n【模型C-Full】完整调节中介模型（a路径+b路径同时调节）")
print(model_c_full.summary().tables[1])
print(f"R² = {model_c_full.rsquared:.4f}, Adj R² = {model_c_full.rsquared_adj:.4f}")

# ============================================================================
# 7. 条件间接效应计算（在HC高/中/低水平）
# ============================================================================

print("\n\n" + "=" * 80)
print("【条件间接效应】在不同HC水平下的间接效应")
print("=" * 80)

# HC的三个水平：-1SD, 平均值, +1SD
hc_levels = {
    '低 (Mean-1SD)': df_analysis['HealthConsciousness'].mean() - df_analysis['HealthConsciousness'].std(),
    '中 (Mean)': df_analysis['HealthConsciousness'].mean(),
    '高 (Mean+1SD)': df_analysis['HealthConsciousness'].mean() + df_analysis['HealthConsciousness'].std()
}

print("\nHealth Consciousness水平:")
for level_name, hc_value in hc_levels.items():
    print(f"  {level_name}: {hc_value:.3f}")

conditional_indirect = {}

for level_name, hc_val in hc_levels.items():
    print(f"\n--- {level_name} 时的效应 ---")
    
    # a路径系数（从model_c2a）
    a_source_trust = model_c2a.params['Source'] + model_c2a.params['SourcexHC'] * hc_val
    a_frame_trust = model_c2a.params['Frame'] + model_c2a.params['FramexHC'] * hc_val
    a_interact_trust = model_c2a.params['SourcexFrame'] + model_c2a.params['InteractionxHC'] * hc_val
    
    a_source_se = model_c2b.params['Source'] + model_c2b.params['SourcexHC'] * hc_val
    a_frame_se = model_c2b.params['Frame'] + model_c2b.params['FramexHC'] * hc_val
    a_interact_se = model_c2b.params['SourcexFrame'] + model_c2b.params['InteractionxHC'] * hc_val
    
    # b路径系数（从model_c1）
    b_trust = model_c1.params['Trust'] + model_c1.params['TrustxHC'] * hc_val
    b_se = model_c1.params['SelfEfficacy'] + model_c1.params['SExHC'] * hc_val
    
    # 间接效应
    ie_source_trust = a_source_trust * b_trust
    ie_source_se = a_source_se * b_se
    ie_source_total = ie_source_trust + ie_source_se
    
    ie_frame_trust = a_frame_trust * b_trust
    ie_frame_se = a_frame_se * b_se
    ie_frame_total = ie_frame_trust + ie_frame_se
    
    ie_interact_trust = a_interact_trust * b_trust
    ie_interact_se = a_interact_se * b_se
    ie_interact_total = ie_interact_trust + ie_interact_se
    
    conditional_indirect[level_name] = {
        'Source': ie_source_total,
        'Frame': ie_frame_total,
        'Interaction': ie_interact_total,
        'Source_via_Trust': ie_source_trust,
        'Source_via_SE': ie_source_se,
        'Frame_via_Trust': ie_frame_trust,
        'Frame_via_SE': ie_frame_se,
        'a_source_trust': a_source_trust,
        'a_frame_se': a_frame_se,
        'b_trust': b_trust,
        'b_se': b_se
    }
    
    print(f"Source间接效应: {ie_source_total:.4f}")
    print(f"  → via Trust: {ie_source_trust:.4f} (a={a_source_trust:.3f}, b={b_trust:.3f})")
    print(f"  → via SE: {ie_source_se:.4f} (a={a_source_se:.3f}, b={b_se:.3f})")
    print(f"Frame间接效应: {ie_frame_total:.4f}")
    print(f"  → via Trust: {ie_frame_trust:.4f} (a={a_frame_trust:.3f}, b={b_trust:.3f})")
    print(f"  → via SE: {ie_frame_se:.4f} (a={a_frame_se:.3f}, b={b_se:.3f})")
    print(f"交互间接效应: {ie_interact_total:.4f}")
    print(f"  → via Trust: {ie_interact_trust:.4f}")
    print(f"  → via SE: {ie_interact_se:.4f}")

# ============================================================================
# 8. 调节效应总结
# ============================================================================

print("\n\n" + "=" * 80)
print("【调节效应总结】HC对各路径的调节强度")
print("=" * 80)

print("\n【b路径调节】(Trust→Intention 和 SE→Intention)")
print(f"Trust×HC系数: {model_c1.params.get('TrustxHC', np.nan):.4f}, p={model_c1.pvalues.get('TrustxHC', np.nan):.4f}")
print(f"SE×HC系数: {model_c1.params.get('SExHC', np.nan):.4f}, p={model_c1.pvalues.get('SExHC', np.nan):.4f}")
print("解释: 正向系数表示HC越高，该中介路径越强")

print("\n【a路径调节-Trust】(IV→Trust)")
print(f"Source×HC: {model_c2a.params.get('SourcexHC', np.nan):.4f}, p={model_c2a.pvalues.get('SourcexHC', np.nan):.4f}")
print(f"Frame×HC: {model_c2a.params.get('FramexHC', np.nan):.4f}, p={model_c2a.pvalues.get('FramexHC', np.nan):.4f}")
print(f"Interaction×HC: {model_c2a.params.get('InteractionxHC', np.nan):.4f}, p={model_c2a.pvalues.get('InteractionxHC', np.nan):.4f}")

print("\n【a路径调节-SE】(IV→SE)")
print(f"Source×HC: {model_c2b.params.get('SourcexHC', np.nan):.4f}, p={model_c2b.pvalues.get('SourcexHC', np.nan):.4f}")
print(f"Frame×HC: {model_c2b.params.get('FramexHC', np.nan):.4f}, p={model_c2b.pvalues.get('FramexHC', np.nan):.4f}")
print(f"Interaction×HC: {model_c2b.params.get('InteractionxHC', np.nan):.4f}, p={model_c2b.pvalues.get('InteractionxHC', np.nan):.4f}")

# ============================================================================
# 9. 条件间接效应表格
# ============================================================================

print("\n\n" + "=" * 80)
print("【条件间接效应对比表】间接效应如何随HC变化")
print("=" * 80)

ie_df = pd.DataFrame({
    'HC水平': list(conditional_indirect.keys()),
    'Source间接效应': [conditional_indirect[k]['Source'] for k in conditional_indirect.keys()],
    'Frame间接效应': [conditional_indirect[k]['Frame'] for k in conditional_indirect.keys()],
    '交互间接效应': [conditional_indirect[k]['Interaction'] for k in conditional_indirect.keys()]
})

print("\n")
print(ie_df.to_string(index=False))

# ============================================================================
# 10. 模型比较
# ============================================================================

print("\n\n" + "=" * 80)
print("【模型比较】调节如何改进模型拟合")
print("=" * 80)

comparison = pd.DataFrame({
    '模型': ['Model 3 (无调节)', 'Model C1 (b路径调节)', 'Model C-Full (全调节)'],
    'R²': [model_3.rsquared, model_c1.rsquared, model_c_full.rsquared],
    'Adj R²': [model_3.rsquared_adj, model_c1.rsquared_adj, model_c_full.rsquared_adj],
    'F统计': [model_3.fvalue, model_c1.fvalue, model_c_full.fvalue],
    'p值': [model_3.f_pvalue, model_c1.f_pvalue, model_c_full.f_pvalue]
})

print("\n")
print(comparison.to_string(index=False))
print("\nR²改进幅度:")
print(f"  Model 3 → Model C1: {(model_c1.rsquared - model_3.rsquared):.4f} ({(model_c1.rsquared/model_3.rsquared - 1)*100:.1f}%)")
print(f"  Model 3 → Model C-Full: {(model_c_full.rsquared - model_3.rsquared):.4f} ({(model_c_full.rsquared/model_3.rsquared - 1)*100:.1f}%)")

print("\n" + "=" * 80)
print("【分析完成】")
print("=" * 80)
