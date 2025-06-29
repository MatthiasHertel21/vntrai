#!/usr/bin/env python3
"""
Migration Script: v036 Format korrigieren
Überträgt config_params, input_params, output_params aus metadata.original_data
in die korrekte Struktur
"""

import os
import json
import sys
from datetime import datetime

def migrate_integration_file(filepath):
    """Migriert eine einzelne Integration-Datei"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if migration needed
        if 'metadata' not in data or 'original_data' not in data['metadata']:
            print(f"Skipping {filepath} - no original_data found")
            return False
        
        original = data['metadata']['original_data']
        
        # Extract v036 format from original_data
        if 'config_params' in original:
            data['config_params'] = original['config_params']
        
        if 'input_params' in original:
            data['input_params'] = original['input_params']
        
        if 'output_params' in original:
            data['output_params'] = original['output_params']
        
        # Keep other v036 fields
        if 'api_documentation_link' in original:
            data['api_documentation_link'] = original['api_documentation_link']
        
        if 'vendor_icon' in original:
            data['vendor_icon'] = original['vendor_icon']
        
        # Remove old incorrect fields
        if 'config' in data:
            del data['config']
        if 'auth' in data:
            del data['auth']
        if 'endpoints' in data:
            del data['endpoints']
        
        # Update timestamps
        data['updated_at'] = datetime.now().isoformat()
        
        # Add migration marker
        data['metadata']['format_corrected'] = True
        data['metadata']['format_correction_date'] = datetime.now().isoformat()
        
        # Save corrected data
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Migrated {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating {filepath}: {e}")
        return False

def main():
    """Main migration function"""
    # Get the script directory and find the data directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))  # Go up from app/utils
    data_dir = os.path.join(project_root, 'data', 'integrations')
    
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        sys.exit(1)
    
    print(f"🔧 Starting v036 format correction in: {data_dir}")
    
    # Find all JSON files
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    
    if not json_files:
        print("❌ No JSON files found")
        sys.exit(1)
    
    print(f"📂 Found {len(json_files)} integration files")
    
    # Process each file
    success_count = 0
    for filename in json_files:
        filepath = os.path.join(data_dir, filename)
        if migrate_integration_file(filepath):
            success_count += 1
    
    print(f"\n✅ Migration completed: {success_count}/{len(json_files)} files processed successfully")

if __name__ == '__main__':
    main()
