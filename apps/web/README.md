# Web application

Owns eligibility, consent, baseline, weekly check-ins, follow-up, recovery, personal trends, withdrawal, and the synthetic public demo. It must not contain real records or compute diagnostic/risk labels.

The default `NEXT_PUBLIC_DEMO_MODE=true` build is a fully local synthetic walkthrough: browser actions never call the research API. Setting the flag to `false` enables the typed API adapter for a separately controlled environment. The flow uses neutral language, explicit missing/nonresponse options, focus management, responsive layout, and a confirmed deletion step. Playwright plus Axe covers the critical desktop and mobile paths.

Run `npm run dev --workspace apps/web` for local development and `npm run build --workspace apps/web` for a production build.

The public release is a static export at `https://joshuajwoo.github.io/disclosure_gap/`. Set `GITHUB_PAGES=true` with `NEXT_PUBLIC_DEMO_MODE=true` to build that base-path-aware export; `.github/workflows/pages.yml` builds, scans, and deploys it. The static release has no API URL, database, server state, or real-data mode.

The Dockerfile remains available for self-hosting: it exposes a bind-mounted `dev` target for Compose and a non-root `production` target containing the Next.js standalone server. The production target defaults to synthetic demo mode and does not define an API URL.
