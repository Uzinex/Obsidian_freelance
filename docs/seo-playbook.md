# SEO playbook (i18n + SSG)

## Metadata rules
1. Titles: `{{Primary keyword}} – {{Value prop}} | Obsidian Freelance` (max 60 chars per locale). For blog posts use `{{Topic}}: {{Outcome}} | Blog Obsidian`.
2. Descriptions: 140–155 chars, active voice, must include locale-specific CTA + trust proof.
3. OG/Twitter: use localized `og:title` and `og:description`, `og:image` per campaign; include `twitter:site` from `LocaleContext` metadata.
4. Schema: minimum `WebSite` + `Organization` on home; `FAQPage` for FAQ, `Article` for blog, `HowTo` for tutorials, `BreadcrumbList` for nested marketing pages. Always localize `headline`, `description`, `articleSection`.
5. Canonicals: ru/uz each have canonical to their own path; add `hreflang` pairs for ru-ru / uz-uz.

## Headline & body structure
- H1: single, keyword-rich, matches `<title>` intent.
- H2: cluster topics (Problem, Solution, Proof, CTA). H3 used for process steps or FAQ entries.
- Include FAQ block with 3–5 Q/A items using `docs/faq-entry-template.md` as source; embed JSON-LD snippet.
- Use bullets for benefit lists, numbered steps for workflows.
- Image alt text localized, contains supporting keywords but not stuffed.

## Blog cadence & workflow
| Step | Owner | Cadence |
| --- | --- | --- |
| Topic backlog grooming | SEO lead + Content owner | Bi-weekly |
| Draft production | Copywriter | 2 posts/month per locale |
| Localization | Linguist via TMS | Within 3 days of EN approval |
| Fact check + SME review | Domain expert | 2 days |
| Publication | Engineering owner | Weekly slot (Wednesday) to leverage crawl budget |
| Refresh audit | SEO lead | Quarterly rerun for top 20 URLs |

## Publication checklist
1. Fill out `docs/blog-page-template.md` (per post) and have SEO lead sign off.
2. Add article entry in `publicContent.blog` for ru/uz, including `slug`, `summary`, `tags`, `faq` (if inline).
3. Update sitemap + ping search engines.
4. Run `npm run build:ssg` + `npx playwright test tests/visual-regression.spec.mjs --grep blog` to capture new baselines.
5. Monitor Search Console coverage/impressions for 14 days; record metrics in `docs/i18n-rollout-report-template.md`.

## FAQ updates
- Batch FAQ edits monthly to limit reindex churn.
- Each item must have: short question (≤90 chars), answer (≤280 chars), `intent` tag (acquisition, conversion, trust), `last_reviewed_by`.
- After merging, run `POST /api/ssg/revalidate` with `/ru/faq` + `/uz/faq`, then re-run visual regression for the FAQ page.
