import json
import sys
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afimpp_config.settings')
django.setup()

from django.core import serializers
from django.apps import apps
from django.db import transaction

def get_import_order():
    """
    Define the order in which models should be imported to respect dependencies.
    Models with no dependencies come first, then models that depend on them.
    """
    return [
        'users.User',  # Users must come first as they're referenced by many models
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
        # Admin log entries should come last as they reference other models
        'admin.LogEntry',
    ]

def export_data():
    """Export data from current database in proper order"""
    print("Exporting data...")

    import_order = get_import_order()
    all_objects = []

    # Get all models except contenttypes and permissions
    for model_path in import_order:
        try:
            app_label, model_name = model_path.lower().split('.')
            model = apps.get_model(app_label, model_name)
            
            objects = model.objects.all()
            if objects.exists():
                print(f"Exporting {objects.count()} objects from {model._meta.label}")
                all_objects.extend(objects)
        except Exception as e:
            print(f"Warning: Could not export {model_path}: {e}")

    # Serialize with proper encoding
    data = serializers.serialize('json', all_objects,
                                 indent=2,
                                 use_natural_foreign_keys=True,
                                 use_natural_primary_keys=True)

    # Write with UTF-8 encoding
    with open('data_export_ordered.json', 'w', encoding='utf-8') as f:
        f.write(data)

    print(f"Successfully exported {len(all_objects)} objects to data_export_ordered.json")

def import_data():
    """Import data into current database with proper error handling"""
    print("Importing data...")

    with open('data_export_ordered.json', 'r', encoding='utf-8') as f:
        data = f.read()

    objects = serializers.deserialize('json', data)

    count = 0
    errors = []
    
    for obj in objects:
        try:
            with transaction.atomic():
                obj.save()
                count += 1
                print(f"Imported: {obj.object.__class__.__name__} - {obj.object}")
        except Exception as e:
            error_msg = f"Error saving {obj.object.__class__.__name__}: {e}"
            print(error_msg)
            errors.append(error_msg)

    print(f"\nSuccessfully imported {count} objects")
    if errors:
        print(f"\n{len(errors)} errors occurred:")
        for error in errors:
            print(f"  - {error}")

def verify_data():
    """Verify data integrity by counting records"""
    print("\nVerifying data integrity...")
    
    import_order = get_import_order()
    
    for model_path in import_order:
        try:
            app_label, model_name = model_path.lower().split('.')
            model = apps.get_model(app_label, model_name)
            count = model.objects.count()
            print(f"{model._meta.label}: {count} records")
        except Exception as e:
            print(f"Warning: Could not verify {model_path}: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python migrate_to_postgres_v2.py [export|import|verify]")
        sys.exit(1)

    action = sys.argv[1]
    if action == 'export':
        export_data()
    elif action == 'import':
        import_data()
    elif action == 'verify':
        verify_data()
    else:
        print("Invalid action. Use 'export', 'import', or 'verify'")
