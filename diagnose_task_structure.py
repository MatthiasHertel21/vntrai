#!/usr/bin/env python3
"""
Test to identify the correct task structure for instructions and goals
"""

def test_task_structure_identification():
    """Test different task structures to understand where instructions/goals are stored"""
    
    # Test case 1: Instructions in ai_config
    task_with_ai_config = {
        'name': 'Test Task',
        'type': 'ai',
        'description': 'A test task',
        'ai_config': {
            'instructions': 'These are the task instructions',
            'goals': ['Goal 1', 'Goal 2']
        }
    }
    
    # Test case 2: Instructions at top level
    task_with_top_level = {
        'name': 'Test Task',
        'type': 'ai',
        'description': 'A test task',
        'instruction': 'These are the task instructions',
        'goals': ['Goal 1', 'Goal 2']
    }
    
    # Test case 3: Mixed structure
    task_mixed = {
        'name': 'Test Task',
        'type': 'ai',
        'description': 'A test task',
        'ai_config': {
            'instructions': 'AI config instructions',
            'system_prompt': 'System prompt text'
        },
        'instruction': 'Top level instruction',
        'goals': ['Top level goal']
    }
    
    print("Testing task structure extraction...")
    
    def extract_instructions_and_goals(task_def):
        """Extract instructions and goals from various possible locations"""
        instructions = []
        goals = []
        
        # Check top-level instruction/instructions
        if 'instruction' in task_def:
            instructions.append(('top-level instruction', task_def['instruction']))
        if 'instructions' in task_def:
            instructions.append(('top-level instructions', task_def['instructions']))
            
        # Check ai_config
        ai_config = task_def.get('ai_config', {})
        if 'instruction' in ai_config:
            instructions.append(('ai_config instruction', ai_config['instruction']))
        if 'instructions' in ai_config:
            instructions.append(('ai_config instructions', ai_config['instructions']))
        if 'system_prompt' in ai_config:
            instructions.append(('ai_config system_prompt', ai_config['system_prompt']))
            
        # Check goals
        if 'goals' in task_def:
            goals.append(('top-level goals', task_def['goals']))
        if 'goals' in ai_config:
            goals.append(('ai_config goals', ai_config['goals']))
            
        return instructions, goals
    
    # Test all task structures
    test_cases = [
        ('ai_config structure', task_with_ai_config),
        ('top-level structure', task_with_top_level),
        ('mixed structure', task_mixed)
    ]
    
    for name, task in test_cases:
        print(f"\n--- {name} ---")
        instructions, goals = extract_instructions_and_goals(task)
        print(f"Instructions found: {instructions}")
        print(f"Goals found: {goals}")
    
    return test_cases

if __name__ == "__main__":
    test_task_structure_identification()
