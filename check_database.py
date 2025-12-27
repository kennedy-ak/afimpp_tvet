"""
Script to check if there's data in the database
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afimpp_config.settings')
django.setup()

from users.models import User
from courses.models import Course, Category, Enrollment, Lesson
from contact.models import Contact

def check_database():
    print("=" * 50)
    print("DATABASE DATA CHECK")
    print("=" * 50)

    # Check Users
    user_count = User.objects.count()
    print(f"\n📊 USERS: {user_count}")
    if user_count > 0:
        print("Sample users:")
        for user in User.objects.all()[:5]:
            print(f"  - {user.username} ({user.email})")

    # Check Categories
    category_count = Category.objects.count()
    print(f"\n📊 CATEGORIES: {category_count}")
    if category_count > 0:
        print("Sample categories:")
        for cat in Category.objects.all()[:5]:
            print(f"  - {cat.name}")

    # Check Courses
    course_count = Course.objects.count()
    print(f"\n📊 COURSES: {course_count}")
    if course_count > 0:
        print("Sample courses:")
        for course in Course.objects.all()[:5]:
            print(f"  - {course.title} (Category: {course.category.name if course.category else 'None'})")

    # Check Lessons
    lesson_count = Lesson.objects.count()
    print(f"\n📊 LESSONS: {lesson_count}")
    if lesson_count > 0:
        print("Sample lessons:")
        for lesson in Lesson.objects.all()[:5]:
            print(f"  - {lesson.title} (Course: {lesson.course.title})")

    # Check Enrollments
    enrollment_count = Enrollment.objects.count()
    print(f"\n📊 ENROLLMENTS: {enrollment_count}")
    if enrollment_count > 0:
        print("Sample enrollments:")
        for enrollment in Enrollment.objects.all()[:5]:
            print(f"  - {enrollment.user.username} enrolled in {enrollment.course.title}")

    # Check Contact Messages
    contact_count = Contact.objects.count()
    print(f"\n📊 CONTACT MESSAGES: {contact_count}")
    if contact_count > 0:
        print("Sample messages:")
        for contact in Contact.objects.all()[:5]:
            print(f"  - {contact.name} ({contact.email}): {contact.subject}")

    print("\n" + "=" * 50)
    total = user_count + category_count + course_count + lesson_count + enrollment_count + contact_count
    if total == 0:
        print("❌ DATABASE IS EMPTY")
    else:
        print(f"✅ DATABASE HAS {total} TOTAL RECORDS")
    print("=" * 50)

if __name__ == "__main__":
    try:
        check_database()
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\nMake sure:")
        print("1. Required packages are installed (pip install python-decouple dj-database-url psycopg2-binary)")
        print("2. Migrations have been run (python manage.py migrate)")
