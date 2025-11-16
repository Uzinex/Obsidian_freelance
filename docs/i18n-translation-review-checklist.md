# Translation review checklist

1. **Glossary compliance** – Each term matches `docs/glossary-uz-ru-v1.md` (escrow, dispute, milestone, etc.).
2. **Tone of voice** – Copy follows tone guide for the target locale (formal "вы" / "siz").
3. **Placeholders & variables** – `{contract_id}`, `{amount}`, links and HTML tags remain intact and ordered correctly.
4. **Numerals & currency** – Thousands separators, decimal symbols, and currency names follow locale conventions.
5. **Length fit** – Run in-app preview (or pseudolocalization) to ensure no truncation or overflow.
6. **Accessibility** – Alt texts, aria-labels, and button labels remain descriptive and unique.
7. **Legal & SEO** – Marketing pages keep canonical URLs, headings, and metadata as specified in `i18n-url-map.md`.
8. **Context notes** – Confirm translator comments are up to date for complex flows (disputes, payouts, moderation).
9. **Regression** – Verify the matrix status moves to `approved` only after QA screenshots or recordings are attached.
