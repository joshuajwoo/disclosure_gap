# Synthetic portfolio release checklist

## No-input local checks

- [x] Synthetic mode is the default and real-data flags default false.
- [x] Demo browser tests fail if any request reaches the API.
- [x] The web production build has no fallback internal API endpoint.
- [x] Generated artifacts and every figure carry the synthetic validation label.
- [x] Contracts, migrations, tests, report rebuild, and container health pass locally.
- [x] The case study avoids novelty, causal, diagnostic, therapeutic, and population claims.
- [x] No real records, exports, credentials, or generated reports are committed.

## Deployment configuration

- [x] Hosting provider and project/account: GitHub Pages for this repository
- [x] Deployment credential or connected repository: GitHub Actions OIDC/Pages permissions
- [x] Public URL: `https://joshuajwoo.github.io/disclosure_gap/`
- [x] HTTPS enforcement and platform security settings: GitHub Pages redirects HTTP to HTTPS and serves HSTS
- [x] Availability monitoring: hourly GitHub Actions probe with quiet marker matching and no response-body retention

## Post-deployment verification

- [x] Confirm the deployment run records the exact source commit; release application commit `d8eee16` deployed successfully.
- [x] Confirm HTTPS returns `200`, HTTP redirects to HTTPS, and HSTS is present.
- [x] Confirm `SYNTHETIC DEMO` remains visible through the complete flow.
- [x] Complete the browser flow and deletion at 1280×900 and 375×760.
- [x] Verify all observed browser network activity stays on `joshuajwoo.github.io`; no research/internal API is contacted.
- [x] Scan the deployable artifact and delivered HTML for credentials, internal endpoints/hostnames, source maps, participant records, and small-cell output.
- [x] Confirm monitoring reports health failures while quiet matching prevents response bodies, tokens, or recovery values from entering logs.
- [x] Record public URL and verification: `https://joshuajwoo.github.io/disclosure_gap/`, 2026-10-05 America/New_York.

REL-01 and REL-02 are complete for the synthetic portfolio environment. This checklist does not clear any real-participant gate.
