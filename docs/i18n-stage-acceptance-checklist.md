# i18n Stage Go/No-Go checklist

## Localization readiness
- [ ] All UI keys tracked in `docs/i18n-string-matrix-v1.md` with ru + uz translations, `npm run i18n:lint` clean (or warnings triaged).
- [ ] Transactional emails + notification payloads reviewed in ru/uz; MJML/JSON snapshots stored.
- [ ] Pseudolocalization build (`npm run i18n:pseudo`) reviewed for registration, order, profile, and FAQ flows.

## SSG + SEO
- [ ] `npm run build:ssg` succeeds, ISR revalidation hooks tested.
- [ ] Canonical + hreflang tags verified on home, blog, FAQ, profiles.
- [ ] Schema (FAQ, Article, Breadcrumb, Organization) validates via Rich Results test for ru/uz URLs.
- [ ] Sitemap regenerated and submitted to search engines.

## Performance & accessibility
- [ ] Lighthouse ≥85 perf on ru/uz home, ≤1.5s TTFB from cache.
- [ ] Core Web Vitals field data within green zone (CrUX last 28 days).
- [ ] Axe scan passes on `/ru`, `/ru/faq`, `/ru/orders` (critical flows) with pseudo locale enabled.

## Analytics & observability
- [ ] Locale dimension added to page_view, signup, order_created events.
- [ ] SEO dashboards (impressions, indexed URLs) updated with ru/uz filters.
- [ ] Error tracking sampling verified for localized bundles; Sentry releases tagged per locale.

## Testing & QA
- [ ] Playwright i18n regression suite green (registration, order, profile, public pages).
- [ ] Visual regression baselines updated & diff-free for ru/uz.
- [ ] Manual accessibility + content QA sign-off recorded in `docs/public-a11y-checklist.md`.
- [ ] Release Go/No-Go recorded with approvals from Eng, Localization PM, SEO, Marketing.

## Dark launch procedure (10–20% traffic)
1. **Enable flag** – ship feature flag `i18n_ssg_stage` disabled by default. Flip to `on` for 10% of anonymous ru traffic + 20% logged-in uz cohort using LaunchDarkly target rules.
2. **Monitoring window (48h)** – track:
   - Page speed (LCP, CLS) for flagged cohort vs control in Datadog.
   - Signup/order conversion deltas by locale.
   - Search Console `coverage` & `discovered URLs` deltas (ensure ru/uz URLs get crawled, no spike in errors).
3. **Success criteria** – no >2% drop in conversion, no spike in JS errors (>0.5% sessions), indexation steady. If met, ramp to 50%, then 100% in 24h increments.
4. **Rollback** – toggle flag off or set `targeting=0%` if metrics regress; purge ISR cache via `/api/ssg/purge` and redeploy previous static bundle. Document rollback in `docs/i18n-rollout-report-template.md`.
