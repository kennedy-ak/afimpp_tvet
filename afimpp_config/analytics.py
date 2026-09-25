"""
Server-side PostHog analytics helpers.

Usage in any view:

    from afimpp_config.analytics import capture, identify_user

    capture(request, 'enrollment_created', {
        'course': course.title,
        'course_slug': course.slug,
        'level': course.level,
    })

Everything is a silent no-op when POSTHOG_KEY is not configured, and staff
users are skipped when POSTHOG_EXCLUDE_STAFF is enabled. Never let analytics
errors break a request - all failures are logged at debug level only.

Distinct IDs match the client-side snippet: authenticated users are keyed by
``str(user.pk)`` so server events merge with the same person PostHog builds
from browser traffic; anonymous visitors get a session-scoped id.
"""

import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def is_configured():
    """True when a PostHog project API key is set."""
    return bool(settings.POSTHOG_PUBLIC_KEY)


def is_excluded_user(user):
    """True when tracking must be skipped for this user (staff opt-out)."""
    if not user or not user.is_authenticated:
        return False
    return settings.POSTHOG_EXCLUDE_STAFF and (
        user.is_staff or user.is_superuser
    )


def distinct_id(request):
    """Stable distinct id: user pk when logged in, else anonymous session id."""
    if request.user.is_authenticated:
        return str(request.user.pk)
    session_key = request.session.session_key
    if not session_key:
        # First touch for this visitor - persist a session so subsequent
        # anonymous events (newsletter, contact) share one distinct id.
        request.session.create()
        session_key = request.session.session_key
    return f'anon:{session_key}'


def _client():
    """Return the configured posthog module, or None when not set up."""
    if not is_configured():
        return None
    try:
        import posthog
    except ImportError:
        logger.debug('posthog package not installed; skipping capture')
        return None

    if posthog.api_key != settings.POSTHOG_PUBLIC_KEY:
        posthog.api_key = settings.POSTHOG_PUBLIC_KEY
        posthog.host = settings.POSTHOG_HOST
        posthog.sync_mode = False  # batched on a background thread
    return posthog


def capture(request, event, props=None):
    """Capture a server-side event for the current request's user/visitor."""
    try:
        client = _client()
        if client is None or is_excluded_user(getattr(request, 'user', None)):
            return
        client.capture(distinct_id(request), event, props or {})
    except Exception:
        logger.debug('PostHog capture failed for event %s', event, exc_info=True)


def identify_user(user):
    """Set person properties for a user (called on signup/login)."""
    try:
        client = _client()
        if client is None or is_excluded_user(user):
            return
        client.identify(
            str(user.pk),
            {
                'email': user.email or '',
                'username': user.get_username(),
                'student_id': user.student_id or '',
                'is_student': bool(user.is_student),
                'name': f'{user.first_name} {user.last_name}'.strip(),
            },
        )
    except Exception:
        logger.debug('PostHog identify failed', exc_info=True)
