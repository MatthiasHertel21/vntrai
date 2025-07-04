#!/usr/bin/env python3
"""
Test the updated build_context_prompt function in Docker
"""

def main():
    # Simple test case
    task_def = {
        'name': 'Test Task',
        'ai_config': {
            'instructions': 'Test instructions from ai_config',
            'goals': ['Test goal 1', 'Test goal 2']
        }
    }
    
    print("Task definition:", task_def)
    print("Expected: Instructions and goals should be found")

if __name__ == "__main__":
    main()
