#!/usr/bin/env python3
"""
Comprehensive test for instructions and goals extraction in build_context_prompt
"""
import sys
import os
sys.path.append('/home/ga/fb1/age')

from app.routes.agents.streaming_api import build_context_prompt, resolve_variables

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
        print(f"Task structure: {task_def}")
        print(f"Task inputs: {inputs}")
        
        try:
            prompt = build_context_prompt(task_def, inputs, agent)
            
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
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_instructions_goals_extraction()
