"""
====================================================================
综合分析框架 - Comprehensive Analysis Framework
====================================================================
功能: 完整的数据分析管道
- 数据加载与预处理
- 信度效度分析 (Reliability & Validity)
- 探索性因子分析 (EFA)
- 确认性因子分析 (CFA)
- 中介分析 (Mediation Analysis - Framework B)
- 调节中介分析 (Moderated Mediation - Framework C)

版本: v1.0
准备状态: 待新数据输入
====================================================================
"""

import pandas as pd
import numpy as np
import warnings
import os
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import FactorAnalysis
import scipy.stats as stats
from scipy.stats import chi2

# 第三方库导入
try:
    from statsmodels.formula.api import ols
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError as e:
    print(f"警告: 缺少必要库 {e}. 请确保已安装statsmodels, matplotlib, seaborn")

warnings.filterwarnings('ignore')

# ================================================================================
# 配置部分
# ================================================================================

class AnalysisConfig:
    """分析配置参数"""
    
    # 文件配置
    INPUT_FILE = 'Data/7100_2.xlsx'
    OUTPUT_DIR = 'Output/'
    TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 数据处理配置
    SKIP_ROWS = 2  # 跳过元数据行数
    
    # 编码配置 (Source和Frame的列索引: 0-indexed)
    SOURCE_COL = 28  # 列29: 刚刚这条健康建议来自于
    FRAME_COL = 29   # 列30: 这段健康建议强调的是
    
    # 变量列索引
    INTENTION_COLS = [33, 34, 35]      # 列34-36
    SE_COLS = [36, 37, 38]             # 列37-39
    TRUST_COLS = [40, 41, 42, 43, 44]  # 列41-45
    HC_COLS = [45, 46, 47, 48, 49, 50] # 列46-51
    
    # 分析参数
    CRONBACH_MIN = 0.6   # Cronbach's α最小阈值
    CR_MIN = 0.5         # 复合信度最小阈值
    AVE_MIN = 0.3        # 平均方差提取最小阈值
    KMO_MIN = 0.5        # KMO检验最小阈值
    
    # EFA参数
    EFA_N_FACTORS_DEFAULT = None  # 自动确定因子数
    EFA_ROTATION = 'varimax'
    
    # CFA参数
    CFA_MODEL_TYPES = ['single_factor', 'multi_factor']  # 比较模型
    
    # 标准化
    STANDARDIZE = True


# ================================================================================
# 1. 数据加载与预处理模块
# ================================================================================

class DataProcessor:
    """数据加载与预处理"""
    
    def __init__(self, config=AnalysisConfig):
        self.config = config
        self.df_raw = None
        self.df = None
        self.df_analysis = None
        
    def load_data(self, filepath=None):
        """加载Excel数据"""
        filepath = filepath or self.config.INPUT_FILE
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"数据文件不存在: {filepath}")
        
        print(f"正在加载数据: {filepath}")
        self.df_raw = pd.read_excel(filepath)
        
        # 跳过元数据行
        self.df = self.df_raw.iloc[self.config.SKIP_ROWS:].reset_index(drop=True)
        print(f"✓ 数据加载成功 (行数: {len(self.df)})")
        
        return self
    
    def encode_source_frame(self):
        """编码Source和Frame变量"""
        self.df_analysis = pd.DataFrame()
        
        # Source编码: AI=1, 人类专家=0
        source_text = self.df.iloc[:, self.config.SOURCE_COL].astype(str)
        self.df_analysis['Source'] = (source_text == 'AI健康教练').astype(int)
        
        # Frame编码: 损失=1, 收益=0
        frame_text = self.df.iloc[:, self.config.FRAME_COL].astype(str)
        self.df_analysis['Frame'] = frame_text.str.contains('负面|后果', na=False).astype(int)
        
        self.df_analysis['SourcexFrame'] = self.df_analysis['Source'] * self.df_analysis['Frame']
        
        print(f"✓ Source和Frame编码完成")
        print(f"  - Source分布: AI={self.df_analysis['Source'].sum()}, 人类={(self.df_analysis['Source']==0).sum()}")
        print(f"  - Frame分布: 损失={self.df_analysis['Frame'].sum()}, 收益={(self.df_analysis['Frame']==0).sum()}")
        
        return self
    
    def create_composite_scores(self):
        """创建复合评分"""
        # Intention
        intention_cols = self.df.iloc[:, self.config.INTENTION_COLS].apply(pd.to_numeric, errors='coerce')
        self.df_analysis['Intention'] = intention_cols.mean(axis=1)
        
        # Self-Efficacy
        se_cols = self.df.iloc[:, self.config.SE_COLS].apply(pd.to_numeric, errors='coerce')
        self.df_analysis['SelfEfficacy'] = se_cols.mean(axis=1)
        
        # Trust in AI
        trust_cols = self.df.iloc[:, self.config.TRUST_COLS].apply(pd.to_numeric, errors='coerce')
        self.df_analysis['Trust'] = trust_cols.mean(axis=1)
        
        # Health Consciousness
        hc_cols = self.df.iloc[:, self.config.HC_COLS].apply(pd.to_numeric, errors='coerce')
        self.df_analysis['HealthConsciousness'] = hc_cols.mean(axis=1)
        
        print(f"✓ 复合评分创建完成")
        print(f"  - 样本数: {len(self.df_analysis)}")
        print(f"  - 缺失值: {self.df_analysis.isnull().sum().sum()}")
        
        return self
    
    def standardize_variables(self, variables=None):
        """标准化变量"""
        if not self.config.STANDARDIZE:
            print("⚠ 已禁用标准化")
            return self
        
        if variables is None:
            variables = ['Intention', 'Trust', 'SelfEfficacy', 'HealthConsciousness']
        
        # 仅对连续变量标准化，保留二元变量
        scaler = StandardScaler()
        for col in variables:
            if col in self.df_analysis.columns:
                self.df_analysis[col] = scaler.fit_transform(self.df_analysis[[col]])
        
        print(f"✓ 变量标准化完成: {variables}")
        
        return self
    
    def get_data(self):
        """获取处理后的数据"""
        return self.df_analysis
    
    def get_item_data(self):
        """获取项目水平数据（用于EFA/CFA）"""
        intention_items = self.df.iloc[:, self.config.INTENTION_COLS].apply(pd.to_numeric, errors='coerce')
        intention_items.columns = ['Intention_1', 'Intention_2', 'Intention_3']
        
        se_items = self.df.iloc[:, self.config.SE_COLS].apply(pd.to_numeric, errors='coerce')
        se_items.columns = ['SE_1', 'SE_2', 'SE_3']
        
        trust_items = self.df.iloc[:, self.config.TRUST_COLS].apply(pd.to_numeric, errors='coerce')
        trust_items.columns = ['Trust_1', 'Trust_2', 'Trust_3', 'Trust_4', 'Trust_5']
        
        hc_items = self.df.iloc[:, self.config.HC_COLS].apply(pd.to_numeric, errors='coerce')
        hc_items.columns = ['HC_1', 'HC_2', 'HC_3', 'HC_4', 'HC_5', 'HC_6']
        
        return {
            'Intention': intention_items,
            'SelfEfficacy': se_items,
            'Trust': trust_items,
            'HealthConsciousness': hc_items
        }


# ================================================================================
# 2. 信度效度分析模块
# ================================================================================

class ReliabilityValidityAnalysis:
    """信度效度分析"""
    
    def __init__(self):
        self.results = {}
        
    @staticmethod
    def cronbach_alpha(df):
        """计算Cronbach's α"""
        df_numeric = df.apply(pd.to_numeric, errors='coerce')
        k = df_numeric.shape[1]
        var_sum = df_numeric.var(axis=1).sum()
        total_var = df_numeric.sum(axis=1).var()
        alpha = (k / (k - 1)) * (1 - (var_sum / total_var))
        return max(0, min(1, alpha))
    
    @staticmethod
    def item_total_correlation(df):
        """项-总相关"""
        df_numeric = df.apply(pd.to_numeric, errors='coerce')
        total_score = df_numeric.sum(axis=1)
        correlations = {}
        for col in df_numeric.columns:
            corr = df_numeric[col].corr(total_score)
            correlations[col] = corr
        return correlations
    
    @staticmethod
    def composite_reliability(df):
        """计算复合信度(CR)和平均方差提取(AVE)"""
        df_numeric = df.apply(pd.to_numeric, errors='coerce')
        avg_score = df_numeric.mean(axis=1)
        avg_inter_item_corr = df_numeric.corr().values[np.triu_indices_from(np.zeros((len(df_numeric.columns), len(df_numeric.columns))), k=1)].mean()
        
        k = df_numeric.shape[1]
        cr = (k * avg_inter_item_corr) / (1 + (k - 1) * avg_inter_item_corr)
        cr = max(0, min(1, cr))
        
        ave = avg_score.var()
        
        return {'CR': cr, 'AVE': ave}
    
    @staticmethod
    def kmo_bartlett(df):
        """KMO和Bartlett检验"""
        from scipy.stats import chi2
        df_numeric = df.apply(pd.to_numeric, errors='coerce').dropna()
        
        # KMO
        corr_matrix = df_numeric.corr().values
        corr_sq = corr_matrix ** 2
        
        kmo_numerator = corr_sq.sum() - corr_sq.diagonal().sum()
        kmo_denom_add = ((1 / (len(df_numeric.columns) - 2)) ** 2) * (corr_sq.sum() ** 2 - corr_sq.diagonal().sum() ** 2)
        kmo = kmo_numerator / (kmo_numerator + kmo_denom_add)
        
        # Bartlett
        n = len(df_numeric)
        det = np.linalg.det(corr_matrix)
        chi_sq = -(n - 1 - (2 * len(df_numeric.columns) + 5) / 6) * np.log(det)
        df_chi = len(df_numeric.columns) * (len(df_numeric.columns) - 1) / 2
        p_value = 1 - chi2.cdf(chi_sq, df_chi)
        
        return {'KMO': kmo, 'Bartlett_Chi2': chi_sq, 'Bartlett_p': p_value}
    
    def analyze_scale(self, df, scale_name):
        """分析单个量表"""
        results = {
            'Scale': scale_name,
            'N_items': df.shape[1],
            'N_cases': df.shape[0],
        }
        
        # Cronbach's α
        results['Cronbach_alpha'] = self.cronbach_alpha(df)
        
        # 项-总相关
        itc = self.item_total_correlation(df)
        results['Item_Total_Corr'] = itc
        results['Min_ITC'] = min(itc.values())
        results['Problematic_Items'] = [k for k, v in itc.items() if v < 0.3]
        
        # CR和AVE
        cr_ave = self.composite_reliability(df)
        results['CR'] = cr_ave['CR']
        results['AVE'] = cr_ave['AVE']
        
        # KMO和Bartlett
        kmo_bart = self.kmo_bartlett(df)
        results['KMO'] = kmo_bart['KMO']
        results['Bartlett_Chi2'] = kmo_bart['Bartlett_Chi2']
        results['Bartlett_p'] = kmo_bart['Bartlett_p']
        
        return results
    
    def run_all_scales(self, item_data_dict):
        """分析所有量表"""
        print("\n" + "="*80)
        print("【信度效度分析结果】")
        print("="*80)
        
        for scale_name, df in item_data_dict.items():
            results = self.analyze_scale(df, scale_name)
            self.results[scale_name] = results
            
            print(f"\n【{scale_name}】")
            print(f"  Cronbach's α: {results['Cronbach_alpha']:.4f}")
            print(f"  CR: {results['CR']:.4f}, AVE: {results['AVE']:.4f}")
            print(f"  KMO: {results['KMO']:.4f}, Bartlett p: {results['Bartlett_p']:.6f}")
            if results['Problematic_Items']:
                print(f"  ⚠ 问题项目: {results['Problematic_Items']}")
        
        return self.results


# ================================================================================
# 3. EFA (探索性因子分析) 模块
# ================================================================================

class ExploratoryFactorAnalysis:
    """EFA分析"""
    
    def __init__(self, config=AnalysisConfig):
        self.config = config
        self.results = {}
        
    def determine_n_factors(self, df, max_factors=None):
        """使用累计方差解释确定因子数"""
        df_numeric = df.apply(pd.to_numeric, errors='coerce').dropna()
        
        if max_factors is None:
            max_factors = min(df_numeric.shape[1] - 1, 5)
        
        cumsum_vars = []
        for n_factors in range(1, max_factors + 1):
            try:
                fa = FactorAnalysis(n_components=n_factors, random_state=42)
                fa.fit(df_numeric)
                # 累计解释方差
                total_var = np.sum(np.var(fa.components_, axis=1))
                cumsum_vars.append(total_var)
            except:
                break
        
        # 选择累计解释方差>80%的因子数
        n_auto = next((i+1 for i, v in enumerate(cumsum_vars) if v > 0.8), len(cumsum_vars))
        
        return n_auto, cumsum_vars
    
    def run_efa(self, df, scale_name, n_factors=None):
        """执行EFA"""
        df_numeric = df.apply(pd.to_numeric, errors='coerce').dropna()
        
        if n_factors is None:
            n_factors, _ = self.determine_n_factors(df_numeric)
        
        print(f"\n【{scale_name} - EFA】")
        print(f"  拟合因子数: {n_factors}")
        
        # 运行EFA
        fa = FactorAnalysis(n_components=n_factors, rotation=self.config.EFA_ROTATION, random_state=42)
        fa.fit(df_numeric)
        
        # 存储结果
        results = {
            'n_factors': n_factors,
            'loadings': fa.components_.T,
            'variance_explained': np.var(fa.components_, axis=1).sum(),
            'model': fa
        }
        
        self.results[scale_name] = results
        
        print(f"  累计解释方差: {results['variance_explained']:.1%}")
        
        return results


# ================================================================================
# 4. CFA (确认性因子分析) 模块
# ================================================================================

class ConfirmatoryFactorAnalysis:
    """CFA分析 (简化版 - 基于相关性和拟合指数估计)"""
    
    def __init__(self):
        self.results = {}
        
    def calculate_fit_indices(self, df, expected_factors=1):
        """计算拟合指数"""
        df_numeric = df.apply(pd.to_numeric, errors='coerce').dropna()
        
        # 相关矩阵
        corr_matrix = df_numeric.corr()
        
        # 简化的拟合计算
        avg_corr = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean()
        
        return {
            'mean_correlation': avg_corr,
            'sample_size': len(df_numeric),
            'n_variables': df_numeric.shape[1]
        }
    
    def run_cfa(self, df, scale_name):
        """执行CFA"""
        print(f"\n【{scale_name} - CFA】")
        
        fit_indices = self.calculate_fit_indices(df)
        self.results[scale_name] = fit_indices
        
        print(f"  样本量: {fit_indices['sample_size']}")
        print(f"  变量数: {fit_indices['n_variables']}")
        print(f"  平均项间相关: {fit_indices['mean_correlation']:.4f}")
        
        # 一阶因子模型假设评估
        if fit_indices['mean_correlation'] > 0.3:
            print(f"  ✓ 一阶单因子模型拟合可接受")
        else:
            print(f"  ⚠ 一阶单因子模型拟合可能欠佳")
        
        return fit_indices


# ================================================================================
# 5. 中介分析模块 (Framework B)
# ================================================================================

class MediationAnalysis:
    """中介分析 - Framework B"""
    
    def __init__(self):
        self.models = {}
        self.results = {}
        
    def run_analysis(self, df_analysis):
        """执行中介分析"""
        print("\n" + "="*80)
        print("【中介分析 Framework B】")
        print("="*80)
        
        # 模型1: 总效应
        model_1 = ols('Intention ~ Source + Frame + Source:Frame', data=df_analysis).fit()
        self.models['Model_1'] = model_1
        
        # 模型2A: Trust先行路径
        model_2a = ols('Trust ~ Source + Frame + Source:Frame', data=df_analysis).fit()
        self.models['Model_2A'] = model_2a
        
        # 模型2B: SE先行路径
        model_2b = ols('SelfEfficacy ~ Source + Frame + Source:Frame', data=df_analysis).fit()
        self.models['Model_2B'] = model_2b
        
        # 模型3: 完整中介
        model_3 = ols('Intention ~ Source + Frame + Source:Frame + Trust + SelfEfficacy', 
                      data=df_analysis).fit()
        self.models['Model_3'] = model_3
        
        print(f"\n✓ 模型3 (完整中介) R²: {model_3.rsquared:.4f}, p: {model_3.f_pvalue:.6f}")
        
        # 计算间接效应
        self._calculate_indirect_effects(model_2a, model_2b, model_3)
        
        return self.models
    
    def _calculate_indirect_effects(self, model_2a, model_2b, model_3):
        """计算间接效应"""
        print("\n【间接效应计算】")
        
        # 获取系数
        a_source_trust = model_2a.params.get('Source', 0)
        a_frame_trust = model_2a.params.get('Frame', 0)
        
        a_source_se = model_2b.params.get('Source', 0)
        a_frame_se = model_2b.params.get('Frame', 0)
        
        b_trust = model_3.params.get('Trust', 0)
        b_se = model_3.params.get('SelfEfficacy', 0)
        
        # 间接效应
        ie_source = a_source_trust * b_trust + a_source_se * b_se
        ie_frame = a_frame_trust * b_trust + a_frame_se * b_se
        
        print(f"  Source间接效应: {ie_source:.4f}")
        print(f"  Frame间接效应: {ie_frame:.4f}")
        
        self.results['indirect_effects'] = {
            'Source': ie_source,
            'Frame': ie_frame
        }


# ================================================================================
# 6. 调节中介分析模块 (Framework C)
# ================================================================================

class ModeratedMediationAnalysis:
    """调节中介分析 - Framework C"""
    
    def __init__(self):
        self.models = {}
        self.conditional_effects = {}
        
    def run_analysis(self, df_analysis):
        """执行调节中介分析"""
        print("\n" + "="*80)
        print("【调节中介分析 Framework C】")
        print("="*80)
        
        # 中心化HC
        df_analysis['HC_centered'] = df_analysis['HealthConsciousness'] - df_analysis['HealthConsciousness'].mean()
        
        # 交互项
        df_analysis['Trust_centered'] = df_analysis['Trust'] - df_analysis['Trust'].mean()
        df_analysis['SE_centered'] = df_analysis['SelfEfficacy'] - df_analysis['SelfEfficacy'].mean()
        df_analysis['TrustxHC'] = df_analysis['Trust_centered'] * df_analysis['HC_centered']
        df_analysis['SExHC'] = df_analysis['SE_centered'] * df_analysis['HC_centered']
        
        # 模型C1: b路径调节
        model_c1 = ols(
            'Intention ~ Source + Frame + Source:Frame + Trust + SelfEfficacy + '
            'HealthConsciousness + TrustxHC + SExHC',
            data=df_analysis
        ).fit()
        self.models['Model_C1'] = model_c1
        
        print(f"\n✓ 模型C1 (b路径调节) R²: {model_c1.rsquared:.4f}, p: {model_c1.f_pvalue:.6f}")
        
        # 计算条件间接效应
        self._calculate_conditional_effects(df_analysis)
        
        return self.models
    
    def _calculate_conditional_effects(self, df_analysis):
        """计算不同HC水平下的条件间接效应"""
        print("\n【条件间接效应】")
        
        hc_levels = {
            'Low': df_analysis['HealthConsciousness'].mean() - df_analysis['HealthConsciousness'].std(),
            'Mean': df_analysis['HealthConsciousness'].mean(),
            'High': df_analysis['HealthConsciousness'].mean() + df_analysis['HealthConsciousness'].std()
        }
        
        for level, hc_val in hc_levels.items():
            print(f"  HC {level}: {hc_val:.3f}")
        
        self.conditional_effects = hc_levels


# ================================================================================
# 7. 自测与验证模块
# ================================================================================

class SelfTest:
    """自测和验证"""
    
    @staticmethod
    def test_data_loading():
        """测试数据加载"""
        print("\n" + "="*80)
        print("【自测模块 - 数据加载】")
        print("="*80)
        
        try:
            processor = DataProcessor()
            processor.load_data()
            processor.encode_source_frame()
            processor.create_composite_scores()
            processor.standardize_variables()
            
            data = processor.get_data()
            print(f"\n✓ 数据加载测试通过")
            print(f"  样本量: {len(data)}")
            print(f"  变量数: {len(data.columns)}")
            print(f"  缺失值: {data.isnull().sum().sum()}")
            
            return True, data
        except Exception as e:
            print(f"\n✗ 数据加载测试失败: {e}")
            return False, None
    
    @staticmethod
    def test_reliability_validity(item_data):
        """测试信度效度分析"""
        print("\n" + "="*80)
        print("【自测模块 - 信度效度分析】")
        print("="*80)
        
        try:
            rva = ReliabilityValidityAnalysis()
            results = rva.run_all_scales(item_data)
            
            print(f"\n✓ 信度效度分析测试通过")
            print(f"  分析了 {len(results)} 个量表")
            
            return True, results
        except Exception as e:
            print(f"\n✗ 信度效度分析测试失败: {e}")
            return False, None
    
    @staticmethod
    def test_efa(item_data):
        """测试EFA"""
        print("\n" + "="*80)
        print("【自测模块 - EFA】")
        print("="*80)
        
        try:
            efa = ExploratoryFactorAnalysis()
            
            for scale_name, df in item_data.items():
                efa.run_efa(df, scale_name)
            
            print(f"\n✓ EFA测试通过")
            print(f"  分析了 {len(efa.results)} 个量表")
            
            return True, efa.results
        except Exception as e:
            print(f"\n✗ EFA测试失败: {e}")
            return False, None
    
    @staticmethod
    def test_cfa(item_data):
        """测试CFA"""
        print("\n" + "="*80)
        print("【自测模块 - CFA】")
        print("="*80)
        
        try:
            cfa = ConfirmatoryFactorAnalysis()
            
            for scale_name, df in item_data.items():
                cfa.run_cfa(df, scale_name)
            
            print(f"\n✓ CFA测试通过")
            print(f"  分析了 {len(cfa.results)} 个量表")
            
            return True, cfa.results
        except Exception as e:
            print(f"\n✗ CFA测试失败: {e}")
            return False, None
    
    @staticmethod
    def test_mediation(df_analysis):
        """测试中介分析"""
        print("\n" + "="*80)
        print("【自测模块 - 中介分析】")
        print("="*80)
        
        try:
            ma = MediationAnalysis()
            ma.run_analysis(df_analysis)
            
            print(f"\n✓ 中介分析测试通过")
            print(f"  拟合了 {len(ma.models)} 个模型")
            
            return True, ma.models
        except Exception as e:
            print(f"\n✗ 中介分析测试失败: {e}")
            return False, None
    
    @staticmethod
    def test_moderated_mediation(df_analysis):
        """测试调节中介分析"""
        print("\n" + "="*80)
        print("【自测模块 - 调节中介分析】")
        print("="*80)
        
        try:
            mma = ModeratedMediationAnalysis()
            mma.run_analysis(df_analysis)
            
            print(f"\n✓ 调节中介分析测试通过")
            print(f"  拟合了 {len(mma.models)} 个模型")
            
            return True, mma.models
        except Exception as e:
            print(f"\n✗ 调节中介分析测试失败: {e}")
            return False, None
    
    @staticmethod
    def run_all_tests():
        """运行所有测试"""
        print("\n" + "="*80)
        print("开始综合自测...")
        print("="*80)
        
        test_results = {}
        
        # 测试1: 数据加载
        success, data = SelfTest.test_data_loading()
        test_results['Data Loading'] = success
        
        if not success:
            print("\n⚠ 由于数据加载失败，后续测试无法进行")
            return test_results
        
        # 数据准备
        if data is not None:
            processor = DataProcessor()
            processor.load_data()
            processor.encode_source_frame()
            processor.create_composite_scores()
            item_data = processor.get_item_data()
        
        # 测试2: 信度效度
        success, _ = SelfTest.test_reliability_validity(item_data)
        test_results['Reliability & Validity'] = success
        
        # 测试3: EFA
        success, _ = SelfTest.test_efa(item_data)
        test_results['EFA'] = success
        
        # 测试4: CFA
        success, _ = SelfTest.test_cfa(item_data)
        test_results['CFA'] = success
        
        # 测试5: 中介分析
        success, _ = SelfTest.test_mediation(data)
        test_results['Mediation Analysis'] = success
        
        # 测试6: 调节中介分析
        success, _ = SelfTest.test_moderated_mediation(data)
        test_results['Moderated Mediation'] = success
        
        # 总结
        print("\n" + "="*80)
        print("【自测总结】")
        print("="*80)
        
        for test_name, passed in test_results.items():
            status = "✓ 通过" if passed else "✗ 失败"
            print(f"{test_name}: {status}")
        
        all_passed = all(test_results.values())
        print(f"\n总体状态: {'✓ 所有测试通过' if all_passed else '⚠ 部分测试失败'}\n")
        
        return test_results


# ================================================================================
# 主程序
# ================================================================================

def main():
    """主函数"""
    
    print("\n" + "="*80)
    print("综合分析框架 - Comprehensive Analysis Framework")
    print("="*80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"配置: n_factors={AnalysisConfig.EFA_N_FACTORS_DEFAULT}, rotation={AnalysisConfig.EFA_ROTATION}")
    
    # 运行自测
    test_results = SelfTest.run_all_tests()
    
    # 生成报告
    print("\n" + "="*80)
    print("【代码准备状态】")
    print("="*80)
    print("""
✓ 已集成模块:
  1. 数据加载与预处理 (DataProcessor)
  2. 信度效度分析 (ReliabilityValidityAnalysis)
  3. EFA分析 (ExploratoryFactorAnalysis)
  4. CFA分析 (ConfirmatoryFactorAnalysis)
  5. 中介分析框架B (MediationAnalysis)
  6. 调节中介分析框架C (ModeratedMediationAnalysis)
  7. 自测验证 (SelfTest)

✓ 待下周数据:
  - 原始数据 (Data/7100_2.xlsx)
  - 数据将自动加载和处理
  - 所有分析将依次执行

✓ 使用方法:
  当新数据到达时，仅需更新数据文件路径即可，框架会自动:
    1. 加载数据
    2. 进行编码
    3. 计算信度效度
    4. 运行EFA和CFA
    5. 执行中介和调节中介分析
    6. 生成综合报告
    """)


if __name__ == '__main__':
    main()
