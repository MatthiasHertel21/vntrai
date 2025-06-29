#!/usr/bin/env python3
"""
Fix Tools Migration - Copy tool_definition from metadata to main object
"""
import sys
import os
import json
from pathlib import Path

sys.path.append('/app')

def fix_tools_migration():
    """Fix tools migration by copying tool_definition from metadata"""
    
    print("=== Fixing Tools Migration ===")
    
    tools_dir = Path('/app/data/tools')
    if not tools_dir.exists():
        print(f"ERROR: Tools directory {tools_dir} does not exist")
        return False
    
    json_files = list(tools_dir.glob('*.json'))
    print(f"Found {len(json_files)} tool files")
    
    fixed_count = 0
    
    for file_path in json_files:
        try:
            # Load tool data
            with open(file_path, 'r', encoding='utf-8') as f:
                tool = json.load(f)
            
            # Check if tool_definition is missing from main object but exists in metadata
            if ('tool_definition' not in tool or not tool['tool_definition']) and \
               'metadata' in tool and \
               'original_data' in tool['metadata'] and \
               'tool_definition' in tool['metadata']['original_data']:
                
                # Copy tool_definition from metadata to main object
                tool_definition = tool['metadata']['original_data']['tool_definition']
                tool['tool_definition'] = tool_definition
                
                # Also copy other important v036 fields if missing
                if 'prefilled_inputs' not in tool and 'prefilled_inputs' in tool['metadata']['original_data']:
                    tool['prefilled_inputs'] = tool['metadata']['original_data']['prefilled_inputs']
                
                if 'locked_inputs' not in tool and 'locked_inputs' in tool['metadata']['original_data']:
                    tool['locked_inputs'] = tool['metadata']['original_data']['locked_inputs']
                
                if 'last_test' not in tool and 'last_test' in tool['metadata']['original_data']:
                    tool['last_test'] = tool['metadata']['original_data']['last_test']
                
                if 'last_execution' not in tool and 'last_execution' in tool['metadata']['original_data']:
                    tool['last_execution'] = tool['metadata']['original_data']['last_execution']
                
                # Update timestamp
                from datetime import datetime
                tool['updated_at'] = datetime.utcnow().isoformat() + 'Z'
                
                # Save fixed tool
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(tool, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Fixed: {tool['name']} -> {tool_definition}")
                fixed_count += 1
            else:
                if 'tool_definition' in tool and tool['tool_definition']:
                    print(f"✓ OK: {tool['name']} -> {tool['tool_definition']}")
                else:
                    print(f"⚠️ No tool_definition found for: {tool['name']}")
        
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    print(f"\n=== Migration Fix Complete ===")
    print(f"Fixed {fixed_count} tools")
    return True

if __name__ == "__main__":
    fix_tools_migration()
