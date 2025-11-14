# Password Policy

The authentication service enforces the following password rules for all accounts:

- Minimum length: **12 characters**.
- Required character classes: at least one uppercase letter, one lowercase letter, one digit, and one non-alphanumeric symbol.
- Prohibited passwords: values appearing in the local deny-list defined in `accounts/passwords.py`. The list contains the most common weak passwords and can be extended if necessary.
- Django's built-in `UserAttributeSimilarityValidator` remains enabled to prevent passwords that are too similar to user attributes (nickname, email, names).

When users submit a new password (during registration, password reset, or manual update), the `PasswordComplexityValidator` and `CommonPasswordListValidator` ensure the policy is applied. Validation errors bubble up to API consumers so the UI can display clear instructions to the user.

> **Operational note:** the deny-list is deliberately local to avoid external dependencies. For higher assurance, the validators can be extended to call third-party breach databases (such as haveibeenpwned) in future iterations.
