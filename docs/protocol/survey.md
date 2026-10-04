# Survey specification

Status: protocol-complete 1.0.0 for synthetic/internal testing; not approved for real recruitment. All original questions offer “Prefer not to answer” unless eligibility or consent makes participation impossible.

## Eligibility and consent

**E1. What is your age today?** `Under 18`; `18–19`; `20–22`; `23 or older`; `Prefer not to answer`.

Only `18–19` and `20–22` are eligible. Do not store an exact birth date.

**C1. I have read the consent information and agree to participate in this research study.** `I agree`; `I do not agree`.

Record the consent-document version and timestamp. A non-agreement ends the flow without creating response records.

## Baseline context

**B1. If you wanted support with a personal concern, how confident are you that at least one trusted person would respond in a way that felt supportive?** `Not at all confident`; `A little confident`; `Somewhat confident`; `Very confident`; `Completely confident`; `Not applicable—I do not have a person in mind`; `Prefer not to answer`.

**B2. In general, how comfortable do you feel talking with a trusted person about everyday problems?** `Not at all comfortable`; `A little comfortable`; `Somewhat comfortable`; `Very comfortable`; `Completely comfortable`; `Not applicable`; `Prefer not to answer`.

**B3. In general, how comfortable do you feel talking with a trusted person about a personal insecurity?** Same response options as B2.

Optional demographic/context fields beyond age band require separate scientific justification and disclosure-risk review before addition.

## Baseline outcome module

Administer the APA DSM-5-TR Severity Measure for Social Anxiety Disorder—Adult exactly as published in the normative PDF linked by `instrument-decision.md`. Preserve its instructions, ten-item order, response labels, attribution, and copyright notice. The wire contract maps the items in order to `SAD01`–`SAD10` and adds `prefer_not_to_answer` as an unanswered response. Store instrument ID, version, language, item codes, responses, and completion timestamp. Do not show a cutoff, diagnosis, severity label, or interpretation.

## Weekly check-in (one per approved weekly window)

Preamble: “The next questions are about the past 7 days. Choosing privacy can be healthy. We are interested in what happened, not in judging whether sharing was the right choice.”

**W1. During the past 7 days, was there a personal concern you wanted to talk about with someone you trust?** `Yes`; `No`; `Not sure`; `Prefer not to answer`.

If W1 is not `Yes`, skip W2–W7. The record remains a completed check-in but is not an eligible denominator week.

**W2. Who did you most want to talk with?** `Friend`; `Family member`; `Partner`; `Another trusted person`; `No particular person`; `Prefer not to answer`.

**W3. Did you talk with that person about the concern during the past 7 days?** `Yes`; `No`; `I chose to keep it private`; `I did not have a safe or appropriate opportunity`; `Not applicable—no particular person`; `Prefer not to answer`.

For the primary feature, `Yes` maps to shared=true. `No` and `I chose to keep it private` map to shared=false but remain separate raw values. Safety/opportunity, not-applicable, and prefer-not-to-answer responses are excluded from the primary denominator and analyzed descriptively.

**W4. Before deciding what to do, how comfortable did you expect you would feel talking with that person?** Five-point scale from `Not at all comfortable` to `Completely comfortable`; plus `Not applicable`; `Prefer not to answer`.

**W5. Was concern about being judged one reason you did not share, or did not share as much as you wanted?** `Yes`; `No`; `Not applicable—I shared as much as I wanted`; `Not applicable for another reason`; `Prefer not to answer`.

**W6. Before deciding what to do, how confident were you that this person would respond supportively?** Five-point scale from `Not at all confident` to `Completely confident`; plus `Not applicable`; `Prefer not to answer`.

**W7. Which best describes the concern?** `An everyday problem`; `A personal insecurity`; `Something else`; `Prefer not to answer`. No free text is collected.

## Follow-up outcome module

Administer the identical `apa_dsm5tr_sad_adult` instrument version, language, wording, order, and response options used at baseline. Store the completion timestamp. Do not include check-in predictor questions in this module.

## Comprehension/usability prompts (internal synthetic pilot only)

After each flow, testers may answer: “Was any question unclear?” and “Did any response option feel missing?” These prompts must not accept sensitive disclosure text and are not part of research data. Real-pilot feedback needs an approved method.
