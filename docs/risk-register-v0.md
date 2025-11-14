# Risk Register v0

| Risk | Impact | Probability | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| OAuth provider outage preventing user logins during auth rollout | High | Medium | Implement redundant social login providers and provide email/password fallback with cached tokens | Engineering Lead |
| Misconfigured JWT expiration causing premature session timeouts | Medium | Medium | Add automated integration tests covering token lifetimes and monitor auth error rates | Backend Engineer |
| Insecure password reset flow enabling account takeover | High | Low | Conduct security review, enforce signed reset links, and add rate limiting on reset requests | Security Engineer |
| Payment gateway downtime impacting escrow funding | High | Medium | Establish backup gateway integration and enable manual funding queue | Payments Lead |
| Incorrect currency conversion in escrow calculations | Medium | Medium | Validate conversions via unit tests, double-entry ledger, and daily reconciliation | Finance Analyst |
| Delayed settlement releases due to queue backlog | Medium | Medium | Scale worker pool, add monitoring for queue depth, and implement auto-scaling alerts | DevOps Engineer |
| Chat message delivery failures under high load | Medium | Medium | Introduce message retry logic, backpressure handling, and load testing before release | Messaging Engineer |
| Unencrypted chat storage exposing sensitive data | High | Low | Encrypt chat transcripts at rest and enforce role-based access controls | Security Engineer |
| Spam or abusive content in communications channels | Medium | High | Deploy moderation filters, user reporting, and manual review workflow | Community Manager |
| Dispute evidence upload failures due to storage limits | Medium | Medium | Increase storage quotas, validate file sizes client-side, and monitor error logs | Support Lead |
| Bias in dispute resolution automation harming trust | High | Low | Review algorithms with cross-functional team, track outcomes, and provide manual override | Product Manager |
| Regulatory non-compliance with escrow handling rules | High | Low | Engage legal counsel, document procedures, and perform quarterly compliance audits | Compliance Officer |
| Data migration errors when enabling multi-stage rollout | Medium | Low | Use migration dry runs, backup databases, and automate schema validation | Backend Engineer |
| Lack of incident response playbooks for disputes escalations | Medium | Medium | Draft and rehearse runbooks, define SLAs, and train on-call responders | Operations Manager |

