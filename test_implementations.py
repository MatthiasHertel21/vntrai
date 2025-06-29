#!/usr/bin/env python3
"""
Test-Script für Implementation Modules
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, '/home/ga/fb1/age')

try:
    from app.implementation_modules import implementation_manager
    from app.implementation_modules.base_implementation import ImplementationRegistry
    
    print("=== Implementation Modules Test ===")
    
    # Liste alle registrierten Implementationen
    implementations = ImplementationRegistry.list_implementations()
    print(f"Registrierte Implementationen: {len(implementations)}")
    
    for impl_name in implementations:
        print(f"  - {impl_name}")
    
    # Prüfe spezifisch Google Sheets
    if 'google_sheets' in implementations:
        print("✓ Google Sheets Implementation ist registriert")
        
        # Versuche eine Instanz zu erstellen
        try:
            impl = ImplementationRegistry.get_implementation('google_sheets')
            print(f"✓ Google Sheets Implementation kann instanziiert werden: {impl}")
            print(f"  Name: {impl.name}")
            print(f"  Description: {impl.description}")
        except Exception as e:
            print(f"✗ Fehler beim Instanziieren: {e}")
    else:
        print("✗ Google Sheets Implementation ist NICHT registriert")
    
    # Prüfe auch OpenAI
    if 'openai_chatcompletion' in implementations:
        print("✓ OpenAI ChatCompletion Implementation ist registriert")
    else:
        print("✗ OpenAI ChatCompletion Implementation ist NICHT registriert")
        
except Exception as e:
    print(f"Fehler beim Testen der Implementationen: {e}")
    import traceback
    traceback.print_exc()
