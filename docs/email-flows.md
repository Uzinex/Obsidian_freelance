# Email Flows

This document summarizes the user-facing email flows managed by the authentication service. All flows rely on signed, single-use tokens stored in the `accounts.OneTimeToken` table. Tokens are valid for 30 minutes by default and are removed (or marked as used) on first successful confirmation.

## Email verification

1. **Trigger:** `POST /api/auth/email/verify/request/` (authenticated).
2. **Action:** backend issues a token with purpose `email_verify`, sends `email_verify.txt` template to the user's current email address.
3. **User journey:** UI prompts the user to paste the token or follow the verification link.
4. **Confirmation:** `POST /api/auth/email/verify/confirm/` with the token. Upon success `User.email_verified` is set to `True` and `User.email_verified_at` records the timestamp.

## Password reset

1. **Trigger:** `POST /api/auth/password/reset/request/` with the account email.
2. **Action:** if the user exists, a `password_reset` token is generated and emailed via `password_reset.txt`.
3. **User journey:** UI accepts the token and new password.
4. **Confirmation:** `POST /api/auth/password/reset/confirm/` with token + new password. Token is consumed and the password updated.

## Email change

1. **Trigger:** `POST /api/auth/email/change/request/` (authenticated) with `new_email`.
2. **Action:** backend creates an `email_change` token containing the requested email and sends `email_change.txt` to the new address.
3. **User journey:** user confirms ownership by submitting the token from their new inbox.
4. **Confirmation:** `POST /api/auth/email/change/confirm/` with the token. Email is updated, verification flags are reset (`email_verified=False`).

### Token lifecycle

- Tokens are cryptographically signed using Django's `signing` module.
- Only the latest active token per user/purpose is kept. Requests invalidate previous outstanding tokens.
- Audit events are recorded for each request and confirmation to support traceability.

### UI considerations

- Each flow should display the expiration window (30 minutes) and allow resending.
- Resend actions map to the same `request` endpoints and automatically invalidate older tokens.
- After confirmation, surfaces should show success messages and clear next steps (e.g., log-in with the new password).
