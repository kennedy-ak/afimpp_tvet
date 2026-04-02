import os
import re
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
import cloudinary.uploader
from core.models import GalleryImage, SiteSettings
from courses.models import Course
from users.models import User


class Command(BaseCommand):
    help = 'Upload local media files to Cloudinary and update database references'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be uploaded without actually uploading',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No actual uploads will occur'))

        media_root = Path(settings.MEDIA_ROOT)

        # Build a map of available local files by base name
        local_files = self.scan_local_files(media_root)

        total_uploaded = 0
        total_failed = 0

        # Process Course images
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Processing Course images...')
        self.stdout.write('='*50)

        # Get all local course images
        local_course_images = local_files.get('courses', [])
        courses_needing_images = []

        for course in Course.objects.all():
            if course.image and hasattr(course.image, 'name') and course.image.name:
                base_name = Path(course.image.name).stem
                extension = Path(course.image.name).suffix
                local_path = self.find_matching_file(base_name, extension, local_course_images)

                if local_path:
                    result = self.upload_file(local_path, f'courses/{Path(local_path).name}', dry_run)
                    if result:
                        if not dry_run:
                            course.image = result['url']
                            course.save()
                        total_uploaded += 1
                    else:
                        total_failed += 1
                else:
                    courses_needing_images.append(course)
                    self.stdout.write(self.style.WARNING(f'  No match found for: {course.image.name}'))

        # Assign available local images to courses that don't have matches
        if courses_needing_images and local_course_images:
            self.stdout.write(self.style.WARNING(f'\n  Assigning available images to {len(courses_needing_images)} courses without matches...'))
            for i, course in enumerate(courses_needing_images):
                if i < len(local_course_images):
                    local_path = local_course_images[i]
                    result = self.upload_file(local_path, f'courses/{Path(local_path).name}', dry_run)
                    if result:
                        if not dry_run:
                            course.image = result['url']
                            course.save()
                        total_uploaded += 1
                        self.stdout.write(self.style.SUCCESS(f'  Assigned {Path(local_path).name} to course: {course.title}'))

        # Process Gallery images
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Processing Gallery images...')
        self.stdout.write('='*50)
        for item in GalleryImage.objects.all():
            if item.image and hasattr(item.image, 'name') and item.image.name:
                base_name = Path(item.image.name).stem
                extension = Path(item.image.name).suffix
                local_path = self.find_matching_file(base_name, extension, local_files.get('gallery', []))

                if local_path:
                    result = self.upload_file(local_path, f'gallery/{Path(local_path).name}', dry_run)
                    if result:
                        if not dry_run:
                            item.image = result['url']
                            item.save()
                        total_uploaded += 1
                    else:
                        total_failed += 1
                else:
                    self.stdout.write(self.style.WARNING(f'  No match found for: {item.image.name}'))

        # Process User profile pictures
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Processing User profile pictures...')
        self.stdout.write('='*50)
        for user in User.objects.all():
            if user.profile_picture and hasattr(user.profile_picture, 'name') and user.profile_picture.name:
                base_name = Path(user.profile_picture.name).stem
                extension = Path(user.profile_picture.name).suffix
                local_path = self.find_matching_file(base_name, extension, local_files.get('profile_pictures', []))

                if local_path:
                    result = self.upload_file(local_path, f'profile_pictures/{Path(local_path).name}', dry_run)
                    if result:
                        if not dry_run:
                            user.profile_picture = result['url']
                            user.save()
                        total_uploaded += 1
                    else:
                        total_failed += 1

        # Process SiteSettings about_image
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Processing SiteSettings images...')
        self.stdout.write('='*50)
        for site_setting in SiteSettings.objects.all():
            if site_setting.about_image and hasattr(site_setting.about_image, 'name') and site_setting.about_image.name:
                base_name = Path(site_setting.about_image.name).stem
                extension = Path(site_setting.about_image.name).suffix
                local_path = self.find_matching_file(base_name, extension, local_files.get('about', []))

                if local_path:
                    result = self.upload_file(local_path, f'about/{Path(local_path).name}', dry_run)
                    if result:
                        if not dry_run:
                            site_setting.about_image = result['url']
                            site_setting.save()
                        total_uploaded += 1
                    else:
                        total_failed += 1

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('SUMMARY')
        self.stdout.write('='*50)
        self.stdout.write(self.style.SUCCESS(f'Successfully processed: {total_uploaded} files'))
        if total_failed > 0:
            self.stdout.write(self.style.ERROR(f'Failed: {total_failed} files'))

        if dry_run:
            self.stdout.write(self.style.WARNING('\nRun without --dry-run to actually upload files'))

    def scan_local_files(self, media_root):
        """Scan media directory and build a map of available files"""
        files = {
            'courses': [],
            'gallery': [],
            'profile_pictures': [],
            'about': [],
        }

        for category in files.keys():
            category_path = media_root / category
            if category_path.exists():
                for file_path in category_path.iterdir():
                    if file_path.is_file():
                        files[category].append(str(file_path))

        return files

    def find_matching_file(self, base_name, extension, local_files):
        """
        Find a matching local file by comparing base names.
        Handles cases where database has random suffixes but local files don't.
        """
        # First try exact match
        for local_file in local_files:
            local_name = Path(local_file).stem
            local_ext = Path(local_file).suffix
            if local_name == base_name and local_ext == extension:
                return local_file

        # Try fuzzy match - find file that starts with the same base name
        # This handles cases like "lev5.jpg" in DB vs "lev5.jpg" on disk
        # or "2-300x225_8v25W6j.jpg" in DB vs "2-300x225.jpg" on disk
        for local_file in local_files:
            local_name = Path(local_file).stem
            local_ext = Path(local_file).suffix

            # Remove random suffix pattern (underscore followed by alphanumeric chars)
            # from database filename
            clean_base_name = re.sub(r'_[a-zA-Z0-9]+$', '', base_name)

            if local_name == clean_base_name and local_ext == extension:
                return local_file

            # Also try direct match
            if local_name == base_name:
                return local_file

        # Try even looser match - same extension and similar name
        for local_file in local_files:
            local_ext = Path(local_file).suffix
            if local_ext == extension:
                local_name = Path(local_file).stem
                # Check if one is a prefix of the other
                if base_name.startswith(local_name[:10]) or local_name.startswith(base_name[:10]):
                    return local_file

        return None

    def upload_file(self, local_path, public_id, dry_run=False):
        """Upload a single file to Cloudinary"""
        if not os.path.exists(local_path):
            self.stdout.write(self.style.WARNING(f'  File not found: {local_path}'))
            return None

        filename = os.path.basename(local_path)
        if dry_run:
            self.stdout.write(f'  Would upload: {filename} -> {public_id}')
            return {'url': f'https://cloudinary.com/{public_id}'}

        try:
            # Upload to Cloudinary with folder structure
            result = cloudinary.uploader.upload(
                local_path,
                public_id=public_id,
                folder='afimpp',
                resource_type='image',
                overwrite=True,
            )
            url = result.get('url', result.get('secure_url'))
            self.stdout.write(self.style.SUCCESS(f'  Uploaded: {filename} -> {url}'))
            return result
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  Failed to upload {filename}: {str(e)}'))
            return None
