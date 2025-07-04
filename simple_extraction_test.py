#!/usr/bin/env python3
"""
Simple test for instructions and goals extraction
"""

import re

def resolve_variables(text: str, variables: dict) -> str:
    """Resolve {{variable}} placeholders in text with actual values"""
    if not text or not variables:
        return text
    
    pattern = r'\{\{([^}]+)\}\}'
    
    def replace_variable(match):
        var_name = match.group(1).strip()
        return str(variables.get(var_name, match.group(0)))
    
    return re.sub(pattern, replace_variable, text)

def extract_instructions_and_goals(task_def, task_inputs):
    """Extract instructions and goals with proper priority"""
    ai_config = task_def.get('ai_config', {})
    
    # Instructions priority: ai_config.instructions > instruction > instructions > ai_config.instruction  
    instructions_sources = [
        ('ai_config.instructions', ai_config.get('instructions', '')),
        ('top-level instruction', task_def.get('instruction', '')),
        ('top-level instructions', task_def.get('instructions', '')),
        ('ai_config.instruction', ai_config.get('instruction', ''))
    ]
    
    instruction = ''
    instruction_source = 'none'
    for source, instr in instructions_sources:
        if instr and instr.strip():
            instruction = resolve_variables(instr, task_inputs)
            instruction_source = source
            break
    
    # Goals priority: ai_config.goals > top-level goals
    goals_sources = [
        ('ai_config.goals', ai_config.get('goals', [])),
        ('top-level goals', task_def.get('goals', []))
    ]
    
    goals = []
    goals_source = 'none'
    for source, goal_list in goals_sources:
        if goal_list:
            goals = goal_list if isinstance(goal_list, list) else [goal_list]
            goals = [resolve_variables(str(goal), task_inputs) for goal in goals]
            goals_source = source
            break
    
    # System prompt
    system_prompt = ai_config.get('system_prompt', '')
    if system_prompt:
        system_prompt = resolve_variables(system_prompt, task_inputs)
    
    return {
        'instruction': instruction,
        'instruction_source': instruction_source,
        'goals': goals,
        'goals_source': goals_source,
        'system_prompt': system_prompt
    }

def main():
    print("=== Testing Instructions and Goals Extraction ===\n")
    
    # Test case 1: Instructions in ai_config.instructions
    task1 = {
        'name': 'AI Config Task',
        'ai_config': {
            'instructions': 'Instructions from ai_config.instructions',
            'goals': ['Goal 1 from ai_config', 'Goal 2 from ai_config'],
            'system_prompt': 'System prompt from ai_config'
        }
    }
    
    # Test case 2: Instructions at top level
    task2 = {
        'name': 'Top Level Task',
        'instruction': 'Top-level instruction',
        'goals': ['Top level goal 1', 'Top level goal 2']
    }
    
    # Test case 3: Multiple sources (priority test)
    task3 = {
        'name': 'Priority Test Task',
        'instruction': 'Top level instruction (should be ignored)',
        'ai_config': {
            'instructions': 'AI config instructions (should be used)',
            'goals': ['AI config goal (should be used)']
        },
        'goals': ['Top level goal (should be ignored)']
    }
    
    # Test case 4: Variable resolution
    task4 = {
        'name': 'Variable Task',
        'ai_config': {
            'instructions': 'Analyze {{topic}} with focus on {{aspect}}',
            'goals': ['Understand {{topic}}', 'Provide {{format}} output']
        }
    }
    
    inputs = {'topic': 'Python', 'aspect': 'OOP', 'format': 'markdown'}
    
    test_cases = [
        ('ai_config structure', task1, {}),
        ('top-level structure', task2, {}),
        ('priority test', task3, {}),
        ('variable resolution', task4, inputs)
    ]
    
    for name, task, task_inputs in test_cases:
        print(f"--- {name} ---")
        result = extract_instructions_and_goals(task, task_inputs)
        
        print(f"Instruction source: {result['instruction_source']}")
        print(f"Instruction: {result['instruction']}")
        print(f"Goals source: {result['goals_source']}")
        print(f"Goals: {result['goals']}")
        print(f"System prompt: {result['system_prompt']}")
        
        has_instruction = bool(result['instruction'])
        has_goals = bool(result['goals'])
        
        print(f"✅ Instructions found: {has_instruction}")
        print(f"✅ Goals found: {has_goals}")
        
        if not has_instruction:
            print("❌ WARNING: No instructions found!")
        if not has_goals:
            print("❌ WARNING: No goals found!")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
