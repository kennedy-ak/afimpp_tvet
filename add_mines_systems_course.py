"""
Script to add the Mines Systems Engineering course to the database
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afimpp_config.settings')
django.setup()

from courses.models import Course

def add_mines_systems_course():
    # Course data from the website
    title = "Higher Professional Certificate II in Mines Systems Engineering (Level 4)"
    short_title = "Mines Systems Engineering (Level 4)"

    overview = """The Higher Professional Certificate II in Mine Systems Engineering is a 12-month Competency-Based Training (CBT) course designed for mining professionals already in the workforce aiming to build on their existing skills, as well as senior secondary school leavers or those with equivalent qualifications seeking in-depth knowledge in mine systems engineering. This program follows a blended learning model, incorporating online sessions with flexible digital classes accessible from anywhere and face-to-face workshops that provide practical, hands-on sessions to enhance technical competence."""

    description = """The Higher Professional Certificate II in Mine Systems Engineering is a 12-month Competency-Based Training (CBT) course designed for mining professionals already in the workforce aiming to build on their existing skills, as well as senior secondary school leavers or those with equivalent qualifications seeking in-depth knowledge in mine systems engineering. This program follows a blended learning model, incorporating online sessions with flexible digital classes accessible from anywhere and face-to-face workshops that provide practical, hands-on sessions to enhance technical competence.

PROGRAM STRUCTURE:

Core Competency Areas Include:
- Mine Safety Regulations
- Basic Electrotechnics & Electronics
- Soil & Rock Mechanics
- Ghana Mining Laws & Regulations
- Mine Ventilation & Environmental Management
- Mine Planning & Design Principles
- Basics of Underground & Surface Mining
- Mineral Processing & Mineral Economics
- Business Ethics & Project Evaluation

Total Credits: 35 (plus electives)

Elective Options: Specialized subjects such as Mine Automation, Advanced Mineral Processing, Sustainable Mining Practices, and more.

ADMISSIONS:
We offer two intakes each year:
- January & June

WHY CHOOSE AFIMPP:
- Industry-Endorsed Curriculum - Delivers up-to-date knowledge for the modern mining sector.
- Flexible Study Format - Seamless blend of online coursework and onsite practical sessions.
- Expert Faculty - Instructors with extensive industry and academic experience.
- Hands-On Training - Practical exercises and case studies that simulate real-world mining scenarios."""

    requirements = """Senior secondary school certificate or equivalent qualifications.
Experience in mining or related industries (preferred for workforce professionals).
Basic understanding of mathematics and science principles."""

    # Check if course already exists
    existing_course = Course.objects.filter(title=title).first()

    if existing_course:
        print(f"Course '{title}' already exists in the database.")
        print(f"Course ID: {existing_course.id}")
        print(f"Slug: {existing_course.slug}")
        return existing_course

    # Create the course
    course = Course.objects.create(
        title=title,
        short_title=short_title,
        description=description,
        level='4',
        duration_months=12,
        overview=overview,
        requirements=requirements,
        learning_mode="Blended Learning (Online + Face-to-Face)",
        price=0.00,  # Set price as needed
        is_active=True,
        featured=True  # Making it featured since it's a major program
    )

    print(f"Successfully created course: {course.title}")
    print(f"  - ID: {course.id}")
    print(f"  - Slug: {course.slug}")
    print(f"  - Level: Level {course.level}")
    print(f"  - Duration: {course.duration_months} months")
    print(f"  - Learning Mode: {course.learning_mode}")

    return course

if __name__ == "__main__":
    print("Adding Mines Systems Engineering course to database...")
    print("-" * 60)
    add_mines_systems_course()
    print("-" * 60)
    print("Done!")
