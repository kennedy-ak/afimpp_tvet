"""
Script to add the Mining and Quarrying Technology course to the database
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afimpp_config.settings')
django.setup()

from courses.models import Course

def add_mining_course():
    # Course data from the website
    title = "Higher Professional Certificate I in Mining and Quarrying Technology (Level 3)"
    short_title = "Mining and Quarrying Technology (Level 3)"

    overview = """The Higher Professional Certificate I in Mining and Quarrying Technology is a 24-month Competency-Based Training (CBT) program designed for individuals with experience in mining and related fields looking to upskill and advance in their careers, as well as junior secondary school leavers or those with equivalent qualifications interested in entering the mining and quarrying industry. This program adopts a blended learning approach, integrating online learning through flexible, interactive virtual classes and face-to-face sessions that provide practical training with industry experts."""

    description = """The Higher Professional Certificate I in Mining and Quarrying Technology is a 24-month Competency-Based Training (CBT) program designed for:

• Individuals with experience in mining and related fields looking to upskill and advance in their careers.
• Junior secondary school leavers or equivalent interested in entering the mining and quarrying industry.

ABOUT THE PROGRAM:
The Higher Professional Certificate I in Mining and Quarrying Technology is a 24-month Competency-Based Training (CBT) program designed for:
• Individuals with experience in mining and related fields looking to upskill and advance in their careers.
• Junior secondary school leavers or equivalent interested in entering the mining and quarrying industry.

ADMISSIONS:
We offer two intakes annually:
• January
• June

ASSESSMENT:
Assessments are conducted at the end of each module. They include:
• Practical Demonstrations: Real-world application of learned skills.
• Written Tests: Evaluation of theoretical knowledge.
• Project Work: Hands-on projects in simulated environments.

ADMISSION REQUIREMENTS:
• Completion of Basic Education Certificate Examination (BECE) or equivalent.
• Proficiency in basic English and Mathematics.
• Interest or prior experience in mining or related industries (preferred but not mandatory).

WHY CHOOSE AFIMPP?
• Industry-Relevant Curriculum – Designed to meet the evolving needs of the mining and quarrying sector.
• Hybrid Learning Model – Study at your convenience with online and in-person training.
• Expert Faculty – Learn from professionals with real-world mining and quarrying experience.
• Hands-On Training – Gain practical skills applicable to the field."""

    requirements = """Completion of Basic Education Certificate Examination (BECE) or equivalent.
Proficiency in basic English and Mathematics.
Interest or prior experience in mining or related industries (preferred but not mandatory)."""

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
        level='3',
        duration_months=24,
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
    print("Adding Mining and Quarrying Technology course to database...")
    print("-" * 60)
    add_mining_course()
    print("-" * 60)
    print("Done!")
