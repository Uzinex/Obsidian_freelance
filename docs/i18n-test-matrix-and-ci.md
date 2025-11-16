# i18n test matrix & CI wiring

## Matrix overview
| Area | Locale(s) | Viewports | Coverage | Tooling |
| --- | --- | --- | --- | --- |
| Navigation + chrome | ru, uz, pseudo | Desktop 1440×900, mobile 390×844 | Header/footer links, locale switcher, CTA buttons, SEO tags | Playwright i18n E2E suite |
| Auth flows | ru, uz, pseudo | Desktop | Login, registration, password reset UI strings, error banners | Playwright i18n E2E suite |
| Orders + profile | ru, uz | Desktop | Orders list/search, create order wizard, profile editor, wallet empty states | Playwright i18n E2E suite + API mocks |
| Marketing/SSG pages | ru, uz | Desktop + mobile | Home, How it works, Escrow, FAQ, Blog index/article, Contacts, Legal pages | Visual regression suite + SEO assertions |
| Emails + notifications | ru, uz | n/a | Markdown/html templates rendered via Storybook snapshot, notification preference UI | Jest snapshot tests (backlog) + lint-only guard |
| Pseudolocalization stress | pseudo | Desktop + mobile | Registration, checkout/order, profile, FAQ/blog pages in stretched strings | Playwright i18n E2E suite with `?locale=pseudo` |

## Checks executed in CI
1. `npm run i18n:lint` – fails on missing locales/keys, warns on unused keys. Exported report is parsed by CI to annotate PRs.
2. `npm run i18n:pseudo` – regenerates `*.pseudo.json` fixtures to keep snapshots fresh before E2E and visual suites.
3. `npx playwright test tests/i18n-regression.spec.mjs` – runs pseudo-locale and locale regression flows headless on Chromium + mobile emulation.
4. `npx playwright test tests/visual-regression.spec.mjs --config tests/visual-regression.config.mjs` – captures or compares baselines for ru/uz across primary marketing and application screens.
5. `npm run build:ssg` – smoke builds SSG bundle to catch broken localized routes and SEO metadata.
6. Nightly: scheduled job hits `/api/emails/preview?locale={ru|uz}` and `/api/notifications/preview` to render MJML + JSON payloads and diff snapshots; failure blocks releases until triaged.

## E2E suite entry points
- Registration flow (pseudo, ru, uz): `/register?locale=pseudo` asserts stretched CTA labels do not overflow, `/ru/register` & `/uz/register` validate localized form hints.
- Order creation (ru, uz): `/ru/orders/create` uses fixture data to submit minimal project, verifies localized success toast and summary.
- Profile update (ru): `/ru/profile` ensures labels + error states render with translations and accessible help text.
- Public browse pages: `/ru/blog`, `/ru/blog/enterprise-cases`, `/ru/faq`, `/ru/escrow` – smoke check hero copy, FAQ accordions, schema blocks.

## CI environment variables
| Variable | Default | Purpose |
| --- | --- | --- |
| `I18N_UNUSED_BEHAVIOR` | `warn` | Set to `error` in release branches to fail PRs with stale keys. |
| `VITE_LOCALE` | unset | Force pseudo locale preview in Playwright cloud workers. |
| `PLAYWRIGHT_BROWSERS_PATH` | `0` | Ensures browsers are installed in CI workspace cache. |
| `BASELINE_BUCKET` | `s3://obsidian-i18n-visual/` | Upload/download Playwright screenshots before/after comparison. |

## Manual smoke before tagging release
- Trigger `npm run i18n:pseudo && npm run dev -- --host` locally, review hero sections on ru/uz/pseudo for cut-off strings.
- Run `npx playwright test tests/visual-regression.spec.mjs --update-snapshots` whenever marketing copy or layout changes; commit the refreshed baselines.
- Confirm `docs/i18n-string-matrix-v1.md` is updated for any new keys referenced in `src/locales/*.source.json`.
