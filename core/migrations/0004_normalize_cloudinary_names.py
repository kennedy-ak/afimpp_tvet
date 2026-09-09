"""
Normalize file names that were stored as full Cloudinary URLs.

The ``upload_to_cloudinary`` command originally saved ``result['url']``
(e.g. ``http://res.cloudinary.com/<cloud>/image/upload/v123/afimpp/courses/x.jpg.jpg``)
into ImageFields. Storage backends expect the Cloudinary public ID
(``afimpp/courses/x.jpg.jpg``) and prepend their own base URL, which produced
broken image links. This migration strips the URL down to the public ID.
Idempotent: names that are already public IDs are left untouched.
"""
import re

from django.db import migrations

_UPLOAD_URL = re.compile(r'^https?://res\.cloudinary\.com/[^/]+/[^/]+/upload/(?:v\d+/)?(?P<public_id>.+)$')

FIELDS = [
    ('core', 'GalleryImage', 'image'),
    ('core', 'SiteSettings', 'about_image'),
    ('courses', 'Course', 'image'),
    ('users', 'User', 'profile_picture'),
]


def _normalize(name):
    match = _UPLOAD_URL.match(name or '')
    return match.group('public_id') if match else name


def forwards(apps, schema_editor):
    for app_label, model_name, field in FIELDS:
        try:
            model = apps.get_model(app_label, model_name)
            model._meta.get_field(field)
        except LookupError:
            continue
        for obj in model.objects.exclude(**{field: ''}).exclude(**{f'{field}__isnull': True}):
            current = getattr(obj, field).name
            new = _normalize(current)
            if new != current:
                setattr(obj, field, new)
                obj.save(update_fields=[field])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_galleryimage_image_and_more'),
        ('courses', '0004_alter_course_image'),
        ('users', '0004_alter_user_profile_picture'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
