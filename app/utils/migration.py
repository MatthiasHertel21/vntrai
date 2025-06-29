#!/usr/bin/env python3
"""
Migration Script für v036 Daten nach vntrai
Migriert Tools, Integrations und Vendor Icons von v036 in das neue Dateisystem
"""

import json
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class V036Migration:
    def __init__(self, v036_path: str, target_path: str):
        self.v036_path = Path(v036_path)
        self.target_path = Path(target_path)
        self.tools_source = self.v036_path / 'data' / 'tools.json'
        self.integrations_source = self.v036_path / 'data' / 'integrations.json'
        self.vendor_icons_source = self.v036_path / 'app' / 'static' / 'icons' / 'vendors'
        
        self.tools_target = self.target_path / 'data' / 'tools'
        self.integrations_target = self.target_path / 'data' / 'integrations'
        self.vendor_icons_target = self.target_path / 'app' / 'static' / 'images' / 'vendor_icons'
        
        self.migration_log = []
        
    def validate_sources(self):
        """Validiert, dass alle Quelldateien existieren"""
        missing = []
        if not self.tools_source.exists():
            missing.append(str(self.tools_source))
        if not self.integrations_source.exists():
            missing.append(str(self.integrations_source))
        if not self.vendor_icons_source.exists():
            missing.append(str(self.vendor_icons_source))
            
        if missing:
            raise FileNotFoundError(f"Quelldateien nicht gefunden: {', '.join(missing)}")
        
        logger.info("Alle Quelldateien gefunden")
        
    def create_target_directories(self):
        """Erstellt die Zielverzeichnisse"""
        self.tools_target.mkdir(parents=True, exist_ok=True)
        self.integrations_target.mkdir(parents=True, exist_ok=True)
        self.vendor_icons_target.mkdir(parents=True, exist_ok=True)
        logger.info("Zielverzeichnisse erstellt")
        
    def migrate_tools(self):
        """Migriert Tools von tools.json zu einzelnen JSON-Dateien"""
        logger.info("Starte Tool-Migration...")
        
        with open(self.tools_source, 'r', encoding='utf-8') as f:
            tools_data = json.load(f)
            
        migrated_count = 0
        
        for tool in tools_data:
            # Generiere UUID für Tool
            tool_id = str(uuid.uuid4())
            
            # Erstelle neues Tool-Schema (bereinigt)
            new_tool = {
                "id": tool_id,
                "name": tool.get("name", ""),
                "description": tool.get("description", ""),
                "tool_definition": tool.get("tool_definition", ""),
                "config": tool.get("config", {}),
                "prefilled_inputs": tool.get("prefilled_inputs", {}),
                "locked_inputs": tool.get("locked_inputs", []),
                "created_at": datetime.utcnow().isoformat() + "Z",
                "updated_at": datetime.utcnow().isoformat() + "Z",
                "status": "active",
                "last_test": tool.get("last_test")
            }
            
            # Speichere Tool als einzelne JSON-Datei
            tool_file = self.tools_target / f"{tool_id}.json"
            with open(tool_file, 'w', encoding='utf-8') as f:
                json.dump(new_tool, f, indent=2, ensure_ascii=False)
                
            migrated_count += 1
            self.migration_log.append({
                "type": "tool",
                "old_name": tool.get("name"),
                "new_id": tool_id,
                "file": str(tool_file)
            })
            
        logger.info(f"Tool-Migration abgeschlossen: {migrated_count} Tools migriert")
        
    def migrate_integrations(self):
        """Migriert Integrations von integrations.json zu einzelnen JSON-Dateien"""
        logger.info("Starte Integration-Migration...")
        
        with open(self.integrations_source, 'r', encoding='utf-8') as f:
            integrations_data = json.load(f)
            
        migrated_count = 0
        
        for integration in integrations_data:
            # Nutze existierende ID oder generiere neue UUID
            integration_id = integration.get("id", str(uuid.uuid4()))
            
            # Erstelle neues Integration-Schema (bereinigt, ohne "options")
            new_integration = {
                "id": integration_id,
                "name": integration.get("name", ""),
                "description": integration.get("description", ""),
                "vendor": integration.get("vendor", ""),
                "api_documentation_link": integration.get("api_documentation_link", ""),
                "config_params": integration.get("config_params", []),
                "input_params": integration.get("input_params", []),
                "output_params": integration.get("output_params", []),
                "created_at": datetime.utcnow().isoformat() + "Z",
                "updated_at": datetime.utcnow().isoformat() + "Z",
                "status": "active",
                "vendor_icon": self.find_vendor_icon(integration_id)
            }
            
            # Entferne "options" Feld falls vorhanden (Design-Entscheidung)
            if "options" in integration:
                logger.info(f"Entferne 'options' Feld aus Integration {integration.get('name')}")
            
            # Speichere Integration als einzelne JSON-Datei
            integration_file = self.integrations_target / f"{integration_id}.json"
            with open(integration_file, 'w', encoding='utf-8') as f:
                json.dump(new_integration, f, indent=2, ensure_ascii=False)
                
            migrated_count += 1
            self.migration_log.append({
                "type": "integration",
                "old_name": integration.get("name"),
                "new_id": integration_id,
                "file": str(integration_file)
            })
            
        logger.info(f"Integration-Migration abgeschlossen: {migrated_count} Integrations migriert")
        
    def find_vendor_icon(self, integration_id: str) -> str:
        """Findet das Vendor-Icon für eine Integration"""
        # Suche nach Icon-Datei mit Integration-ID
        for ext in ['.png', '.jpg', '.jpeg', '.svg']:
            icon_file = self.vendor_icons_source / f"{integration_id}{ext}"
            if icon_file.exists():
                return f"vendor_icons/{integration_id}{ext}"
        return "vendor_icons/default.png"
        
    def migrate_vendor_icons(self):
        """Migriert Vendor-Icons"""
        logger.info("Starte Vendor-Icon-Migration...")
        
        migrated_count = 0
        
        # Kopiere alle Vendor-Icons
        for icon_file in self.vendor_icons_source.iterdir():
            if icon_file.is_file() and icon_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.svg']:
                target_file = self.vendor_icons_target / icon_file.name
                shutil.copy2(icon_file, target_file)
                migrated_count += 1
                
                self.migration_log.append({
                    "type": "vendor_icon",
                    "old_file": str(icon_file),
                    "new_file": str(target_file)
                })
                
        # Kopiere Default-Icon falls nicht vorhanden
        default_icon = self.vendor_icons_target / "default.png"
        if not default_icon.exists():
            # Nutze ein vorhandenes Icon als Default oder erstelle Placeholder
            icons = list(self.vendor_icons_target.glob("*.png"))
            if icons:
                shutil.copy2(icons[0], default_icon)
                
        logger.info(f"Vendor-Icon-Migration abgeschlossen: {migrated_count} Icons migriert")
        
    def create_migration_report(self):
        """Erstellt einen Migrationsbericht"""
        report = {
            "migration_date": datetime.utcnow().isoformat() + "Z",
            "source_path": str(self.v036_path),
            "target_path": str(self.target_path),
            "summary": {
                "tools": len([log for log in self.migration_log if log["type"] == "tool"]),
                "integrations": len([log for log in self.migration_log if log["type"] == "integration"]),
                "vendor_icons": len([log for log in self.migration_log if log["type"] == "vendor_icon"])
            },
            "details": self.migration_log
        }
        
        report_file = self.target_path / "migration_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Migrationsbericht erstellt: {report_file}")
        return report
        
    def run_migration(self):
        """Führt die komplette Migration durch"""
        logger.info("Starte v036 Migration...")
        
        try:
            self.validate_sources()
            self.create_target_directories()
            self.migrate_tools()
            self.migrate_integrations()
            self.migrate_vendor_icons()
            report = self.create_migration_report()
            
            logger.info("Migration erfolgreich abgeschlossen!")
            logger.info(f"Migriert: {report['summary']['tools']} Tools, {report['summary']['integrations']} Integrations, {report['summary']['vendor_icons']} Icons")
            
            return True
            
        except Exception as e:
            logger.error(f"Migration fehlgeschlagen: {e}")
            return False

def main():
    """Main Migration Function"""
    v036_path = "/home/ga/fb1/age/v036"
    target_path = "/home/ga/fb1/age"
    
    migration = V036Migration(v036_path, target_path)
    success = migration.run_migration()
    
    if success:
        print("✅ Migration erfolgreich abgeschlossen!")
    else:
        print("❌ Migration fehlgeschlagen!")
        
    return success

if __name__ == "__main__":
    main()
