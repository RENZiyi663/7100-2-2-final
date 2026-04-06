# Lavaan脚本故障排除与诊断指南

## 🔍 诊断工具包

### 没等式！快速检查一下系统设置

#### 第一步：检查R环境

```r
# 检查R版本
R.version$version.string  # 应该 >= 4.0

# 检查工作目录
getwd()  # 应该类似 /Users/davidrenqqq

# 列出已安装的包
installed.packages()[,1]  # 查看是否有 lavaan, readxl 等
```

---

#### 第二步：检查数据文件

```r
# 最关键的检查！
file.exists("~/Desktop/7100/7100.xlsx")  # 必须返回 TRUE

# 如果返回 FALSE，尝试这个
file.exists("/Users/davidrenqqq/Desktop/7100/7100.xlsx")

# 查看文件夹内容
dir("~/Desktop/7100/")
```

---

#### 第三步：手动加载数据测试

```r
# 先装包
install.packages("readxl")
library(readxl)

# 手动加载
data_raw <- read_excel("~/Desktop/7100/7100.xlsx", skip = 2)

# 检查数据大小
dim(data_raw)  # 应该显示接近 199 行, 59 列

# 查看前几行
head(data_raw)

# 检查列名
colnames(data_raw)
```

---

## 🚨 常见问题诊断树

### 问题1：脚本运行前几秒就停止了

```r
# 检查是否卡在包加载
# 症状：卡在 【第1板块】正在加载R包...

# 解决：查看哪个包有问题
install.packages("lavaan")  # 一个一个试
library(lavaan)
```

如果某个包无法安装，可能原因：
- 网络问题 → 换源或稍后重试
- Mac版本太旧 → 更新R和包
- 包不兼容 → 用 `install.packages("lavaan", repos="https://cloud.r-project.org")`

---

### 问题2：出现 "找不到文件" 错误

```
Error: Cannot open specified file
```

**诊断步骤：**

```r
# (1) 确认文件存在
file.exists("~/Desktop/7100/7100.xlsx")

# (2) 尝试完整路径（不用~符号）
# 打开一个新的R session，输入：
Sys.getenv("HOME")  # 查看Mac的Home路径

# (3) 然后用完整路径试试（替换YOUR_USERNAME为你的用户名）
data_path <- "/Users/YOUR_USERNAME/Desktop/7100/7100.xlsx"
data_raw <- readxl::read_excel(data_path, skip = 2)

# (4) 如果还不行，用文件选择器
data_path <- file.choose()  # 手动选择文件
```

---

### 问题3：数据加载成功但列号不对

```
Warning: trying to select with out-of-bounds indices
或
Error: subscript out of bounds
```

**诊断步骤：**

```r
# (1) 查看Excel的实际列数
library(readxl)
data_test <- read_excel("~/Desktop/7100/7100.xlsx", skip = 2)
ncol(data_test)  # 应该显示 59

# (2) 查看各列名称
colnames(data_test)

# (3) 查看特定列
data_test[, 28]  # 应该是 Source
data_test[, 29]  # 应该是 Frame

# (4) 如果列号真的不对，手动修改脚本
# 在脚本中找到这些行：
# source_col_idx <- 28
# frame_col_idx <- 29
# 改成你确认的真实列号
```

---

### 问题4：Cronbach Alpha计算有问题

```
Error: non-numeric argument to mathematical function
或
Cronbach Alpha为 NA
```

**诊断步骤：**

```r
# (1) 检查Intention那三列是否都是数字
summary(data_analysis[, c("intent1", "intent2", "intent3")])

# (2) 查看是否有缺失值
colSums(is.na(data_analysis[, c("intent1", "intent2", "intent3")]))

# (3) 手动计算一个Alpha试试
library(psych)
print(alpha(data_analysis[, c("intent1", "intent2", "intent3")]))

# (4) 如果还有问题，检查变量是否都被成功创建
colnames(data_analysis)  # 查看是否有 intent1, intent2 等
```

---

### 问题5：模型无法拟合 (不收敛)

```
Warning: some lavaan WARNINGS in summary()
或
estimates of model parameters could not be updated
或
iteration limit reached
```

**诊断步骤：**

```r
# (1) 检查数据的基本统计
summary(data_analysis)

# (2) 查看是否有极端值或缺失
apply(data_analysis, 2, function(x) sum(is.na(x)))
apply(data_analysis, 2, function(x) mean(abs(scale(x)) > 3))  # 异常值比例

# (3) 检查相关矩阵是否有问题
cor_matrix <- cor(data_analysis, use = "complete.obs")
print(det(cor_matrix))  # 不应该是0或很接近0

# (4) 简化模型试试
simple_model <- '
  Intention ~ Source + Frame
'
fit_simple <- lavaan::sem(simple_model, data = data_analysis)
summary(fit_simple)  # 这个应该没问题

# (5) 如果简单模型可以，逐步加复杂性
```

---

### 问题6：输出文件没有生成

```
Error: cannot open file '~/Desktop/7100/lavaan_analysis_results.txt'
```

**诊断步骤：**

```r
# (1) 检查文件夹是否存在
dir.exists("~/Desktop/7100/")

# (2) 检查是否有写入权限
# 尝试手动创建一个文件
writeLines("test", "~/Desktop/7100/test.txt")

# (3) 如果权限有问题，用其他位置
# 在脚本中改输出路径为：
output_path <- "~/lavaan_results.txt"  # 改到用户主目录
```

---

## 🛠️ 高级诊断命令集

### 如果前面的都不行，用这个终极诊断

```r
# ===== 完整系统诊断脚本 =====

cat("======== R环境诊断 ========\n")
cat("R版本:", R.version$version.string, "\n")
cat("操作系统:", Sys.info()['sysname'], "\n")
cat("工作目录:", getwd(), "  # 应该显示 /Users/your_username\n\n")

cat("======== 数据文件诊断 ========\n")
excel_path <- "~/Desktop/7100/7100.xlsx"
cat("检查文件:", excel_path, "\n")
cat("存在?", file.exists(excel_path), "\n")
if(file.exists(excel_path)){
  cat("文件大小:", file.size(excel_path), " 字节\n")
}
cat("\n")

cat("======== 包诊断 ========\n")
packages_needed <- c("readxl", "dplyr", "psych", "lavaan", "semPlot", "tidyverse")
for(pkg in packages_needed){
  status <- ifelse(require(pkg, character.only = TRUE, quietly = TRUE), "✓", "✗")
  cat(status, pkg, "\n")
}
cat("\n")

cat("======== 数据加载诊断 ========\n")
tryCatch({
  data_raw <- readxl::read_excel(excel_path, skip = 2)
  cat("✓ 数据加载成功\n")
  cat("  维度:", nrow(data_raw), "行 ×", ncol(data_raw), "列\n")
  cat("  前5个列名:", paste(colnames(data_raw)[1:5], collapse=", "), "\n")
  cat("  缺失值:", sum(is.na(data_raw)), "个\n")
}, error = function(e){
  cat("✗ 数据加载失败:", e$message, "\n")
})
```

运行这个诊断，把输出告诉我。

---

## 📱 当所有都不行的时候

### 方案A：用简化版脚本

```r
# 最小化功能脚本
library(readxl)
library(lavaan)
library(psych)

# 加载数据
data <- read_excel("~/Desktop/7100/7100.xlsx", skip = 2)

# 只看相关矩阵
cor(data[, c(28, 29, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49)])

# 计算Alpha
alpha(data[, 33:35])  # Intention
alpha(data[, 36:38])  # SE
alpha(data[, 39:43]) # Trust
alpha(data[, 44:49]) # HC

# 最简单的模型
fit <- lavaan:::sem('
  Intention ~ Source + Frame
', data = data)
summary(fit)
```

### 方案B：在线求助

准备好这些信息：
1. R的版本
2. 操作系统
3. 完整的错误信息(包括error代码)
4. 诊断命令的输出
5. 数据的summary()输出

---

## 🧪 自测：脚本检查表

在运行完整脚本前，先做这个自测：

```r
# 自测第1部分：基础环境
[ ] R版本 >= 4.0
[ ] 所有需要的包都能加载
[ ] 数据文件存在且可读
[ ] 数据是199行59列

# 自测第2部分：数据质量
[ ] 没有全缺失的列
[ ] Source/Frame/Intention等变量都存在
[ ] 缺失值 < 5%
[ ] 没有极端异常值

# 自测第3部分：基本计算
[ ] cor()能正常运算
[ ] 相关矩阵没有NA
[ ] alpha()能计算Cronbach Alpha
[ ] 所有Alpha值都 > 0.7

# 自测第4部分：模型拟合
[ ] 简单模型(只有Main Effect)能拟合
[ ] 中等模型(有中介)能拟合
[ ] 完整模型(有调节)能拟合
```

---

## 🎯 最常见的5个错误及秒解

| 错误 | 秒解 |
|------|------|
| `Cannot find file` | `file.exists("~/Desktop/7100/7100.xlsx")` |
| `Package not found` | `install.packages("lavaan")` |
| `Column doesn't exist` | 检查列号: `colnames(data_raw)[28:35]` |
| `Model won't converge` | 检查数据: `summary(data)` |
| `NA in calculations` | 检查缺失值: `colSums(is.na(data))` |

---

## 📞 快速问题排查

**Q: 为什么第1板块要等这么久？**
A: 第一次装包会比较久。以后就快了。

**Q: 我改了代码想重新跑，需要重启R吗？**
A: 不需要。直接改脚本，重新 source() 或复制粘贴新代码就行。

**Q: 能不能只跑某个模型？**
A: 可以。把你需要的模型代码复制出来单独跑。但要保证前面的数据准备代码都跑过。

**Q: 输出结果和Python版本不一样怎么办？**
A: 1) 检查数据是否完全相同 2) 检查列号对应 3) 对比Python脚本中哪些变量。

**Q: 进度条显示多少才算正常？**
A: 没有进度条。就看能不能看到 ✓ 确认消息。

---

## 💾 备份和恢复

### 如果脚本出问题了

```r
# 完整重启（最后的办法）
rm(list = ls())  # 清空所有变量
gc()  # 清理内存
# 重新source脚本
source("~/Desktop/7100/lavaan_complete_analysis.R")
```

### 如果某个中间结果有问题

```r
# 保存中间结果（以防出错）
saveRDS(data_analysis, "~/Desktop/7100/data_backup.rds")

# 以后可以直接读取
data_analysis <- readRDS("~/Desktop/7100/data_backup.rds")
```

---

## 🚀 性能优化

如果你的电脑比较慢：

```r
# (1) 关闭不必要的输出
options(digits = 2)  # 减少输出位数

# (2) 不生成那么复杂的图
# 注释掉 semPaths() 这行

# (3) 用简化模型测试
# 先跑Model 1，再逐步加复杂度

# (4) 检查内存使用
object.size(data_analysis)
```

---

**如果用了这个指南还搞不定，直接复制"诊断工具包"运行，把结果告诉我！**
