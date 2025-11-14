# Database Restore & Seeding Guide

This guide describes how to restore a PostgreSQL backup and bring a fresh environment up to date
with Django migrations and demo seed data.

## Prerequisites

- PostgreSQL client utilities (`psql`, `pg_restore`).
- The database credentials for the target environment.
- Access to the Django project settings (`backend/obsidian_backend/settings.py`).
- A backup file in either plain SQL (`.sql`) or custom (`.dump`) format.

## 1. Prepare the database

1. Stop any application processes that are writing to the database.
2. Create or reset the target database:
   ```bash
   createdb obsidian
   # or drop and recreate
   dropdb obsidian
   createdb obsidian
   ```
3. Ensure the database user used by Django has ownership of the database.

## 2. Restore from backup

Choose the restore command that matches your backup format.

### Plain SQL backup

```bash
psql -h <host> -U <user> -d obsidian -f /path/to/backup.sql
```

### Custom/Directory backup

```bash
pg_restore -h <host> -U <user> -d obsidian /path/to/backup.dump
```

Add `--clean` if the target database already has objects and you want them dropped before
restoration. Use `--no-owner` when restoring as a different database user.

## 3. Apply Django migrations

After the raw data is restored, run migrations to ensure the schema matches the current code:

```bash
cd backend
python manage.py migrate
```

Use `python manage.py showmigrations` to verify the state.

## 4. Load demo seed data

The repository provides an idempotent management command that populates safe test data (fake users,
categories, and skills). Run it after migrations:

```bash
cd backend
python manage.py seed_demo_data
```

The command creates:

- Baseline categories and skills for the marketplace.
- One demo client profile and one demo freelancer profile with obviously fake contact data.
- Wallets for each profile so financial flows can be tested without manual setup.

You can rerun the command safely; it updates existing demo objects instead of duplicating them.

## 5. Post-restore checks

1. Start the application and verify it can connect to the database.
2. Confirm the demo users can authenticate (default password: `ChangeMe!123`).
3. Inspect the categories and skills in the admin or via API to confirm they are present.
4. If sensitive production data should not be present, truncate or anonymize tables as required
   after restoration.

## Troubleshooting

- Use `pg_restore --list backup.dump` to inspect the contents of a custom backup before applying it.
- If migrations fail because of conflicts with restored data, review the failing migration and
  adjust the database manually before rerunning `python manage.py migrate`.
- Ensure the environment variables (e.g., `DATABASE_URL`) point to the restored database before
  running migrations and seed commands.
