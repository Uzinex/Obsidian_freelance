# Profile Domain Schema & Index Reference

## accounts.Profile
| Field | Type | Notes |
| --- | --- | --- |
| user | FK → accounts.User | 1:1 identity link. |
| role | Char(20) | `freelancer`/`client`. |
| slug | Slug(160) | Unique, default `uuid4`, indexed (implicit + discovery). |
| headline | Char(255) | Short pitch shown in cards. |
| bio | Text | Rich about section. |
| hourly_rate | Decimal(10,2) | Nullable; participates in `profile_rate_idx`. |
| min_budget | Decimal(12,2) | Nullable; participates in `profile_rate_idx`. |
| availability | Enum | `full_time`/`part_time`/`project`. |
| timezone | Char(64) | Olson timezone identifier. |
| languages | JSON | Stored as list of `{code, level}`; `profile_languages_gin` GIN index for filtering. |
| location | JSON | Country/region/city lat-lon payload. |
| links | JSON | Array of verified URLs. |
| contact_pref | Enum | `platform`/`email`/`phone`. |
| visibility | Enum | `public`/`private`/`link_only`; part of `profile_verified_idx`. |
| freelancer_type..house | Existing company data retained. |
| is_completed | Bool | Profile completeness flag. |
| is_verified | Bool | Combined with visibility in `profile_verified_idx`. |
| last_activity_at | DateTime | Indexed via `profile_last_activity_idx`. |
| created_at / updated_at | DateTime | Audit columns. |
| skills | M2M → marketplace.Skill | Tagged abilities. |

Indexes:
- `profile_languages_gin(languages)` – multi-language filters.
- `profile_rate_idx(hourly_rate, min_budget)` – budget sliders.
- `profile_verified_idx(is_verified, visibility)` – discovery filters.
- `profile_last_activity_idx(last_activity_at)` – "recently active" sort.

## profiles.ProfileStats
| Field | Type | Notes |
| --- | --- | --- |
| profile | 1:1 FK | Unique constraint via OneToOne. |
| views/invites | PositiveInteger | Rolling counts. |
| hire_rate / completion_rate / dispute_rate / escrow_share | Decimal(5,2) | Stored as percentage snapshots. |
| response_time | Duration | Average reply SLA. |

## marketplace.Category
| Field | Type | Notes |
| --- | --- | --- |
| name/slug/description | legacy default locale fields. |
| title_ru / title_uz | Char(150) | Localized labels. |
| description_ru / description_uz | Text | Localized descriptions. |
| parent | Self FK | Enables taxonomy nesting. |

Indexes: `marketplace_category_slug_idx(slug)`.

## marketplace.Skill
| Field | Type | Notes |
| --- | --- | --- |
| name/slug | Unique canonical identifiers. |
| category | FK → Category | `marketplace_skill_category_idx`. |
| title_ru/title_uz | Char(150) | Localization. |
| description / description_ru / description_uz | Text | Multi-lingual copy. |
| is_active | Bool | Soft deactivation for deprecated skills. |
| popularity | PositiveInteger | Ranking weight. |

Indexes:
- `marketplace_skill_slug_idx(slug)`
- `marketplace_skill_category_idx(category, name)`

## marketplace.SkillSynonym
| Field | Type | Notes |
| --- | --- | --- |
| skill | FK → Skill | Cascade deletes. |
| language | Enum (`ru`,`uz`,`en`) | Controls search locale. |
| value | Char(150) | Synonym text; unique per skill+language. |

Index: `skill_synonym_language_idx(language, value)`.

## profiles.PortfolioItem
| Field | Type | Notes |
| --- | --- | --- |
| profile | FK → accounts.Profile | Owner. |
| title | Char(255) | Case study headline. |
| role | Char(255) | Role performed (designer, PM...). |
| problem / solution / result | Text | Narrative blocks enforcing flow. |
| media | JSON | Ordered list of asset URLs + captions. |
| tags | JSON | Quick filters (tech stack, industry). |
| featured | Bool | Spotlight on profile page. |
| client_permission | Enum | `public`/`private`/`client_only`. |
| status | Enum | `draft`/`moderation`/`published`; `portfolio_status_idx`. |
| created_at / updated_at | DateTime | Audit.

Indexes: `portfolio_status_idx(status)`, `portfolio_featured_idx(profile, featured)`.

## profiles.Review
| Field | Type | Notes |
| --- | --- | --- |
| contract | FK → marketplace.Contract | Ensures escrow linkage. |
| rater / ratee | FK → accounts.Profile | Unique per contract+rater. |
| sub_scores | JSON | Map of dimensions (quality, communication, deadlines). |
| text | Text | Public feedback. |
| helpful_votes | PositiveInteger | Denormalized counter. |
| status | Enum | `draft`/`published`/`removed`. |
| blind_until | DateTime | Double-blind release end. |
| created_at | DateTime | Submission time. |

Constraints: `unique_contract_rater`, status choices; reports reference this row. Index inherits from FK (contract_id for contract-based queries).

## profiles.ProfileBadge
| Field | Type | Notes |
| --- | --- | --- |
| profile | FK → accounts.Profile | Recipient. |
| badge_type | Enum (`top_rated`,`verified`,`rising_talent`) | Filtered via `profile_badge_type_idx`. |
| rules_snapshot | JSON | Captures issuing rule version for audits. |
| issued_at / expires_at | DateTime | Validity window. |

Constraint: unique on (`profile`,`badge_type`,`issued_at`).

## profiles.FavoriteProfile
| Field | Type | Notes |
| --- | --- | --- |
| client | FK → accounts.Profile | Saver (must be client role at service layer). |
| favorite | FK → accounts.Profile | Talent saved. |
| created_at | DateTime | Sorting by recency via `favorite_created_idx`.

Constraint: unique pair (client,favorite).

## profiles.Report
| Field | Type | Notes |
| --- | --- | --- |
| reporter | FK → accounts.Profile | Complainer. |
| target_profile | FK nullable | For direct user reports. |
| target_portfolio_item | FK nullable | For showcase moderation. |
| target_review | FK nullable | For review disputes. |
| reason | Char(255) | Controlled vocabulary at API level. |
| description | Text | Optional free-form evidence. |
| status | Enum | `open`/`under_review`/`resolved`/`rejected`. |
| created_at | DateTime | Received timestamp. |

Constraint: `report_has_target` ensures at least one target reference.
