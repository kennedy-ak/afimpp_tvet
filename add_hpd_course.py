"""
Script to add the Higher Professional Diploma (HPD) in Mines System Engineering course to the database
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afimpp_config.settings')
django.setup()

from courses.models import Course

def add_hpd_course():
    # Course data from the website
    title = "Higher Professional Diploma (HPD) in Mines System Engineering (Level 5)"
    short_title = "HPD in Mines System Engineering (Level 5)"

    overview = """The Higher Professional Diploma (HPD) in Mines System Engineering is an advanced Level 5 program designed to provide comprehensive knowledge and skills in mine systems engineering. This program is structured to develop competent professionals capable of managing and optimizing mining operations and systems."""

    description = """The Higher Professional Diploma (HPD) in Mines System Engineering (Level 5) is an advanced program designed for professionals seeking to advance their expertise in mine systems engineering.

COURSE STRUCTURE:
Total Credits: 60

The program covers advanced topics in mine systems engineering, preparing graduates for senior technical and management roles in the mining industry.

This qualification builds upon foundational knowledge and develops advanced competencies required for modern mining operations."""

    requirements = """Completion of Higher Professional Certificate II (Level 4) or equivalent qualification.
Relevant work experience in mining or related engineering fields.
Strong foundation in mathematics, science, and engineering principles."""

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
        level='5',
        duration_months=18,  # Typical duration for Level 5 diploma, adjust if you have specific info
        overview=overview,
        requirements=requirements,
        learning_mode="Blended Learning (Online + Face-to-Face)",
        price=0.00,  # Set price as needed
        is_active=True,
        featured=True  # Making it featured since it's an advanced program
    )

    print(f"Successfully created course: {course.title}")
    print(f"  - ID: {course.id}")
    print(f"  - Slug: {course.slug}")
    print(f"  - Level: Level {course.level}")
    print(f"  - Duration: {course.duration_months} months")
    print(f"  - Learning Mode: {course.learning_mode}")
    print(f"  - Total Credits: 60")

    return course

if __name__ == "__main__":
    print("Adding Higher Professional Diploma (HPD) course to database...")
    print("-" * 60)
    add_hpd_course()
    print("-" * 60)
    print("Done!")
    print("\nNote: You may want to update the course details through Django admin")
    print("or provide more detailed content for the description sections.")
