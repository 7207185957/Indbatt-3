# Unit Administration System

A secure, **LAN-only** Django web application for managing **non-operational**
unit administration records (personnel master data, leave/TD/absence,
daily strength, and administrative duty rosters) for an infantry unit.

> **Security note:** This system is designed only for **non-classified**
> administrative records. It must **never** be used to store live
> operational deployment details, classified locations, weapon/ammunition
> operational readiness, or any sensitive tactical information. It has
> no internet/cloud dependency and is intended to run entirely inside the
> unit's closed LAN, on a single server PC.

---

## 1. What this system does

| Module | Purpose |
|---|---|
| **Dashboard** | Role-scoped snapshot: strength, absentees, today's duties, upcoming returns, recent activity. |
| **Personnel** | Master database of unit personnel (army no., rank, name, posting, status). |
| **Leave / TD / Absence** | Leave, Temporary Duty, Course, Hospital/Sick, Attachment records; due-to-return list. |
| **Daily Strength** | One strength return per company/sub-unit per day, with unit/company summaries. |
| **Duty Roster** | Administrative duty roster (guard, orderly, fatigue, etc.) with generic, non-sensitive location text only. |
| **Reports** | Personnel, strength, absence, duty roster and due-to-return reports, each exportable to CSV. |
| **Admin** | Django admin for unit structure (Company/Platoon/Section/Appointment) and user accounts. |

Every user has an **individual login** (no shared/common accounts). Access
is controlled by **role-based access control (RBAC)**:

| Role | Access |
|---|---|
| **Super Admin** | Full access to everything, including user account management and Django admin. |
| **Adjt / Admin Branch** | Full view/manage access to all administrative records, unit-wide. |
| **Company Clerk** | Can add/edit records only for their own assigned company/sub-unit. Cross-company access is blocked both in the UI (dropdowns are pre-filtered) and at the server level (forms/querysets are re-validated). |
| **Viewer** | Read-only dashboard and reports across the unit. |

Every record tracks `created_by`, `updated_by`, `created_at`, `updated_at`
for audit purposes.

---

## 2. Technical overview

- **Backend:** Django 4.2 (Python), function/class-based views, Django
  ORM, Django forms/model forms, Django's built-in authentication.
- **Database (prototype):** SQLite (`db.sqlite3`), zero configuration.
- **Database (production-ready migration path):** PostgreSQL - see
  [Section 8](#8-migrating-from-sqlite-to-postgresql).
- **Frontend:** Django templates + a small, framework-free custom CSS
  (no CDN, no external JS/CSS dependency - fully usable offline on the LAN).
- **Deployment target:** one server PC on the unit LAN; other unit
  computers reach it via `http://<SERVER_IP>:8000` in a browser.

### Project layout

```
config/            Django project settings/urls/wsgi/asgi
core/               Shared base model (audit fields), RBAC roles/mixins,
                    context processor, seed_demo_data management command
accounts/           Custom User model (role, company), user management views
unitstructure/      Company, Platoon, Section, Appointment models + admin
personnel/          Personnel master module
absence/            Leave / TD / Course / Hospital / Attachment module
strength/           Daily Strength module
dutyroster/         Duty Roster module
dashboard/          Role-scoped dashboard view
reports/            Report pages + CSV export
templates/          All HTML templates (base layout, per-module pages)
static/css/         Custom stylesheet (no external dependency)
scripts/            Optional smoke-test scripts used during development
```

### Role-based access control implementation

RBAC is implemented centrally in `core/roles.py` (role constants and
helper functions) and `core/mixins.py` (reusable class-based-view mixins):

- `RoleRequiredMixin` / `SuperAdminRequiredMixin` / `EditRequiredMixin` -
  gate whole views by role.
- `CompanyScopedQuerysetMixin` - automatically filters list/detail
  querysets to a Company Clerk's own company.
- `CompanyScopedFormMixin` / `PersonCompanyScopedFormMixin` /
  `PersonnelDetailedScopedFormMixin` - restrict the choices offered in
  create/edit forms (e.g. company, person, personnel-detailed dropdowns)
  to what the current user is allowed to touch, and re-validate on save
  so a scoped user cannot bypass the UI by posting a different id
  directly.
- `AuditFieldsMixin` - stamps `created_by` / `updated_by` automatically.

This mirrors the audit-friendly, defense-in-depth pattern used
throughout every module (personnel, absence, strength, duty roster).

---

## 3. Local/LAN deployment - step by step

These steps are written for the **server PC** that will host the
application inside the unit LAN. No internet access is required except
to initially install Python and the pinned Python packages.

### 3.1 Install Python

Install Python 3.10+ from [python.org](https://www.python.org/downloads/)
(or your OS package manager). Verify with:

```bash
python3 --version
```

### 3.2 Get the project onto the server PC

Copy/clone this project folder onto the server PC, e.g. to
`C:\UnitAdmin\` (Windows) or `/opt/unitadmin/` (Linux).

### 3.3 Create a virtual environment

```bash
cd unitadmin              # project folder
python3 -m venv venv
```

Activate it:

- **Linux/macOS:** `source venv/bin/activate`
- **Windows (cmd):** `venv\Scripts\activate.bat`
- **Windows (PowerShell):** `venv\Scripts\Activate.ps1`

### 3.4 Install requirements

```bash
pip install -r requirements.txt
```

### 3.5 Run migrations

```bash
python manage.py migrate
```

### 3.6 Create a Super Admin account

```bash
python manage.py createsuperuser
```

Follow the prompts (username, email, password). This is your first
**individual** login with full access - do not share it.

### 3.7 (Optional) Load demo/seed data for testing

To try out the system with realistic sample data (companies, platoons,
personnel, absence records, strength returns, duty rosters, and a demo
account per role):

```bash
python manage.py seed_demo_data
```

The command prints the demo usernames/passwords it creates. **Change
these passwords (or delete the demo accounts) before real use.** Re-running
the command is safe - it only creates records that do not already exist.

### 3.8 Start the application on the server PC

```bash
python manage.py runserver 0.0.0.0:8000
```

Leave this terminal window running (or set it up as a Windows/Linux
service - see [Section 9](#9-running-as-a-background-service-optional))
while the office needs the system available.

### 3.9 Access from other LAN computers

On the server PC, find its LAN IP address:

- **Windows:** `ipconfig` (look for "IPv4 Address")
- **Linux:** `ip addr` or `hostname -I`

From **any other computer on the same unit LAN**, open a browser and go to:

```
http://SERVER_IP:8000
```

For example, if the server's LAN IP is `192.168.1.50`:

```
http://192.168.1.50:8000
```

The first screen is the **login page**. Each user logs in with their own
individual account.

> Do not port-forward this application to the internet and do not expose
> port 8000 outside the unit LAN/firewall. See [Section 7](#7-security-notes).

---

## 4. Day-to-day usage

- **Adding companies/platoons/sections/appointments:** log in as Super
  Admin (or a staff account) and use **Admin** in the sidebar (Django
  admin) to manage unit structure and, if needed, user accounts.
- **Adding a new user:** Super Admin -> **Users** in the sidebar -> **Add
  User**. Assign a role, and for Company Clerk accounts, assign exactly
  one company/sub-unit.
- **Daily strength entry:** each company should submit one **Daily
  Strength** entry per day; the system blocks a second entry for the
  same company/date.
- **Reports:** use the **Reports** module for printable/exportable
  personnel, strength, absence, duty roster, and due-to-return reports
  (CSV export button on every report page).

---

## 5. Seed/demo data command

`python manage.py seed_demo_data` populates:

- The 6 example companies (HQ Coy, A Coy, B Coy, C Coy, D Coy, Support Coy),
  platoons, sections, and a set of common appointments/trades.
- Demo user accounts for each role (see command output for credentials).
- A realistic personnel master list distributed across companies/platoons.
- Sample leave/TD/course/hospital/attachment records.
- A week of daily strength returns per company.
- A window of duty roster entries (past, today, upcoming).

Use `python manage.py seed_demo_data --flush-personnel` to wipe and
regenerate personnel/absence/strength/duty data (unit structure and user
accounts are left untouched).

---

## 6. Running the test scripts (optional, for developers)

Two lightweight functional scripts are included under `scripts/` (not a
replacement for a full test suite, but useful smoke checks after making
changes):

```bash
python manage.py shell -c "exec(open('scripts/smoke_test.py').read())"
python manage.py shell -c "exec(open('scripts/coverage_check.py').read())"
```

`smoke_test.py` exercises login, CRUD, RBAC company-scoping, duplicate
strength prevention, and CSV export. `coverage_check.py` hits every major
URL under each demo role and flags any server errors.

---

## 7. Security notes

- **LAN-only:** run this application only inside the unit's closed LAN.
  Do not expose it to the public internet (no port forwarding, no cloud
  hosting for the prototype).
- **Individual accounts only:** never share a login between multiple
  people. Create a separate account per user with the minimum role they
  need.
- **Strong passwords:** enforce strong, unique passwords for every
  account (Django's password validators already require a minimum
  length and reject common/numeric-only passwords).
- **Non-classified data only:** do not enter operational deployment
  details, classified locations, weapon/ammunition operational
  readiness, or any tactical information anywhere in this system - it is
  built and reviewed only for non-classified administrative use
  (personnel admin status, leave/TD, daily strength, and generic
  administrative duty rosters).
- **Change the secret key:** before any real deployment, set the
  `DJANGO_SECRET_KEY` environment variable to a new, random value instead
  of relying on the default development key in `config/settings.py`.
- **Turn off debug mode in production:** set `DJANGO_DEBUG=False` once
  the deployment is stable, and set `DJANGO_ALLOWED_HOSTS` to the
  server's LAN hostname/IP.
- **Keep the OS and Python patched**, and restrict physical/network
  access to the server PC to authorized unit personnel.

---

## 8. Migrating from SQLite to PostgreSQL

The application was written so that switching databases requires **no
application code changes** - every module uses the Django ORM only.

1. Install PostgreSQL on the target server and create a database/user
   for the application.
2. Install the PostgreSQL driver in the virtual environment:

   ```bash
   pip install psycopg2-binary
   ```

3. Set the following environment variables before starting the app (or
   put them in a `.env` file loaded by your process manager):

   ```bash
   export DJANGO_DB_ENGINE=django.db.backends.postgresql
   export DJANGO_DB_NAME=unitadmin
   export DJANGO_DB_USER=unitadmin
   export DJANGO_DB_PASSWORD="<strong password>"
   export DJANGO_DB_HOST=127.0.0.1
   export DJANGO_DB_PORT=5432
   ```

4. Run migrations against the new database:

   ```bash
   python manage.py migrate
   ```

5. (Optional) Migrate existing SQLite data using Django's `dumpdata`/
   `loaddata`:

   ```bash
   # while still pointed at SQLite
   python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > data.json
   # switch environment variables to PostgreSQL, run migrate, then:
   python manage.py loaddata data.json
   ```

---

## 9. Running as a background service (optional)

For production-style reliability (auto-restart, no dependency on a
logged-in terminal session), run the app under a process manager instead
of a bare `runserver`:

- **Linux (systemd):** create a `unitadmin.service` unit that runs
  `gunicorn config.wsgi:application --bind 0.0.0.0:8000` (install
  `gunicorn` via pip) inside the virtual environment, with
  `Restart=on-failure`.
- **Windows:** use **NSSM** (Non-Sucking Service Manager) or Task
  Scheduler to run `python manage.py runserver 0.0.0.0:8000` (or
  `waitress-serve --port=8000 config.wsgi:application` with the
  `waitress` package) at startup.

`python manage.py runserver` is fine for the prototype and for small
units; a WSGI server (gunicorn/waitress) is recommended once the system
becomes part of daily routine.

---

## 10. Backup guidance

The SQLite prototype stores everything in two places:

1. **`db.sqlite3`** - the entire database (all personnel, absence,
   strength, duty roster, and user account records).
2. **`media/`** - any uploaded files (reserved for future use; currently
   unused by default).

### Recommended backup routine

- **Daily backup:** copy `db.sqlite3` (and the `media/` folder, if in
  use) to an **authorized external drive** at the end of each working
  day. A simple approach:

  ```bash
  # Linux/macOS example
  cp db.sqlite3 /path/to/authorized-backup-drive/db_$(date +%Y%m%d).sqlite3
  ```

  ```powershell
  # Windows PowerShell example
  Copy-Item db.sqlite3 "D:\Backups\db_$(Get-Date -Format yyyyMMdd).sqlite3"
  ```

- **Keep multiple dated copies** (not just one rolling backup) so a bad
  entry or accidental deletion can be recovered from an earlier day.
- **Do not** back up to any cloud/internet storage - keep backups on
  unit-authorized removable media or another unit-controlled machine
  only.
- **Test your restore process** occasionally: copy a backup `db.sqlite3`
  back into the project folder (with the app stopped) and confirm the
  app starts and shows the expected data.
- When you migrate to PostgreSQL for production, use `pg_dump`/`pg_restore`
  for backups instead of copying a file.

### General operating guidance

- Do not expose this application to the public internet.
- Use strong, unique passwords for every individual account.
- Review user accounts periodically (Super Admin -> Users) and disable
  accounts of personnel who have been posted out.
- Restrict who has physical and network access to the server PC.

---

## 11. Roadmap ideas (not implemented in this prototype)

The code is structured to make these additions straightforward without
major rework:

- **Excel/PDF export:** `reports/utils.py` already isolates the export
  logic behind a `(filename, headers, rows)`-style helper
  (`export_csv`); adding `export_xlsx()`/`export_pdf()` with the same
  signature and wiring a second URL/button per report is all that is
  required.
- **PostgreSQL in production:** see [Section 8](#8-migrating-from-sqlite-to-postgresql).
- **Calendar view for duty roster:** the duty roster list/upcoming views
  already expose date-based querysets that a calendar widget could
  consume directly.
