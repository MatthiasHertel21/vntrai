"""
File Operations Utilities für vntrai Data Management
Handles JSON file operations for integrations and tools
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

class DataManager:
    """Base class for data management operations"""
    
    def __init__(self, data_type: str):
        self.data_type = data_type  # 'integrations' or 'tools'
        self.data_dir = Path(__file__).parent.parent.parent / "data" / data_type
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def get_all_ids(self) -> List[str]:
        """Get all item IDs"""
        return [f.stem for f in self.data_dir.glob("*.json")]
    
    def exists(self, item_id: str) -> bool:
        """Check if item exists"""
        return (self.data_dir / f"{item_id}.json").exists()
    
    def load(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Load single item by ID"""
        file_path = self.data_dir / f"{item_id}.json"
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading {self.data_type} {item_id}: {e}")
            return None
    
    def load_all(self) -> List[Dict[str, Any]]:
        """Load all items"""
        items = []
        for file_path in self.data_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    item = json.load(f)
                    items.append(item)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading {file_path}: {e}")
                continue
        
        return sorted(items, key=lambda x: x.get('name', ''))
    
    def save(self, item: Dict[str, Any]) -> bool:
        """Save single item"""
        item_id = item.get('id')
        if not item_id:
            item_id = str(uuid.uuid4())
            item['id'] = item_id
        
        # Update timestamp
        item['updated_at'] = datetime.now().isoformat()
        if 'created_at' not in item:
            item['created_at'] = item['updated_at']
        
        file_path = self.data_dir / f"{item_id}.json"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(item, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving {self.data_type} {item_id}: {e}")
            return False
    
    def delete(self, item_id: str) -> bool:
        """Delete single item"""
        file_path = self.data_dir / f"{item_id}.json"
        if not file_path.exists():
            return False
        
        try:
            file_path.unlink()
            return True
        except IOError as e:
            print(f"Error deleting {self.data_type} {item_id}: {e}")
            return False
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all items - alias for load_all"""
        return self.load_all()
    
    def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get item by ID - alias for load"""
        return self.load(item_id)
    
    def create(self, data: Dict[str, Any]) -> bool:
        """Create new item with provided data"""
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow().isoformat() + 'Z'
        
        data['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        
        return self.save(data)
    
    def update(self, item_id: str, data: Dict[str, Any]) -> bool:
        """Update existing item"""
        data['id'] = item_id  # Ensure ID is set
        data['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        
        return self.save(data)
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search items by query"""
        all_items = self.load_all()
        query_lower = query.lower()
        
        results = []
        for item in all_items:
            # Search in name, description, and vendor (if exists)
            searchable_text = (
                item.get('name', '').lower() + ' ' +
                item.get('description', '').lower() + ' ' +
                item.get('vendor', '').lower() + ' ' +
                item.get('tool_definition', '').lower()
            )
            
            if query_lower in searchable_text:
                results.append(item)
        
        return results

    def filter_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Filter items by status"""
        all_items = self.load_all()
        return [item for item in all_items if item.get('status') == status]
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about items"""
        all_items = self.load_all()
        
        stats = {
            'total': len(all_items),
            'active': 0,
            'inactive': 0,
            'other': 0
        }
        
        for item in all_items:
            status = item.get('status', 'unknown')
            if status == 'active':
                stats['active'] += 1
            elif status == 'inactive':
                stats['inactive'] += 1
            else:
                stats['other'] += 1
        
        return stats


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


class ToolsManager(DataManager):
    """Manager for tools data"""
    
    def __init__(self):
        super().__init__('tools')
    
    def create_tool(self, name: str, category: str = 'utility', tool_type: str = 'script') -> Dict[str, Any]:
        """Create new tool with defaults"""
        tool = {
            'id': str(uuid.uuid4()),
            'name': name,
            'category': category,
            'type': tool_type,
            'description': '',
            'status': 'inactive',
            'executable': '',
            'arguments': [],
            'environment': {},
            'config': {},
            'dependencies': [],
            'version': '1.0.0',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        if self.save(tool):
            return tool
        return None
    
    def filter_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Filter tools by category"""
        all_tools = self.load_all()
        return [item for item in all_tools if item.get('category') == category]
    
    def filter_by_type(self, tool_type: str) -> List[Dict[str, Any]]:
        """Filter tools by type"""
        all_tools = self.load_all()
        return [item for item in all_tools if item.get('type') == tool_type]
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        all_tools = self.load_all()
        categories = set(tool.get('category', 'utility') for tool in all_tools)
        return sorted(list(categories))


class IconManager:
    """Manager for vendor icons"""
    
    def __init__(self):
        self.icons_dir = Path(__file__).parent.parent / "static" / "icons" / "vendors"
        self.icons_dir.mkdir(parents=True, exist_ok=True)
    
    def get_icon_path(self, integration_id: str) -> Optional[str]:
        """Get icon path for integration"""
        # Check for various formats
        for ext in ['.png', '.jpg', '.jpeg', '.svg']:
            icon_path = self.icons_dir / f"{integration_id}{ext}"
            if icon_path.exists():
                return f"/static/icons/vendors/{integration_id}{ext}"
        
        return None
    
    def has_icon(self, integration_id: str) -> bool:
        """Check if integration has an icon"""
        return self.get_icon_path(integration_id) is not None
    
    def save_icon(self, integration_id: str, file_data: bytes, filename: str) -> bool:
        """Save icon file"""
        # Get file extension
        ext = Path(filename).suffix.lower()
        if ext not in ['.png', '.jpg', '.jpeg', '.svg']:
            return False
        
        icon_path = self.icons_dir / f"{integration_id}{ext}"
        try:
            with open(icon_path, 'wb') as f:
                f.write(file_data)
            return True
        except IOError:
            return False
    
    def delete_icon(self, integration_id: str) -> bool:
        """Delete icon file"""
        for ext in ['.png', '.jpg', '.jpeg', '.svg']:
            icon_path = self.icons_dir / f"{integration_id}{ext}"
            if icon_path.exists():
                try:
                    icon_path.unlink()
                    return True
                except IOError:
                    pass
        return False


# Global instances
integrations_manager = IntegrationsManager()
tools_manager = ToolsManager()
icon_manager = IconManager()
