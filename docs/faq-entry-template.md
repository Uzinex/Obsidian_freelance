# FAQ entry template

- **Question (ru)**:
- **Answer (ru)**:
- **Question (uz)**:
- **Answer (uz)**:
- **Intent**: acquisition / conversion / trust / support
- **Schema anchor**: `marketing.escrow.faq.release`
- **Owner**:
- **Last reviewed (date + reviewer)**:

## Notes
- Keep answers ≤280 chars; link to deep resources sparingly.
- Reference glossary (`docs/glossary-uz-ru-v1.md`) for terminology.
- Add entry to `docs/public-pages-content-brief-uz-ru.md` if it impacts campaigns.

## Publishing steps
1. Update `publicContent[locale].faq` array.
2. Re-run `npm run i18n:lint` + `npm run build:ssg`.
3. Trigger revalidate for `/ru/faq` and `/uz/faq`.
4. Capture updated screenshot via `npx playwright test tests/visual-regression.spec.mjs --grep faq --update-snapshots`.
