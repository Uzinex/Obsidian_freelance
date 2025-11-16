# i18n rollout report template

- **Release**: `i18n-ssg-vX`
- **Date window**:
- **Owner**:
- **Environments**: Stage → Prod
- **Dark launch cohort**: % + targeting rules

## Summary
- Objective:
- Highlights:
- Blockers / incidents:

## Launch timeline
| Time | Action | Owner |
| --- | --- | --- |
|  | Feature flag enabled (10%) |  |
|  | Metrics checkpoint (24h) |  |
|  | Ramp to 50% |  |
|  | Full rollout |  |

## Metrics snapshot (pre vs post)
| Metric | Locale | Pre | Post (24h) | Post (72h) | Delta |
| --- | --- | --- | --- | --- | --- |
| LCP p75 | ru |  |  |  |  |
| Signup conversion | ru |  |  |  |  |
| Order creation | uz |  |  |  |  |
| Indexed URLs | ru |  |  |  |  |
| Blog impressions | uz |  |  |  |  |
| Error rate | both |  |  |  |  |

## Testing evidence
- Playwright i18n regression: link to CI run
- Visual regression diff: link or S3 path
- Manual QA notes: attach checklist references

## SEO & content ops
- Revalidated paths:
- Sitemap ping timestamp:
- Search Console issues/new coverage:
- Content updates shipped:

## Dark launch recap
1. Feature flag timeline & % ramp.
2. Metrics observed vs success criteria.
3. Any anomalies and mitigations.
4. Decision on full rollout (Go/No-Go) + approvals.

## Post-launch actions
- [ ] Update `docs/roadmap-stage1-3.md` with completion note
- [ ] Archive visual baselines in baseline bucket
- [ ] Schedule retro if incidents occurred
