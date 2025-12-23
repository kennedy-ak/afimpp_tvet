"""
Script to view all courses in the database
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afimpp_config.settings')
django.setup()

from courses.models import Course

def view_all_courses():
    courses = Course.objects.all().order_by('level', 'id')

    print("=" * 80)
    print(f"TOTAL COURSES IN DATABASE: {courses.count()}")
    print("=" * 80)

    for course in courses:
        print(f"\nCourse ID: {course.id}")
        print(f"Title: {course.title}")
        print(f"Short Title: {course.short_title}")
        print(f"Level: Level {course.level}")
        print(f"Duration: {course.duration_months} months")
        print(f"Learning Mode: {course.learning_mode}")
        print(f"Slug: {course.slug}")
        print(f"Active: {course.is_active} | Featured: {course.featured}")
        print(f"Created: {course.created_at}")
        print("-" * 80)

if __name__ == "__main__":
    view_all_courses()
