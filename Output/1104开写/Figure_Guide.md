# Visualization Guide for Research Results

## Overview
This folder contains three publication-ready figures (PNG and PDF formats) that visualize the key findings from the structural equation modeling analysis of exercise behavioral intention.

---

## Figure Descriptions

### **Figure 1: Structural Path Diagram (Figure1_PathDiagram.png/pdf)**

**Purpose:** Displays the entire structural equation model with all direct paths, mediating relationships, and moderation effects.

**Key Features:**
- **Blue boxes (left)**: Exogenous variables (Information Source, Message Frame)
- **Green boxes (middle)**: Mediating variables (Attitude, Trust, Self-efficacy) and moderator (Health Consciousness)
- **Red box (right)**: Outcome variable (Behavioral Intention)

**Path Interpretation:**
- **Green arrows (thick/medium width)**: Significant effects (*** p<.001, ** p<.01, * p<.05)
- **Orange arrows (medium width)**: Weak but significant effects
- **Red arrows (thin)**: Non-significant effects
- **Purple arrows**: Moderation effect of Health Consciousness

**Key Findings Highlighted:**
- **Strongest path**: Attitude → Intention (β=.69***)
- **Strong upstream effect**: Information Source → Trust (β=-.50***)
- **Failed relationships**: Information Source/Frame → Intention (ns), Trust → Intention (ns)
- **Moderation**: Health Consciousness moderates Source effect on Intention (β=-.39**)

---

### **Figure 2: Health Consciousness Moderation Effect (Figure2_ModerationEffect.png/pdf)**

**Purpose:** Illustrates how Health Consciousness moderates the effect of Information Source on Behavioral Intention.

**Two Subpanels:**

**2A: Conditional Effects Line Plot**
- **X-axis**: Information Source (AI vs. Human)
- **Y-axis**: Behavioral Intention (intention to exercise)
- **Three lines**: 
  - Red line: Low Health Consciousness (High sensitivity to source)
  - Blue line: Medium Health Consciousness
  - Green line: High Health Consciousness (Low sensitivity to source)

**Interpretation**: 
Higher HC individuals show flatter lines, indicating reduced dependence on source characteristics. Lower HC individuals show steeper source-dependent variation.

**2B: Source Effect Across HC Levels (Bar Chart)**
- Shows the magnitude of Information Source effect at different HC levels
- Negative bar slopes downward → Source effect diminishes with higher HC
- Interpretation: HC acts as a "protective buffer" against source-based persuasion

---

### **Figure 3: Indirect Effects Comparison (Figure3_IndirectEffects.png/pdf)**

**Purpose:** Compares the magnitude of all proposed indirect effects and shows why mediation pathways failed.

**Two Subpanels:**

**3A: Indirect Effects Bar Chart (Horizontal)**
- Lists 6 proposed indirect pathways
- **Red bars**: Non-significant pathways (p ≥ .05)
- **Green bars**: Significant pathways (p < .05) — All are red!
- All indirect effects shown with p-values

**3B: Effect Size Hierarchy (Vertical Bar Chart)**
- **Attitude → Intention (Direct)**: β=.69*** (Dominates!)
- **Total Indirect Effects**: β=.02 (negligible)
- **Direct Source/Frame Effects**: β≈.02 (negligible)

**Key Message**: 
Attitude single-handedly explains most of Behavioral Intention variance. All hypothesized indirect pathways are non-significant, representing a "cognitive-behavioral disconnection."

---

## How to Use These Figures

### In Your Manuscript:
1. **Figure 1** goes in Results section (after describing model fit)
2. **Figure 2** goes in Results section (after describing moderation effects)
3. **Figure 3** can go in Results (to summarize indirect effects) or Discussion (to explain why hypotheses H3-H6 failed)

### In Your Presentation/Defense:
- Start with Figure 1 to show the full model structure
- Use Figure 2 to explain H7 (Health Consciousness moderation)
- Use Figure 3 to explain why H1-H6 showed complex patterns of support/non-support

### Format:
- **PNG files** (432-410 KB): Use for presentations, web, quick sharing
- **PDF files** (41-49 KB): Use for publication, high-quality printing

---

## Statistical Significance Legend

| Notation | Meaning | p-value |
|----------|---------|---------|
| *** | Highly significant | p < .001 |
| ** | Very significant | p < .01 |
| * | Significant | p < .05 |
| ns | Not significant | p ≥ .05 |

---

## Key Takeaways to Communicate

1. **Path Diagram (Figure 1)**: Shows that while exogenous variables affect mediators, these don't cascade to intention through proposed mechanisms.

2. **Moderation (Figure 2)**: Health Consciousness significantly moderates Source effects—supporting H7 despite broader mediation failures.

3. **Indirect Effects (Figure 3)**: Reveals why hypotheses H3-H6 failed: the attitude-intention link is overwhelmingly strong and bypasses all indirect pathways.

---

## Technical Notes

- Figures created using Python (matplotlib)
- All coefficients, p-values, and effect sizes based on actual analysis results
- Interaction plot (Figure 2A) based on conditional effect calculations at ±1 SD from HC mean
- Bar colors consistently indicate significance patterns across all figures

---

**Last Updated:** April 12, 2026  
**File Location:** `/workspaces/7100-2-2-final/Output/1104开写/`
