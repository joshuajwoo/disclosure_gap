# Synthetic portfolio release checklist

## No-input local checks

- [x] Synthetic mode is the default and real-data flags default false.
- [x] Demo browser tests fail if any request reaches the API.
- [x] The web production build has no fallback internal API endpoint.
- [x] Generated artifacts and every figure carry the synthetic validation label.
- [x] Contracts, migrations, tests, report rebuild, and container health pass locally.
- [x] The case study avoids novelty, causal, diagnostic, therapeutic, and population claims.
- [x] No real records, exports, credentials, or generated reports are committed.

## External deployment inputs still required

- [ ] Hosting provider and project/account
- [ ] Deployment credential or connected repository
- [ ] Public domain or provider URL
- [ ] HTTPS enforcement and platform security settings
- [ ] Availability/error monitoring destination with sensitive-data collection disabled

## Post-deployment verification

- [ ] Confirm the deployed commit/image digest.
- [ ] Confirm HTTPS and HTTP redirect behavior.
- [ ] Confirm `SYNTHETIC DEMO` is visible on every stage.
- [ ] Complete the browser flow and deletion on desktop and mobile.
- [ ] Verify browser network activity never targets a research/internal API.
- [ ] Search delivered assets and logs for secrets, local database URLs, internal hostnames, source maps, participant records, and small-cell output.
- [ ] Confirm monitoring captures health failures but no response bodies, tokens, or recovery values.
- [ ] Record the public URL and verification date in this file.

REL-01 and REL-02 remain incomplete until these external and post-deployment items are finished.
