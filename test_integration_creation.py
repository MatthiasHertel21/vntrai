#!/usr/bin/env python3
"""
Test Script: Neue Integration anlegen
Testet die Integration-Erstellung über die DataManager-API
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.utils.data_manager import IntegrationsManager

def test_integration_creation():
    """Test der Integration-Erstellung"""
    
    print("🧪 Testing Integration Creation...")
    
    # Initialize manager
    integrations_manager = IntegrationsManager()
    
    # Test 1: Create new integration
    print("\n1. Creating new test integration...")
    test_integration = integrations_manager.create_integration(
        name="Test Integration",
        vendor="Test Vendor",
        integration_type="api"
    )
    
    if test_integration:
        print(f"✅ Integration created successfully: {test_integration['id']}")
        print(f"   Name: {test_integration['name']}")
        print(f"   Vendor: {test_integration['vendor']}")
        print(f"   Type: {test_integration['type']}")
        print(f"   Has config_params: {'config_params' in test_integration}")
        print(f"   Has input_params: {'input_params' in test_integration}")
        print(f"   Has output_params: {'output_params' in test_integration}")
        
        # Test 2: Load the created integration
        print("\n2. Loading created integration...")
        loaded_integration = integrations_manager.load(test_integration['id'])
        
        if loaded_integration:
            print("✅ Integration loaded successfully")
            print(f"   Config params: {len(loaded_integration.get('config_params', []))}")
            print(f"   Input params: {len(loaded_integration.get('input_params', []))}")
            print(f"   Output params: {len(loaded_integration.get('output_params', []))}")
        else:
            print("❌ Failed to load created integration")
        
        # Test 3: Update integration with v036 data
        print("\n3. Updating integration with v036 format data...")
        loaded_integration['config_params'] = [
            {
                "name": "api_key",
                "type": "text",
                "required": True,
                "description": "API Key for authentication"
            }
        ]
        loaded_integration['input_params'] = [
            {
                "name": "message",
                "type": "text",
                "required": True,
                "description": "Message to process"
            }
        ]
        loaded_integration['output_params'] = [
            {
                "name": "result",
                "type": "text",
                "description": "Processing result"
            }
        ]
        
        if integrations_manager.save(loaded_integration):
            print("✅ Integration updated with v036 data")
        else:
            print("❌ Failed to update integration")
        
        # Test 4: Verify final state
        print("\n4. Verifying final state...")
        final_integration = integrations_manager.load(test_integration['id'])
        
        if final_integration:
            print("✅ Final verification successful")
            print(f"   Config params count: {len(final_integration.get('config_params', []))}")
            print(f"   Input params count: {len(final_integration.get('input_params', []))}")
            print(f"   Output params count: {len(final_integration.get('output_params', []))}")
            
            # Show actual content
            print(f"\n   Config params: {final_integration.get('config_params', [])}")
            print(f"   Input params: {final_integration.get('input_params', [])}")
            print(f"   Output params: {final_integration.get('output_params', [])}")
        else:
            print("❌ Final verification failed")
        
        # Clean up (optional - comment out to keep test data)
        print(f"\n5. Cleaning up test integration {test_integration['id']}...")
        if integrations_manager.delete(test_integration['id']):
            print("✅ Test integration deleted")
        else:
            print("❌ Failed to delete test integration")
    
    else:
        print("❌ Failed to create integration")
        return False
    
    print("\n🎉 Integration creation test completed!")
    return True

if __name__ == "__main__":
    test_integration_creation()
