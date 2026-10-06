# Synthetic internal usability review

**Review date:** 2026-10-04

**Scope:** heuristic developer review and automated critical-flow testing with fictional responses only

**Not in scope:** participant research, clinical validation, or evidence about question comprehension in the target population

## Walkthrough

The reviewed path covers introduction, eligibility and synthetic consent, baseline context, the separately presented ten-code outcome grid, four weekly check-ins, follow-up, a neutral personal summary, recovery, and confirmed deletion. Desktop and 375-pixel mobile layouts are exercised. The demo blocks every request to the live API during browser tests.

| Review question                                 | Result              | Evidence or disposition                                                                                                      |
| ----------------------------------------------- | ------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Is the purpose clear?                           | Pass                | The first screen calls the experience fictional, synthetic, non-diagnostic, and an engineering demonstration.                |
| Is choosing privacy treated neutrally?          | Pass                | Prompts state that keeping something private can be healthy; `chose_private` remains distinct from other non-sharing states. |
| Are sensitive free-text disclosures invited?    | Pass                | No names, contacts, exact locations, social accounts, or disclosure-content fields exist.                                    |
| Are missing choices understandable?             | Pass                | Not applicable, prefer not to answer, no person in mind, and no desire to share remain distinct.                             |
| Is the instrument separate from predictors?     | Pass                | Baseline context precedes a separate instrument fieldset; public wording is linked rather than copied.                       |
| Can a session be resumed without contact data?  | Pass                | Recovery uses a participant ID and one-time-displayed recovery code, with a warning to protect it.                           |
| Are trends neutral and sparse-safe?             | Pass                | The summary reports personal counts only and shows an insufficient-information state where needed.                           |
| Are withdrawal consequences clear?              | Pass                | Deletion explains response and credential removal and requires explicit confirmation.                                        |
| Is keyboard and screen-reader structure viable? | Pass after revision | Each stage now has one focused `h1`; labels, fieldsets, alert association, focus order, and Axe scans pass.                  |
| Does the mobile page overflow?                  | Pass                | The critical 375×760 flow has no horizontal overflow.                                                                        |

The automated synthetic walkthrough completes in seconds because it uses default values and automation. That number is not a human completion-time estimate. A timed human usability session remains part of any optional approved pilot.

## Observed revisions

1. Non-welcome stages originally used second-level headings. Axe correctly flagged the missing level-one heading; each stage now exposes and focuses a single `h1`.
2. The keyboard test originally advanced focus twice and therefore skipped the primary action. It now verifies the actual first-tab target.
3. Next.js adds its own route-announcer alert. Validation assertions now select the visible application alert by its message rather than assuming only one alert exists.
4. The public demo omits copied APA item wording and links to the official source, avoiding an unreviewed public reproduction while retaining fixed item codes.

No survey-contract meaning changed during these revisions, so no new contract version, migration, fixture rewrite, or analysis amendment was required.
