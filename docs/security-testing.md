# Security Testing Pipeline

This document describes the automated security testing approach for the Obsidian Freelance platform. It covers static analysis (SAST), secret scanning, dynamic analysis (DAST), and the acceptance criteria tied to these controls.

## Static Application Security Testing (SAST)

### Backend (Python)
- **Tool**: [Bandit](https://bandit.readthedocs.io/)
- **Execution**: Triggered by the `Security and Quality Checks` GitHub Actions workflow for every push to `main` and each pull request.
- **Command**: `bandit -r backend -q --severity-level medium --confidence-level medium`
- **Failure Criteria**: The workflow fails if Bandit reports any Medium or High severity findings with at least Medium confidence. Pull requests cannot be merged while the job is failing.

### Frontend (JavaScript/TypeScript)
- **Tool**: ESLint (already part of the frontend tooling).
- **Execution**: Runs in the same workflow as a required check for each push and pull request.
- **Command**: `npm run lint -- --max-warnings=0`
- **Failure Criteria**: The job fails on any lint error or warning (warnings are treated as errors via `--max-warnings=0`).

### Secret Scanning
- **Tool**: [Gitleaks](https://gitleaks.io/)
- **Execution**: Runs in the workflow for every push and pull request.
- **Failure Criteria**: The job fails on any detected secret (default Gitleaks rules). The finding must be resolved before merging.

## Dynamic Application Security Testing (DAST)

### Tooling Recommendation
Run the [OWASP ZAP Baseline Scan](https://www.zaproxy.org/docs/docker/baseline-scan/) against the staging environment as part of release readiness checks.

### Configuration
Create a configuration file `.zap-baseline.conf` alongside deployment manifests with the following content:

```
# Target stage URL (replace with actual stage hostname)
TARGET=https://stage.obsidian.example.com
# Optional include context file defining auth/session, if needed
CONTEXT_FILE=zap/stage-auth.context
# Allow spider to run longer for authenticated areas
MAX_DURATION=900
# Fail build on Medium or High risk alerts
FAIL_ON=Medium
```

### Invocation
Run the scan from CI/CD or a release pipeline job:

```
docker run --rm -v $(pwd)/zap:/zap/wrk/:rw -t owasp/zap2docker-stable \
  zap-baseline.py -t $TARGET -c /zap/wrk/.zap-baseline.conf \
  -r zap-baseline-report.html -w zap-baseline-warnings.md
```

Artifacts (`zap-baseline-report.html`, `zap-baseline-warnings.md`) should be uploaded to the pipeline run for review.

### Acceptance Criteria
- No **High** severity alerts in the OWASP ZAP baseline report.
- Medium severity alerts must be reviewed and have documented mitigations or be remediated before release.

## Summary of Merge Gates
To merge into `main`, a pull request must satisfy all of the following:
- `Security and Quality Checks` workflow is green.
- Bandit reports zero Medium/High severity findings.
- ESLint reports zero warnings or errors.
- Gitleaks detects no secrets.
- The latest stage DAST report contains no High severity alerts, with open Medium findings tracked.
