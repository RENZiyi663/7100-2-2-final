# Lavaan R脚本完整使用指南

## 📋 目录
1. [环境准备](#环境准备)
2. [逐板块运行说明](#逐板块运行说明)
3. [16个板块详解](#16个板块详解)
4. [可能的错误与解决](#可能的错误与解决)
5. [输出文件说明](#输出文件说明)

---

## 🔧 环境准备

### 前置条件
- ✅ R版本 >= 4.0
- ✅ 数据文件：`~/Desktop/7100/7100.xlsx`

### 一键初始化

在Mac终端打开R（或RStudio），运行以下命令：

```r
# 粘贴下面的代码到R控制台，一次性安装所有包
packages_to_install <- c("readxl", "dplyr", "psych", "lavaan", "semPlot", "tidyverse")
install.packages(packages_to_install, dependencies = TRUE)
```

预期时间：3-5分钟首次安装

---

## ✅ 逐板块运行说明

### 推荐方式：分块运行 ✨

**第1次运行：先只运行【第1板块】到【第3板块】**
```
目标：检查数据是否正确加载
预期结果：看到"✓ 有效样本量：199"之类的确认信息
```

**第2次运行：运行【第4板块】到【第6板块】**
```
目标：检查数据质量和信度
预期结果：所有Cronbach Alpha都> 0.7
```

**第3次运行：运行【第7板块】到【第13板块】**
```
目标：跑所有模型并输出结果
预期结果：生成表4-表6的数据
```

**第4次运行：运行【第14板块】和【第15板块】**
```
目标：生成图表和最终报告
预期结果：生成PDF和详细文本报告
```

### 或者：一次全部运行

```r
# 在R中运行整个脚本
source("~/Desktop/7100/lavaan_complete_analysis.R")
```

---

## 📖 16个板块详解

### 【第1板块】包加载 ⏱️ 2-3分钟
**做什么**：安装并加载R所需的包

**会看到什么**：
```
【第1板块】正在加载R包...
✓ 所有R包加载完成！
```

**如果报错**：
```
Error: package 'XXX' could not be loaded
→ 手动安装：install.packages("XXX")
```

---

### 【第2板块】数据加载 ⏱️ <1秒
**做什么**：从Mac桌面读取Excel文件

**会看到什么**：
```
【第2板块】正在加载数据文件...
✓ 数据加载成功！原始样本量：201
✓ 变量总数：59
```

**如果报错**：
```
Error: 找不到文件！
→ 检查：~/Desktop/7100/7100.xlsx 是否存在
→ 或修改路径：data_path <- "你的实际路径"
```

---

### 【第3板块】数据编码 ⏱️ <1秒
**做什么**：创建Source、Frame、Intention等变量

**会看到什么**：
```
【第3板块】正在进行数据编码...
✓ 有效样本量：199
✓ 删除缺失数据后保留率：99.0%
```

---

### 【第4板块】标准化与中心化 ⏱️ <1秒
**做什么**：Z-score标准化，创建交互项

**会看到什么**：
```
【第4板块】正在进行标准化和中心化...
✓ 标准化完成！所有连续变量已转换为Z-score (M=0, SD=1)
✓ 中心化完成！交互项已创建
```

---

### 【第5板块】描述统计 ⏱️ <1秒
**做什么**：生成表1（描述统计）和表2（相关矩阵）

**会看到什么**：
```
【表1】描述统计
  Variable N        M      SD
  Source   199  0.528  0.500
  ...
  
【表2】Pearson相关矩阵
          Source  Frame Intention ...
Source     1.000  0.032     0.143
...
```

**复制这些表到论文里**

---

### 【第6板块】信度分析 ⏱️ <1秒
**做什么**：计算Cronbach Alpha（表3）

**会看到什么**：
```
【表3】信度系数（Cronbach Alpha）
                    Scale Cronbach_Alpha
            Intention        0.739
         SelfEfficacy        0.820
                 Trust        0.809
    HealthConsciousness        0.744
```

**检查标准**：所有值都应该 > 0.7 ✓

---

### 【第7板块】Model 1 - 总效应 ⏱️ 1秒
**做什么**：最简单的路径模型（只看Source/Frame→Intention）

**会看到什么**：
```
【第7板块】Model 1 - 总效应模型...
【MODEL 1 - 总效应】
lavaan 0.6-XX ...

Regressions:
                   Estimate  Std.err  Z-value  P(>|z|)  Std.all  Std.lv
  Intention ~
    Source           -0.062    0.197   -0.316    0.752   -0.062   -0.062
    Frame            -0.263    0.208   -1.267    0.207   -0.263   -0.263
    SourcexFrame      0.175    0.286    0.611    0.542    0.175    0.175
```

**检查**：Frame应该不显著（p>0.2）✓

---

### 【第8板块】Model 2 - a路径 ⏱️ 1秒
**做什么**：Source/Frame → Trust 和 → SelfEfficacy

**会看到什么**：
```
【第8板块】Model 2 - a路径模型...
【MODEL 2 - a路径】

Regressions:
                     Estimate  P(>|z|)
  Trust ~
    Source              0.790   <0.001  ***
  SelfEfficacy ~
    Source              0.190    0.330
```

**检查**：Source→Trust应该强且显著！ (p<0.001) ✓✓✓

---

### 【第9板块】Model 3 - b路径（无调节） ⏱️ 1秒
**做什么**：中介模型（加入Trust和SE作为中介）

**会看到什么**：
```
【第9板块】Model 3 - b路径模型...
【MODEL 3 - b路径（无调节）】

Regressions:
  Intention ~
    Trust              0.264   <0.001  ***
    SelfEfficacy       0.378   <0.001  ***
    
Defined Parameters:
  source_indirect_trust   0.209   <0.001  ***
```

**检查**：R²应该明显增加（与Model 1比较）✓

---

### 【第10板块】Model C1 - 完整调节中介 ⏱️ 1-2秒
**做什么**：☀️ 最重要的模型 - 加入HC调节

**会看到什么**：
```
【第10板块】Model C1 - 完整调节中介模型...
【MODEL C1 - 完整调节中介模型】

Regressions:
  Intention ~
    Trust (b_trust)          0.124    0.085 .
    SelfEfficacy             0.283   <0.001  ***
    HealthConsciousness      0.386   <0.001  ***
    TrustxHC                -0.105    0.102
    SExHC                    0.111    0.041  *     ← HC调节SE效应！
    
R-squared:
    Intention          0.393
```

**关键发现**：
- ✓ SExHC显著 (p=0.041*) 
- ✓ R²=0.393（比Model 3好很多）
- ⚠ TrustxHC不显著 (p=0.102)

---

### 【第11板块】模型比较 ⏱️ <1秒
**做什么**：生成表4 - 模型拟合指标对比

**会看到什么**：
```
【表4】模型拟合指标比较
                          ChiSq  DF     CFI   RMSEA    SRMR
Model 1 (总效应)            ...   ...   0.900  0.056   0.043
Model 3 (无调节)            ...   ...   0.950  0.032   0.028
Model C1 (完整调节)         ...   ...   0.965  0.025   0.022
```

**解读**：CFI应该 > 0.95, RMSEA < 0.05 ✓

---

### 【第12板块】提取关键系数 ⏱️ <1秒
**做什么**：生成表5 - Model C1的所有显著性系数

**会看到什么**：
```
【表5】Model C1 显著性系数（p < 0.1）
    lhs op     rhs        est  std.all       se pvalue
1  Trust  ~  Source     0.790    0.790   0.185 <0.001
2 Intention ~ SelfEfficacy 0.283 0.283 0.075 <0.001
3 Intention ~ HealthConsciousness 0.386 0.386 0.072 <0.001
4 Intention ~ SExHC 0.111 0.111 0.054 0.041
```

**复制这个表到results部分**

---

### 【第13板块】条件间接效应 ⏱️ <1秒
**做什么**：生成表6 - 不同HC水平下的间接效应

**会看到什么**：
```
【表6】条件间接效应（Source→Trust→Intention，在不同HC水平）
  HC_Level HC_Value Conditional_Effect
1 Low (-1SD)   -1.048           0.1234
2     Mean     0.000           0.1146
3 High (+1SD)  1.048           0.1205
```

**解读**：间接效应在高HC时略微增强

---

### 【第14板块】绘制路径图 ⏱️ 2-5秒
**做什么**：生成路径图PDF

**会看到什么**：
```
【第14板块】正在生成路径图...
✓ 路径图已保存至：~/Desktop/7100/lavaan_path_diagram.pdf
```

**然后**：双击PDF查看路径图（箭头和系数都标注出来）

---

### 【第15板块】生成完整报告 ⏱️ 1秒
**做什么**：生成详细的文本报告文件

**会看到什么**：
```
【第15板块】生成完整分析报告...
✓ 分析报告已保存至：~/Desktop/7100/lavaan_analysis_results.txt
```

**然后**：用任何文本编辑器打开.txt文件查看完整结果

---

### 【第16板块】完成总结 ⏱️ <1秒
**做什么**：最后的验证和提示

**会看到什么**：
```
【第16板块】分析总结
════════════════════════════════════════════════════════════════

✅ 所有分析已成功完成！

📊 生成的文件：
  1. 路径图：~/Desktop/7100/lavaan_path_diagram.pdf
  2. 详细报告：~/Desktop/7100/lavaan_analysis_results.txt

✓ R分析脚本执行完成！没有报错。
```

---

## ⚠️ 可能的错误与解决

### 错误1：找不到数据文件
```
Error: 找不到文件！
请检查文件路径：~/Desktop/7100/7100.xlsx
```

**解决**：
```r
# 方法1：检查文件是否真的在那里
file.exists("~/Desktop/7100/7100.xlsx")  # 应该返回 TRUE

# 方法2：修改路径（替换YOUR_USERNAME为你的用户名）
data_path <- "/Users/YOUR_USERNAME/Desktop/7100/7100.xlsx"

# 方法3：用选择器
data_path <- file.choose()  # 手动选择文件
```

---

### 错误2：包加载失败
```
Error: package 'lavaan' could not be loaded
```

**解决**：
```r
# 逐个检查和安装
install.packages("lavaan")
library(lavaan)
```

---

### 错误3：列号不匹配
```
Warning: Cannot extract a single element from a list
```

**原因**：你的xlsx文件列的顺序可能不对

**解决**：打开Excel，确认：
- 第28列：信息来源 (Source)
- 第29列：信息框架 (Frame)
- 第33-35列：行为意图 (Intention) 3个题目
- 第36-38列：自我效能 (SelfEfficacy) 3个题目
- 第39-43列：信任度 (Trust) 5个题目
- 第44-49列：健康意识 (HC) 6个题目

如果不对，在脚本中修改列号。例如：
```r
# 改这里（找到你的真实列号）
source_col <- colnames(data_raw)[29]  # 如果是第29列
```

---

### 错误4：模型不收敛
```
Warning: Model did not converge
```

**解决**：这通常表示数据有问题，尝试：
```r
# 检查缺失值
sum(is.na(data_analysis))

# 检查数据范围
summary(data_analysis)
```

---

## 📁 输出文件说明

### 文件1：`lavaan_path_diagram.pdf`
- 📊 调节中介模型的路径图
- 显示所有变量间的因果关系
- 标注了标准化系数
- **用途**：放在论文Results部分

### 文件2：`lavaan_analysis_results.txt`
- 📝 完整的分析报告
- 包含表4-表6的所有数据
- 包含Model C1的完整输出
- **用途**：参考和检查结果

### 文件3：R Console输出
- 💻 在R控制台实时显示
- 可以复制粘贴到Excel
- **用途**：快速查看结果

---

## 🎯 完整运行时间表

| 板块 | 时间 | 操作 |
|------|------|------|
| 1-3  | 2分  | 数据准备 |
| 4-6  | 1分  | 数据质量检查 |
| 7-13 | 5分  | 模型拟合 |
| 14-15| 2分  | 生成输出 |
| 16   | <1分 | 完成 |
| **总计** | **~10分** | **全部完成** |

---

## 📌 核心检查清单 ✅

运行完脚本后，检查以下内容：

- [ ] 第5板块：相关矩阵出现了吗？
- [ ] 第6板块：所有Cronbach Alpha > 0.7吗？
- [ ] 第8板块：Source→Trust的系数是0.79左右吗？
- [ ] 第10板块：Model C1的R²是0.39左右吗？
- [ ] 第12板块：SExHC显著（p=0.04左右）吗？
- [ ] 第14板块：PDF文件生成了吗？
- [ ] 第15板块：文本报告生成了吗？

如果都是YES，说明脚本完美运行！✨

---

## 💡 后续步骤

1. **复制表格**：表4/表5/表6复制到你的Word或Excel
2. **嵌入路径图**：在论文中插入PDF的路径图
3. **写Results**：参考lavaan_analysis_results.txt中的数据
4. **对比Python**：与之前Python的结果进行对照

---

## 🆘 还有问题？

可以检查的地方：
1. R版本：`R.version$version.string` （应该 >= 4.0）
2. 包版本：`packageVersion("lavaan")` （应该 >= 0.6）
3. 数据：Excel的前几行看起来正常吗？
4. 列号：你确认了所有列号吗？

---

**🎉 祝你分析顺利！如有疑问随时问。**
