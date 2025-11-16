# Content Ops guide

## Adding or updating copy, categories, and skills
1. Update source of truth:
   - Application/product strings – edit `frontend/src/locales/*.source.json` and mirror the keys in `docs/i18n-string-matrix-v1.md`.
   - Marketing/public content – edit `frontend/src/mocks/publicContent.js` for one-off changes or add structured entries via `docs/blog-page-template.md` / `docs/faq-entry-template.md` before porting to CMS.
   - Category/skill catalogs – use `frontend/src/mocks/publicContent.js` (`categories` + `skills`) and the admin CSV import script.
2. Run `npm run i18n:lint` to confirm ru/uz coverage. Any missing translation blocks CI.
3. Run `npm run i18n:pseudo` and take a local pass on `/ru`, `/ru/how-it-works`, `/ru/blog` with `?locale=pseudo` to catch length issues.
4. Update `docs/public-pages-content-brief-uz-ru.md` with rationale, owner, and approval notes.

## Triggering prerender and re-index jobs
| Action | When to run | Command / trigger |
| --- | --- | --- |
| Marketing copy or navigation change | Every content PR touching `src/mocks/publicContent.js` or localized markdown | `npm run build:ssg` locally + upload artifacts to preview bucket; merge triggers Vercel ISR. |
| Blog/FAQ publish | After staging approval | `POST /api/ssg/revalidate` with payload `{"paths":["/ru/blog/...","/uz/blog/..."]}` via Release bot. |
| Search reindex | After categories/skills CRUD or major FAQ edits | Trigger `SearchIndexer` workflow in GitHub Actions (`content_index.yml`). |
| Sitemap refresh | Weekly or if >5 URLs change in a batch | `POST /api/seo/sitemap` to regenerate XML + ping Yandex/Google endpoints. |

## Roles and SLAs
| Role | Responsibility | SLA |
| --- | --- | --- |
| Content owner (Marketing) | Draft/update copy, ensure glossary alignment, request translations. | 2 business days to supply draft, 1 day to fix blockers. |
| Localization PM | Validates matrix updates, runs `i18n:lint`, coordinates linguists. | Same-day review during sprint, escalations within 4h. |
| SEO lead | Approves metadata, OG, schema, monitors index coverage after publish. | 1 business day for approvals, 12h for regression fixes. |
| Engineering owner | Runs SSG build, merges PR, triggers prerender + search reindex, monitors CI. | Immediate action upon approval, rollback within 30 min if SEO/A11y regress. |
| Editorial QA | Checks pseudo/ru/uz rendering, visual diffs, accessibility for new assets. | Smoke pass within 1 business day after content freeze. |

## Operational checklist per content drop
1. Create content brief referencing KPIs + target personas.
2. Draft copy + visuals, validate with SEO lead (keywords, schema type).
3. Update locales + `publicContent` files, run lint + pseudo.
4. Capture new Playwright visual baselines (ru/uz) for touched pages, commit artifacts.
5. Stage deployment + run `docs/i18n-stage-acceptance-checklist.md`.
6. Trigger prerender + reindex actions.
7. Monitor Search Console and analytics for 72h, publish post-deploy report via `docs/i18n-rollout-report-template.md`.
