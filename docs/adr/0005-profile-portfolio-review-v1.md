# ADR 0005: Profile, Portfolio & Review Domain (v1)

- **Status:** Accepted (2025-02-??)
- **Context:** Stage "Профили/Портфолио/Отзывы" requires a cohesive schema that connects freelancer identity, discovery metadata, deliverable showcases, reviews tied to escrow-backed contracts, and moderation/reporting primitives. We must support multilingual skill taxonomy, ranking signals, and compliance (double-blind reviews, badge retention).

## Decision

1. **Extend `accounts.Profile`** with slugged public identifiers, commercial metadata (rates, availability), JSON locales (languages, links, geo payload), and discovery controls (visibility, contact preferences, last_activity). Added GIN + btree indexes for slug, language filters, rates, verification + last activity.
2. **Introduce supporting models in `profiles` app:**
   - `ProfileStats` as analytics sink (1:1) storing views/invites/hire-rate/response/completion/dispute/escrow-share. Values updated asynchronously (no business logic inside models).
   - `PortfolioItem` capturing `problem → solution → result` narrative, JSON media/tags, moderation status + featured flag.
   - `Review` bound to `marketplace.Contract` with rater/ratee references, JSON sub-scores, helpful votes, status & `blind_until`. Unique constraint prevents duplicate reviews from the same party.
   - `ProfileBadge` snapshotting badge type + issuance rule for retention; index by badge type to support verified/badged filters.
   - `FavoriteProfile` (client bookmarks) and `Report` (complaints targeting profile/portfolio/review) with uniqueness + check constraints.
3. **Enhance Skill taxonomy (`marketplace`):** add localized labels/descriptions, optional parent categories, and new `SkillSynonym` for RU/UZ/EN search keywords. Added indexes on category/slug/language pairs for fast filtering.
4. **Contract & Escrow linkage:** `Review.contract` keeps integrity with the hiring pipeline; `ProfileStats.escrow_share` stores revenue share aggregated from escrow releases. Reports referencing reviews/portfolio items ensure moderation can block escrow release if needed.
5. **Retention / Compliance:** All badge issuances keep `rules_snapshot` + `issued_at/expires_at`. Reviews maintain `blind_until` for dual release; reports and favorite bookmarks include timestamps for audit trails.

## Invariants

- `accounts.Profile.slug` is unique per user; last_activity is nullable but indexed.
- `profiles.ProfileStats` must exist exactly once per profile (enforced by OneToOne).
- `profiles.Review` unique per (`contract`, `rater`).
- `profiles.ProfileBadge` unique per (`profile`, `badge_type`, `issued_at`).
- `profiles.FavoriteProfile` unique per (`client`, `favorite`).
- `profiles.Report` check constraint ensures at least one of `target_profile`, `target_portfolio_item`, or `target_review` is set.
- `marketplace.SkillSynonym` unique per (`skill`, `language`, `value`).

## Consequences

- Discovery queries can filter by rate, language, verification status, badges, and recency using dedicated indexes.
- Localization-ready taxonomy enables RU/UZ UI and fuzzy search via synonyms without denormalizing orders/contracts.
- Moderation pipeline gains structured targets (portfolio/review/profile) plus reporting statuses; portfolio + review rows can be hard-locked by status transitions without schema changes.
- Badge + stats tables provide retention-friendly history for compliance with marketplace policies.
- Additional migrations add JSON/GiN dependencies (Postgres required) and require populating `slug` defaults via UUIDs for existing profiles.
