#!/usr/bin/env python3
"""
Migration Script für v036 Daten nach vntrai
Migriert Integrations und Tools von v036 JSON-Format in neue Einzeldatei-Struktur
Kann mit python3 oder über Docker ausgeführt werden
"""

import json
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path

class V036DataMigrator:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.project_root = self.script_dir.parent
        self.v036_dir = self.project_root / "v036"
        self.data_dir = self.project_root / "data"
        self.integrations_dir = self.data_dir / "integrations"
        self.tools_dir = self.data_dir / "tools"
        self.icons_dir = self.project_root / "app" / "static" / "icons"
        
        # Migration Log
        self.migration_log = {
            "timestamp": datetime.now().isoformat(),
            "integrations": {
                "source_count": 0,
                "migrated_count": 0,
                "failed": []
            },
            "tools": {
                "source_count": 0,
                "migrated_count": 0,
                "failed": []
            },
            "icons": {
                "copied_count": 0,
                "failed": []
            }
        }
    
    def ensure_directories(self):
        """Erstellt alle notwendigen Verzeichnisse"""
        dirs = [
            self.integrations_dir,
            self.tools_dir,
            self.icons_dir / "vendors"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Directory ensured: {dir_path}")
    
    def load_v036_data(self):
        """Lädt die Original-Daten aus v036"""
        integrations_file = self.v036_dir / "data" / "integrations.json"
        tools_file = self.v036_dir / "data" / "tools.json"
        
        integrations = []
        tools = []
        
        if integrations_file.exists():
            with open(integrations_file, 'r', encoding='utf-8') as f:
                integrations = json.load(f)
                self.migration_log["integrations"]["source_count"] = len(integrations)
                print(f"✓ Loaded {len(integrations)} integrations from v036")
        else:
            print(f"⚠ No integrations file found at {integrations_file}")
        
        if tools_file.exists():
            with open(tools_file, 'r', encoding='utf-8') as f:
                tools = json.load(f)
                self.migration_log["tools"]["source_count"] = len(tools)
                print(f"✓ Loaded {len(tools)} tools from v036")
        else:
            print(f"⚠ No tools file found at {tools_file}")
        
        return integrations, tools
    
    def migrate_integration(self, integration):
        """Migriert eine einzelne Integration"""
        try:
            # Generate UUID if not present
            integration_id = integration.get('id', str(uuid.uuid4()))
            
            # Transform data structure (remove 'options' field if present)
            migrated_integration = {
                "id": integration_id,
                "name": integration.get("name", "Unnamed Integration"),
                "vendor": integration.get("vendor", "unknown"),
                "type": integration.get("type", "api"),
                "description": integration.get("description", ""),
                "status": integration.get("status", "inactive"),
                "config": integration.get("config", {}),
                "auth": integration.get("auth", {}),
                "endpoints": integration.get("endpoints", {}),
                "version": integration.get("version", "1.0.0"),
                "created_at": integration.get("created_at", datetime.now().isoformat()),
                "updated_at": datetime.now().isoformat(),
                "metadata": {
                    "migrated_from": "v036",
                    "migration_date": datetime.now().isoformat(),
                    "original_data": integration
                }
            }
            
            # Save to individual file
            file_path = self.integrations_dir / f"{integration_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(migrated_integration, f, indent=2, ensure_ascii=False)
            
            self.migration_log["integrations"]["migrated_count"] += 1
            print(f"✓ Migrated integration: {integration.get('name', integration_id)}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to migrate integration {integration.get('id', 'unknown')}: {str(e)}"
            self.migration_log["integrations"]["failed"].append(error_msg)
            print(f"✗ {error_msg}")
            return False
    
    def migrate_tool(self, tool):
        """Migriert ein einzelnes Tool"""
        try:
            # Generate UUID if not present
            tool_id = tool.get('id', str(uuid.uuid4()))
            
            # Transform data structure
            migrated_tool = {
                "id": tool_id,
                "name": tool.get("name", "Unnamed Tool"),
                "category": tool.get("category", "utility"),
                "type": tool.get("type", "script"),
                "description": tool.get("description", ""),
                "status": tool.get("status", "inactive"),
                "executable": tool.get("executable", ""),
                "arguments": tool.get("arguments", []),
                "environment": tool.get("environment", {}),
                "config": tool.get("config", {}),
                "dependencies": tool.get("dependencies", []),
                "version": tool.get("version", "1.0.0"),
                "created_at": tool.get("created_at", datetime.now().isoformat()),
                "updated_at": datetime.now().isoformat(),
                "metadata": {
                    "migrated_from": "v036",
                    "migration_date": datetime.now().isoformat(),
                    "original_data": tool
                }
            }
            
            # Save to individual file
            file_path = self.tools_dir / f"{tool_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(migrated_tool, f, indent=2, ensure_ascii=False)
            
            self.migration_log["tools"]["migrated_count"] += 1
            print(f"✓ Migrated tool: {tool.get('name', tool_id)}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to migrate tool {tool.get('id', 'unknown')}: {str(e)}"
            self.migration_log["tools"]["failed"].append(error_msg)
            print(f"✗ {error_msg}")
            return False
    
    def migrate_icons(self):
        """Migriert Vendor Icons aus v036"""
        v036_icons_dir = self.v036_dir / "app" / "static" / "icons" / "vendors"
        target_icons_dir = self.icons_dir / "vendors"
        
        if not v036_icons_dir.exists():
            print(f"⚠ No vendor icons directory found at {v036_icons_dir}")
            return
        
        for icon_file in v036_icons_dir.glob("*"):
            if icon_file.is_file():
                try:
                    target_file = target_icons_dir / icon_file.name
                    shutil.copy2(icon_file, target_file)
                    self.migration_log["icons"]["copied_count"] += 1
                    print(f"✓ Copied icon: {icon_file.name}")
                except Exception as e:
                    error_msg = f"Failed to copy icon {icon_file.name}: {str(e)}"
                    self.migration_log["icons"]["failed"].append(error_msg)
                    print(f"✗ {error_msg}")
    
    def save_migration_log(self):
        """Speichert das Migration-Log"""
        log_file = self.project_root / "migration" / "migration_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.migration_log, f, indent=2, ensure_ascii=False)
        print(f"✓ Migration log saved to {log_file}")
    
    def print_summary(self):
        """Druckt eine Zusammenfassung der Migration"""
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        
        # Integrations
        int_stats = self.migration_log["integrations"]
        print(f"Integrations: {int_stats['migrated_count']}/{int_stats['source_count']} migrated")
        if int_stats['failed']:
            print(f"  Failed: {len(int_stats['failed'])}")
        
        # Tools
        tool_stats = self.migration_log["tools"]
        print(f"Tools: {tool_stats['migrated_count']}/{tool_stats['source_count']} migrated")
        if tool_stats['failed']:
            print(f"  Failed: {len(tool_stats['failed'])}")
        
        # Icons
        icon_stats = self.migration_log["icons"]
        print(f"Icons: {icon_stats['copied_count']} copied")
        if icon_stats['failed']:
            print(f"  Failed: {len(icon_stats['failed'])}")
        
        print("="*60)
    
    def run_migration(self):
        """Führt die komplette Migration durch"""
        print("Starting v036 Data Migration...")
        print("="*60)
        
        # 1. Ensure directories
        self.ensure_directories()
        
        # 2. Load v036 data
        integrations, tools = self.load_v036_data()
        
        # 3. Migrate integrations
        print(f"\nMigrating {len(integrations)} integrations...")
        for integration in integrations:
            self.migrate_integration(integration)
        
        # 4. Migrate tools
        print(f"\nMigrating {len(tools)} tools...")
        for tool in tools:
            self.migrate_tool(tool)
        
        # 5. Migrate icons
        print(f"\nMigrating vendor icons...")
        self.migrate_icons()
        
        # 6. Save log and print summary
        self.save_migration_log()
        self.print_summary()

def main():
    """Main entry point"""
    try:
        migrator = V036DataMigrator()
        migrator.run_migration()
        print("\n✓ Migration completed successfully!")
        return 0
    except Exception as e:
        print(f"\n✗ Migration failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
