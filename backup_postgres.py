import json
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afimpp_config.settings')
django.setup()

from django.core import serializers
from django.apps import apps
from datetime import datetime

def backup_postgresql():
    """Backup PostgreSQL database to JSON file"""
    print("Creating PostgreSQL database backup...")
    
    # Get all models
    all_objects = []
    for model in apps.get_models():
        if model._meta.app_label == 'contenttypes':
            continue
        if model._meta.model_name == 'permission' and model._meta.app_label == 'auth':
            continue

        objects = model.objects.all()
        if objects.exists():
            print(f"Backing up {objects.count()} objects from {model._meta.label}")
            all_objects.extend(objects)

    # Serialize with proper encoding
    data = serializers.serialize('json', all_objects,
                                 indent=2,
                                 use_natural_foreign_keys=True,
                                 use_natural_primary_keys=True)

    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'postgres_backup_{timestamp}.json'

    # Write with UTF-8 encoding
    with open(backup_filename, 'w', encoding='utf-8') as f:
        f.write(data)

    print(f"\nSuccessfully backed up {len(all_objects)} objects to {backup_filename}")
    print(f"Backup completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    backup_postgresql()
