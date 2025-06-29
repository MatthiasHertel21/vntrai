#!/usr/bin/env python3
"""
Debug-Script für Google Sheets Implementation Problem
"""

import sys
import os
import traceback

# Add the project root to Python path
sys.path.insert(0, '/home/ga/fb1/age')

def debug_google_sheets():
    print("=== Google Sheets Implementation Debug ===")
    
    try:
        # Test 1: Import base modules
        print("1. Testing base imports...")
        from app.implementation_modules import ImplementationManager
        from app.implementation_modules.base_implementation import ImplementationRegistry
        print("   ✓ Base modules imported successfully")
        
        # Test 2: Check available implementations
        print("2. Checking available implementations...")
        available = ImplementationRegistry.list_implementations()
        print(f"   Available implementations: {available}")
        
        # Test 3: Try to get Google Sheets implementation
        print("3. Testing Google Sheets implementation...")
        try:
            google_impl_class = ImplementationRegistry.get_implementation('google_sheets')
            if google_impl_class:
                print(f"   ✓ Google Sheets implementation found: {google_impl_class}")
                
                # Test creating instance
                instance = google_impl_class()
                print(f"   ✓ Instance created: {instance.name}")
                print(f"   Description: {instance.description}")
                
                # Test validation
                validation = instance.validate_config()
                print(f"   Validation result: {validation}")
                
            else:
                print("   ✗ Google Sheets implementation not found")
        except Exception as e:
            print(f"   ✗ Error getting Google Sheets implementation: {e}")
            traceback.print_exc()
        
        # Test 4: Try ImplementationManager
        print("4. Testing ImplementationManager...")
        manager = ImplementationManager()
        available_manager = manager.list_implementations()
        print(f"   Manager implementations: {available_manager}")
        
        try:
            google_instance = manager.get_implementation('google_sheets')
            print(f"   ✓ Manager found Google Sheets: {google_instance}")
        except Exception as e:
            print(f"   ✗ Manager error: {e}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_google_sheets()
