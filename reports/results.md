# Cookie Cats analysis results

Retrospective reproduction; differences are gate 40 minus gate 30. Every assigned player is included in the primary analysis.

| Metric | Gate 30 | Gate 40 | Difference | 95% normal CI | p-value |
|---|---:|---:|---:|---:|---:|
| retention_1 | 44.82% | 44.23% | -0.59 pp | -1.24 to +0.06 pp | 0.0744 |
| retention_7 | 19.02% | 18.20% | -0.82 pp | -1.33 to -0.31 pp | 0.0016 |

Allocation check, assuming 50/50: p = 0.0086. This needs assignment logs to investigate, and does not prove faulty randomization.

## Sensitivity checks

- without_max_rounds: Day 7 difference -0.82 pp, p = 0.0016.
- positive_rounds_only: Day 7 difference -0.81 pp, p = 0.0026.

## Recommendation

Keep the gate at level 30 pending investigation of allocation and revenue trade-offs.

## Interpretation limits

- Day 7 is the decision metric for this reproduction; no historical preregistration is claimed.
- Day 1 is supporting evidence. A non-significant result does not establish equivalence.
- The bootstrap fraction favoring gate 30 is not a probability that it is truly better.
- Positive-round players are a post-assignment subset; that check is descriptive, not a new causal estimate.
- No revenue, assignment logs, gate exposure, or longer-term outcomes are available.
- The large game-round observation is not proven to be an error; exclusion is only a sensitivity check.
