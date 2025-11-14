# Rate Limiting and WAF Policy

The backend enforces application-level throttling via Django REST Framework and
is complemented by optional edge rules (Nginx/Ingress) to absorb bursts before
traffic reaches the application pods.

## Application-level throttling

The following throttle scopes are configured in
`accounts.throttling.EndpointIPRateThrottle` and
`EndpointUserRateThrottle`. Each protected view declares a `throttle_scope`
value which is expanded into `<scope>_ip` and `<scope>_user` rate keys.

| Endpoint | Throttle scope | IP limit | User limit | Notes |
| --- | --- | --- | --- | --- |
| `POST /api/accounts/login/` | `login` | `10/min` | `5/min` | Backoff for repeated credential attempts. Pair with login failure backoff in `accounts.security`. |
| `POST /api/accounts/register/` | `register` | `5/min` | `3/min` | Protects sign-up flow from abuse and bot floods. |
| `POST /api/accounts/password/reset/request/` | `password_reset` | `5/min` | `3/min` | Prevents bulk password-reset spam targeting a victim. |
| `POST /api/accounts/email/verify/request/` | `email_verify` | `5/min` | `3/min` | Limits verification e-mail blasts and link enumeration. |
| `POST /api/uploads/documents/upload/` | `upload` | `20/hour` | `10/hour` | Governs sensitive uploads (KYC, financial docs). Additional storage quotas apply per business rules. |

When a threshold is exceeded the API responds with HTTP 429 (Too Many Requests)
and the response payload indicates when the caller may retry. The audit log
records the `access_denied` event for rate-limit denials because they return a
403/401 from the perspective of authorization checks.

## Basic WAF and edge rate limiting

Deploying an additional ingress layer ensures abusive traffic is throttled
before consuming application resources. The snippet below illustrates an Nginx
configuration that mirrors the per-endpoint rates and applies a minimal WAF
rule-set.

```nginx
# Define shared zones for per-IP and per-user throttles.
limit_req_zone $binary_remote_addr zone=login_ip:10m rate=10r/m;
limit_req_zone $binary_remote_addr zone=register_ip:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=password_ip:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=email_verify_ip:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=upload_ip:10m rate=20r/h;

# Optional: derive a user fingerprint from Authorization/refresh cookies.
map $http_authorization $rl_user {
    default "";
    ~^Bearer\s+(?<token>.+)$ $token;
}
limit_req_zone $rl_user zone=user_tokens:10m rate=100r/m;

server {
    listen 443 ssl;
    server_name api.obsidian.local;

    # Basic WAF hardening: block request smuggling patterns.
    if ($http_transfer_encoding ~* "chunked") {
        return 403;
    }

    location = /api/accounts/login/ {
        limit_req zone=login_ip burst=20 nodelay;
        limit_req zone=user_tokens burst=20 nodelay;
        include proxy_backend.conf;
    }

    location = /api/accounts/register/ {
        limit_req zone=register_ip burst=10 nodelay;
        include proxy_backend.conf;
    }

    location = /api/accounts/password/reset/request/ {
        limit_req zone=password_ip burst=10 nodelay;
        include proxy_backend.conf;
    }

    location = /api/accounts/email/verify/request/ {
        limit_req zone=email_verify_ip burst=10 nodelay;
        include proxy_backend.conf;
    }

    location = /api/uploads/documents/upload/ {
        limit_req zone=upload_ip burst=5;
        include proxy_backend.conf;
    }
}
```

For Kubernetes environments you can express the same behaviour with
`nginx.ingress.kubernetes.io/limit-*` annotations or with a service mesh rate
limiter. Ensure edge limits are slightly more permissive than application
limits to keep DRF as the ultimate source of truth while still shielding the
application from surges.

## Operational guidelines

- Keep edge and application rate definitions in sync with the table above.
- Monitor HTTP 429/403 counts and adjust limits for legitimate traffic spikes
  (e.g. marketing campaigns).
- Extend the WAF policy with organisation-specific rules (GeoIP, bot
  fingerprints) as threat models evolve.
