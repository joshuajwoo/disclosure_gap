# Synthetic scenario specification

Synthetic cohorts are software test inputs, not simulations claimed to represent real people. Every dataset, cohort, and participant carries `synthetic: true`; generator parameters describe code behavior only.

| Scenario       | Declared generator behavior                                                                           | Pipeline expectation                                                        |
| -------------- | ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `null`         | Follow-up equals baseline regardless of the gap.                                                      | Adjusted gap signal remains zero.                                           |
| `weak_effect`  | A small positive coefficient is applied to the centered gap.                                          | Direction is positive but smaller than `known_effect`.                      |
| `known_effect` | A larger positive coefficient is applied to the centered gap.                                         | Pipeline recovers a clear positive direction.                               |
| `confounded`   | Direct gap coefficient is zero; a synthetic latent factor affects both the gap pattern and follow-up. | An apparent association exists and must be labeled confounded.              |
| `missingness`  | Some participants have only two check-ins.                                                            | Gap is missing with the explicit `fewer_than_3_check_ins` reason.           |
| `attrition`    | Some participants withdraw before follow-up.                                                          | Records remain synthetic; no outcome is invented and attrition is reported. |

Within cohorts, fixtures also cover complete participation, no desire to share, sharing after intent, choosing privacy, prefer-not-to-answer, friend/family audiences, zero and one-event denominators, and both supported check-in contract versions. The generator is deterministic for the same seed, version, scenario, and size.

Validation checks markers, unique IDs, assessment and check-in contracts, expected feature values, range assumptions, scenario direction, missingness, and attrition. The committed regression fixture freezes a small raw-to-feature-to-summary example independently of the larger generated cohorts.
