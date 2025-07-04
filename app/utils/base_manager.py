"""
Base Data Manager for vntrai Data Management
Contains the base DataManager class with common functionality
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
        self.data_type = data_type  # 'integrations', 'tools', 'agents', 'agentrun'
        
        # Try to use Flask app config if available, otherwise use relative path
        try:
            from flask import current_app
            self.data_dir = Path(current_app.config.get('DATA_DIR', '/app/data')) / data_type
        except (ImportError, RuntimeError):
            # Fallback for when not in Flask app context
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
