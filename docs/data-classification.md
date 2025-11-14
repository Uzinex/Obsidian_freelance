# Data Classification and Handling

This guide defines the sensitivity classes for data processed by the platform
and prescribes storage, access, and retention controls.

## Categories

### Personally Identifiable Information (PII)

Examples: first name, last name, patronymic, birth year, email, phone number,
IP addresses, device identifiers.

Controls:
- Stored in primary PostgreSQL database with strict RBAC enforced by
  `accounts.permissions.RoleBasedAccessPermission`.
- Mask PII in logs and analytics pipelines unless aggregated.
- Allow users to update or delete PII in accordance with GDPR/UZ privacy law.

### Know Your Customer (KYC)

Examples: passport scans, national ID numbers, proof-of-address documents,
selfie verifications.

Controls:
- Stored exclusively via `uploads.SecureDocument` using private storage backends.
- Access restricted to document owners and roles granted `uploads:manage` or
  `uploads:link` capabilities (moderators, finance).
- All access events (`kyc_upload`, `kyc_view`) are logged in the audit log with
  trace/span IDs for incident reconstruction.
- **Encryption at rest:** Wrap critical fields (passport number, series) in an
  application-level encrypted field. Implement a model mixin using a library
  like `django-fernet-fields` or a custom `EncryptedTextField` that derives
  per-record keys from a master secret stored in an HSM/secret manager.

### Financial Data

Examples: wallet balances, transaction history, payout account numbers,
tax identifiers.

Controls:
- Stored in PostgreSQL with row-level integrity enforced by transactional
  updates in `accounts.models.Wallet`.
- Limit exposure through API serializers (no full card/PAN storage).
- Log finance-related actions in audit logs when funds move across wallets.
- Encrypt high-risk fields such as bank account or IBAN details using the same
  field-level encryption pattern recommended for KYC identifiers.

### Public Data

Examples: marketplace listings intended for publication, anonymised metrics,
landing page content.

Controls:
- May be served via CDN or caching layers.
- No access restrictions beyond general API authentication/authorization.
- Ensure public datasets do not contain PII or KYC spillover.

## Application-level encryption approach

To implement field-level encryption for sensitive identifiers (e.g. passport
numbers), create a reusable encrypted model field:

```python
from django.db import models
from some_encryption_lib import encrypt, decrypt

class EncryptedCharField(models.CharField):
    def get_prep_value(self, value):
        plain = super().get_prep_value(value)
        if plain is None:
            return None
        return encrypt(plain)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        return decrypt(value)
```

Store encryption keys outside of the database (e.g. HashiCorp Vault, AWS KMS)
and rotate regularly. Keep hashed digests in metadata if you need deterministic
lookups without revealing plaintext.

## KYC retention and deletion policy

- **Retention:** Retain KYC documents for the shorter of 5 years or the period
  mandated by local AML regulations. Review retention annually.
- **Deletion authority:** Only finance officers or moderators with explicit
  `uploads:manage` permission may delete KYC artefacts. Deletions must be
  accompanied by an `AuditEvent` entry referencing the request ID and reason.
- **User requests:** Honour verified user requests to remove outdated KYC
  submissions unless legal holds apply. Ensure backups are purged in the same
  retention window.
- **Backups:** Encrypt backup archives and restrict access to the security
  team. Track restoration drills involving KYC data in change management logs.
