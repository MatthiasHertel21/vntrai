#!/usr/bin/env python3
"""
Test output rendering inclusion in Docker container
"""
import sys
import os
sys.path.append('/home/ga/fb1/age')

def test_context_prompt_output_rendering():
    """Test that output rendering is included in context prompt"""
    
    # Import the function we want to test
    try:
        from app.routes.agents.streaming_api import build_context_prompt
        print("✅ Successfully imported build_context_prompt")
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        return
    
    # Test task with output rendering
    task_def = {
        'name': 'Test Task',
        'type': 'ai',
        'description': 'Task with output rendering',
        'output_type': 'html',
        'output_description': 'Generate formatted HTML',
        'output_rendering': 'Use proper HTML structure with semantic tags. Include CSS classes: .header, .content, .footer',
        'output_variable': 'html_result',
        'ai_config': {
            'instructions': 'Create well-formatted HTML content',
            'goals': ['Generate semantic HTML', 'Include proper CSS classes']
        }
    }
    
    task_inputs = {}
    agent = {
        'name': 'HTML Generator',
        'description': 'Specialized in creating HTML content'
    }
    
    print("\n=== Testing Output Rendering in Context Prompt ===")
    print(f"Task: {task_def['name']}")
    print(f"Output Type: {task_def['output_type']}")
    print(f"Output Rendering: {task_def['output_rendering']}")
    
    try:
        prompt = build_context_prompt(task_def, task_inputs, agent)
        
        print("\n--- Generated Context Prompt ---")
        print(prompt)
        print("--- End of Prompt ---")
        
        # Check if output rendering is included
        has_output_requirements = 'Output Requirements:' in prompt
        has_rendering_instructions = 'Rendering Instructions:' in prompt
        has_output_rendering_content = 'CSS classes' in prompt
        
        print(f"\n✅ Output Requirements section: {has_output_requirements}")
        print(f"✅ Rendering Instructions: {has_rendering_instructions}")
        print(f"✅ Rendering content included: {has_output_rendering_content}")
        
        if not has_output_requirements:
            print("❌ ERROR: Output Requirements section missing!")
        if not has_rendering_instructions:
            print("❌ ERROR: Rendering Instructions missing!")
        if not has_output_rendering_content:
            print("❌ ERROR: Actual rendering content missing!")
            
        if has_output_requirements and has_rendering_instructions and has_output_rendering_content:
            print("🎉 SUCCESS: Output rendering is properly included in context prompt!")
        else:
            print("⚠️  WARNING: Output rendering inclusion may be incomplete")
            
    except Exception as e:
        print(f"❌ ERROR during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_context_prompt_output_rendering()
