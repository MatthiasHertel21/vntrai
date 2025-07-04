"""
Prompt Builder
Handles context prompt building and variable resolution
"""

from .api_utils import log_info


def build_context_prompt(task_def: dict, task_inputs: dict, agent: dict) -> str:
    """Build a context prompt from task definition, inputs, and agent data"""
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
    
    # Add language instruction if specified
    language = task_inputs.get('_language', '')
    if language and language != 'auto':
        language_names = {
            'de': 'German',
            'en': 'English', 
            'fr': 'French',
            'es': 'Spanish',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean'
        }
        language_name = language_names.get(language, language)
        prompt_parts.extend([
            f"Language: Please respond in {language_name}.",
            ""
        ])
    
    # Add task inputs (excluding internal language parameter)
    if task_inputs:
        filtered_inputs = {k: v for k, v in task_inputs.items() if not k.startswith('_')}
        if filtered_inputs:
            prompt_parts.append("Input Parameters:")
            for key, value in filtered_inputs.items():
                prompt_parts.append(f"- {key}: {value}")
            prompt_parts.append("")
    
    # Add output format instructions - check both nested 'output' object and top-level fields
    output_config = task_def.get('output', {})
    
    # Check top-level output fields first (newer format)
    output_type = task_def.get('output_type', output_config.get('type', 'text'))
    output_description = task_def.get('output_description', output_config.get('description', ''))
    output_rendering = task_def.get('output_rendering', output_config.get('rendering', ''))
    output_variable = task_def.get('output_variable', '')
    
    log_info(f"Output config - type: {output_type}, description: {bool(output_description)}, rendering: {bool(output_rendering)}, variable: {output_variable}")
    
    if output_type or output_description or output_rendering or output_variable:
        prompt_parts.append("Output Requirements:")
        
        if output_variable:
            prompt_parts.append(f"- Output Variable: {output_variable}")
            
        if output_description:
            # Resolve variables in output description
            resolved_output_desc = resolve_variables(output_description, task_inputs)
            prompt_parts.append(f"- Description: {resolved_output_desc}")
        
        if output_type == 'html':
            prompt_parts.append("- Format: HTML")
        elif output_type == 'markdown':
            prompt_parts.append("- Format: Markdown")
        elif output_type == 'json':
            prompt_parts.append("- Format: JSON")
        elif output_type == 'text':
            prompt_parts.append("- Format: Plain text")
        else:
            prompt_parts.append(f"- Format: {output_type}")
        
        if output_rendering:
            # Resolve variables in output rendering instructions
            resolved_rendering = resolve_variables(output_rendering, task_inputs)
            log_info(f"Adding output rendering to prompt: {resolved_rendering}")
            prompt_parts.append(f"- Rendering Instructions: {resolved_rendering}")
        
        prompt_parts.append("")
    
    # Add knowledge base items if available
    knowledge_base = agent.get('knowledge_base', [])
    if knowledge_base:
        prompt_parts.append("Available Knowledge:")
        for item in knowledge_base[:5]:  # Limit to first 5 items
            item_title = item.get('title', 'Knowledge Item')
            item_content = item.get('content', '')[:200]
            # Resolve variables in knowledge base content
            resolved_title = resolve_variables(item_title, task_inputs)
            resolved_content = resolve_variables(item_content, task_inputs)
            prompt_parts.append(f"- {resolved_title}: {resolved_content}")
        prompt_parts.append("")
    
    # Add global variables from agent if available
    global_variables = agent.get('global_variables', {})
    if global_variables:
        prompt_parts.append("Global Variables:")
        for key, value in global_variables.items():
            prompt_parts.append(f"- {key}: {value}")
        prompt_parts.append("")
    
    prompt_parts.append("Please provide your response based on the above information.")
    
    final_prompt = "\n".join(filter(None, prompt_parts))
    log_info(f"Final prompt length: {len(final_prompt)} characters")
    return final_prompt


def resolve_variables(text: str, variables: dict) -> str:
    """Resolve {{variable}} placeholders in text with actual values"""
    if not text or not variables:
        log_info(f"resolve_variables: text={bool(text)}, variables={bool(variables)}")
        return text
    
    log_info(f"Resolving variables in text: '{text[:100]}...'")
    log_info(f"Available variables: {variables}")
    
    resolved_text = text
    for key, value in variables.items():
        # Replace {{key}} with the actual value
        placeholder = f"{{{{{key}}}}}"
        if placeholder in resolved_text:
            log_info(f"Replacing {placeholder} with '{value}'")
            resolved_text = resolved_text.replace(placeholder, str(value))
    
    log_info(f"Resolved text: '{resolved_text[:100]}...'")
    return resolved_text


def render_response_content(content: str, output_type: str) -> str:
    """Render AI response content based on output type"""
    
    if output_type == 'html':
        # Return HTML content directly
        return content
    elif output_type == 'markdown':
        # For now, wrap in pre tags - could add markdown parser later
        return f'<div class="markdown-content"><pre class="whitespace-pre-wrap">{content}</pre></div>'
    else:  # text or default
        # Escape HTML and preserve formatting
        import html
        escaped_content = html.escape(content)
        return f'<div class="text-content"><pre class="whitespace-pre-wrap">{escaped_content}</pre></div>'
