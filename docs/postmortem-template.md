# Postmortem & Incident Communication Template

## 1. Incident communications

### Initial customer update
```
Subject: [Incident] <Service/Component> degradation
Timestamp (UTC): <hh:mm>
Statuspage component(s): <API/Web/Payments/Webhooks/DB/CDN>
Impact: <summary of user impact>
Next update: <+30 minutes>
```

### Update (every 30 min or on status change)
```
Timestamp (UTC): <hh:mm>
Current status: <investigating/mitigating/monitoring>
Actions since last update: <bullet list>
Estimated next milestone: <ETA>
```

### Resolved message
```
Timestamp (UTC): <hh:mm>
Incident window: <start - end>
Resolution summary: <root cause + fix>
Customer actions: <e.g., retry payments>
Follow-up: Postmortem will be published by <date>.
```

## 2. Postmortem document

### Summary
Provide a concise overview of the incident, including affected services, customer impact, SLAs breached, and resolution status.

### Timeline
List key events with timestamps (UTC) covering detection, response, mitigation, and recovery.

### Root Cause Analysis
Describe the technical and organizational contributors that led to the incident. Identify triggering event, contributing factors, and detection gaps.

### Impact
Detail scope: affected features, duration, number of users/orders/payments, regulatory or financial implications.

### Detection & Response
- What alerted us (Statuspage, Sentry, Prometheus, customer reports)?
- How long to acknowledge, mitigate, and resolve?
- Which runbooks or DR steps were executed?

### Communications
Summarize Statuspage updates, customer emails, and internal briefings. Link to incident templates above.

### Preventive + Corrective Actions
| Action Item | Owner | Due Date | Status |
| --- | --- | --- | --- |
|  |  |  |  |

### Lessons Learned
Highlight what worked, what failed, tooling/process gaps, and training needs.

### Evidence
Attach graphs, logs, PRs, and relevant change requests proving remediation.

