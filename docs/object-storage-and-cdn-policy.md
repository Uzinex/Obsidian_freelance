# Object Storage and CDN Policy

## Storage
- Provider: S3-compatible (MinIO in Stage, AWS S3 in Prod) bucket `obsidian-media` with versioning enabled.
- Static assets uploaded via CI (`frontend/dist`) to `static/<git-sha>/...` prefix.
- Media (user uploads) reside in `media/<user-id>/...` and are written using presigned URLs valid for 10 minutes.
- Use `PUT` presigned URLs for uploads and `GET` for private downloads; CDN signs requests for authenticated users.

## Security
- IAM policies limit write access to CI role and read access to CDN origin identity.
- KMS SSE enabled. Large uploads use multipart presigned URLs with 64 MB parts.

## Lifecycle Policies
| Prefix | Action | TTL |
| --- | --- | --- |
| `static/` | Transition to Intelligent-Tiering | 30 days |
| `static/` | Expire | 365 days (new releases keep only latest 4 versions) |
| `media/tmp/` | Delete incomplete uploads | 3 days |
| `media/portfolio/archived/` | Transition to Glacier | 180 days |
| `media/chat-attachments/` | Expire | 90 days |

## CDN/Edge Caching
- Provider: CloudFront/Cloudflare with origin shield to object storage.
- Cache key structure: `<path>?locale=<uz|ru>&static_version=<git-sha>&role=<anon|auth>`.
- Headers forwarded: `Accept-Language`, `Authorization` (only for private media through signed cookies), `If-None-Match`.
- Use `stale-while-revalidate=60` for static assets and `Cache-Control: private, max-age=60` for authenticated media.

## Invalidation Policy
- **Frontend release**: CI publishes new `static/<sha>` and updates `static/current` manifest; run `cdn-cli invalidate --paths '/static/current/*'`.
- **Portfolio/media updates**: when artist edits assets, backend invalidates `media/portfolio/<artist_id>/*` via asynchronous job.
- **Emergency**: security fix triggers wildcard invalidation with `--quiet-time 5m` to avoid global thundering herd.

## Presigned URL Flow
1. Client requests upload slot via API → backend generates `PUT` presigned URL with content-type restrictions.
2. Client uploads directly to S3; on success notifies backend with checksum.
3. Backend stores metadata row (`status=pending`) and Celery job validates MIME + virus scan before marking `ready`.

## CDN Cache Busting
- Include `x-static-version: <git-sha>` header for SPA HTML responses.
- Media URLs incorporate `?v=<updated_at_epoch>` to force CDN revalidation after edits.
- For localized pages, cache key includes locale; fallback to default locale when header missing.

## Monitoring & Alerts
- Track S3 4xx/5xx via CloudWatch metrics; alert if error rate >1% for 5 minutes.
- CDN cache-hit ratio alert at <85%.
- Object storage lifecycle job success logged to `obsidian.object_storage.lifecycles` metric.
