import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afimpp_config.settings')
django.setup()

from django.apps import apps

def verify_data():
    """Verify data integrity by counting records in current database"""
    print("Verifying data integrity in current database...")
    print("=" * 60)
    
    # Define models to check
    models_to_check = [
        'users.User',
        'users.RegistrationCode',
        'core.SiteSettings',
        'core.Newsletter',
        'core.GalleryImage',
        'courses.Course',
        'courses.CourseModule',
        'courses.Enrollment',
        'courses.Payment',
        'courses.CourseRegistration',
        'contact.ContactMessage',
        'admin.LogEntry',
    ]
    
    total_records = 0
    
    for model_path in models_to_check:
        try:
            app_label, model_name = model_path.lower().split('.')
            model = apps.get_model(app_label, model_name)
            count = model.objects.count()
            total_records += count
            print(f"{model._meta.label:30s}: {count:4d} records")
        except Exception as e:
            print(f"{model_path:30s}: ERROR - {e}")
    
    print("=" * 60)
    print(f"Total records: {total_records}")
    print("\nExpected from SQLite export:")
    print("  - 9 admin log entries")
    print("  - 6 gallery images")
    print("  - 3 courses")
    print("  - 6 course modules")
    print("  - 2 users")
    print("  - Total: 26 objects")

if __name__ == '__main__':
    verify_data()
