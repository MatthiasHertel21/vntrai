"""
Icon Manager for vendor icons
Handles storage and retrieval of vendor icon files
"""

from pathlib import Path
from typing import Optional

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

# Global instance
icon_manager = IconManager()
