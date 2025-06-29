#!/usr/bin/env python3
"""
Migration Script: v036 Format wiederherstellen
Konvertiert alle Integrations von config/auth/endpoints zu config_params/input_params/output_params
"""

import json
import os
import sys
from datetime import datetime

def fix_integration_format():
    """Migriert alle Integrations zum korrekten v036-Format"""
    
    integrations_dir = '/home/ga/fb1/age/data/integrations'
    if not os.path.exists(integrations_dir):
        print(f"ERROR: {integrations_dir} not found")
        return False
    
    fixed_count = 0
    error_count = 0
    
    for filename in os.listdir(integrations_dir):
        if not filename.endswith('.json'):
            continue
            
        filepath = os.path.join(integrations_dir, filename)
        print(f"Processing: {filename}")
        
        try:
            # JSON laden
            with open(filepath, 'r', encoding='utf-8') as f:
                integration = json.load(f)
            
            # Prüfen ob original_data vorhanden
            original_data = integration.get('metadata', {}).get('original_data', {})
            if not original_data:
                print(f"  WARNING: No original_data found in {filename}")
                continue
            
            # v036-Daten extrahieren
            config_params = original_data.get('config_params', [])
            input_params = original_data.get('input_params', [])
            output_params = original_data.get('output_params', [])
            
            if not config_params and not input_params and not output_params:
                print(f"  WARNING: No v036 params found in {filename}")
                continue
            
            # v036-Format wiederherstellen
            integration['config_params'] = config_params
            integration['input_params'] = input_params
            integration['output_params'] = output_params
            
            # Vendor Icon aus original_data übernehmen
            if 'vendor_icon' in original_data:
                integration['vendor_icon'] = original_data['vendor_icon']
            
            # API Documentation Link übernehmen
            if 'api_documentation_link' in original_data:
                integration['api_documentation_link'] = original_data['api_documentation_link']
            
            # Vendor aus original_data übernehmen falls leer
            if not integration.get('vendor') and original_data.get('vendor'):
                integration['vendor'] = original_data['vendor']
            
            # Alte Felder entfernen
            integration.pop('config', None)
            integration.pop('auth', None)
            integration.pop('endpoints', None)
            
            # Updated timestamp
            integration['updated_at'] = datetime.now().isoformat()
            
            # Zurückschreiben
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(integration, f, indent=2, ensure_ascii=False)
            
            print(f"  ✅ Fixed: {integration['name']}")
            print(f"     Config params: {len(config_params)}")
            print(f"     Input params: {len(input_params)}")
            print(f"     Output params: {len(output_params)}")
            
            fixed_count += 1
            
        except Exception as e:
            print(f"  ❌ ERROR processing {filename}: {str(e)}")
            error_count += 1
    
    print(f"\n🎯 Migration Summary:")
    print(f"   Fixed: {fixed_count} integrations")
    print(f"   Errors: {error_count} integrations")
    
    return error_count == 0

if __name__ == '__main__':
    print("🔄 Starting Integration Format Migration...")
    success = fix_integration_format()
    if success:
        print("✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("❌ Migration completed with errors!")
        sys.exit(1)
