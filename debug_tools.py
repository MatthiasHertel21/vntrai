#!/usr/bin/env python3
"""
Debug script for tools page
"""
import sys
import os
import json
from pathlib import Path

# Add app to path
sys.path.insert(0, '/app')

def test_tools_loading():
    """Test tools loading directly"""
    print("=== Tools Loading Debug ===")
    
    # Check if data directory exists
    data_dir = Path('/app/data')
    print(f"Data directory: {data_dir}")
    print(f"Data directory exists: {data_dir.exists()}")
    
    tools_dir = data_dir / 'tools'
    print(f"Tools directory: {tools_dir}")
    print(f"Tools directory exists: {tools_dir.exists()}")
    
    if tools_dir.exists():
        json_files = list(tools_dir.glob('*.json'))
        print(f"JSON files found: {len(json_files)}")
        
        if json_files:
            print("Files:")
            for i, file in enumerate(json_files[:3]):  # Show first 3
                print(f"  {i+1}. {file.name}")
                
            # Try to load first file
            try:
                with open(json_files[0], 'r') as f:
                    data = json.load(f)
                    print(f"First file loaded successfully:")
                    print(f"  Name: {data.get('name', 'No name')}")
                    print(f"  UUID: {data.get('uuid', 'No UUID')}")
                    print(f"  Tool Definition: {data.get('tool_definition', 'No tool_definition')}")
            except Exception as e:
                print(f"Error loading first file: {e}")
    
    print()
    
    # Test DataManager import
    try:
        from app.utils.data_manager import ToolsManager
        print("✓ ToolsManager imported successfully")
        
        tm = ToolsManager()
        print(f"ToolsManager data_dir: {tm.data_dir}")
        print(f"ToolsManager data_dir exists: {tm.data_dir.exists()}")
        
        tools = tm.get_all()
        print(f"Tools loaded by ToolsManager: {len(tools)}")
        
        if tools:
            tool = tools[0]
            print(f"First tool: {tool.get('name', 'No name')}")
        
    except Exception as e:
        print(f"Error importing/using ToolsManager: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tools_loading()
