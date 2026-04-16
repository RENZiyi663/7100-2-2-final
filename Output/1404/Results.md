# Results

All statistical analyses were conducted using R (version 4.5.2). Confirmatory factor analysis (CFA) and structural path analysis were performed using the *lavaan* package (Rosseel, 2012), with robust maximum likelihood estimation (MLR) and Satorra-Bentler scaled test statistics for the measurement model. Reliability analysis was conducted via the *psych* package. The analytical strategy proceeded in three stages: (1) evaluation of the measurement model to establish construct validity and reliability prior to hypothesis testing, (2) estimation of a structural path model to simultaneously examine the direct effects of information source and message frame on exercise behavioural intention, as well as the hypothesised indirect effects through attitude, trust, and self-efficacy (H1–H6), and (3) moderated regression analyses to test whether health consciousness moderates the information source effect on exercise intention (H7). Information source was coded as 0 = human and 1 = AI; message frame was coded as 0 = loss-framed and 1 = gain-framed. Sex was included as a control variable in all models.

Before testing the substantive hypotheses, a confirmatory factor analysis was conducted on the five latent constructs—Attitude (3 items), Trust (5 items), Self-efficacy (3 items), Health Consciousness (6 items), and Behavioural Intention (3 items)—to ensure that the measurement instruments adequately captured their intended constructs, as valid hypothesis testing requires well-measured constructs. The CFA model demonstrated acceptable fit to the data (χ²(160) = 273.39, *p* < .001; CFI = .91; TLI = .90; RMSEA = .06, 90% CI [.05, .07]; SRMR = .06; see Table 4). All standardised factor loadings were statistically significant and ranged from .43 to .87. Construct reliability was evaluated using Cronbach's alpha (α) and McDonald's omega (ω), and convergent validity was assessed via average variance extracted (AVE). As shown in Table 3, all constructs demonstrated adequate reliability (α ranging from .64 to .82; ω ranging from .65 to .82). Self-efficacy exhibited strong convergent validity (AVE = .60), Intention showed adequate convergent validity (AVE = .49), and Trust was acceptable (AVE = .46), while Attitude (AVE = .39) and Health Consciousness (AVE = .35) showed lower but acceptable values given the number of items and the breadth of the constructs measured.

**Table 3**
*Reliability and Validity Indices*

| Construct | α | ω | AVE |
|:----------|:-----:|:-----:|:-----:|
| Attitude | .6449 | .6528 | .3892 |
| Intention | .7393 | .7450 | .4945 |
| Self-efficacy | .8166 | .8202 | .6049 |
| Trust | .8068 | .8085 | .4592 |
| Health Consciousness | .7434 | .7529 | .3468 |

**Table 4**
*Confirmatory Factor Analysis Fit Indices*

| Index | Value |
|:------|------:|
| χ² (scaled) | 273.39 |
| *df* | 160 |
| *p* | < .001 |
| CFI (scaled) | .914 |
| TLI (scaled) | .897 |
| RMSEA (scaled) | .060 |
| RMSEA 90% CI | [.048, .071] |
| SRMR | .060 |

Table 1 presents descriptive statistics for all study variables across 199 participants. All constructs were measured on 7-point Likert scales and demonstrated reasonable variability. Normality was adequate, with skewness values ranging from -1.16 to -0.54 and kurtosis values from -0.05 to 3.00. Bivariate Pearson correlations are presented in Table 2. Notably, Attitude and Behavioural Intention were strongly positively correlated (*r* = .76, *p* < .001), and Health Consciousness demonstrated moderate positive correlations with Attitude (*r* = .53, *p* < .001), Intention (*r* = .56, *p* < .001), and Self-efficacy (*r* = .53, *p* < .001). Information Source showed significant negative correlations with Trust (*r* = -.36, *p* < .001) and Self-efficacy (*r* = -.17, *p* < .05), indicating that participants exposed to the AI source reported lower trust and self-efficacy compared to those receiving human-sourced information. Message Frame demonstrated weak, non-significant correlations with all study variables. Multicollinearity diagnostics confirmed that all variance inflation factors were below 2 (range: 1.01–1.81), indicating no problematic multicollinearity among predictors.

**Table 1**
*Descriptive Statistics (N = 199)*

| Variable | *M* | *SD* | Min | Max | Skewness | Kurtosis | α |
|:---------|:-----:|:-----:|:-----:|:-----:|:--------:|:--------:|:-----:|
| Attitude | 6.11 | 0.61 | 3.33 | 7.00 | -1.03 | 1.85 | .6449 |
| Trust | 5.61 | 0.69 | 2.40 | 7.00 | -0.79 | 1.68 | .8068 |
| Self-efficacy | 5.53 | 0.92 | 1.67 | 7.00 | -1.16 | 2.20 | .8166 |
| Health Consciousness | 5.77 | 0.58 | 4.00 | 7.00 | -0.54 | -0.05 | .7434 |
| Intention | 5.83 | 0.68 | 2.67 | 7.00 | -1.07 | 3.00 | .7393 |

*Note.* All variables measured on 7-point scales.

**Table 2**
*Bivariate Correlation Matrix (N = 199)*

| | Source | Frame | Attitude | Trust | SE | HC | Intention | Sex |
|:----------|:--------:|:------:|:--------:|:--------:|:--------:|:--------:|:---------:|:------:|
| Source | — | .02 | .04 | -.36\*\*\* | -.17\* | -.11 | -.01 | -.01 |
| Frame | .02 | — | .08 | .05 | .05 | .08 | .09 | .06 |
| Attitude | .04 | .08 | — | .35\*\*\* | .39\*\*\* | .53\*\*\* | .76\*\*\* | .08 |
| Trust | -.36\*\*\* | .05 | .35\*\*\* | — | .41\*\*\* | .47\*\*\* | .37\*\*\* | .05 |
| SE | -.17\* | .05 | .39\*\*\* | .41\*\*\* | — | .53\*\*\* | .47\*\*\* | .14 |
| HC | -.11 | .08 | .53\*\*\* | .47\*\*\* | .53\*\*\* | — | .56\*\*\* | .12 |
| Intention | -.01 | .09 | .76\*\*\* | .37\*\*\* | .47\*\*\* | .56\*\*\* | — | .12 |
| Sex | -.01 | .06 | .08 | .05 | .14 | .12 | .12 | — |

*Note.* SE = Self-efficacy; HC = Health Consciousness. \**p* < .05. \*\*\**p* < .001.

To test the hypothesised direct and indirect relationships among variables (H1–H6), a structural path model was estimated using *lavaan*. Information Source, Message Frame, and Sex served as exogenous predictors; Attitude, Trust, and Self-efficacy as mediators; and Behavioural Intention as the outcome. Health Consciousness (mean-centred) and its interaction with Information Source were also included in the Intention equation to simultaneously account for the moderation hypothesis (H7). This integrated model permits the estimation of all direct and indirect pathways within a single framework rather than relying on separate analyses. The full set of structural path coefficients is presented in Table 5. Information Source did not significantly predict Behavioural Intention directly (β = 0.02, *SE* = 0.07, *p* = .76, 95% CI [-0.11, 0.15]), nor did Message Frame (β = 0.02, *SE* = 0.06, *p* = .73, 95% CI [-0.10, 0.13]). These results do not support Hypothesis 1 (that human-sourced information increases exercise behavioural intention more than AI-sourced information) or Hypothesis 2 (that gain-framed messages increase intention more than loss-framed messages). Attitude emerged as the dominant predictor of Behavioural Intention (β = 0.69, *SE* = 0.08, *p* < .001, 95% CI [0.52, 0.83]), and Self-efficacy served as a secondary predictor (β = 0.10, *SE* = 0.04, *p* = .013, 95% CI [0.03, 0.19]), whereas Trust did not significantly predict Intention (β = 0.03, *SE* = 0.06, *p* = .65). Regarding the upstream a-paths linking the independent variables to the mediators, Information Source significantly predicted Trust (β = -0.50, *SE* = 0.09, *p* < .001, 95% CI [-0.68, -0.31]) and Self-efficacy (β = -0.30, *SE* = 0.13, *p* = .019, 95% CI [-0.55, -0.05]), with AI-sourced information associated with lower trust and self-efficacy relative to human-sourced information. Information Source did not significantly predict Attitude (β = 0.05, *SE* = 0.09, *p* = .59). Message Frame showed no significant effects on any mediator (all *p* > .30).

**Table 5**
*Structural Path Coefficients*

| Path | β | *SE* | *p* | Sig | 95% CI |
|:-----|------:|------:|------:|:---:|:------:|
| Attitude ← Source | 0.0478 | 0.0877 | .5855 | | [-0.126, 0.220] |
| Attitude ← Frame | 0.0884 | 0.0873 | .3113 | | [-0.080, 0.262] |
| Attitude ← Sex | 0.0910 | 0.0862 | .2910 | | [-0.076, 0.260] |
| Trust ← Source | -0.4951 | 0.0922 | < .001 | \*\*\* | [-0.676, -0.313] |
| Trust ← Frame | 0.0681 | 0.0914 | .4565 | | [-0.113, 0.245] |
| Trust ← Sex | 0.0662 | 0.0900 | .4621 | | [-0.112, 0.246] |
| SE ← Frame | 0.0838 | 0.1275 | .5110 | | [-0.169, 0.337] |
| SE ← Source | -0.3033 | 0.1288 | .0185 | \* | [-0.549, -0.050] |
| SE ← Sex | 0.2467 | 0.1237 | .0462 | \* | [0.004, 0.494] |
| Intention ← Source | 0.0198 | 0.0652 | .7617 | | [-0.106, 0.150] |
| Intention ← Frame | 0.0205 | 0.0593 | .7300 | | [-0.098, 0.133] |
| Intention ← Attitude | 0.6943 | 0.0807 | < .001 | \*\*\* | [0.517, 0.832] |
| Intention ← Trust | 0.0269 | 0.0588 | .6473 | | [-0.079, 0.153] |
| Intention ← SE | 0.1025 | 0.0415 | .0134 | \* | [0.026, 0.188] |
| Intention ← HC (centred) | 0.1689 | 0.1034 | .1024 | | [-0.022, 0.385] |
| Intention ← Source × HC | 0.0007 | 0.1144 | .9948 | | [-0.235, 0.213] |
| Intention ← Sex | 0.0440 | 0.0590 | .4565 | | [-0.074, 0.161] |

*Note.* SE = Self-efficacy; HC = Health Consciousness. \**p* < .05. \*\*\**p* < .001.

To test the proposed mediation hypotheses (H3–H6), indirect effects were computed as the products of the relevant a-path and b-path coefficients, with 95% confidence intervals derived via the delta method. This approach assesses whether information source and message frame influence behavioural intention *through* the hypothesised mediating mechanisms rather than directly. As presented in Table 6, the indirect effect of Information Source through Attitude on Intention (H3: Source → Attitude → Intention) was not significant (β = 0.03, *SE* = 0.06, *p* = .58, 95% CI [-0.09, 0.15]). The indirect effect of Message Frame through Attitude (H4: Frame → Attitude → Intention) was likewise non-significant (β = 0.06, *SE* = 0.06, *p* = .33, 95% CI [-0.05, 0.20]). The indirect effect of Information Source through Trust (H5: Source → Trust → Intention) was non-significant (β = -0.01, *SE* = 0.03, *p* = .64, 95% CI [-0.07, 0.04]), despite the significant Source → Trust path, because Trust itself did not significantly predict Intention (b-path *p* = .65). The indirect effect of Message Frame through Self-efficacy (H6: Frame → SE → Intention) was also non-significant (β = 0.01, *SE* = 0.01, *p* = .55, 95% CI [-0.02, 0.04]). The total indirect effects were non-significant for both Information Source (β = 0.02, *SE* = 0.07, *p* = .77, 95% CI [-0.11, 0.15]) and Message Frame (β = 0.07, *SE* = 0.07, *p* = .31, 95% CI [-0.06, 0.22]), and total effects (direct + indirect combined) were likewise non-significant (Source: β = 0.04, *SE* = 0.09, *p* = .64, 95% CI [-0.13, 0.21]; Frame: β = 0.09, *SE* = 0.09, *p* = .31, 95% CI [-0.08, 0.27]). Hypotheses 3 through 6 were therefore not supported.

**Table 6**
*Indirect and Total Effects*

| Effect | β | *SE* | *p* | Sig | 95% CI |
|:-------|------:|------:|------:|:---:|:------:|
| H3: Source → Attitude → Intention | 0.0332 | 0.0606 | .5837 | | [-0.090, 0.152] |
| H4: Frame → Attitude → Intention | 0.0614 | 0.0626 | .3268 | | [-0.050, 0.197] |
| H5: Source → Trust → Intention | -0.0133 | 0.0286 | .6412 | | [-0.073, 0.041] |
| H6: Frame → SE → Intention | 0.0086 | 0.0144 | .5496 | | [-0.019, 0.039] |
| Total indirect (Source) | 0.0199 | 0.0670 | .7665 | | [-0.114, 0.149] |
| Total indirect (Frame) | 0.0700 | 0.0692 | .3120 | | [-0.057, 0.216] |
| Total effect (Source) | 0.0397 | 0.0857 | .6435 | | [-0.128, 0.205] |
| Total effect (Frame) | 0.0904 | 0.0892 | .3108 | | [-0.085, 0.265] |

*Note.* \**p* < .05. \*\*\**p* < .001.

To test Hypothesis 7—that health consciousness moderates the information source effect on exercise intention, with stronger effects for those with low health consciousness—two ordinary least squares (OLS) regression models were estimated. This two-model approach was adopted to distinguish between moderation of the direct effect (controlling for mediators) and moderation of the total effect (without mediator controls), because the moderating influence of health consciousness may operate at different levels of the causal chain. The first model (Table 7) tested whether the Source × Health Consciousness interaction predicted Intention while controlling for Attitude, Trust, Self-efficacy, Frame, and Sex. The interaction term was not significant (β = 0.001, *SE* = 0.11, *t* = 0.007, *p* = .99), indicating that health consciousness did not moderate the direct effect of information source on intention after accounting for the mediating variables. The second model (Table 8) tested the same interaction on the total effect of Source on Intention—without mediator controls—to assess whether health consciousness moderates the overall influence of information source, including portions transmitted through trust, attitude, and self-efficacy. Here, the Source × Health Consciousness interaction was significant (β = -0.39, *SE* = 0.14, *t* = -2.86, *p* = .005), demonstrating that health consciousness moderated the total effect of information source on behavioural intention. The negative interaction coefficient indicates that the information source effect was attenuated among individuals with higher health consciousness: for those low in health consciousness (1 *SD* below the mean), information source exerted a larger differentiating effect on intention, whereas for those high in health consciousness (1 *SD* above the mean), the source-based differences in intention were substantially reduced. Hypothesis 7 was therefore supported.

**Table 7**
*Moderation Analysis: Direct Effect of Source on Intention (Controlling for Mediators)*

| Predictor | β | *SE* | *t* | *p* | Sig |
|:----------|------:|------:|-------:|------:|:---:|
| (Intercept) | 0.8309 | 0.4665 | 1.781 | .0765 | |
| Source | 0.0198 | 0.0657 | 0.301 | .7638 | |
| HC (centred) | 0.1689 | 0.0957 | 1.765 | .0792 | |
| Frame | 0.0205 | 0.0602 | 0.340 | .7342 | |
| Attitude | 0.6943 | 0.0630 | 11.023 | < .001 | \*\*\* |
| Trust | 0.0269 | 0.0550 | 0.490 | .6250 | |
| SE | 0.1025 | 0.0401 | 2.559 | .0113 | \* |
| Sex | 0.0440 | 0.0608 | 0.723 | .4706 | |
| Source × HC | 0.0007 | 0.1093 | 0.007 | .9946 | |

*Note.* SE = Self-efficacy; HC = Health Consciousness. \**p* < .05. \*\*\**p* < .001.

**Table 8**
*Moderation Analysis: Total Effect of Source on Intention (Without Mediator Controls)*

| Predictor | β | *SE* | *t* | *p* | Sig |
|:----------|------:|------:|-------:|------:|:---:|
| (Intercept) | 5.7172 | 0.0769 | 74.316 | < .001 | \*\*\* |
| Source | 0.0690 | 0.0796 | 0.867 | .3870 | |
| HC (centred) | 0.8528 | 0.0973 | 8.768 | < .001 | \*\*\* |
| Frame | 0.0518 | 0.0794 | 0.652 | .5154 | |
| Sex | 0.0847 | 0.0799 | 1.060 | .2904 | |
| Source × HC | -0.3918 | 0.1370 | -2.861 | .0047 | \*\* |

*Note.* HC = Health Consciousness. \**p* < .05. \*\**p* < .01. \*\*\**p* < .001.

The structural model accounted for 56.7% of the variance in Behavioural Intention (*R*² = .567; Table 9), representing substantial explanatory power for the outcome variable. The experimental manipulations and control variables explained 13.6% of the variance in Trust—primarily driven by Information Source—4.9% in Self-efficacy, and 1.3% in Attitude, indicating that the experimental conditions had their strongest upstream impact on participants' trust perceptions.

**Table 9**
*Variance Explained (R²)*

| Variable | *R*² |
|:---------|------:|
| Attitude | .0131 |
| Trust | .1356 |
| Self-efficacy | .0485 |
| Intention | .5671 |

In summary, of the seven hypotheses tested, only Hypothesis 7 received empirical support: health consciousness significantly moderated the total effect of information source on exercise behavioural intention (β = -0.39, *p* = .005), with stronger source effects among individuals with low health consciousness. Hypotheses 1 and 2, which predicted that human-sourced and gain-framed messages would lead to greater exercise intention, were not supported as neither information source nor message frame directly predicted behavioural intention. Hypotheses 3 through 6, proposing that attitude, trust, and self-efficacy would mediate the relationships between the independent variables and intention, were also not supported despite significant upstream effects of information source on trust (*p* < .001) and self-efficacy (*p* = .019), because these upstream effects did not translate into significant indirect pathways to intention.
