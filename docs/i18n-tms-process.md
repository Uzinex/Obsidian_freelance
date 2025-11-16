# i18n TMS process

## Key roles
- **Copy author** – designs the source (English) string and owns product context.
- **Translator** – produces uz/ru variants in the TMS, follows glossary & tone guide.
- **Reviewer** – approves linguistic quality and checks product accuracy (PM or locale lead).

## Status workflow
1. `new` – auto-created when a developer adds a key to `app_ui.source.json`.
2. `in_review` – translator submitted uz/ru variants, awaiting reviewer sign-off.
3. `approved` – reviewer confirmed both locales; CI allows deployment.

## Update rules
- Source edits must preserve key IDs; if semantics change, create a new key and deprecate the old one.
- Do not edit locale JSON directly in feature branches; use the TMS export to avoid merge conflicts.
- When removing UI components, mark their keys as `deprecated` in the matrix so translations can be archived.
- Never change URLs or slugs in marketing copy without coordinating with SEO lead; update the `i18n-url-map.md` appendix when necessary.

## Automation
- `npm run i18n:lint` (to be wired into CI) parses `src/locales/*.json` and fails build if:
  - A key exists in source but is missing in uz or ru files.
  - Components reference a key that is not in the matrix (via eslint rule `no-hardcoded-copy`).
- PR template requires linking the diff to updated keys in `docs/i18n-string-matrix-v1.md`.

## Pseudolocalization
- Dev server accepts `?locale=pseudo` or `VITE_LOCALE=pseudo` env variable.
- Pseudo mode stretches characters (e.g., `Loading…` → `~Łøāđīņğ…~`) and adds padding to uncover layout issues.
- QA checklist: run regression in pseudo mode on desktop + mobile breakpoints, capture any clipped buttons or overflowing labels.

## Translation-friendly releases
- Feature flags must gate incomplete languages; do not expose mixed-language screens.
- Batch marketing updates so that Terms/Privacy URLs remain stable; use redirects if anchor text changes.
- Keep `.po` or JSON exports under version control for auditability.
