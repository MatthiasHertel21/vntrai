"""
Integrations Manager for vntrai Data Management
Handles integrations data operations
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from .base_manager import DataManager

class IntegrationsManager(DataManager):
    """Manager for integrations data"""
    
    def __init__(self):
        super().__init__('integrations')
    
    def create_integration(self, name: str, vendor: str, integration_type: str = 'api') -> Dict[str, Any]:
        """Create new integration with v036 format"""
        integration = {
            'id': str(uuid.uuid4()),
            'name': name,
            'vendor': vendor,
            'type': integration_type,
            'description': '',
            'status': 'inactive',
            'config_params': [],
            'input_params': [],
            'output_params': [],
            'api_documentation_link': '',
            'vendor_icon': '',
            'version': '1.0.0',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        if self.save(integration):
            return integration
        return None
    
    def filter_by_vendor(self, vendor: str) -> List[Dict[str, Any]]:
        """Filter integrations by vendor"""
        all_integrations = self.load_all()
        return [item for item in all_integrations if item.get('vendor', '').lower() == vendor.lower()]
    
    def filter_by_type(self, integration_type: str) -> List[Dict[str, Any]]:
        """Filter integrations by type"""
        all_integrations = self.load_all()
        return [item for item in all_integrations if item.get('type') == integration_type]
    
    def get_by_implementation(self, implementation: str) -> Optional[Dict[str, Any]]:
        """Get integration by implementation type"""
        all_integrations = self.load_all()
        for integration in all_integrations:
            if integration.get('implementation') == implementation:
                return integration
        return None

# Global instance
integrations_manager = IntegrationsManager()
