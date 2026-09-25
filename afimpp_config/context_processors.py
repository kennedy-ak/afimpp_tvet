"""
Context processors for third-party monitoring/analytics snippets in base.html.

- posthog: PostHog JS snippet configuration (see analytics docs in CLAUDE.md)
- sentry: Sentry browser SDK (frontend errors, web vitals) - enabled when
  SENTRY_DSN is set; renders nothing otherwise.
"""

import json

from django.conf import settings


def _person_props(user):
    return {
        'email': user.email or '',
        'username': user.get_username(),
        'student_id': user.student_id or '',
        'is_student': bool(user.is_student),
        'name': f'{user.first_name} {user.last_name}'.strip(),
    }


def posthog(request):
    user = getattr(request, 'user', None)
    excluded = user is not None and user.is_authenticated and (
        settings.POSTHOG_EXCLUDE_STAFF and (user.is_staff or user.is_superuser)
    )

    tracked_user = user if (
        user is not None and user.is_authenticated and not excluded
    ) else None

    # One-shot flag set by the logout view so the client drops the old identity.
    reset_flag = False
    if request.session.get('_posthog_reset'):
        reset_flag = True
        del request.session['_posthog_reset']

    return {
        'posthog_api_key': settings.POSTHOG_PUBLIC_KEY,
        'posthog_host': settings.POSTHOG_HOST,
        'posthog_session_replay': settings.POSTHOG_SESSION_REPLAY,
        'posthog_excluded': excluded,
        'posthog_user_id': str(tracked_user.pk) if tracked_user else None,
        'posthog_person': json.dumps(_person_props(tracked_user)) if tracked_user else None,
        'posthog_reset': reset_flag,
    }


def sentry(request):
    """Expose Sentry browser SDK settings; empty dict values disable the snippet."""
    dsn = getattr(settings, 'SENTRY_DSN', '') or ''
    if not dsn:
        return {'sentry_browser': None}

    # DSN: https://<public_key>@<org_id>.ingest.<region>.sentry.io/<project_id>
    # The CDN loader script is addressed by the public key alone, but its
    # host must match the project's region (US vs EU).
    try:
        public_key = dsn.split('//', 1)[1].split('@', 1)[0]
        dsn_host = dsn.split('@', 1)[1].split('/', 1)[0]
        if '.ingest.de.sentry.io' in dsn_host or dsn_host.startswith('de.ingest.sentry.io'):
            loader_url = f'https://js.de.sentry-cdn.com/{public_key}.min.js'
        else:
            loader_url = f'https://js.sentry-cdn.com/{public_key}.min.js'
    except IndexError:
        return {'sentry_browser': None}

    return {
        'sentry_browser': {
            'loader_url': loader_url,
            'environment': settings.SENTRY_ENVIRONMENT,
            'release': settings.SENTRY_RELEASE,
            'traces_sample_rate': settings.SENTRY_TRACES_SAMPLE_RATE,
            'replays_sample_rate': settings.SENTRY_REPLAYS_SAMPLE_RATE,
            'replays_on_error_sample_rate': settings.SENTRY_REPLAYS_ON_ERROR_SAMPLE_RATE,
        }
    }
