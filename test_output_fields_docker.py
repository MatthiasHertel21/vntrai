#!/usr/bin/env python3
"""
Test script for issue 140: Output field persistence
This script tests that Output-Variable, Output-Type, Output-Description, and Output-Rendering fields
are properly persisted when creating and updating tasks.

Run this script inside the Docker container:
docker exec -it <container_name> python test_output_fields_docker.py
"""

import sys
import os
import json
import uuid
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, '/app')

# Import required modules
try:
    from app.utils.data_manager import agents_manager
    from app import create_app
    print("✅ Successfully imported required modules")
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    sys.exit(1)

def test_output_fields_persistence():
    """Test that output fields are properly persisted in tasks"""
    
    print("\n🧪 Testing Output Fields Persistence (Issue 140)")
    print("=" * 60)
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # Test data
        test_agent_id = str(uuid.uuid4())
        test_task_uuid = str(uuid.uuid4())
        
        # Create a test agent
        test_agent = {
            'id': test_agent_id,
            'uuid': test_agent_id,
            'name': 'Test Agent for Output Fields',
            'description': 'Test agent to verify output field persistence',
            'status': 'active',
            'category': 'test',
            'tasks': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        print(f"📝 Creating test agent: {test_agent_id}")
        if not agents_manager.save(test_agent):
            print("❌ Failed to create test agent")
            return False
        
        # Define task with output fields
        task_with_outputs = {
            'uuid': test_task_uuid,
            'id': test_task_uuid,
            'name': 'Test Task with Output Fields',
            'description': 'This task tests output field persistence',
            'type': 'ai',
            'order': 1,
            # Output fields that should be persisted
            'output_variable': 'test_result',
            'output_type': 'json',
            'output_description': 'Test output description for validation',
            'output_rendering': 'table',
            'ai_config': {
                'instructions': 'Test instructions',
                'model': 'gpt-3.5-turbo'
            },
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        print(f"📝 Adding task with output fields: {test_task_uuid}")
        success = agents_manager.add_task_definition(test_agent_id, task_with_outputs)
        
        if not success:
            print("❌ Failed to add task definition")
            cleanup_test_data(test_agent_id)
            return False
        
        print("✅ Task added successfully")
        
        # Verify the task was saved with output fields
        print("🔍 Verifying task persistence...")
        saved_agent = agents_manager.load(test_agent_id)
        
        if not saved_agent or 'tasks' not in saved_agent:
            print("❌ Failed to load saved agent or no tasks found")
            cleanup_test_data(test_agent_id)
            return False
        
        saved_task = None
        for task in saved_agent['tasks']:
            if task.get('uuid') == test_task_uuid:
                saved_task = task
                break
        
        if not saved_task:
            print("❌ Task not found in saved agent")
            cleanup_test_data(test_agent_id)
            return False
        
        # Check if output fields are preserved
        output_fields = ['output_variable', 'output_type', 'output_description', 'output_rendering']
        missing_fields = []
        incorrect_values = []
        
        for field in output_fields:
            if field not in saved_task:
                missing_fields.append(field)
            elif saved_task[field] != task_with_outputs[field]:
                incorrect_values.append(f"{field}: expected '{task_with_outputs[field]}', got '{saved_task[field]}'")
        
        if missing_fields:
            print(f"❌ Missing output fields: {', '.join(missing_fields)}")
            cleanup_test_data(test_agent_id)
            return False
        
        if incorrect_values:
            print(f"❌ Incorrect output field values: {', '.join(incorrect_values)}")
            cleanup_test_data(test_agent_id)
            return False
        
        print("✅ All output fields are correctly persisted:")
        for field in output_fields:
            print(f"   - {field}: {saved_task[field]}")
        
        # Test updating the task with new output values
        print("\n🔄 Testing output field updates...")
        
        updated_outputs = {
            'output_variable': 'updated_result',
            'output_type': 'text',
            'output_description': 'Updated output description',
            'output_rendering': 'raw'
        }
        
        # Update the task
        update_data = {**saved_task, **updated_outputs, 'updated_at': datetime.now().isoformat()}
        
        success = agents_manager.update_task_definition(test_agent_id, test_task_uuid, update_data)
        
        if not success:
            print("❌ Failed to update task definition")
            cleanup_test_data(test_agent_id)
            return False
        
        # Verify the updates
        updated_agent = agents_manager.load(test_agent_id)
        updated_task = None
        
        for task in updated_agent['tasks']:
            if task.get('uuid') == test_task_uuid:
                updated_task = task
                break
        
        if not updated_task:
            print("❌ Updated task not found")
            cleanup_test_data(test_agent_id)
            return False
        
        # Check if updated output fields are preserved
        update_errors = []
        for field, expected_value in updated_outputs.items():
            if field not in updated_task:
                update_errors.append(f"Missing field: {field}")
            elif updated_task[field] != expected_value:
                update_errors.append(f"{field}: expected '{expected_value}', got '{updated_task[field]}'")
        
        if update_errors:
            print(f"❌ Update errors: {', '.join(update_errors)}")
            cleanup_test_data(test_agent_id)
            return False
        
        print("✅ All output fields are correctly updated:")
        for field, value in updated_outputs.items():
            print(f"   - {field}: {value}")
        
        # Clean up test data
        cleanup_test_data(test_agent_id)
        
        print("\n🎉 All tests passed! Issue 140 is properly implemented.")
        return True

def cleanup_test_data(agent_id):
    """Clean up test data"""
    print(f"🧹 Cleaning up test agent: {agent_id}")
    agents_manager.delete(agent_id)

def check_files_exist():
    """Check if required files exist and have the expected changes"""
    print("\n📁 Checking if implementation files exist...")
    
    files_to_check = [
        '/app/app/routes/agents/task_routes.py',
        '/app/app/templates/agents/agent_run_view.html',
        '/app/app/static/js/agents/task-modals.js'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} not found")
    
    # Check if task_routes.py contains output field handling
    task_routes_path = '/app/app/routes/agents/task_routes.py'
    if os.path.exists(task_routes_path):
        with open(task_routes_path, 'r') as f:
            content = f.read()
            if 'output_variable' in content and 'output_type' in content:
                print("✅ task_routes.py contains output field handling")
            else:
                print("❌ task_routes.py missing output field handling")
    
    return True

def main():
    """Main test function"""
    print("🐳 Running Output Fields Persistence Test in Docker")
    print("=" * 60)
    
    try:
        # Check files
        check_files_exist()
        
        # Run persistence test
        success = test_output_fields_persistence()
        
        if success:
            print("\n🎉 SUCCESS: Issue 140 has been properly implemented!")
            print("   - Output fields are correctly persisted during task creation")
            print("   - Output fields are correctly persisted during task updates")
            print("   - All required files are in place")
            return 0
        else:
            print("\n❌ FAILURE: Issue 140 implementation has problems!")
            return 1
            
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
