"""
Script to view the Mining and Quarrying Technology course from the database
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afimpp_config.settings')
django.setup()

from courses.models import Course

def view_course():
    course = Course.objects.filter(
        title="Higher Professional Certificate I in Mining and Quarrying Technology (Level 3)"
    ).first()

    if not course:
        print("Course not found!")
        return

    print("=" * 80)
    print("COURSE DETAILS")
    print("=" * 80)
    print(f"ID: {course.id}")
    print(f"Title: {course.title}")
    print(f"Short Title: {course.short_title}")
    print(f"Slug: {course.slug}")
    print(f"Level: Level {course.level}")
    print(f"Duration: {course.duration_months} months")
    print(f"Learning Mode: {course.learning_mode}")
    print(f"Price: GHS {course.price}")
    print(f"Active: {course.is_active}")
    print(f"Featured: {course.featured}")
    print(f"Created: {course.created_at}")
    print(f"Updated: {course.updated_at}")
    print("\n" + "=" * 80)
    print("OVERVIEW")
    print("=" * 80)
    print(course.overview)
    print("\n" + "=" * 80)
    print("REQUIREMENTS")
    print("=" * 80)
    print(course.requirements)
    print("\n" + "=" * 80)
    print("DESCRIPTION")
    print("=" * 80)
    print(course.description)
    print("=" * 80)

if __name__ == "__main__":
    view_course()
