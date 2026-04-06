"""
中介模型分析 - 框架B
Mediation Model Analysis Framework B

IV: Source, Frame, Source×Frame
M1: Trust in AI (中介1)
M2: Self-efficacy (中介2)
DV: Intention (运动行为意图)

目标：检验Source和Frame如何通过Trust和Self-efficacy影响Intention
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy.stats import norm
import warnings
warnings.filterwarnings('ignore')

BASE = "/workspaces/7100-2-2-final"
DATA_FILE = f"{BASE}/Data/7100_2.xlsx"
OUT_DIR = f"{BASE}/Output"

# ===== 数据读取与预处理 =====

df = pd.read_excel(DATA_FILE)
df = df.iloc[2:].reset_index(drop=True)

# 定义变量列索引
source_col = 28      # 来源操纵检验
frame_col = 29       # 框架操纵检验

# Intention (3项平均)
intention_cols = [33, 34, 35]

# Trust in AI (5项平均)
trust_cols = [40, 41, 42, 43, 44]

# Self-efficacy (3项平均)
se_cols = [36, 37, 38]

# Health Consciousness (6项平均，用于后续调节)
hc_cols = [45, 46, 47, 48, 49, 50]

# 提取并转换数据
df_analysis = pd.DataFrame()

# Source (文本编码)
# 0 = 人类专家, 1 = AI健康教练
source_text = df.iloc[:, source_col].astype(str)
df_analysis['Source'] = (source_text == 'AI健康教练').astype(int)

# Frame (文本编码)
# 0 = 采取行动的好处, 1 = 不采取健康行动的负面后果
frame_text = df.iloc[:, frame_col].astype(str)
df_analysis['Frame'] = frame_text.str.contains('负面|负面后果', na=False).astype(int)

# Intention (平均)
intention_data = df.iloc[:, intention_cols].copy()
for col in intention_data.columns:
    intention_data[col] = pd.to_numeric(intention_data[col], errors='coerce')
df_analysis['Intention'] = intention_data.mean(axis=1)

# Trust (平均)
trust_data = df.iloc[:, trust_cols].copy()
for col in trust_data.columns:
    trust_data[col] = pd.to_numeric(trust_data[col], errors='coerce')
df_analysis['Trust'] = trust_data.mean(axis=1)

# Self-efficacy (平均)
se_data = df.iloc[:, se_cols].copy()
for col in se_data.columns:
    se_data[col] = pd.to_numeric(se_data[col], errors='coerce')
df_analysis['SelfEfficacy'] = se_data.mean(axis=1)

# Health Consciousness (平均)
hc_data = df.iloc[:, hc_cols].copy()
for col in hc_data.columns:
    hc_data[col] = pd.to_numeric(hc_data[col], errors='coerce')
df_analysis['HealthConsciousness'] = hc_data.mean(axis=1)

# 创建交互项
df_analysis['Source_x_Frame'] = df_analysis['Source'] * df_analysis['Frame']

# 标准化处理
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
for col in ['Source', 'Frame', 'Source_x_Frame', 'Trust', 'SelfEfficacy', 'Intention']:
    df_analysis[col] = scaler.fit_transform(df_analysis[[col]])

# 删除缺失值
df_clean = df_analysis.dropna()
print(f"有效样本数: {len(df_clean)}")

# ===== 中介分析 =====

print("\n" + "="*80)
print("中介模型分析 - 框架B")
print("="*80)

# 1. 模型1: IV → DV (c pathway - 总效应)
print("\n【模型1】总效应 (Total Effect)")
print("DV ~ Source + Frame + Source×Frame")
print("-" * 80)

X = df_clean[['Source', 'Frame', 'Source_x_Frame']]
X = sm.add_constant(X)
Y = df_clean['Intention']

model_total = sm.OLS(Y, X).fit()
print(model_total.summary().tables[1])

c_source = model_total.params['Source']
c_frame = model_total.params['Frame']
c_inter = model_total.params['Source_x_Frame']

# 2. 模型2A: IV → M1 (a pathway - Trust)
print("\n【模型2A】先行路径 - Trust (a pathway)")
print("Trust ~ Source + Frame + Source×Frame")
print("-" * 80)

M1 = df_clean['Trust']
model_a1 = sm.OLS(M1, X).fit()
print(model_a1.summary().tables[1])

a1_source = model_a1.params['Source']
a1_frame = model_a1.params['Frame']
a1_inter = model_a1.params['Source_x_Frame']

# 3. 模型2B: IV → M2 (a pathway - Self-efficacy)
print("\n【模型2B】先行路径 - Self-efficacy (a pathway)")
print("Self-efficacy ~ Source + Frame + Source×Frame")
print("-" * 80)

M2 = df_clean['SelfEfficacy']
model_a2 = sm.OLS(M2, X).fit()
print(model_a2.summary().tables[1])

a2_source = model_a2.params['Source']
a2_frame = model_a2.params['Frame']
a2_inter = model_a2.params['Source_x_Frame']

# 4. 模型3: IV + M1 + M2 → DV (b & c' pathways)
print("\n【模型3】结果路径 (b pathway & 直接效应 c')")
print("Intention ~ Source + Frame + Source×Frame + Trust + Self-efficacy")
print("-" * 80)

X_full = df_clean[['Source', 'Frame', 'Source_x_Frame', 'Trust', 'SelfEfficacy']]
X_full = sm.add_constant(X_full)
Y = df_clean['Intention']

model_full = sm.OLS(Y, X_full).fit()
print(model_full.summary().tables[1])

b1_trust = model_full.params['Trust']
b2_se = model_full.params['SelfEfficacy']

c_prime_source = model_full.params['Source']
c_prime_frame = model_full.params['Frame']
c_prime_inter = model_full.params['Source_x_Frame']

# ===== 间接效应计算 =====

print("\n" + "="*80)
print("间接效应汇总 (Indirect Effects Summary)")
print("="*80)

# Source的间接效应
indirect_source_via_trust = a1_source * b1_trust
indirect_source_via_se = a2_source * b2_se
indirect_source_total = indirect_source_via_trust + indirect_source_via_se

# Frame的间接效应
indirect_frame_via_trust = a1_frame * b1_trust
indirect_frame_via_se = a2_frame * b2_se
indirect_frame_total = indirect_frame_via_trust + indirect_frame_via_se

# 交互的间接效应
indirect_inter_via_trust = a1_inter * b1_trust
indirect_inter_via_se = a2_inter * b2_se
indirect_inter_total = indirect_inter_via_trust + indirect_inter_via_se

print("\n【通过 Trust 的间接效应】")
print(f"Source → Trust → Intention: {indirect_source_via_trust:.4f}")
print(f"Frame → Trust → Intention: {indirect_frame_via_trust:.4f}")
print(f"Source×Frame → Trust → Intention: {indirect_inter_via_trust:.4f}")

print("\n【通过 Self-efficacy 的间接效应】")
print(f"Source → Self-efficacy → Intention: {indirect_source_via_se:.4f}")
print(f"Frame → Self-efficacy → Intention: {indirect_frame_via_se:.4f}")
print(f"Source×Frame → Self-efficacy → Intention: {indirect_inter_via_se:.4f}")

print("\n【总的间接效应 (Total Indirect)】")
print(f"Source: {indirect_source_total:.4f} (via Trust: {indirect_source_via_trust:.4f}, via SE: {indirect_source_via_se:.4f})")
print(f"Frame: {indirect_frame_total:.4f} (via Trust: {indirect_frame_via_trust:.4f}, via SE: {indirect_frame_via_se:.4f})")
print(f"Source×Frame: {indirect_inter_total:.4f} (via Trust: {indirect_inter_via_trust:.4f}, via SE: {indirect_inter_via_se:.4f})")

print("\n【直接效应 (Direct Effect c')】")
print(f"Source → Intention (direct): {c_prime_source:.4f}")
print(f"Frame → Intention (direct): {c_prime_frame:.4f}")
print(f"Source×Frame → Intention (direct): {c_prime_inter:.4f}")

print("\n【总效应 (Total Effect c)】")
print(f"Source: {c_source:.4f}")
print(f"Frame: {c_frame:.4f}")
print(f"Source×Frame: {c_inter:.4f}")

print("\n【效应分解】")
print(f"Source: 直接 {c_prime_source:.4f} + 间接 {indirect_source_total:.4f} = 总计 {c_source:.4f}")
print(f"Frame: 直接 {c_prime_frame:.4f} + 间接 {indirect_frame_total:.4f} = 总计 {c_frame:.4f}")
print(f"Source×Frame: 直接 {c_prime_inter:.4f} + 间接 {indirect_inter_total:.4f} = 总计 {c_inter:.4f}")

# ===== R平方与拟合度 =====

print("\n" + "="*80)
print("模型拟合度 (Model Fit)")
print("="*80)

print(f"\n模型1 (总效应模型):")
print(f"  R² = {model_total.rsquared:.4f}")
print(f"  Adj R² = {model_total.rsquared_adj:.4f}")
print(f"  F = {model_total.fvalue:.4f}, p = {model_total.f_pvalue:.4e}")

print(f"\n模型2A (Trust作为依变量):")
print(f"  R² = {model_a1.rsquared:.4f}")
print(f"  Adj R² = {model_a1.rsquared_adj:.4f}")

print(f"\n模型2B (Self-efficacy作为依变量):")
print(f"  R² = {model_a2.rsquared:.4f}")
print(f"  Adj R² = {model_a2.rsquared_adj:.4f}")

print(f"\n模型3 (完整中介模型):")
print(f"  R² = {model_full.rsquared:.4f}")
print(f"  Adj R² = {model_full.rsquared_adj:.4f}")
print(f"  F = {model_full.fvalue:.4f}, p = {model_full.f_pvalue:.4e}")

# ===== 关键结论 =====

print("\n" + "="*80)
print("关键发现 (Key Findings)")
print("="*80)

print("\n【主要路径强度排序】")
pathways = [
    ("Source → Self-efficacy → Intention", indirect_source_via_se),
    ("Source → Trust → Intention", indirect_source_via_trust),
    ("Frame → Self-efficacy → Intention", indirect_frame_via_se),
    ("Frame → Trust → Intention", indirect_frame_via_trust),
    ("Source×Frame → Self-efficacy → Intention", indirect_inter_via_se),
    ("Source×Frame → Trust → Intention", indirect_inter_via_trust),
]
pathways.sort(key=lambda x: abs(x[1]), reverse=True)
for i, (path, effect) in enumerate(pathways, 1):
    print(f"{i}. {path}: {effect:.4f}")

print("\n【中介机制结论】")
if model_full.f_pvalue < 0.05:
    print("✓ 完整中介模型显著(p<0.05)")
else:
    print("~ 完整中介模型不显著(p≥0.05)")

if abs(indirect_source_total) > 0.05:
    print(f"✓ Source通过Trust和SE的总间接效应显著 ({indirect_source_total:.4f})")
else:
    print(f"~ Source的间接效应较弱 ({indirect_source_total:.4f})")

if abs(indirect_frame_total) > 0.05:
    print(f"✓ Frame通过Trust和SE的总间接效应显著 ({indirect_frame_total:.4f})")
else:
    print(f"~ Frame的间接效应较弱 ({indirect_frame_total:.4f})")

if abs(b1_trust) > 0.1:
    print(f"✓ Trust → Intention显著 (b={b1_trust:.4f})")
else:
    print(f"~ Trust效应较弱 (b={b1_trust:.4f})")

if abs(b2_se) > 0.1:
    print(f"✓ Self-efficacy → Intention显著 (b={b2_se:.4f})")
else:
    print(f"~ Self-efficacy效应较弱 (b={b2_se:.4f})")

print("\n【下一步建议】")
if abs(indirect_source_via_trust) > abs(indirect_source_via_se):
    print("→ Trust是Source影响Intention的主要中介")
else:
    print("→ Self-efficacy是Source影响Intention的主要中介")

if abs(c_prime_source) < 0.05 and abs(indirect_source_total) > 0.05:
    print("→ Source存在完全中介效应(direct≈0, indirect>0)")
elif abs(c_prime_source) > 0.05 and abs(indirect_source_total) > 0.05:
    print("→ Source存在部分中介效应(direct>0, indirect>0)")
else:
    print("→ Source主要是直接效应，中介效应较弱")

print("\n" + "="*80)
