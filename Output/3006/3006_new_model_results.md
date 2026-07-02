# 3006 新模型运行结果

模型：`Intention ~ Source_clean * Frame_clean * HealthC_c`

## 1. 数据口径检查

- 原始数据行数：199
- 主模型完整样本：199
- 本脚本残差 df：191
- SPSS 截图残差 df：179
- 是否匹配 SPSS 截图 df：否

### clean 条件样本数

| Source | Frame | n |
|---|---|---:|
| Human expert | Loss frame | 48 |
| Human expert | Gain frame | 51 |
| AI coach | Loss frame | 51 |
| AI coach | Gain frame | 49 |

## 2. 信度

| Scale | Items | N complete | alpha |
|---|---:|---:|---:|
| Intention | 3 | 199 | 0.739 |
| HealthC | 6 | 199 | 0.743 |

## 3. 主模型

| Model | N | df model | df error | R2 | F | p |
|---|---:|---:|---:|---:|---:|---:|
| Source * Frame * HealthC | 199 | 7 | 191 | 0.403 | 18.412 | 0.0000 |

## 4. Type-III 风格 partial F 检验

| Effect | df | F | p | sig | partial eta squared |
|---|---:|---:|---:|:---:|---:|
| Source | 1, 191 | 0.125 | 0.7235 |  | 0.001 |
| Frame | 1, 191 | 1.523 | 0.2186 |  | 0.008 |
| HealthC_c | 1, 191 | 41.122 | 1.10e-09 | *** | 0.177 |
| Source_x_Frame | 1, 191 | 0.300 | 0.5847 |  | 0.002 |
| Source_x_HealthC | 1, 191 | 0.372 | 0.5428 |  | 0.002 |
| Frame_x_HealthC | 1, 191 | 14.970 | 1.50e-04 | *** | 0.073 |
| Source_x_Frame_x_HealthC | 1, 191 | 3.591 | 0.0596 | . | 0.018 |

## 5. Source simple effects

对比为 `AI coach - Human expert`，并对 Frame 两个水平取平均。

| HealthC level | estimate | p | sig |
|---|---:|---:|:---:|
| Low HealthC (-1 SD) | -0.298 | 0.0069 | ** |
| Mean HealthC | -0.081 | 0.2946 |  |
| High HealthC (+1 SD) | 0.136 | 0.2150 |  |

## 6. Frame simple effects

对比为 `Gain frame - Loss frame`，并对 Source 两个水平取平均。

| HealthC level | estimate | p | sig |
|---|---:|---:|:---:|
| Low HealthC (-1 SD) | 0.357 | 0.0013 | ** |
| Mean HealthC | 0.093 | 0.2291 |  |
| High HealthC (+1 SD) | -0.171 | 0.1210 |  |

## 7. 假设检查

| Hypothesis | Result | Evidence |
|---|---|---|
| H1 | supported | F=41.1216, p=1.10e-09, eta_p2=0.1772 |
| H2 | not supported | F=0.3716, p=0.5428, eta_p2=0.0019 |
| H3 | supported | F=14.9700, p=1.50e-04, eta_p2=0.0727 |
| H4 | not supported | F=3.5913, p=0.0596, eta_p2=0.0185 |

## 8. 自动诊断

- 警告：当前 CSV 复现模型的残差 df 与 SPSS 截图不一致。截图 `F(7,179)` 暗示主模型样本约为 187，而当前 clean 数据主模型样本为 199。这说明 SPSS 很可能使用了不同筛选规则、不同数据文件或额外缺失值处理。
- 额外敏感性检查：直接使用原 CSV 的 Source/Frame 数值列时，模型仍为 N=199、df_error=191、R2=0.402，因此也不能解释 SPSS 截图中的 df=179。
- Source/Frame 使用 Stimuli 标签重建 clean 编码；不要直接按原 CSV 数值列解释方向。
- 主效应不应作为核心假设；新模型核心应放在 HealthC 主效应和交互项。
- 09 交叉检验与组员 PDF 摘要已纳入主脚本自动生成。
