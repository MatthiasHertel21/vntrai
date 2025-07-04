"""
Prompt Builder
Handles context prompt building and variable resolution
"""

from .api_utils import log_info


def build_context_prompt(task_def: dict, task_inputs: dict, agent: dict, agent_run: dict = None) -> str:
    """Build a context prompt from task definition, inputs, agent data, and agent run"""
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
    
    # Add language instruction from agent run preference
    language = ''
    if agent_run:
        language = agent_run.get('language_preference', '')
    
    # Fallback to task inputs if not set in agent run
    if not language:
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
    
    # Add output rendering information from task definition
    # Check both old (output.type) and new (output_rendering) field structures
    output_rendering = task_def.get('output_rendering', '')
    output_type = task_def.get('output_type', '')
    
    if not output_rendering:
        # Fallback to old structure
        output_config = task_def.get('output', {})
        output_rendering = output_config.get('type', 'text')
    
    # If we have custom output rendering instructions, use them directly
    if output_rendering and output_rendering not in ['text', 'markdown', 'html', 'markup']:
        # Custom output rendering instructions
        prompt_parts.extend([
            "Output Requirements:",
            f"Type: {output_type if output_type else 'text'}",
            f"Rendering Instructions: {output_rendering}",
            ""
        ])
    elif output_rendering == 'markdown' or output_rendering == 'markup':
        prompt_parts.extend([
            "Output Rendering: Your response will be rendered using Markdown formatting.",
            "Please use appropriate Markdown syntax including headings, lists, code blocks, tables, and other elements.",
            "The markdown will be processed server-side and styled with the application's theme.",
            "IMPORTANT: For HTML elements like tables, buttons, or forms, embed them directly in the markdown without code block syntax (```html).",
            "Use raw HTML tags directly in the markdown text where needed.",
            ""
        ])
    elif output_rendering == 'html':
        prompt_parts.extend([
            "Output Rendering: Your response will be displayed as HTML content.",
            "You may use HTML tags for formatting, but keep the content semantic and accessible.",
            ""
        ])
    else:  # text or default
        prompt_parts.extend([
            "Output Rendering: Your response will be displayed as plain text.",
            "Use clear paragraphs and natural formatting without special markup.",
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
    
    # Note: Output format instructions removed per backlog item 33
    # The AI should respond naturally without format constraints
    
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
    
    log_info(f"render_response_content called with output_type: {output_type}")
    log_info(f"Content length: {len(content)}")
    log_info(f"Content preview: {content[:200]}...")
    
    if output_type == 'html':
        log_info("Rendering as HTML")
        # Return HTML content directly
        return content
    elif output_type == 'markdown' or output_type == 'markup':
        log_info("Rendering as Markdown/Markup")
        # Server-side markdown rendering with application styling
        import markdown
        import bleach
        
        # Configure markdown with extensions for better rendering
        md = markdown.Markdown(extensions=[
            'markdown.extensions.fenced_code',  # For code blocks
            'markdown.extensions.tables',       # For tables
            'markdown.extensions.nl2br',        # Convert newlines to <br>
            'markdown.extensions.toc'           # Table of contents
        ])
        
        # Convert markdown to HTML
        html_content = md.convert(content)
        
        # Post-process: Convert HTML code blocks to actual HTML
        # This handles cases where AI sends HTML as ```html code blocks
        import re
        
        # Pattern to find HTML code blocks and convert them to actual HTML
        html_code_pattern = r'<pre><code class="language-html">(.*?)</code></pre>'
        
        def replace_html_code_blocks(match):
            html_code = match.group(1)
            # Unescape HTML entities that were escaped by markdown
            import html as html_lib
            unescaped_html = html_lib.unescape(html_code)
            return unescaped_html
        
        # Replace HTML code blocks with actual HTML
        html_content = re.sub(html_code_pattern, replace_html_code_blocks, html_content, flags=re.DOTALL)
        
        # Sanitize HTML to prevent XSS attacks but allow more HTML elements
        allowed_tags = [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'p', 'br', 'strong', 'em', 'u', 'strike', 'b', 'i',
            'ul', 'ol', 'li', 'blockquote', 'code', 'pre',
            'table', 'thead', 'tbody', 'tr', 'th', 'td',
            'a', 'img', 'div', 'span', 'section', 'article',
            'button', 'input', 'textarea', 'select', 'option',
            'form', 'label', 'fieldset', 'legend', 'hr',
            'sub', 'sup', 'small', 'del', 'ins', 'mark'
        ]
        allowed_attributes = {
            'a': ['href', 'title', 'target'],
            'img': ['src', 'alt', 'title', 'width', 'height'],
            'code': ['class'],
            'pre': ['class'],
            'div': ['class', 'id', 'style'],
            'span': ['class', 'id', 'style'],
            'button': ['class', 'type', 'onclick'],
            'input': ['type', 'class', 'placeholder', 'value', 'name'],
            'textarea': ['class', 'placeholder', 'rows', 'cols'],
            'select': ['class', 'name'],
            'option': ['value'],
            'form': ['class', 'method', 'action'],
            'table': ['class'],
            'th': ['class', 'colspan', 'rowspan'],
            'td': ['class', 'colspan', 'rowspan']
        }
        
        clean_html = bleach.clean(html_content, tags=allowed_tags, attributes=allowed_attributes)
        
        # Wrap in a styled container using application's primary color palette
        styled_html = f'''
        <div class="markdown-content">
            <style>
                .markdown-content h1 {{ color: #0cc0df; border-bottom: 2px solid #0cc0df; padding-bottom: 0.5rem; margin-bottom: 1rem; }}
                .markdown-content h2 {{ color: #0cc0df; border-bottom: 1px solid #0cc0df; padding-bottom: 0.3rem; margin-bottom: 0.8rem; }}
                .markdown-content h3 {{ color: #0a9fb8; margin-bottom: 0.6rem; }}
                .markdown-content h4 {{ color: #0a9fb8; margin-bottom: 0.5rem; }}
                .markdown-content h5 {{ color: #087d91; margin-bottom: 0.4rem; }}
                .markdown-content h6 {{ color: #087d91; margin-bottom: 0.3rem; }}
                .markdown-content a {{ color: #0cc0df; text-decoration: underline; }}
                .markdown-content a:hover {{ color: #0a9fb8; }}
                .markdown-content blockquote {{ 
                    border-left: 4px solid #0cc0df; 
                    background-color: #f0fdff; 
                    padding: 1rem; 
                    margin: 1rem 0; 
                    font-style: italic; 
                }}
                .markdown-content code {{ 
                    background-color: #f0fdff; 
                    color: #087d91; 
                    padding: 0.2rem 0.4rem; 
                    border-radius: 0.25rem; 
                    font-family: 'Courier New', monospace; 
                }}
                .markdown-content pre {{ 
                    background-color: #f8fafc; 
                    border: 1px solid #e2e8f0; 
                    border-left: 4px solid #0cc0df; 
                    padding: 1rem; 
                    margin: 1rem 0; 
                    border-radius: 0.375rem; 
                    overflow-x: auto; 
                }}
                .markdown-content pre code {{ 
                    background-color: transparent; 
                    padding: 0; 
                    color: #334155; 
                }}
                .markdown-content table {{ 
                    border-collapse: collapse; 
                    width: 100%; 
                    margin: 1rem 0; 
                }}
                .markdown-content th {{ 
                    background-color: #0cc0df; 
                    color: white; 
                    padding: 0.75rem; 
                    text-align: left; 
                    border: 1px solid #0a9fb8; 
                }}
                .markdown-content td {{ 
                    padding: 0.75rem; 
                    border: 1px solid #e2e8f0; 
                }}
                .markdown-content tr:nth-child(even) {{ 
                    background-color: #f8fafc; 
                }}
                .markdown-content ul, .markdown-content ol {{ 
                    margin: 0.5rem 0; 
                    padding-left: 1.5rem; 
                }}
                .markdown-content li {{ 
                    margin: 0.25rem 0; 
                }}
                .markdown-content strong {{ 
                    font-weight: 600; 
                }}
                .markdown-content em {{ 
                    font-style: italic; 
                }}
            </style>
            {clean_html}
        </div>
        '''
        
        return styled_html
        
    else:  # text or default
        log_info(f"Rendering as plain text (output_type: {output_type})")
        # Escape HTML and preserve formatting
        import html
        escaped_content = html.escape(content)
        return f'<div class="text-content"><pre class="whitespace-pre-wrap">{escaped_content}</pre></div>'
