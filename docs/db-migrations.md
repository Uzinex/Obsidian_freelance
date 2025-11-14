# Database Migration Workflow

The project uses Django migrations for the `accounts`, `marketplace`, and `media` apps. The
migration files live under:

- `backend/accounts/migrations`
- `backend/marketplace/migrations`
- `backend/media/migrations`

Follow the principles below to keep the history reliable and reproducible.

## Core principles

- **Never edit an applied migration.** Once a migration has shipped (merged into the main
  branch or deployed), leave the original file untouched. If a change is required, create a new
  migration that amends the schema or data.
- **Additive workflow.** New database changes are introduced exclusively through new migration
  files created with `python manage.py makemigrations`. Do not delete or reorder existing files.
- **Deterministic ordering.** Each migration has a numerical prefix that encodes its order. When
  multiple apps receive changes, generate migrations in a single branch to avoid conflicts, and
  merge branches sequentially so Django can resolve dependencies correctly.

## Creating migrations

1. Update the models.
2. Run `python manage.py makemigrations <app_label>` to generate a new migration file. Inspect the
   file before committing it.
3. Run `python manage.py migrate` locally to validate that the migration applies cleanly.
4. Commit the migration file alongside the model changes.

## Applying migrations in environments

1. Ensure the target environment has the desired code deployed.
2. Run `python manage.py migrate` to apply all unapplied migrations in dependency order.
3. Use `python manage.py showmigrations` to inspect the state if needed.
4. For selective application, run `python manage.py migrate <app_label>` to process a single app.

## Rolling back migrations

1. Identify the migration you want to roll back to with `python manage.py showmigrations`.
2. Run `python manage.py migrate <app_label> <migration_name>` to migrate backwards to the
   migration listed (Django will unapply any migrations that come after it for that app).
3. If a migration fails mid-rollback, fix the underlying issue, then rerun the same command.
4. Use `--plan` to preview what Django will apply or unapply before executing: `python manage.py
   migrate --plan`.

## Troubleshooting tips

- If you accidentally generated a migration you no longer need and it has **not** been applied or
  committed, delete the file safely and regenerate.
- If the migration history gets out of sync (e.g., an environment has extra migrations), use
  `python manage.py migrate --fake` to align the state carefully after confirming the schema is in
  the correct shape.
- Always back up production data before rolling back schema migrations.
