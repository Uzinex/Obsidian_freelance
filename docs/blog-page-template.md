# Blog page template

- **Title (EN)**:
- **Title (ru)**:
- **Title (uz)**:
- **Slug**: `/blog/...`
- **Primary keyword / intent**:
- **Persona**:
- **Draft owner**:
- **SEO reviewer**:
- **Publish window**:

## Outline
1. Problem statement (H2)
2. Solution or framework (H2)
3. Proof/case studies (H2)
4. CTA (H2) – link to `/ru/orders` or `/ru/contacts` depending on offer

## Assets
- Hero image: `s3://...`
- Infographics / embeds:
- OG image variant:

## Schema snippets
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "",
  "description": "",
  "author": {
    "@type": "Person",
    "name": ""
  },
  "image": "https://.../blog.png",
  "datePublished": "2024-01-01",
  "articleSection": [""],
  "inLanguage": "ru",
  "mainEntityOfPage": "https://obsidianfreelance.com/ru/blog/..."
}
```

## FAQ block (optional)
| Question | Answer | Intent |
| --- | --- | --- |
|  |  |  |

## Localization checklist
- [ ] Added to `publicContent.blog` entries for ru + uz
- [ ] Strings mirrored in `docs/i18n-string-matrix-v1.md`
- [ ] OG/Twitter copy localized and <280 chars
- [ ] Screenshots captured for ru/uz, uploaded to baseline repo
