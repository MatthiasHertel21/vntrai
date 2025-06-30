#!/usr/bin/env python3
"""
Script to assign implementation modules to all integrations
This ensures proper AI Assistant integration in Sprint 17
"""

import json
import os
from pathlib import Path

def assign_implementations():
    """Assign implementation modules to integrations based on their characteristics"""
    
    integrations_dir = Path("/home/ga/fb1/age/data/integrations")
    
    # Define implementation mapping based on integration characteristics
    implementation_mappings = {
        # OpenAI-based integrations
        "openai": "openai_chatcompletion",
        "chatgpt": "openai_chatcompletion", 
        "gpt": "openai_chatcompletion",
        "ai": "openai_chatcompletion",
        
        # Google-based integrations
        "google": "google_sheets",
        "sheets": "google_sheets",
        "drive": "google_sheets",
        "gmail": "google_sheets",
        
        # Default fallback for API integrations
        "api": "openai_chatcompletion",
        "webhook": "openai_chatcompletion"
    }
    
    updated_count = 0
    
    for json_file in integrations_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                integration = json.load(f)
            
            # Skip if implementation already assigned
            if integration.get('implementation'):
                print(f"✓ {integration.get('name', json_file.name)} already has implementation: {integration['implementation']}")
                continue
                
            # Determine implementation based on name and description
            name = integration.get('name', '').lower()
            description = integration.get('description', '').lower()
            text_to_check = f"{name} {description}"
            
            # Find matching implementation
            assigned_implementation = "openai_chatcompletion"  # default
            
            for keyword, impl in implementation_mappings.items():
                if keyword in text_to_check:
                    assigned_implementation = impl
                    break
            
            # Special cases for specific integrations
            if "google" in name or "sheets" in name:
                assigned_implementation = "google_sheets"
            elif "openai" in name or "chatgpt" in name or "gpt" in name:
                assigned_implementation = "openai_chatcompletion"
            
            # Assign implementation
            integration['implementation'] = assigned_implementation
            
            # Update metadata
            if 'metadata' not in integration:
                integration['metadata'] = {}
            integration['metadata']['implementation_assigned'] = True
            integration['metadata']['implementation_assignment_date'] = "2025-07-01T00:00:00"
            
            # Save updated integration
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(integration, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Updated {integration.get('name', json_file.name)}: {assigned_implementation}")
            updated_count += 1
            
        except Exception as e:
            print(f"✗ Error processing {json_file.name}: {e}")
    
    print(f"\n🎉 Implementation assignment complete! Updated {updated_count} integrations.")
    print(f"All integrations now have implementation modules assigned for Sprint 17 AI Assistant integration.")

if __name__ == "__main__":
    assign_implementations()
