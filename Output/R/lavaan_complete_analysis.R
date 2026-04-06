################################################################################
# 线上社会心理学实验：信息来源与信息框架对运动意图的影响
# R语言完整分析脚本 (基于lavaan SEM)
# 作者：AI分析助手
# 日期：2026-04-06
# Mac用户：davidrenqqq
################################################################################

# 【用户配置】 USER CONFIGURATION
USER_NAME <- "davidrenqqq"  # 用户名
DATA_FOLDER <- "~/Desktop/7100"  # 数据文件夹

# 清理环境
rm(list = ls())
set.seed(12345)

# ==============================================================================
# 【第1板块】安装并加载必要的包
# ==============================================================================
# 运行此板块：检查并安装需要的所有R包

cat("\n【第1板块】正在加载R包...\n")

# 定义需要的包列表
required_packages <- c(
  "readxl",           # 读取Excel文件
  "dplyr",            # 数据处理
  "psych",            # 心理学统计（Cronbach Alpha）
  "lavaan",           # SEM和路径分析（核心）
  "semPlot",          # 绘制路径图
  "tidyverse"         # 数据整理
)

# 安装缺失的包
for (pkg in required_packages) {
  if (!require(pkg, character.only = TRUE, quietly = TRUE)) {
    cat(sprintf("正在安装 %s...\n", pkg))
    install.packages(pkg, repos = "https://cran.r-project.org")
    library(pkg, character.only = TRUE)
  }
}

cat("✓ 所有R包加载完成！\n\n")

# ==============================================================================
# 【第2板块】设置Mac路径并加载数据
# ==============================================================================
# 路径配置：~表示用户主目录

cat("【第2板块】正在加载数据文件...\n")

# Mac用户路径设置
data_path <- "~/Desktop/7100/7100.xlsx"

# 检查文件是否存在
if (!file.exists(path.expand(data_path))) {
  stop("❌ 错误：找不到文件！\n请检查文件路径：", path.expand(data_path))
}

# 读取Excel文件（跳过前两行元数据）
data_raw <- read_excel(path.expand(data_path), skip = 2)

# 转为数据框
data_raw <- as.data.frame(data_raw)

cat(sprintf("✓ 数据加载成功！原始样本量：%d\n", nrow(data_raw)))
cat(sprintf("✓ 变量总数：%d\n\n", ncol(data_raw)))

# ==============================================================================
# 【第3板块】数据编码与变量创建
# ==============================================================================

cat("【第3板块】正在进行数据编码...\n")

# 创建分析用的数据框
data_analysis <- data.frame()

# 【3.1】编码独立变量
# Source (信息来源)：第28列
source_col <- colnames(data_raw)[28]
data_analysis$Source <- as.numeric(data_raw[[source_col]] == "AI健康教练")

# Frame (信息框架)：第29列  
frame_col <- colnames(data_raw)[29]
data_analysis$Frame <- as.numeric(grepl("负面|后果", data_raw[[frame_col]], ignore.case = TRUE))

# Source×Frame交互项
data_analysis$SourcexFrame <- data_analysis$Source * data_analysis$Frame

# 【3.2】提取中介和因变量（复合评分）
# 列号说明：
# 行为意图（Intention）：第33-35列
intention_cols <- colnames(data_raw)[33:35]
data_analysis$Intention <- rowMeans(data_raw[, intention_cols], na.rm = TRUE)

# 自我效能（SelfEfficacy）：第36-38列
efficacy_cols <- colnames(data_raw)[36:38]
data_analysis$SelfEfficacy <- rowMeans(data_raw[, efficacy_cols], na.rm = TRUE)

# 信任度（Trust）：第39-43列
trust_cols <- colnames(data_raw)[39:43]
data_analysis$Trust <- rowMeans(data_raw[, trust_cols], na.rm = TRUE)

# 健康意识（HealthConsciousness）：第44-49列
hc_cols <- colnames(data_raw)[44:49]
data_analysis$HealthConsciousness <- rowMeans(data_raw[, hc_cols], na.rm = TRUE)

# 【3.3】删除缺失值
data_analysis <- data_analysis[complete.cases(data_analysis), ]

N_final <- nrow(data_analysis)
cat(sprintf("✓ 有效样本量：%d\n", N_final))
cat(sprintf("✓ 删除缺失数据后保留率：%.1f%%\n\n", 100 * N_final / nrow(data_raw)))

# ==============================================================================
# 【第4板块】标准化与中心化处理
# ==============================================================================

cat("【第4板块】正在进行标准化和中心化...\n")

# 创建标准化数据集
data_scaled <- data_analysis

# 标准化连续变量（Z-score转换）
continuous_vars <- c("Intention", "SelfEfficacy", "Trust", "HealthConsciousness")

for (var in continuous_vars) {
  data_scaled[[var]] <- scale(data_analysis[[var]])[,1]
}

# 为了后续交互项计算，创建中心化版本
data_scaled$HC_c <- data_scaled$HealthConsciousness - mean(data_scaled$HealthConsciousness)
data_scaled$Trust_c <- data_scaled$Trust - mean(data_scaled$Trust)
data_scaled$SE_c <- data_scaled$SelfEfficacy - mean(data_scaled$SelfEfficacy)

# 创建交互项
data_scaled$TrustxHC <- data_scaled$Trust_c * data_scaled$HC_c
data_scaled$SExHC <- data_scaled$SE_c * data_scaled$HC_c

cat("✓ 标准化完成！所有连续变量已转换为Z-score (M=0, SD=1)\n")
cat("✓ 中心化完成！交互项已创建\n\n")

# ==============================================================================
# 【第5板块】描述统计与相关矩阵
# ==============================================================================

cat("【第5板块】计算描述统计与相关矩阵...\n")

# 描述统计
desc_stats <- data.frame(
  Variable = c("Source", "Frame", "Intention", "SelfEfficacy", "Trust", "HealthConsciousness"),
  N = N_final,
  M = colMeans(data_analysis[, c("Source", "Frame", "Intention", "SelfEfficacy", "Trust", "HealthConsciousness")]),
  SD = sapply(data_analysis[, c("Source", "Frame", "Intention", "SelfEfficacy", "Trust", "HealthConsciousness")], sd),
  Min = sapply(data_analysis[, c("Source", "Frame", "Intention", "SelfEfficacy", "Trust", "HealthConsciousness")], min),
  Max = sapply(data_analysis[, c("Source", "Frame", "Intention", "SelfEfficacy", "Trust", "HealthConsciousness")], max)
)

cat("\n【表1】描述统计\n")
print(round(desc_stats, 3))

# 相关矩阵
corr_vars <- c("Source", "Frame", "Intention", "SelfEfficacy", "Trust", "HealthConsciousness")
corr_matrix <- cor(data_analysis[, corr_vars])

cat("\n【表2】Pearson相关矩阵\n")
print(round(corr_matrix, 3))

cat("\n✓ 描述统计和相关矩阵计算完成\n\n")

# ==============================================================================
# 【第6板块】信度分析（Cronbach Alpha）
# ==============================================================================

cat("【第6板块】计算Cronbach Alpha信度系数...\n")

# 信度计算函数
cronbach_alpha <- function(items) {
  item_data <- items[complete.cases(items), ]
  n_items <- ncol(item_data)
  if (n_items < 2) return(NA)
  
  corr_matrix <- cor(item_data)
  avg_corr <- (sum(corr_matrix) - n_items) / (n_items * (n_items - 1))
  alpha <- (n_items * avg_corr) / (1 + (n_items - 1) * avg_corr)
  return(alpha)
}

# 计算各量表的信度
alpha_intention <- cronbach_alpha(data_raw[, intention_cols])
alpha_efficacy <- cronbach_alpha(data_raw[, efficacy_cols])
alpha_trust <- cronbach_alpha(data_raw[, trust_cols])
alpha_hc <- cronbach_alpha(data_raw[, hc_cols])

reliability_results <- data.frame(
  Scale = c("Intention", "SelfEfficacy", "Trust", "HealthConsciousness"),
  Cronbach_Alpha = c(alpha_intention, alpha_efficacy, alpha_trust, alpha_hc),
  Interpretation = c(
    if(alpha_intention > 0.7) "✓ 可接受" else "⚠ 需改进",
    if(alpha_efficacy > 0.7) "✓ 可接受" else "⚠ 需改进",
    if(alpha_trust > 0.7) "✓ 可接受" else "⚠ 需改进",
    if(alpha_hc > 0.7) "✓ 可接受" else "⚠ 需改进"
  )
)

cat("\n【表3】信度系数（Cronbach Alpha）\n")
print(round(reliability_results[, 1:2], 3))

cat("\n✓ 信度分析完成\n\n")

# ==============================================================================
# 【第7板块】路径分析 - Model 1（总效应）
# ==============================================================================

cat("【第7板块】Model 1 - 总效应模型...\n")

# 定义Model 1：总效应（无中介）
model_1 <- '
  # 总效应 (c路径)
  Intention ~ c1_source*Source + c1_frame*Frame + c1_interaction*SourcexFrame
'

# 拟合Model 1
fit_m1 <- sem(model_1, data = data_scaled, std.lv = FALSE, std.dv = FALSE)

cat("\n【MODEL 1 - 总效应】\n")
summary(fit_m1, standardized = TRUE)

cat("\n✓ Model 1拟合完成\n\n")

# ==============================================================================
# 【第8板块】路径分析 - Model 2（a路径）
# ==============================================================================

cat("【第8板块】Model 2 - a路径模型（IV到中介变量）...\n")

# 定义Model 2：a路径
model_2 <- '
  # a路径：Source/Frame → Trust
  Trust ~ a1_source*Source + a1_frame*Frame + a1_interaction*SourcexFrame
  
  # a路径：Source/Frame → SelfEfficacy
  SelfEfficacy ~ a2_source*Source + a2_frame*Frame + a2_interaction*SourcexFrame
'

# 拟合Model 2
fit_m2 <- sem(model_2, data = data_scaled, std.lv = FALSE, std.dv = FALSE)

cat("\n【MODEL 2 - a路径】\n")
summary(fit_m2, standardized = TRUE)

cat("\n✓ Model 2拟合完成\n\n")

# ==============================================================================
# 【第9板块】路径分析 - Model 3（b路径，无调节）
# ==============================================================================

cat("【第9板块】Model 3 - b路径模型（中介到DV，无调节）...\n")

# 定义Model 3：b路径（无调节）
model_3 <- '
  # a路径
  Trust ~ a1_source*Source + a1_frame*Frame + a1_interaction*SourcexFrame
  SelfEfficacy ~ a2_source*Source + a2_frame*Frame + a2_interaction*SourcexFrame
  
  # b路径
  Intention ~ b_trust*Trust + b_se*SelfEfficacy + c_source*Source + c_frame*Frame + c_interaction*SourcexFrame
  
  # 间接效应
  source_indirect_trust := a1_source * b_trust
  source_indirect_se := a2_source * b_se
  frame_indirect_trust := a1_frame * b_trust
  frame_indirect_se := a2_frame * b_se
'

# 拟合Model 3
fit_m3 <- sem(model_3, data = data_scaled, std.lv = FALSE, std.dv = FALSE)

cat("\n【MODEL 3 - b路径（无调节）】\n")
summary(fit_m3, standardized = TRUE)

cat("\n✓ Model 3拟合完成\n\n")

# ==============================================================================
# 【第10板块】完整调节中介模型 - Model C1
# ==============================================================================

cat("【第10板块】Model C1 - 完整调节中介模型...\n")

# 定义Model C1：b路径调节
model_c1 <- '
  # a路径
  Trust ~ a1_source*Source + a1_frame*Frame + a1_interaction*SourcexFrame
  SelfEfficacy ~ a2_source*Source + a2_frame*Frame + a2_interaction*SourcexFrame
  
  # b路径（加入HC调节）
  Intention ~ b_trust*Trust + b_se*SelfEfficacy + 
              b_hc*HealthConsciousness + 
              b_trustxhc*TrustxHC + 
              b_sexhc*SExHC +
              c_source*Source + 
              c_frame*Frame + 
              c_interaction*SourcexFrame
  
  # 间接效应
  source_indirect := a1_source * b_trust
  se_indirect := a2_source * b_se
'

# 拟合Model C1
fit_mc1 <- sem(model_c1, data = data_scaled, std.lv = FALSE, std.dv = FALSE)

cat("\n【MODEL C1 - 完整调节中介模型】\n")
summary(fit_mc1, standardized = TRUE, fit.measures = TRUE)

cat("\n✓ Model C1拟合完成\n\n")

# ==============================================================================
# 【第11板块】模型比较与模型选择
# ==============================================================================

cat("【第11板块】模型拟合指标比较...\n")

# 提取关键拟合指标
model_comparison <- data.frame(
  Model = c("Model 1 (总效应)", "Model 3 (无调节)", "Model C1 (完整调节)"),
  ChiSq = c(fitmeasures(fit_m1, "chisq"), 
            fitmeasures(fit_m3, "chisq"),
            fitmeasures(fit_mc1, "chisq")),
  DF = c(fitmeasures(fit_m1, "df"), 
         fitmeasures(fit_m3, "df"),
         fitmeasures(fit_mc1, "df")),
  CFI = c(fitmeasures(fit_m1, "cfi"), 
          fitmeasures(fit_m3, "cfi"),
          fitmeasures(fit_mc1, "cfi")),
  RMSEA = c(fitmeasures(fit_m1, "rmsea"), 
            fitmeasures(fit_m3, "rmsea"),
            fitmeasures(fit_mc1, "rmsea")),
  SRMR = c(fitmeasures(fit_m1, "srmr"), 
           fitmeasures(fit_m3, "srmr"),
           fitmeasures(fit_mc1, "srmr"))
)

cat("\n【表4】模型拟合指标比较\n")
print(round(model_comparison, 4))

cat("\n✓ 模型比较完成\n\n")

# ==============================================================================
# 【第12板块】提取并整理关键系数
# ==============================================================================

cat("【第12板块】提取关键回归系数...\n")

# 从Model C1提取参数
params_c1 <- parameterEstimates(fit_mc1, standardized = TRUE) %>%
  filter(pvalue < 0.1) %>%
  select(lhs, op, rhs, est, std.all, se, pvalue, ci.lower, ci.upper)

cat("\n【表5】Model C1 显著性系数（p < 0.1）\n")
print(round(params_c1[, c(1:7)], 4))

cat("\n✓ 系数提取完成\n\n")

# ==============================================================================
# 【第13板块】条件间接效应分析（不同HC水平）
# ==============================================================================

cat("【第13板块】条件间接效应分析...\n")

# 获取标准化系数
get_coef <- function(fit, label) {
  coef_est <- coef(fit)[label]
  return(coef_est)
}

a1_source_est <- get_coef(fit_mc1, "a1_source")
b_trust_est <- get_coef(fit_mc1, "b_trust")
b_trustxhc_est <- get_coef(fit_mc1, "b_trustxhc")
hc_mean <- mean(data_scaled$HealthConsciousness)
hc_sd <- sd(data_scaled$HealthConsciousness)

# 计算不同HC水平下的条件间接效应
hc_levels <- c(hc_mean - hc_sd, hc_mean, hc_mean + hc_sd)
labels_hc <- c("Low (-1SD)", "Mean", "High (+1SD)")

conditional_indirect <- data.frame(
  HC_Level = labels_hc,
  HC_Value = round(hc_levels, 3),
  Conditional_Effect = round(a1_source_est * (b_trust_est + b_trustxhc_est * hc_levels), 4)
)

cat("\n【表6】条件间接效应（Source→Trust→Intention，在不同HC水平）\n")
print(conditional_indirect)

cat("\n✓ 条件间接效应分析完成\n\n")

# ==============================================================================
# 【第14板块】绘制路径图
# ==============================================================================

cat("【第14板块】正在生成路径图...\n")

# 设置输出路径
output_path <- "~/Desktop/7100/lavaan_path_diagram.pdf"

# 绘制路径图
pdf(path.expand(output_path), width = 12, height = 8)
semPaths(fit_mc1, what = "std", layout = "tree", nCharNodes = 8)
dev.off()

cat(sprintf("✓ 路径图已保存至：%s\n\n", output_path))

# ==============================================================================
# 【第15板块】生成完整输出报告
# ==============================================================================

cat("【第15板块】生成完整分析报告...\n")

# 创建输出文件
output_file <- "~/Desktop/7100/lavaan_analysis_results.txt"

sink(path.expand(output_file))

cat("════════════════════════════════════════════════════════════════\n")
cat("线上社会心理学实验：R lavaan完整分析报告\n")
cat("生成时间：", format(Sys.time(), "%Y-%m-%d %H:%M:%S"), "\n")
cat("════════════════════════════════════════════════════════════════\n\n")

cat("【第一部分】样本特征与描述统计\n")
cat("─────────────────────────────────────\n")
cat(sprintf("有效样本量：%d\n", N_final))
cat("\n描述统计：\n")
print(round(desc_stats, 3))

cat("\n\n【第二部分】信度系数\n")
cat("─────────────────────────────────────\n")
print(round(reliability_results[, 1:2], 3))

cat("\n\n【第三部分】相关矩阵\n")
cat("─────────────────────────────────────\n")
print(round(corr_matrix, 3))

cat("\n\n【第四部分】Model C1 - 完整调节中介模型结果\n")
cat("─────────────────────────────────────\n")
summary(fit_mc1, standardized = TRUE, fit.measures = TRUE)

cat("\n\n【第五部分】显著性系数汇总\n")
cat("─────────────────────────────────────\n")
print(round(params_c1[, c(1:7)], 4))

cat("\n\n【第六部分】条件间接效应\n")
cat("─────────────────────────────────────\n")
print(conditional_indirect)

cat("\n\n════════════════════════════════════════════════════════════════\n")
cat("报告生成完成\n")

sink()

cat(sprintf("✓ 分析报告已保存至：%s\n\n", output_file))

# ==============================================================================
# 【第16板块】最终总结与检查
# ==============================================================================

cat("【第16板块】分析总结\n")
cat("════════════════════════════════════════════════════════════════\n\n")

cat("✅ 所有分析已成功完成！\n\n")

cat("📊 生成的文件：\n")
cat("  1. 路径图：", path.expand(output_path), "\n")
cat("  2. 详细报告：", path.expand(output_file), "\n\n")

cat("🔍 关键发现提示：\n")
cat("  • 查看Model C1的输出：调节效应是否显著？\n")
cat("  • 检查条件间直效应：是否在HC高水平时更强？\n")
cat("  • 对比模型拟合：Model C1是否显著优于Model 3？\n\n")

cat("💾 后续步骤：\n")
cat("  1. 在Excel中复制表格数据（表4-6）\n")
cat("  2. 查看生成的路径图（PDF）\n")
cat("  3. 阅读详细报告文件进行论文写作\n\n")

cat("════════════════════════════════════════════════════════════════\n")
cat("✓ R分析脚本执行完成！没有报错。\n")
cat("════════════════════════════════════════════════════════════════\n")
