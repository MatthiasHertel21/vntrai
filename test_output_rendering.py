#!/usr/bin/env python3
"""
Test output rendering inclusion in context prompt
"""

def test_output_rendering_inclusion():
    """Test that output rendering is properly included in context prompt"""
    
    # Simulated task definition with output rendering (current format)
    task_with_output_rendering = {
        'name': 'Test Task with Output Rendering',
        'type': 'ai',
        'description': 'Task with output rendering instructions',
        'output_type': 'html',
        'output_description': 'Generate a formatted HTML response',
        'output_rendering': 'Use proper HTML structure with headings, paragraphs, and lists. Include CSS classes for styling.',
        'output_variable': 'formatted_result',
        'ai_config': {
            'instructions': 'Process the input and create formatted output',
            'goals': ['Create well-formatted HTML output']
        }
    }
    
    # Task with variable substitution in output rendering
    task_with_variables = {
        'name': 'Variable Test Task',
        'type': 'ai',
        'description': 'Task with variables in output rendering',
        'output_type': 'markdown',
        'output_description': 'Generate {{format}} output for {{audience}}',
        'output_rendering': 'Format the response as {{format}} with focus on {{aspect}}. Target audience: {{audience}}.',
        'ai_config': {
            'instructions': 'Create content based on input parameters'
        }
    }
    
    # Task with nested output config (legacy format)
    task_legacy_format = {
        'name': 'Legacy Format Task',
        'type': 'ai',
        'description': 'Task with legacy output format',
        'output': {
            'type': 'json',
            'description': 'Return structured JSON data',
            'rendering': 'Use proper JSON formatting with clear structure'
        },
        'ai_config': {
            'instructions': 'Generate structured data'
        }
    }
    
    # Sample inputs for variable resolution
    task_inputs = {
        'format': 'markdown',
        'audience': 'developers',
        'aspect': 'technical details'
    }
    
    # Sample agent
    agent = {
        'name': 'Test Agent',
        'description': 'Agent for testing output rendering'
    }
    
    test_cases = [
        ('current format with output rendering', task_with_output_rendering, {}),
        ('variable substitution in output', task_with_variables, task_inputs),
        ('legacy nested output format', task_legacy_format, {})
    ]
    
    print("=== Testing Output Rendering Inclusion in Context Prompt ===\n")
    
    for test_name, task_def, inputs in test_cases:
        print(f"--- {test_name} ---")
        print(f"Task definition keys: {list(task_def.keys())}")
        print(f"Output type: {task_def.get('output_type', task_def.get('output', {}).get('type', 'None'))}")
        print(f"Output rendering: {task_def.get('output_rendering', task_def.get('output', {}).get('rendering', 'None'))}")
        print(f"Task inputs: {inputs}")
        
        # Simulate the context prompt building logic
        def extract_output_config(task_def, task_inputs):
            """Extract and resolve output configuration"""
            output_config = task_def.get('output', {})
            
            # Check top-level output fields first (newer format)
            output_type = task_def.get('output_type', output_config.get('type', 'text'))
            output_description = task_def.get('output_description', output_config.get('description', ''))
            output_rendering = task_def.get('output_rendering', output_config.get('rendering', ''))
            output_variable = task_def.get('output_variable', '')
            
            # Simple variable resolution (for testing)
            def resolve_variables_simple(text, variables):
                if not text or not variables:
                    return text
                for key, value in variables.items():
                    text = text.replace(f'{{{{{key}}}}}', str(value))
                return text
            
            if output_description:
                output_description = resolve_variables_simple(output_description, task_inputs)
            if output_rendering:
                output_rendering = resolve_variables_simple(output_rendering, task_inputs)
            
            return {
                'type': output_type,
                'description': output_description,
                'rendering': output_rendering,
                'variable': output_variable
            }
        
        output_config = extract_output_config(task_def, inputs)
        
        print(f"\nExtracted output config:")
        for key, value in output_config.items():
            print(f"  {key}: {value}")
        
        # Check if output rendering would be included
        has_output_requirements = any([
            output_config['type'] and output_config['type'] != 'text',
            output_config['description'],
            output_config['rendering'],
            output_config['variable']
        ])
        
        print(f"\n✅ Output requirements would be included: {has_output_requirements}")
        print(f"✅ Output rendering would be included: {bool(output_config['rendering'])}")
        
        if output_config['rendering']:
            print(f"✅ Resolved rendering instructions: '{output_config['rendering']}'")
        else:
            print("❌ WARNING: No output rendering instructions found!")
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_output_rendering_inclusion()
