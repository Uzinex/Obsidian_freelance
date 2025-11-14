# Observability

## Sentry projects

- **Backend**: Django API service deployed from the `backend/` project.
- **Frontend**: React single-page application built from the `frontend/` project.

## Required environment variables

### Backend

Set these variables for the Django service:

- `SENTRY_DSN` — DSN of the backend project.
- `SENTRY_ENVIRONMENT` — deployment environment identifier (e.g. `dev`, `stage`, `prod`).
- `SENTRY_RELEASE` — optional release identifier to correlate deployments (defaults to `TODO_SET_RELEASE`).
- `SENTRY_TRACES_SAMPLE_RATE` — optional override for tracing sample rate (defaults to `0.2`).
- `SENTRY_PROFILES_SAMPLE_RATE` — optional override for profiling sample rate (defaults to `0.2`).

### Frontend

Expose these variables to the Vite build (e.g. through `.env` files with `VITE_` prefix):

- `VITE_SENTRY_DSN` — DSN of the frontend project.
- `VITE_SENTRY_ENV` — environment identifier (e.g. `dev`, `stage`, `prod`).
- `VITE_SENTRY_RELEASE` — optional release identifier passed to Sentry.
- `VITE_SENTRY_TRACES_SAMPLE_RATE` — optional override for tracing sample rate (defaults to `0.2`).
- `VITE_SENTRY_PROFILES_SAMPLE_RATE` — optional override for profiling sample rate (defaults to `0.2`).

To upload source maps via the Vite plugin, configure these build-time variables as well:

- `SENTRY_ORG`, `SENTRY_PROJECT`, `SENTRY_AUTH_TOKEN` — credentials for the Sentry Vite plugin (only required when enabling automatic source map uploads during builds).

## Alerting ideas

Set up alert rules in each Sentry project to cover the most critical signals:

- Error-level alerts that trigger on every new unhandled exception.
- Spike alerts for significant increases in error frequency relative to the baseline.
- Performance alerts tracking high latency, such as requests with `p95` duration breaching agreed thresholds.
