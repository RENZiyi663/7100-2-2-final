"""
线上社会心理学实验：信息来源、信息框架对运动意图的影响研究
完整分析框架（Python 3.12.1）

【调节中介模型 - Model C】
研究问题：Health Consciousness如何调节Trust和Self-Efficacy介导的信息效果路径？

数据说明：
- 收集平台：国内专业问卷平台Credamo
- 样本量：201人
- 样本特征：18岁以上在职职场人员，绝大多数城市群体
- 数据收集时间：2026年3月30日-2026年4月6日
- 实验类型：线上社会心理学实验
- 分析工具：Python 3.12.1 + statsmodels + scikit-learn
"""

import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.formula.api import ols
from sklearn.preprocessing import StandardScaler
import warnings
import os
from datetime import datetime
warnings.filterwarnings('ignore')

# ============================================================================
# 0. 初始化与文件配置
# ============================================================================

OUTPUT_DIR = '/workspaces/7100-2-2-final/Output/0604Final'
DATA_FILE = '/workspaces/7100-2-2-final/Data/7100_Final.xlsx'

# 创建输出文件
output_file = os.path.join(OUTPUT_DIR, '终极分析报告_含Methods.txt')
output_handle = open(output_file, 'w', encoding='utf-8')

def log_output(content):
    """同时打印和保存输出"""
    print(content)
    output_handle.write(content + '\n')

# ============================================================================
# 1. 论文Methods部分（完整版）
# ============================================================================

log_output("=" * 100)
log_output("《线上社会心理学实验：信息来源和信息框架对运动意图的影响研究》")
log_output("=" * 100)
log_output("")
log_output("数据收集时间：2026年3月30日-2026年4月6日")
log_output("方法学版本：Python 3.12.1 & statsmodels")
log_output("生成时间：" + datetime.now().strftime("%Y年%m月%d日 %H:%M:%S"))
log_output("")

log_output("=" * 100)
log_output("《Methods（方法学部分）》")
log_output("=" * 100)
log_output("")

log_output("### 1. 研究参与者")
log_output("---")
log_output("""
本研究通过国内领先的专业问卷平台Credamo进行在线数据收集。研究参与者包括N=201名在职
职场人员，年龄均为18岁以上。样本主要特征如下：

• 样本来源：Credamo在线问卷平台（国内主要社会调查、商业问卷、学术研究平台）
• 样本量：N = 201
• 样本特征：
  - 年龄：18岁以上的全职/兼职/灵活就业/自雇等在职人员
  - 地理分布：绝大多数参与者为城市群体
  - 包含多种职业类型和工作方式
  
• 数据收集期间：2026年3月30日至2026年4月6日（共8天）
• 收集方式：在线问卷填答
• 填答设备：涵盖桌面/移动等多种设备类型和浏览器
""")

log_output("\n### 2. 研究设计")
log_output("---")
log_output("""
本研究采用线上2×2因子实验设计（between-subjects），自变量包括：
  
• 独立变量（Independent Variable）：
  1) 信息来源（Source）：{AI健康教练 vs. 人类专家} 
  2) 信息框架（Frame）：{损失框架 vs. 收益框架}
    - 损失框架：强调"不采取健康行动的负面后果"
    - 收益框架：强调"采取行动的好处"

• 因变量（Dependent Variable）：
  - 行为意图（Behavioral Intention）：参与者对采取推荐运动行为的意图

• 中介变量（Mediators）：
  - 信任度（Trust）：对信息来源的信任程度
  - 自我效能（Self-Efficacy）：对自己能完成推荐运动的能力信心

• 调节变量（Moderator）：
  - 健康意识（Health Consciousness）：个体对健康问题的关注程度和自我认知
  
参与者被随机分配到四种实验条件之一（AI-损失、AI-收益、人类-损失、人类-收益），
然后阅读相应的健身计划建议，并对上述变量进行评分。
""")

log_output("\n### 3. 测量工具")
log_output("---")
log_output("""
所有测量工具均采用李克特量表（Likert Scale），并通过复合评分（composite score）
进行聚合分析。具体如下：

#### 3.1 行为意图（Behavioral Intention, Q4部分）- 3个题目
  题目示例：
  • 我预计会按照健身计划的建议去做
  • 我想要按照给的健身计划的建议去做
  • 我打算按照健身计划的建议去做
  计分：取三项平均值作为意图得分
  
#### 3.2 自我效能（Self-Efficacy）- 3个题目
  题目示例：
  • 如果你真的很有动力，对你来说，接下来一个月里坚持规律运动的难易程度是？
  • 如果你真的很有动力，你有多大信心能在接下来一个月里坚持规律运动？
  • 如果你真的很有动力，你有多确定自己能在接下来一个月里坚持规律运动？
  计分：取三项平均值
  
#### 3.3 信任度（Trust）- 5个题目
  题目示例：
  • 您觉得AI聊天机器人/专家是[可靠的、值得信赖的、诚实的、有能力的、值得尊重的]
  计分：取五项平均值
  
#### 3.4 健康意识（Health Consciousness）- 6个题目
  题目示例：
  • 我经常思考我的健康问题
  • 我非常在意自己的健康
  • 我非常关注自己的健康
  • 我经常检查自己的健康状况
  • 我会注意一天当中身体的感受
  • 我通常能意识到自己的健康状况
  计分：取六项平均值
""")

log_output("\n### 4. 数据处理与编码")
log_output("---")
log_output("""
#### 4.1 编码方案
• Source（信息来源）：虚拟编码
  - AI健康教练 = 1
  - 人类专家 = 0
  
• Frame（信息框架）：虚拟编码
  - 损失框架（"不采取...负面后果"） = 1
  - 收益框架（"采取...好处"） = 0
  
• Source × Frame：交互项 = Source × Frame

#### 4.2 标准化处理
所有连续变量（Intention、Trust、Self-Efficacy、Health Consciousness）
采用Z-score标准化处理（M=0, SD=1）。虚拟变量（0/1）保持原样。

#### 4.3 中心化处理
在计算交互项时，将连续变量（HC、Trust、SE）进行均值中心化处理，
以提高交互项的可解释性，并减少多重共线性问题。

#### 4.4 样本量与缺失值处理
• 初始样本量：201人
• 有效样本量：[分析后显示]
• 缺失值处理：采用完全案例分析（Complete Case Analysis），
  删除任何关键变量缺失的个案
""")

log_output("\n### 5. 分析方法")
log_output("---")
log_output("""
采用Hayes (2017) PROCESS macro的思想框架，进行逐步OLS回归分析：

#### 5.1 模型框架（Model C - Moderated Mediation）

【m路径】独立变量 → 中介变量
  • Model 2A: Trust ~ Source + Frame + Source×Frame
  • Model 2B: Self-Efficacy ~ Source + Frame + Source×Frame

【b路径调节】中介变量 → 因变量（加入HC调节）
  • Model C1: Intention ~ M + HC + M×HC
  其中M包括Trust和Self-Efficacy

【a路径调节】独立变量 → 中介变量（加入HC调节）
  • Model C2A: Trust ~ Source + Frame + Source×Frame + HC + (IV×HC)
  • Model C2B: SE ~ Source + Frame + Source×Frame + HC + (IV×HC)

【完整模型】
  • Model C-Full: 同时包含a路径和b路径的调节效应

#### 5.2 统计检验
• 总效应（c pathway）：Source/Frame/交互项对Intention的直接效应
• 直接效应（c' pathway）：控制中介变量后的效应
• 间接效应：通过中介变量的路径（a×b）
• 条件间接效应：在不同HC水平（-1SD, Mean, +1SD）下的间接效应
• 模型拟合：R²、调整R²、F统计量及其p值
• 显著性检验：p < 0.05为显著

#### 5.3 分析软件
• Python版本：3.12.1
• 关键库：
  - pandas (数据处理)
  - numpy (数值计算)
  - statsmodels (OLS回归)
  - scikit-learn (标准化处理)
""")

log_output("\n### 6. 伦理考虑")
log_output("---")
log_output("""
• 知情同意：所有参与者在填答问卷前阅读知情同意书
• 数据保护：通过Credamo平台进行数据收集和管理，确保隐私安全
• 匿名性：数据采集时记录参与者ID，确保数据追踪，同时在分析中不涉及个人身份信息
• 自由退出：参与者可随时退出研究
""")

log_output("\n" + "=" * 100)
log_output("================================ 实证结果部分 ================================")
log_output("=" * 100)
log_output("")

# ============================================================================
# 2. 数据加载与处理
# ============================================================================

log_output("【步骤1】数据加载与探描性统计")
log_output("-" * 100)

df_raw = pd.read_excel(DATA_FILE)

# 跳过元数据行（第1-2行），从第3行开始
df = df_raw.iloc[2:].reset_index(drop=True)

log_output(f"✓ 数据文件加载完成")
log_output(f"  • 原始样本量：{len(df_raw)}")
log_output(f"  • 去除元数据后有效样本：{len(df)}")
log_output(f"  • 总变量数：{len(df.columns)}")
log_output("")

# 初始化分析数据集
df_analysis = pd.DataFrame()

# 【独立变量编码】
source_text = df.iloc[:, 27].astype(str)
df_analysis['Source'] = (source_text == 'AI健康教练').astype(int)

frame_text = df.iloc[:, 28].astype(str)
df_analysis['Frame'] = frame_text.str.contains('负面|后果', na=False).astype(int)

# 交互项
df_analysis['SourcexFrame'] = df_analysis['Source'] * df_analysis['Frame']

# 【因变量与中介变量 - 复合评分】
intention_cols = df.iloc[:, [32, 33, 34]].apply(pd.to_numeric, errors='coerce')
df_analysis['Intention'] = intention_cols.mean(axis=1)

se_cols = df.iloc[:, [35, 36, 37]].apply(pd.to_numeric, errors='coerce')
df_analysis['SelfEfficacy'] = se_cols.mean(axis=1)

trust_cols = df.iloc[:, [38, 39, 40, 41, 42]].apply(pd.to_numeric, errors='coerce')
df_analysis['Trust'] = trust_cols.mean(axis=1)

hc_cols = df.iloc[:, [43, 44, 45, 46, 47, 48]].apply(pd.to_numeric, errors='coerce')
df_analysis['HealthConsciousness'] = hc_cols.mean(axis=1)

log_output("✓ 编码和复合评分完成")
log_output(f"\n编码说明：")
log_output(f"  Source: AI健康教练=1, 人类专家=0")
log_output(f"  Frame:  损失框架=1, 收益框架=0")
log_output(f"  Intention: Q4_1-Q4_3的平均值")
log_output(f"  SelfEfficacy: Q5_1-Q5_3的平均值")
log_output(f"  Trust: Q6_1-Q6_5的平均值")
log_output(f"  HealthConsciousness: Q7_1-Q7_6的平均值")
log_output(f"")

# 删除缺失值
valid_indexs = df_analysis.notna().all(axis=1)
df_analysis = df_analysis[valid_indexs].reset_index(drop=True)

log_output(f"✓ 缺失值处理")
log_output(f"  • 删除后有效样本：{len(df_analysis)}")
log_output("")

# 描述性统计
log_output("【描述性统计】")
log_output("")
log_output(df_analysis.describe().to_string())
log_output("")

# 因子分布
log_output("【因子设计检验】")
log_output("")
contingency = pd.crosstab(df_analysis['Source'], df_analysis['Frame'], margins=True)
log_output(contingency.to_string())
log_output("")

# ============================================================================
# 3. 标准化与中心化处理
# ============================================================================

log_output("\n【步骤2】标准化与中心化处理")
log_output("-" * 100)

scaler = StandardScaler()
continuous_vars = ['Intention', 'Trust', 'SelfEfficacy', 'HealthConsciousness']

for col in continuous_vars:
    df_analysis[col] = scaler.fit_transform(df_analysis[[col]])
    
log_output("✓ Z-score标准化完成（M=0, SD=1）")

# 创建中心化版本
df_analysis['HC_centered'] = df_analysis['HealthConsciousness'] - df_analysis['HealthConsciousness'].mean()
df_analysis['Trust_centered'] = df_analysis['Trust'] - df_analysis['Trust'].mean()
df_analysis['SE_centered'] = df_analysis['SelfEfficacy'] - df_analysis['SelfEfficacy'].mean()

# 交互项
df_analysis['SourcexHC'] = df_analysis['Source'] * df_analysis['HC_centered']
df_analysis['FramexHC'] = df_analysis['Frame'] * df_analysis['HC_centered']
df_analysis['InteractionxHC'] = df_analysis['SourcexFrame'] * df_analysis['HC_centered']

df_analysis['TrustxHC'] = df_analysis['Trust_centered'] * df_analysis['HC_centered']
df_analysis['SExHC'] = df_analysis['SE_centered'] * df_analysis['HC_centered']

log_output("✓ 中心化处理完成")
log_output(f"  • HC, Trust, SE 变量均进行了均值中心化处理")
log_output(f"  • 交互项已计算")
log_output("")

# ============================================================================
# 4. 核心回归分析：调节中介模型
# ============================================================================

log_output("\n【步骤3】调节中介模型分析（Model C）")
log_output("-" * 100)
log_output("")

# 模型1: 总效应
model_1 = ols('Intention ~ Source + Frame + SourcexFrame', data=df_analysis).fit()
log_output("\n【模型1】总效应 (M→DV without mediation)")
log_output(str(model_1.summary()))
log_output(f"R² = {model_1.rsquared:.4f}, Adj R² = {model_1.rsquared_adj:.4f}")
log_output(f"F = {model_1.fvalue:.4f}, p = {model_1.f_pvalue:.6f}")

# 模型2A: Trust a-pathway
model_2a = ols('Trust ~ Source + Frame + SourcexFrame', data=df_analysis).fit()
log_output("\n【模型2A】a-pathway: 信息来源/框架 → 信任度")
log_output(str(model_2a.summary()))

# 模型2B: SE a-pathway
model_2b = ols('SelfEfficacy ~ Source + Frame + SourcexFrame', data=df_analysis).fit()
log_output("\n【模型2B】a-pathway: 信息来源/框架 → 自我效能")
log_output(str(model_2b.summary()))

# 模型3: 完整中介（无调节）
model_3 = ols('Intention ~ Source + Frame + SourcexFrame + Trust + SelfEfficacy', 
              data=df_analysis).fit()
log_output("\n【模型3】完整中介（无调节）")
log_output(str(model_3.summary()))
log_output(f"R² = {model_3.rsquared:.4f}, Adj R² = {model_3.rsquared_adj:.4f}")
log_output(f"F = {model_3.fvalue:.4f}, p = {model_3.f_pvalue:.6f}")

# 模型C1: b路径调节
model_c1 = ols(
    'Intention ~ Source + Frame + SourcexFrame + Trust + SelfEfficacy + '
    'HealthConsciousness + TrustxHC + SExHC',
    data=df_analysis
).fit()

log_output("\n【模型C1】b-路径调节 (HC调节M→DV关系)")
log_output(str(model_c1.summary()))
log_output(f"R² = {model_c1.rsquared:.4f}, Adj R² = {model_c1.rsquared_adj:.4f}")
log_output(f"F = {model_c1.fvalue:.4f}, p = {model_c1.f_pvalue:.6f}")

# 模型C2A: a路径调节-Trust
model_c2a = ols(
    'Trust ~ Source + Frame + SourcexFrame + HealthConsciousness + '
    'SourcexHC + FramexHC + InteractionxHC',
    data=df_analysis
).fit()

log_output("\n【模型C2A】a-路径调节 (HC调节IV→Trust关系)")
log_output(str(model_c2a.summary()))

# 模型C2B: a路径调节-SE
model_c2b = ols(
    'SelfEfficacy ~ Source + Frame + SourcexFrame + HealthConsciousness + '
    'SourcexHC + FramexHC + InteractionxHC',
    data=df_analysis
).fit()

log_output("\n【模型C2B】a-路径调节 (HC调节IV→SE关系)")
log_output(str(model_c2b.summary()))

# ============================================================================
# 5. 条件间接效应计算
# ============================================================================

log_output("\n【步骤4】条件间接效应分析")
log_output("-" * 100)

hc_levels = {
    '低 (Mean-1SD)': -1.0,
    '中 (Mean)': 0.0,
    '高 (Mean+1SD)': 1.0
}

log_output("\n【在不同HC水平下的条件间接效应】\n")

conditional_results = {}

for level_name, hc_val in hc_levels.items():
    log_output(f"\n--- {level_name} (HC值={hc_val:.2f}) ---")
    
    # a路径系数
    a_source_trust = model_c2a.params['Source'] + model_c2a.params['SourcexHC'] * hc_val
    a_frame_trust = model_c2a.params['Frame'] + model_c2a.params['FramexHC'] * hc_val
    a_interact_trust = model_c2a.params['SourcexFrame'] + model_c2a.params['InteractionxHC'] * hc_val
    
    a_source_se = model_c2b.params['Source'] + model_c2b.params['SourcexHC'] * hc_val
    a_frame_se = model_c2b.params['Frame'] + model_c2b.params['FramexHC'] * hc_val
    a_interact_se = model_c2b.params['SourcexFrame'] + model_c2b.params['InteractionxHC'] * hc_val
    
    # b路径系数
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
    
    conditional_results[level_name] = {
        'Source': ie_source_total,
        'Frame': ie_frame_total,
        'Interaction': ie_interact_total,
        'Source_via_Trust': ie_source_trust,
        'Source_via_SE': ie_source_se,
        'Frame_via_Trust': ie_frame_trust,
        'Frame_via_SE': ie_frame_se,
    }
    
    log_output(f"  Source间接效应: {ie_source_total:+.4f}")
    log_output(f"    → via Trust: {ie_source_trust:+.4f} (a={a_source_trust:.3f}, b={b_trust:.3f})")
    log_output(f"    → via SE:    {ie_source_se:+.4f} (a={a_source_se:.3f}, b={b_se:.3f})")
    log_output("")
    log_output(f"  Frame间接效应:  {ie_frame_total:+.4f}")
    log_output(f"    → via Trust: {ie_frame_trust:+.4f} (a={a_frame_trust:.3f}, b={b_trust:.3f})")
    log_output(f"    → via SE:    {ie_frame_se:+.4f} (a={a_frame_se:.3f}, b={b_se:.3f})")
    log_output("")
    log_output(f"  Source×Frame: {ie_interact_total:+.4f}")
    log_output(f"    → via Trust: {ie_interact_trust:+.4f}")
    log_output(f"    → via SE:    {ie_interact_se:+.4f}")

# ============================================================================
# 6. 模型对比表
# ============================================================================

log_output("\n\n【步骤5】模型拟合对比")
log_output("-" * 100)

comparison = pd.DataFrame({
    '模型': ['Model 1\n(总效应)', 'Model 3\n(中介)', 'Model C1\n(b调节)', 'Model C2A\n(a调节-Trust)', 'Model C2B\n(a调节-SE)'],
    'R²': [model_1.rsquared, model_3.rsquared, model_c1.rsquared, model_c2a.rsquared, model_c2b.rsquared],
    'Adj R²': [model_1.rsquared_adj, model_3.rsquared_adj, model_c1.rsquared_adj, 
               model_c2a.rsquared_adj, model_c2b.rsquared_adj],
    'F统计': [model_1.fvalue, model_3.fvalue, model_c1.fvalue, model_c2a.fvalue, model_c2b.fvalue],
    'p值': [model_1.f_pvalue, model_3.f_pvalue, model_c1.f_pvalue, model_c2a.f_pvalue, model_c2b.f_pvalue]
})

log_output("\n")
log_output(comparison.to_string(index=False))

log_output("\n\n【R²改进分析】")
log_output(f"  Model 1 → Model 3:   ΔR² = {(model_3.rsquared - model_1.rsquared):.4f} ({(model_3.rsquared/model_1.rsquared - 1)*100:.1f}% 提升)")
log_output(f"  Model 3 → Model C1:  ΔR² = {(model_c1.rsquared - model_3.rsquared):.4f} ({(model_c1.rsquared/model_3.rsquared - 1)*100:.1f}% 提升)")

# ============================================================================
# 7. 调节效应总结
# ============================================================================

log_output("\n\n【步骤6】调节效应显著性检验")
log_output("-" * 100)

log_output("\n【b路径调节效应】(HC调节中介→结果的关系)")
log_output(f"  Trust × HC: β = {model_c1.params.get('TrustxHC', np.nan):+.4f}, ")
log_output(f"              p = {model_c1.pvalues.get('TrustxHC', np.nan):.4f} {'***' if model_c1.pvalues.get('TrustxHC', np.nan) < 0.01 else '**' if model_c1.pvalues.get('TrustxHC', np.nan) < 0.05 else '*' if model_c1.pvalues.get('TrustxHC', np.nan) < 0.10 else 'ns'}")
log_output(f"  SE × HC:    β = {model_c1.params.get('SExHC', np.nan):+.4f}, ")
log_output(f"              p = {model_c1.pvalues.get('SExHC', np.nan):.4f} {'***' if model_c1.pvalues.get('SExHC', np.nan) < 0.01 else '**' if model_c1.pvalues.get('SExHC', np.nan) < 0.05 else '*' if model_c1.pvalues.get('SExHC', np.nan) < 0.10 else 'ns'}")

log_output("\n【a路径调节效应】(HC调节独立变量→中介的关系)")
log_output("\n  Trust路径：")
log_output(f"    Source × HC:      β = {model_c2a.params.get('SourcexHC', np.nan):+.4f}, p = {model_c2a.pvalues.get('SourcexHC', np.nan):.4f}")
log_output(f"    Frame × HC:       β = {model_c2a.params.get('FramexHC', np.nan):+.4f}, p = {model_c2a.pvalues.get('FramexHC', np.nan):.4f}")
log_output(f"    Interaction × HC: β = {model_c2a.params.get('InteractionxHC', np.nan):+.4f}, p = {model_c2a.pvalues.get('InteractionxHC', np.nan):.4f}")

log_output("\n  SE路径：")
log_output(f"    Source × HC:      β = {model_c2b.params.get('SourcexHC', np.nan):+.4f}, p = {model_c2b.pvalues.get('SourcexHC', np.nan):.4f}")
log_output(f"    Frame × HC:       β = {model_c2b.params.get('FramexHC', np.nan):+.4f}, p = {model_c2b.pvalues.get('FramexHC', np.nan):.4f}")
log_output(f"    Interaction × HC: β = {model_c2b.params.get('InteractionxHC', np.nan):+.4f}, p = {model_c2b.pvalues.get('InteractionxHC', np.nan):.4f}")

# ============================================================================
# 8. 最终总结
# ============================================================================

log_output("\n\n" + "=" * 100)
log_output("【分析完成总结】")
log_output("=" * 100)

log_output(f"""
✓ 数据集：7100_Final.xlsx (N = {len(df_analysis)})
✓ 分析方法：调节中介模型（Moderated Mediation）
✓ 分析工具：Python 3.12.1 + statsmodels
✓ 处理方式：Z-score标准化 + 均值中心化 + 完全案例分析
✓ 生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

关键发现：
• 信息来源和信息框架对运动意图的直接效应
• Trust和Self-Efficacy的中介作用
• Health Consciousness对上述路径的调节作用

下一步：
1. 条件间接效应的可信区间计算（bootstrap）
2. 效应量的统计和报告
3. 论文写作与结果解释
""")

output_handle.close()
print(f"\n✓ 完整分析报告已保存至：{output_file}")
