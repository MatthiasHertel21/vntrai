#!/usr/bin/env python3
"""
Direct test of build_context_prompt logic without Flask dependencies
"""

def resolve_variables(text: str, variables: dict) -> str:
    """Resolve {{variable}} placeholders in text with actual values"""
    if not text or not variables:
        return text
    
    import re
    pattern = r'\{\{([^}]+)\}\}'
    
    def replace_variable(match):
        var_name = match.group(1).strip()
        return str(variables.get(var_name, match.group(0)))
    
    return re.sub(pattern, replace_variable, text)

def log_info(message):
    """Simple logging replacement"""
    print(f"[LOG] {message}")

def build_context_prompt_test(task_def: dict, task_inputs: dict, agent: dict) -> str:
    """Test version of build_context_prompt function"""
    log_info(f"Building context prompt for task: {task_def.get('name', 'Unknown')}")
    log_info(f"Task inputs: {task_inputs}")
    log_info(f"Task definition keys: {list(task_def.keys())}")
    
    # Start with agent context
    agent_name = agent.get('name', 'AI Assistant')
    agent_description = agent.get('description', '')
    
    prompt_parts = [
        f"You are {agent_name}.",
        f"Agent Description: {agent_description}" if agent_description else "",
        "",
        f"Task: {task_def.get('name', 'Unnamed Task')}",
        f"Task Description: {task_def.get('description', 'No description provided')}",
        ""
    ]
    
    # Add task instructions from multiple possible locations
    ai_config = task_def.get('ai_config', {})
    
    # Check for instructions in multiple locations (priority order)
    instructions_sources = [
        ('ai_config.instructions', ai_config.get('instructions', '')),
        ('top-level instruction', task_def.get('instruction', '')),
        ('top-level instructions', task_def.get('instructions', '')),
        ('ai_config.instruction', ai_config.get('instruction', ''))
    ]
    
    task_instruction = ''
    instruction_source = 'none'
    for source, instruction in instructions_sources:
        if instruction and instruction.strip():
            task_instruction = instruction
            instruction_source = source
            break
    
    log_info(f"Task instruction found from {instruction_source}: {bool(task_instruction)}")
    if task_instruction:
        log_info(f"Original instruction: {task_instruction}")
        # Resolve {{variables}} in instruction with input values
        resolved_instruction = resolve_variables(task_instruction, task_inputs)
        log_info(f"Resolved instruction: {resolved_instruction}")
        prompt_parts.extend([
            "Task Instructions:",
            resolved_instruction,
            ""
        ])
    
    # Add task goals from multiple possible locations
    goals_sources = [
        ('ai_config.goals', ai_config.get('goals', [])),
        ('top-level goals', task_def.get('goals', []))
    ]
    
    task_goals = []
    goals_source = 'none'
    for source, goals in goals_sources:
        if goals:
            task_goals = goals if isinstance(goals, list) else [goals]
            goals_source = source
            break
    
    log_info(f"Task goals found from {goals_source}: {len(task_goals)} goals")
    if task_goals:
        prompt_parts.append("Goals:")
        for i, goal in enumerate(task_goals):
            log_info(f"Original goal {i}: {goal}")
            # Resolve variables in each goal
            resolved_goal = resolve_variables(str(goal), task_inputs)
            log_info(f"Resolved goal {i}: {resolved_goal}")
            prompt_parts.append(f"- {resolved_goal}")
        prompt_parts.append("")
    
    # Add AI configuration system prompt if available
    if ai_config.get('system_prompt'):
        log_info(f"System prompt found in ai_config: {bool(ai_config.get('system_prompt'))}")
        # Resolve variables in system prompt
        resolved_system_prompt = resolve_variables(ai_config['system_prompt'], task_inputs)
        prompt_parts.extend([
            "System Instructions:",
            resolved_system_prompt,
            ""
        ])
    
    prompt_parts.append("Please provide your response based on the above information.")
    
    final_prompt = "\n".join(filter(None, prompt_parts))
    log_info(f"Final prompt length: {len(final_prompt)} characters")
    return final_prompt

def test_instructions_goals_extraction():
    """Test that instructions and goals are properly extracted from various task structures"""
    
    # Test case 1: Instructions in ai_config.instructions
    task_ai_config_instructions = {
        'name': 'AI Config Task',
        'type': 'ai',
        'description': 'Task with instructions in ai_config',
        'ai_config': {
            'instructions': 'These are instructions from ai_config.instructions',
            'goals': ['AI Config Goal 1', 'AI Config Goal 2'],
            'system_prompt': 'System prompt from ai_config'
        }
    }
    
    # Test case 2: Instructions at top level
    task_top_level = {
        'name': 'Top Level Task',
        'type': 'ai',
        'description': 'Task with top-level instructions',
        'instruction': 'These are top-level instructions',
        'goals': ['Top Level Goal 1', 'Top Level Goal 2']
    }
    
    # Test case 3: Multiple instruction sources (should prioritize ai_config.instructions)
    task_multiple_sources = {
        'name': 'Multiple Sources Task',
        'type': 'ai',
        'description': 'Task with multiple instruction sources',
        'instruction': 'Top level instruction (should be ignored)',
        'ai_config': {
            'instructions': 'AI config instructions (should be used)',
            'goals': ['AI config goals (should be used)'],
            'system_prompt': 'AI config system prompt'
        },
        'goals': ['Top level goals (should be ignored)']
    }
    
    # Test case 4: Variable resolution in instructions and goals
    task_with_variables = {
        'name': 'Variable Task',
        'type': 'ai',
        'description': 'Task with variables in instructions and goals',
        'ai_config': {
            'instructions': 'Analyze the {{topic}} with focus on {{aspect}}',
            'goals': ['Understand {{topic}} thoroughly', 'Provide {{output_format}} response']
        }
    }
    
    # Sample inputs for variable resolution
    task_inputs = {
        'topic': 'Python programming',
        'aspect': 'object-oriented design',
        'output_format': 'markdown'
    }
    
    # Sample agent
    agent = {
        'name': 'Test Agent',
        'description': 'A test agent for instruction/goals testing'
    }
    
    test_cases = [
        ('ai_config.instructions', task_ai_config_instructions, {}),
        ('top-level instruction', task_top_level, {}),
        ('multiple sources (priority test)', task_multiple_sources, {}),
        ('variable resolution', task_with_variables, task_inputs)
    ]
    
    print("=== Testing Instructions and Goals Extraction ===\n")
    
    for test_name, task_def, inputs in test_cases:
        print(f"--- {test_name} ---")
        print(f"Task structure keys: {list(task_def.keys())}")
        if 'ai_config' in task_def:
            print(f"AI config keys: {list(task_def['ai_config'].keys())}")
        print(f"Task inputs: {inputs}")
        
        try:
            prompt = build_context_prompt_test(task_def, inputs, agent)
            
            print(f"\nGenerated prompt:")
            print("=" * 60)
            print(prompt)
            print("=" * 60)
            
            # Check if instructions are included
            has_instructions = ('Task Instructions:' in prompt or 'System Instructions:' in prompt)
            has_goals = 'Goals:' in prompt
            
            print(f"\n✅ Instructions included: {has_instructions}")
            print(f"✅ Goals included: {has_goals}")
            
            if not has_instructions:
                print("❌ WARNING: No instructions found in prompt!")
            if not has_goals:
                print("❌ WARNING: No goals found in prompt!")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_instructions_goals_extraction()
