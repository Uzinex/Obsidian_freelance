# CI/CD Pipeline

```
          +-----------------+
          | Push / Merge PR |
          +-----------------+
                    |
                    v
        +-----------------------+
        | Stage 1: Lint & Test  |
        | (pytest, mypy, eslint)|
        +-----------------------+
                    |
                    v
        +-----------------------+
        | Stage 2: Build       |
        | Docker + SBOM + scan |
        +-----------------------+
                    |
                    v
        +-----------------------+
        | Stage 3: Deploy Stage|
        | + run migrations     |
        +-----------------------+
                    |
            Manual Go/No-Go ----> Checklist in docs/deploy-go-no-go-checklist.md
                    |
                    v
        +-----------------------+
        | Stage 4: Prod Canary |
        | 10% traffic, SLI gate|
        +-----------------------+
                    |
                    v
        +-----------------------+
        | Stage 5: Prod Full   |
        | Blue/Green flip      |
        +-----------------------+
```

## Sample GitHub Actions Workflow
```yaml
name: obsidian-ci
on:
  push:
    branches: [main]
  pull_request:
jobs:
  lint-test:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r backend/requirements.txt
      - run: make lint test
  build-sbom:
    needs: lint-test
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - run: docker build -f infra/docker/api.Dockerfile -t registry/obsidian:${{ github.sha }} .
      - run: syft registry/obsidian:${{ github.sha }} -o json > sbom.json
      - run: trivy image --exit-code 1 registry/obsidian:${{ github.sha }}
      - uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom.json
  deploy-stage:
    needs: build-sbom
    environment: stage
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - run: ./ci/run_safe_migrations.sh --env stage
      - run: ./ci/deploy.sh --env stage --image registry/obsidian:${{ github.sha }}
      - run: ./ci/run_post_deploy_checks.sh --env stage
  manual-approval:
    needs: deploy-stage
    runs-on: ubuntu-22.04
    steps:
      - uses: trstringer/manual-approval@v1
        with:
          secret: ${{ secrets.GITHUB_TOKEN }}
          approvers: sre-oncall
  deploy-prod-canary:
    needs: manual-approval
    environment: production
    runs-on: ubuntu-22.04
    steps:
      - run: ./ci/deploy.sh --env prod --strategy canary --traffic 10
      - run: ./ci/run_safe_migrations.sh --env prod --phase verify
      - id: check_sli
        run: ./ci/check_sli.py --threshold-file ci/sli-thresholds.yaml
  deploy-prod-bluegreen:
    needs: deploy-prod-canary
    runs-on: ubuntu-22.04
    if: success() && steps.check_sli.outputs.status == 'pass'
    steps:
      - run: ./ci/deploy.sh --env prod --strategy blue-green --promote
      - run: ./ci/post_release_rollback_guard.sh
  rollback:
    if: failure() && github.ref == 'refs/heads/main'
    runs-on: ubuntu-22.04
    steps:
      - run: ./ci/rollback.sh --env prod --previous-release
```

## Key Behaviors
- `run_safe_migrations.sh` enforces expand/backfill/contract order and pauses if replica lag > 5s.
- Canary monitors API p95, error rate, queue depth. Auto rollback triggered when thresholds from `ci/sli-thresholds.yaml` violated for 2 consecutive checks (1 minute apart).
- Blue/Green uses separate ASG pools; traffic switch happens only after health checks + DB migrations confirmed.
- SBOM stored as artifact and attached to release.
