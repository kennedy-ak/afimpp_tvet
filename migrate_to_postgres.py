import json
import sys
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afimpp_config.settings')
django.setup()

from django.core import serializers
from django.apps import apps

def export_data():
    """Export data from current database"""
    print("Exporting data...")

    # Get all models except contenttypes and permissions
    all_objects = []
    for model in apps.get_models():
        if model._meta.app_label == 'contenttypes':
            continue
        if model._meta.model_name == 'permission' and model._meta.app_label == 'auth':
            continue

        objects = model.objects.all()
        if objects.exists():
            print(f"Exporting {objects.count()} objects from {model._meta.label}")
            all_objects.extend(objects)

    # Serialize with proper encoding
    data = serializers.serialize('json', all_objects,
                                 indent=2,
                                 use_natural_foreign_keys=True,
                                 use_natural_primary_keys=True)

    # Write with UTF-8 encoding
    with open('data_export.json', 'w', encoding='utf-8') as f:
        f.write(data)

    print(f"Successfully exported {len(all_objects)} objects to data_export.json")

def import_data():
    """Import data into current database"""
    print("Importing data...")

    with open('data_export.json', 'r', encoding='utf-8') as f:
        data = f.read()

    objects = serializers.deserialize('json', data)

    count = 0
    for obj in objects:
        try:
            obj.save()
            count += 1
        except Exception as e:
            print(f"Error saving {obj}: {e}")

    print(f"Successfully imported {count} objects")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python migrate_to_postgres.py [export|import]")
        sys.exit(1)

    action = sys.argv[1]
    if action == 'export':
        export_data()
    elif action == 'import':
        import_data()
    else:
        print("Invalid action. Use 'export' or 'import'")