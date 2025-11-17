# Auth Registration & Login Overhaul Spec

This document defines the target architecture, backend contracts, frontend UX, anti-abuse protections, deliverability requirements, and Definition of Done for the new two-step email registration, Google SSO, hardened login, password reset, and supporting controls.

## 1. Two-Step Email Registration Flow

### 1.1 UX
- Single form collects: first/middle/last name, nickname, Gmail, birth year, password, and "I agree" checkbox, with inline validation (email format, password strength, async nickname uniqueness).
- After submit and successful reCAPTCHA v3 (or invisible v2), user sees inline OTP step without page navigation: six-digit code input, resend timer block, attempts counter.
- Neutral messaging: "If the email is correct, we sent a code…" regardless of registration status to avoid account enumeration.

### 1.2 Backend Architecture
- Model `PendingRegistration` (expires after 24h) stores email, normalized Gmail (strip dots and "+tag"), nickname, full name fields, birth year, salted password hash, hashed OTP (with salt/pepper), TTL timestamp, attempts_left (start 5), resend_at, IP/UA metadata, and audit timestamps.
- Service `EmailOTPService` generates cryptographically random six-digit codes, hashes them (no plaintext storage), enforces TTL 10 minutes with ±30s clock drift, and decrements attempts.
- Rate limits: per email and per IP maximum 1 send per 60s and 5 sends per 24h. Attempts >5 or expired TTL cause soft block for 1h.
- reCAPTCHA score threshold 0.7; failing score requires explicit captcha challenge before resubmission.
- Events logged to audit log with tags `flow=register` and steps `otp_send`, `otp_verify` for Sentry and analytics.

### 1.3 API Contracts
- `POST /auth/register`: validates reCAPTCHA token, upserts PendingRegistration if no active record, sends OTP via email template (uz/ru). Response always states code sent if email valid.
- `POST /auth/register/verify`: payload email + code; verifies hashed OTP, attempts, and TTL; on success creates `User`, flags `email_verified=true`, issues refresh JWT in HttpOnly SameSite=Strict Secure cookie (session or 30 days when "Log me in automatically" checked), deletes PendingRegistration, logs audit event.
- `POST /auth/register/resend`: enforces cooldown and daily caps before invoking EmailOTP service; response indicates countdown, never leaks if email registered.

## 2. Google SSO (Register & Login)

### 2.1 Flow
- Frontend renders "Continue with Google" button (GIS brand compliant) on login/register screens and may enable One Tap.
- GIS returns ID token; backend verifies signature, `aud`, `iss`, `nonce`, and `email_verified=true`.
- New email: create user with `email_verified=true`, prompt for unique nickname if absent in token.
- Existing email: require password login first, then allow linking Google (`google_sub` stored) to prevent takeover.
- Login via Google allowed only when linked and email verified.

### 2.2 Security & Sessions
- Never store Google access tokens; only keep `google_sub` and metadata.
- Use same refresh-cookie policy: `Max-Age=30d` when "Remember me" toggled, else session-only.
- Risk logging tags `flow=google_sso` with steps `token_verify`, `link`, `login`.

## 3. Password Login with Remember Me & Risk Challenge

### 3.1 Baseline Login
- Accepts nickname or email plus password, with reCAPTCHA triggered after 2–3 failures or low v3 score.
- Bruteforce mitigations: rate-limit per IP and account, lockout/pause for 15 minutes after 5 consecutive failures.
- Successful login issues access token (5–10 min) and refresh cookie (session vs 30 days per Remember Me).

### 3.2 Risk-Based OTP Challenge
- After correct password, evaluate signals (new device, geovelocity, recent password change, low captcha score). If triggered, send six-digit code to email with same OTP service, TTL/attempt rules, and trust-device option for 30 days.
- UX transitions inline to OTP input, timer, resend button with same rate limits.

## 4. Password Reset Flow & Policy

### 4.1 Flow
- User submits email; response always generic. reCAPTCHA enforced by default or after first request.
- Email contains single-use reset link (preferred) or six-digit code, TTL 15 minutes, invalidated after first use.
- Reset page enforces password policy: length ≥10, class mix, rejects passwords matching name/nickname/email, and checks compromised list (pwned password style). After success, optionally auto-log in.
- Limit reset requests per IP/email per day; log audit events `flow=password_reset` steps `request`, `token_validate`, `success`.

## 5. reCAPTCHA Integration
- Always required for initial registration submits and resend attempts.
- Login: triggered on anomaly or after 2–3 invalid attempts.
- Password reset: required always or after first request. Server validates scores, logs to Sentry for tuning.

## 6. Email Deliverability
- Use transactional ESP with SPF/DKIM/DMARC aligned domain. Track bounce/complaints; auto-suppress hard bounces.
- Provide localized (uz/ru) templates with subject "Подтверждение почты (6-значный код)" for OTP and consistent domain links. Keep design lightweight to avoid Promotions tab.

## 7. Audit, Analytics, Alerts
- Persist structured audit log entries for: registration attempt, OTP send, OTP verify success/failure, login success/failure, risk challenge trigger/verify, Google SSO events, password reset requests/completions.
- Metrics: conversion from registration to verified email, share of risk challenges, OTP delivery success rate, time from registration to first login.
- Alerts: spikes in failed logins (bruteforce), rising undelivered email/bounce >2%, degraded reCAPTCHA scores.

## 8. UX Details & Localization
- Buttons cycle states: "Send", "Sent (59s)", "Send again" with disabled countdown per spec.
- Friendly yet non-leaky error copy; bilingual support (uz/ru) with locale-driven template selection.
- Risk challenge screens include "Trust this device for 30 days" checkbox.

## 9. Definition of Done Checklist
- Registration enforces reCAPTCHA + OTP (TTL 10 min, ≤5 attempts, resend limits) before activating user.
- Google SSO works end-to-end with backend token verification and safe linking for existing accounts.
- Login handles nickname/email + password, Remember Me toggles refresh Max-Age, bruteforce mitigations in place, and risk challenge triggers only on defined scenarios.
- Password reset uses single-use tokens/links, hides account existence, and honors policy requirements.
- Email deliverability monitored (bounce <2%), localized templates, and sending actions logged.
- Audit log + metrics + alerts configured for auth events.

## 10. Risk Mitigations
- OTP spam: strict send/attempt caps plus reCAPTCHA and bot heuristics.
- Account hijack via Google: require prior password auth before linking, enforce `email_verified`.
- User friction from OTP: risk-based triggers only for login, not every session.
- Localization trust: consistent uz/ru messaging, canonical domain links, compliance with Google branding.
