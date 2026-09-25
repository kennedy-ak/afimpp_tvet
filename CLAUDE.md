# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

```bash
# Development
python manage.py runserver              # Start dev server at http://127.0.0.1:8000

# Database
python manage.py migrate                # Run migrations
python manage.py makemigrations         # Create migrations
python manage.py createsuperuser        # Create admin user

# Static files
python manage.py collectstatic          # Collect static files for production

# Testing
python manage.py test                   # Run tests
python manage.py test <app_name>        # Run tests for specific app

# Dependencies
pip install -r pyproject.toml           # Install dependencies (alternative: uv sync)
```

## Project Architecture

This is a Django 6.0 web application for AfIMMP (African Institute for Mining and Mineral Processing), a technical and vocational training center.

### Django Apps

| App | Purpose |
|-----|---------|
| `afimpp_config` | Project configuration (settings, URLs, WSGI) |
| `core` | Homepage, about, gallery, site-wide settings, newsletter |
| `courses` | Course catalog, enrollment, payments, registration forms |
| `users` | Custom user model, authentication, registration codes |
| `contact` | Contact forms |

### Key Architectural Details

**Custom User Model**: The project uses a custom User model (`users.models.User`) that extends `AbstractUser`. Key fields:
- `email` (unique) - used for login
- `is_student` - boolean flag for student role
- `student_id` - unique student identifier
- `terms_accepted` - for registration tracking

Always use `get_user_model()` or import User from the users app when referencing the User model.

**Registration Flow**: Students must have a valid `RegistrationCode` before enrolling. Codes are generated in admin and can have expiration dates. The code links to the user who uses it.

**Course Levels**: Three-tier system (Level 3 = Foundation, Level 4 = Intermediate, Level 5 = Advanced).

**Enrollment Workflow**:
1. User browses courses → creates account (requires registration code)
2. Enrolls in course → creates `Enrollment` record (status=pending)
3. Completes `CourseRegistration` form (personal info, documents)
4. Makes payment → creates `Payment` record
5. Admin approves enrollment → changes status to 'approved'

### Configuration

- Environment variables managed via `python-decouple`
- `DATABASE_URL` for PostgreSQL (uses SQLite if not set)
- Static files in `/static/`, media uploads in `/media/`
- Admin panel accessed at `/mgmt-portal/` (not `/admin/`)
- Log shipping via Observo middleware (`observo_handler.middleware.RequestIDMiddleware`)
- PostHog analytics: client snippet in `templates/base.html` + server-side events via `afimpp_config.analytics.capture(request, event, props)`. Configure with `POSTHOG_KEY`, `POSTHOG_HOST`, `POSTHOG_SESSION_REPLAY`, `POSTHOG_EXCLUDE_STAFF` in `.env`. Distinct ID is `str(user.pk)` (matches JS `identify`); staff/superusers are excluded when `POSTHOG_EXCLUDE_STAFF=True`.
- Sentry: error tracking, tracing and performance monitoring. Server SDK inits in `settings.py` (covers manage.py, runserver and gunicorn); browser SDK renders in `base.html` via the `sentry` context processor. Fully disabled until `SENTRY_DSN` is set in `.env`. Toggles: `SENTRY_TRACES_SAMPLE_RATE` (default 1.0), `SENTRY_PROFILES_SAMPLE_RATE` (default 0), `SENTRY_REPLAYS_SAMPLE_RATE` / `SENTRY_REPLAYS_ON_ERROR_SAMPLE_RATE` (default 0), `SENTRY_SEND_PII` (default True), `SENTRY_ENVIRONMENT`, `SENTRY_RELEASE` (defaults to git short SHA).

### Dependencies

Key packages from `pyproject.toml`:
- `django>=6.0` - Framework
- `crispy-forms`, `crispy-bootstrap5` - Form rendering
- `psycopg2-binary`, `dj-database-url` - PostgreSQL support
- `pillow` - Image handling
- `waitress` - Production WSGI server
- `observo-handler` - Log shipping integration

### File Upload Patterns

Uploaded files are organized by type:
- `profile_pictures/` - User avatars
- `gallery/` - Site gallery images
- `courses/` - Course images
- `documents/passport_photos/` - Registration documents
- `documents/birth_certificates/` - Registration documents
- `documents/education_certificates/` - Registration documents

### URLs Structure

- `/` → Core app (home, about, gallery)
- `/courses/` → Course catalog, detail, enrollment
- `/users/` → Auth (register, login, profile)
- `/contact/` → Contact form
- `/mgmt-portal/` → Django admin
