# Validation change log

Changes here record usability or release findings and their downstream version impact.

| Date       | Finding                                                                                                   | Change                                                                          | Contract/protocol impact                                                 |
| ---------- | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| 2026-10-04 | Stage transitions needed a consistent screen-reader destination.                                          | Promoted each active-stage title to `h1` and retained programmatic focus.       | Presentation-only; no contract change.                                   |
| 2026-10-04 | The validation test collided with Next.js's route-announcer alert.                                        | Selected the application alert by visible text.                                 | Test-only; no participant or analysis change.                            |
| 2026-10-04 | A public copy of instrument wording could diverge from the normative source and complicate rights review. | Display item codes and link the official APA form.                              | Presentation-only; instrument identity and scoring remain fixed.         |
| 2026-10-04 | Baseline context needed persistence distinct from the outcome instrument.                                 | Added the versioned, idempotent baseline-context endpoint and migration `0003`. | Additive storage/API change; feature lineage and deletion tests updated. |
| 2026-10-04 | Public builds should not fall back to an internal development endpoint.                                   | Removed the browser client's `localhost` API fallback.                          | Configuration hardening; synthetic behavior unchanged.                   |

Future wording or response-code changes must be classified under `packages/contracts/evolution.md`. A meaning change requires a new contract version, mapping decision, fixtures, protocol review, and analysis impact assessment before collection.
