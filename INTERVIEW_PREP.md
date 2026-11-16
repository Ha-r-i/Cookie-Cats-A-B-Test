# Explain this project in an interview

## A 45-second explanation

I reproduced a public experiment from the mobile game Cookie Cats. Players were
assigned to see their first progression gate at level 30 or level 40. I compared
the proportion who returned after one day and seven days, keeping all 90,189
assigned players in the main analysis. Day 7 retention was 19.02% at level 30 and
18.20% at level 40: a decrease of 0.82 percentage points. A proportion test and
bootstrap intervals supported the difference. I recommended keeping level 30,
with caveats about uneven assignment and missing revenue data.

## What did you implement?

A reproducible Python workflow, data validation, an assignment diagnostic,
retention tests, bootstrap intervals, sensitivity checks, generated reports,
and charts. The source question and dataset are public and credited. The
implementation was AI-assisted; do not imply you designed or ran the original
game experiment. Walk through the code yourself before using the resume entry.

## The numbers to remember

| Item | Value |
|---|---:|
| Players | 90,189 |
| Gate 30 / gate 40 | 44,700 / 45,489 |
| Day 7 retained players | 8,502 / 8,279 |
| Day 7 retention | 19.02% / 18.20% |
| Gate 40 minus gate 30 | -0.82 percentage points |
| Relative change | about -4.3% |
| Day 7 p-value | 0.0016 |
| Day 7 normal 95% CI | -1.33 to -0.31 percentage points |
| Day 1 p-value | 0.0744 |
| Allocation diagnostic p-value | 0.0086 |

## Questions you should answer without memorizing a script

**Why Day 7?** It measures whether players return a week after installation.
It is the primary decision metric for this reproduction. I did not preregister
the historical experiment; the public result was already available.

**What is the null hypothesis?** The population Day 7 retention rates are equal.
The two-sided alternative allows either an increase or a decrease.

**What is a p-value?** Assuming equal true rates and valid test assumptions,
it measures how often a difference at least this extreme would arise. It is
not the probability that the null hypothesis is true.

**Why a proportion z-test?** Retention is binary and both groups contain many
retained and non-retained players. Under the null, the shared rate is estimated
by pooling both groups. The confidence interval estimates the difference with
separate group variances.

**What does the confidence interval mean?** Repeating this procedure over many
valid samples would produce intervals covering the true difference about 95%
of the time. This interval is entirely negative in the gate-40-minus-gate-30
direction, consistent with lower retention at gate 40.

**What is bootstrapping?** Repeatedly sample each group's observed players with
replacement, then compute the difference. Binary outcomes let us draw the
number retained directly from the equivalent binomial distribution. The 2.5th
and 97.5th percentiles form a percentile interval. A fixed seed makes it reproducible.

**Percentage points versus percent?** 19.02% to 18.20% is a 0.82 point decrease.
Dividing 0.82 by 19.02 gives about a 4.3% relative decrease. Neither is revenue uplift.

**Why keep players who played no rounds?** Assignment defines the comparison.
Filtering on later engagement can change who is being compared and introduce bias.
The positive-round check is descriptive and does not repair that bias.

**Why keep the extreme round count?** A large engagement value does not make its
binary retention record invalid. Its removal is a sensitivity check, not an
assumption that it is a bot or logging error.

**Does p = 0.0744 prove Day 1 is unchanged?** No. The interval includes small
harms and small benefits. Establishing equivalence requires a practical margin
and an appropriate test; it is not established by a non-significant p-value.

**What about unequal group sizes?** Assuming intended 50/50 assignment, a
chi-square diagnostic gives p = 0.0086. I would check assignment logs, eligibility,
missing records, platform, time, and experiment instrumentation before rollout.
The diagnostic alone cannot identify the cause.

**Is retaining gate 30 guaranteed to help the business?** No. Retention favors
gate 30 in the observed data, but revenue, gate exposure, and long-term outcomes
are missing. I would investigate those trade-offs before a production decision.

## Quick preparation sequence

1. Explain the business question and the five data columns aloud.
2. Run `python analyze.py` and trace `load_players`, `compare`, and `analyze`.
3. Calculate 8,502 / 44,700 and 8,279 / 45,489 yourself.
4. Explain the difference between a p-value, an interval, and practical impact.
5. Explain why filtering after assignment can bias a comparison.
6. Practice the recommendation plus its two biggest caveats without reading notes.

## Why choose this over the two alternatives?

Cookie Cats has one intervention, two groups, and an easily explained outcome.
[Hardwood](https://github.com/anurag2506/hardwood) also involves a simulated product,
NBA data pipelines, staggered difference-in-differences, treatment heterogeneity,
and causal-inference assumptions.
[Dark Store Intelligence](https://github.com/anurag2506/dark_store_intelligence_analytics)
uses synthetic operational data, a multi-table SQL model, contribution margins,
availability modeling, estimated elasticities, and impact assumptions. Both are
valuable learning projects, but require more preparation to defend their scope.

For the immediate Perceptive Analytics application, focus on the Data Analytics
role and pair this project with your existing SQL/dashboard experience. This is
a fit judgment based on the project scope and the company's public careers page,
not a prediction of its private resume screening criteria.
