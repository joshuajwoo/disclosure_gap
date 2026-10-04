# Social-anxiety instrument decision

Status: **selected and specified for research use**. Decision version 1.0.0, 2026-10-04.

## Selection

The primary baseline and follow-up outcome is the American Psychiatric Association’s **Severity Measure for Social Anxiety Disorder (Social Phobia)—Adult**, DSM-5-TR version (“APA SAD-D Adult”). It is a 10-item self-report measure for adults age 18 and older using a past-seven-days recall period. The study will use its continuous total raw or prorated raw score, not diagnostic categories.

Normative wording, order, instructions, response labels, attribution, and scoring source:

- https://www.psychiatry.org/File%20Library/Psychiatrists/Practice/DSM/DSM-5-TR/APA-DSM5TR-SeverityMeasureForSocialAnxietyDisorderAdult.pdf
- APA assessment-measures index: https://www.psychiatry.org/psychiatrists/practice/dsm/educational-resources/assessment-measures

The official PDF is the normative item source. Repository contracts identify items as `SAD01`–`SAD10` without creating an independently edited wording copy.

## Permission

The official measure states that researchers may reproduce it without requesting permission. This grant covers the study’s research administration. Preserve the measure, response labels, attribution, and copyright notice without modification. Translations, commercial reuse, altered items, or uses outside the stated grant require a separate rights review.

The synthetic public demo must not imply APA endorsement. It may use clearly fictional responses under the research-reproduction grant; if the demo’s public/portfolio use is later judged outside that grant, show only derived fictional scores or obtain separate permission.

## Age and repeated measurement

- The official instructions specify age 18 and older, matching the study’s 18–22 population.
- The measure uses a seven-day recall period and the instructions allow regular repeated completion to track change.
- Initial development found clinical/nonclinical score separation and associations with clinician-rated severity: https://pubmed.ncbi.nlm.nih.gov/23148016/
- A community study of 930 adults found evidence for unidimensionality, measurement invariance, internal consistency, test–retest reliability, and convergent/divergent validity: https://pmc.ncbi.nlm.nih.gov/articles/PMC6877262/
- A later Australian community study evaluated the 10-item scale in 1,052 adults: https://pubmed.ncbi.nlm.nih.gov/34704259/

Evidence is not specific to a four-week U.S. convenience sample of people ages 18–22. The measure was created as a disorder-severity measure and should not be treated as a diagnosis or population screening result. These limitations remain prespecified.

## Scoring

Each of the 10 items is coded from 0 to 4 under the official response labels.

- With 10 answered items: sum the item scores; range 0–40.
- With 8 or 9 answered items: calculate `(answered-item sum × 10) / answered-item count`, then round to the nearest whole number under the official instructions.
- With 7 or fewer answered items: do not calculate a total; store the outcome as missing.
- Preserve unanswered/“prefer not to answer” separately from score 0.
- Record item values, answered-item count, raw sum, whether prorating occurred, and final total.

The primary model uses the 0–40 final total continuously. The application will not show severity labels, cutoffs, diagnoses, or treatment recommendations.

## Version control

Contract identifier: `apa_dsm5tr_sad_adult`; instrument version: `DSM-5-TR-2022`; language: `en`. Before real recruitment, the institutional submission must include the official measure and this decision. Any upstream revision requires a new contract version and a documented comparability decision.
