"""
Assistant Discovery and Management Routes
Provides comprehensive assistant management functionality
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app.utils.data_manager import agents_manager, tools_manager, integrations_manager
from app.utils.openai_assistant_wrapper import OpenAIAssistantAPI
import asyncio
import json
import openai
import traceback
from datetime import datetime
import uuid

assistants_bp = Blueprint('assistants', __name__, url_prefix='/assistants')

def get_openai_api_key():
    """Get OpenAI API key with preference for Assistant API tools"""
    all_tools = tools_manager.get_all()
    
    # First, try to find an OpenAI Assistant API specific tool
    for tool in all_tools:
        tool_name = tool.get('name', '').lower()
        
        # Look for assistant-specific tools first
        if 'assistant' in tool_name or ('openai' in tool_name and 'assistant' in tool_name):
            config = tool.get('config', {})
            for key, value in config.items():
                if 'api_key' in key.lower() and value and isinstance(value, str) and len(value) > 10:
                    return value
    
    # Second priority: any OpenAI tool
    for tool in all_tools:
        tool_name = tool.get('name', '').lower()
        if 'openai' in tool_name or 'gpt' in tool_name:
            config = tool.get('config', {})
            for key, value in config.items():
                if 'api_key' in key.lower() and value and isinstance(value, str) and len(value) > 10:
                    return value
    
    # Last resort: any tool with an API key
    for tool in all_tools:
        config = tool.get('config', {})
        for key, value in config.items():
            if 'api_key' in key.lower() and value and isinstance(value, str) and len(value) > 10:
                return value
    
    return None

@assistants_bp.route('/')
def list_assistants():
    """Assistant Discovery and Management Dashboard"""
    debug_mode = request.args.get('debug', False)
    debug_log = []
    
    try:
        # Get all tools and check for assistant options and API keys
        all_tools = tools_manager.get_all()
        debug_log.append(f"Found {len(all_tools)} tools")
        
        tools_with_assistant_options = []
        api_keys_found = []
        all_assistants = []
        
        # Collect tools with assistant options and API keys
        for tool in all_tools:
            # Check assistant options
            options = tool.get('options', {})
            assistant_options = options.get('assistant', {})
            if assistant_options.get('enabled', False):
                tools_with_assistant_options.append({
                    'tool': tool,
                    'assistant_id': assistant_options.get('assistant_id', ''),
                    'model': assistant_options.get('model', 'gpt-4-turbo-preview'),
                    'instructions': assistant_options.get('instructions', ''),
                    'auto_create': assistant_options.get('auto_create', True)
                })
            
            # Check for API keys in config
            config = tool.get('config', {})
            for key, value in config.items():
                if 'api_key' in key.lower() and value and isinstance(value, str) and len(value) > 10:
                    api_keys_found.append({
                        'tool_name': tool.get('name'),
                        'tool_id': tool.get('id'),
                        'key_name': key,
                        'key_hash': value[:8] + '...' + value[-4:] if len(value) > 12 else value,
                        'api_key': value
                    })
        
        debug_log.append(f"Found {len(tools_with_assistant_options)} tools with assistant options")
        debug_log.append(f"Found {len(api_keys_found)} API keys")
        
        # Get unique API keys and fetch assistants
        unique_api_keys = {}
        for api_key_info in api_keys_found:
            api_key = api_key_info['api_key']
            if api_key not in unique_api_keys:
                unique_api_keys[api_key] = api_key_info
        
        debug_log.append(f"Found {len(unique_api_keys)} unique API keys")
        
        assistants_by_api_key = {}
        for api_key, api_key_info in unique_api_keys.items():
            debug_log.append(f"Testing API key from {api_key_info['tool_name']}")
            try:
                client = openai.OpenAI(api_key=api_key)
                assistants_response = client.beta.assistants.list(limit=100)
                assistants = assistants_response.data
                debug_log.append(f"Successfully fetched {len(assistants)} assistants")
                
                # Convert to dict format
                assistants_list = []
                for assistant in assistants:
                    # Format created_at timestamp
                    created_at_formatted = 'Unknown'
                    if hasattr(assistant, 'created_at') and assistant.created_at:
                        try:
                            from datetime import datetime
                            created_at_formatted = datetime.fromtimestamp(assistant.created_at).strftime('%d.%m.%Y %H:%M')
                        except:
                            created_at_formatted = str(assistant.created_at)
                    
                    # Safely get file_ids - it might not exist or have a different name
                    file_ids = []
                    if hasattr(assistant, 'file_ids'):
                        file_ids = assistant.file_ids or []
                    elif hasattr(assistant, 'tool_resources'):
                        # New API structure
                        if hasattr(assistant.tool_resources, 'file_search') and hasattr(assistant.tool_resources.file_search, 'vector_store_ids'):
                            file_ids = assistant.tool_resources.file_search.vector_store_ids or []
                    
                    # Safely get tools
                    tools_list = []
                    if hasattr(assistant, 'tools') and assistant.tools:
                        tools_list = [tool.type if hasattr(tool, 'type') else str(tool) for tool in assistant.tools]
                    
                    assistants_list.append({
                        'id': assistant.id,
                        'name': assistant.name or 'Unnamed Assistant',
                        'description': assistant.description or '',
                        'model': assistant.model,
                        'instructions': assistant.instructions or '',
                        'tools': tools_list,
                        'file_ids': file_ids,
                        'metadata': assistant.metadata or {} if hasattr(assistant, 'metadata') else {},
                        'created_at': assistant.created_at if hasattr(assistant, 'created_at') else None,
                        'created_at_formatted': created_at_formatted
                    })
                
                debug_log.append(f"Converted {len(assistants_list)} assistants to dict format")
                
                assistants_by_api_key[api_key_info['key_hash']] = {
                    'tool_name': api_key_info['tool_name'],
                    'assistants': assistants_list,
                    'success': True,
                    'error': None
                }
                
                all_assistants.extend(assistants_list)
                debug_log.append(f"Total assistants now: {len(all_assistants)}")
                
            except Exception as e:
                debug_log.append(f"Error with API key from {api_key_info['tool_name']}: {str(e)}")
                assistants_by_api_key[api_key_info['key_hash']] = {
                    'tool_name': api_key_info['tool_name'],
                    'assistants': [],
                    'success': False,
                    'error': str(e)
                }
        
        debug_log.append(f"Final total assistants: {len(all_assistants)}")
        
        # Get all agents for mapping
        agents = agents_manager.get_all()
        assistant_to_agent = {}
        for agent in agents:
            if agent.get('assistant_id'):
                assistant_to_agent[agent['assistant_id']] = agent
        
        # Enhance assistants with agent mapping
        for assistant in all_assistants:
            assistant['agent'] = assistant_to_agent.get(assistant['id'])
            assistant['status'] = 'mapped' if assistant['id'] in assistant_to_agent else 'orphaned'
        
        # Statistics
        stats = {
            'total_tools': len(all_tools),
            'tools_with_assistant_options': len(tools_with_assistant_options),
            'api_keys_found': len(api_keys_found),
            'unique_api_keys': len(unique_api_keys),
            'total_assistants': len(all_assistants),
            'mapped_assistants': len([a for a in all_assistants if a['status'] == 'mapped']),
            'orphaned_assistants': len([a for a in all_assistants if a['status'] == 'orphaned'])
        }
        
        debug_log.append(f"Stats: {stats}")
        
        if debug_mode:
            debug_html = "<h1>Debug Log</h1><ul>"
            for log_entry in debug_log:
                debug_html += f"<li>{log_entry}</li>"
            debug_html += "</ul>"
            return debug_html
        
        return render_template('assistants/list.html',
                             tools_with_assistant_options=tools_with_assistant_options,
                             api_keys_found=api_keys_found,
                             assistants_by_api_key=assistants_by_api_key,
                             all_assistants=all_assistants,
                             stats=stats,
                             all_tools=all_tools)
                             
    except Exception as e:
        debug_log.append(f"MAIN ERROR: {str(e)}")
        if debug_mode:
            debug_html = "<h1>Debug Log with Error</h1><ul>"
            for log_entry in debug_log:
                debug_html += f"<li>{log_entry}</li>"
            debug_html += f"</ul><h2>Error Details</h2><p>{str(e)}</p><pre>{traceback.format_exc()}</pre>"
            return debug_html
            
        flash(f'Error loading assistants: {str(e)}', 'error')
        return render_template('assistants/list.html', 
                             tools_with_assistant_options=[],
                             api_keys_found=[],
                             assistants_by_api_key={},
                             all_assistants=[],
                             stats={},
                             all_tools=[])

@assistants_bp.route('/analytics')
def analytics():
    """Comprehensive Assistant Analytics Dashboard"""
    try:
        # Get all assistants
        all_tools = tools_manager.get_all()
        api_keys_found = []
        all_assistants = []
        
        # Collect API keys from tools
        for tool in all_tools:
            config = tool.get('config', {})
            for key, value in config.items():
                if 'api_key' in key.lower() and value and isinstance(value, str) and len(value) > 10:
                    api_keys_found.append({
                        'tool_name': tool.get('name'),
                        'tool_id': tool.get('id'),
                        'key_name': key,
                        'api_key': value
                    })
        
        # Get unique API keys and fetch assistants
        unique_api_keys = {}
        for api_key_info in api_keys_found:
            api_key = api_key_info['api_key']
            if api_key not in unique_api_keys:
                unique_api_keys[api_key] = api_key_info
        
        # Fetch assistants from each API key
        for api_key, api_key_info in unique_api_keys.items():
            try:
                client = openai.OpenAI(api_key=api_key)
                assistants_response = client.beta.assistants.list(limit=100)
                assistants = assistants_response.data
                
                for assistant in assistants:
                    # Safely get file_ids
                    file_ids = []
                    if hasattr(assistant, 'file_ids'):
                        file_ids = assistant.file_ids or []
                    elif hasattr(assistant, 'tool_resources'):
                        if hasattr(assistant.tool_resources, 'file_search') and hasattr(assistant.tool_resources.file_search, 'vector_store_ids'):
                            file_ids = assistant.tool_resources.file_search.vector_store_ids or []
                    
                    # Safely get tools
                    tools_list = []
                    if hasattr(assistant, 'tools') and assistant.tools:
                        tools_list = [tool.type if hasattr(tool, 'type') else str(tool) for tool in assistant.tools]
                    
                    all_assistants.append({
                        'id': assistant.id,
                        'name': assistant.name or 'Unnamed Assistant',
                        'model': assistant.model,
                        'tools': tools_list,
                        'file_ids': file_ids,
                        'created_at': assistant.created_at if hasattr(assistant, 'created_at') else None,
                        'api_key_source': api_key_info['tool_name']
                    })
                    
            except Exception as e:
                print(f"Error fetching assistants from {api_key_info['tool_name']}: {e}")
        
        # Get all agents for mapping
        agents = agents_manager.get_all()
        assistant_to_agent = {}
        for agent in agents:
            if agent.get('assistant_id'):
                assistant_to_agent[agent['assistant_id']] = agent
        
        # Enhanced analytics calculation
        analytics_data = {
            'total_assistants': len(all_assistants),
            'mapped_assistants': len([a for a in all_assistants if a['id'] in assistant_to_agent]),
            'orphaned_assistants': len([a for a in all_assistants if a['id'] not in assistant_to_agent]),
            'total_files': sum(len(a['file_ids']) for a in all_assistants),
            'unique_api_keys': len(unique_api_keys),
            'total_agents': len(agents),
            'agents_with_assistants': len([a for a in agents if a.get('assistant_id')]),
            'models_used': {},
            'tools_used': {},
            'api_key_distribution': {},
            'creation_timeline': {},
            'file_distribution': {}
        }
        
        # Model usage statistics
        for assistant in all_assistants:
            model = assistant['model']
            analytics_data['models_used'][model] = analytics_data['models_used'].get(model, 0) + 1
        
        # Tool usage statistics  
        for assistant in all_assistants:
            for tool in assistant['tools']:
                analytics_data['tools_used'][tool] = analytics_data['tools_used'].get(tool, 0) + 1
        
        # API key distribution
        for assistant in all_assistants:
            source = assistant['api_key_source']
            analytics_data['api_key_distribution'][source] = analytics_data['api_key_distribution'].get(source, 0) + 1
        
        # Creation timeline (by month)
        from datetime import datetime
        for assistant in all_assistants:
            if assistant['created_at']:
                try:
                    created_date = datetime.fromtimestamp(assistant['created_at'])
                    month_key = created_date.strftime('%Y-%m')
                    analytics_data['creation_timeline'][month_key] = analytics_data['creation_timeline'].get(month_key, 0) + 1
                except:
                    pass
        
        # File distribution
        file_counts = [len(a['file_ids']) for a in all_assistants]
        analytics_data['file_distribution'] = {
            'no_files': len([c for c in file_counts if c == 0]),
            'few_files': len([c for c in file_counts if 1 <= c <= 5]),
            'many_files': len([c for c in file_counts if c > 5]),
            'avg_files': sum(file_counts) / len(file_counts) if file_counts else 0
        }
        
        return render_template('assistants/analytics.html', 
                             analytics=analytics_data,
                             all_assistants=all_assistants,
                             assistant_to_agent=assistant_to_agent)
                             
    except Exception as e:
        flash(f'Error loading analytics: {str(e)}', 'error')
        return render_template('assistants/analytics.html', 
                             analytics={},
                             all_assistants=[],
                             assistant_to_agent={})

@assistants_bp.route('/api/delete/<assistant_id>', methods=['POST'])
def api_delete_assistant(assistant_id):
    """Delete an assistant via API"""
    try:
        # Get API key using our helper function
        api_key = get_openai_api_key()
        
        if not api_key:
            return jsonify({'success': False, 'message': 'No API key found for deletion'})
        
        # Direct OpenAI call
        import openai
        client = openai.OpenAI(api_key=api_key)
        delete_response = client.beta.assistants.delete(assistant_id)
        
        # OpenAI delete returns an object with deleted=True
        success = getattr(delete_response, 'deleted', False)
        
        if success:
            # Also remove assistant_id from any agents
            agents = agents_manager.get_all()
            for agent in agents:
                if agent.get('assistant_id') == assistant_id:
                    agent['assistant_id'] = None
                    agents_manager.save(agent)
            
            return jsonify({'success': True, 'message': 'Assistant deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to delete assistant'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting assistant: {str(e)}'})

@assistants_bp.route('/health')
def health_monitoring():
    """Comprehensive Assistant Health Monitoring Dashboard"""
    try:
        # Get all tools and API keys
        all_tools = tools_manager.get_all()
        api_keys_found = []
        
        for tool in all_tools:
            config = tool.get('config', {})
            for key, value in config.items():
                if 'api_key' in key.lower() and value and isinstance(value, str) and len(value) > 10:
                    api_keys_found.append({
                        'tool_name': tool.get('name'),
                        'tool_id': tool.get('id'),
                        'key_name': key,
                        'api_key': value
                    })
        
        # Health check results
        health_results = {
            'overall_status': 'healthy',
            'api_keys_status': [],
            'assistants_status': [],
            'performance_metrics': {
                'total_api_keys': len(set(api['api_key'] for api in api_keys_found)),
                'working_api_keys': 0,
                'failed_api_keys': 0,
                'total_assistants': 0,
                'response_times': [],
                'error_rate': 0
            },
            'recommendations': []
        }
        
        # Test each unique API key
        unique_api_keys = {}
        for api_key_info in api_keys_found:
            api_key = api_key_info['api_key']
            if api_key not in unique_api_keys:
                unique_api_keys[api_key] = api_key_info
        
        for api_key, api_key_info in unique_api_keys.items():
            start_time = datetime.now()
            api_status = {
                'tool_name': api_key_info['tool_name'],
                'key_hash': api_key[:8] + '...' + api_key[-4:],
                'status': 'unknown',
                'response_time': 0,
                'assistants_count': 0,
                'error_message': None,
                'last_checked': start_time.isoformat()
            }
            
            try:
                # Test API connectivity
                client = openai.OpenAI(api_key=api_key)
                assistants_response = client.beta.assistants.list(limit=5)
                
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds() * 1000  # in ms
                
                api_status.update({
                    'status': 'healthy',
                    'response_time': round(response_time, 2),
                    'assistants_count': len(assistants_response.data),
                    'error_message': None
                })
                
                health_results['performance_metrics']['working_api_keys'] += 1
                health_results['performance_metrics']['total_assistants'] += len(assistants_response.data)
                health_results['performance_metrics']['response_times'].append(response_time)
                
            except Exception as e:
                api_status.update({
                    'status': 'error',
                    'response_time': 0,
                    'assistants_count': 0,
                    'error_message': str(e)
                })
                
                health_results['performance_metrics']['failed_api_keys'] += 1
                health_results['overall_status'] = 'degraded'
                
            health_results['api_keys_status'].append(api_status)
        
        # Calculate performance metrics
        if health_results['performance_metrics']['response_times']:
            avg_response_time = sum(health_results['performance_metrics']['response_times']) / len(health_results['performance_metrics']['response_times'])
            health_results['performance_metrics']['avg_response_time'] = round(avg_response_time, 2)
        else:
            health_results['performance_metrics']['avg_response_time'] = 0
        
        # Calculate error rate
        total_keys = health_results['performance_metrics']['total_api_keys']
        failed_keys = health_results['performance_metrics']['failed_api_keys']
        health_results['performance_metrics']['error_rate'] = (failed_keys / total_keys * 100) if total_keys > 0 else 0
        
        # Generate recommendations
        if failed_keys > 0:
            health_results['recommendations'].append({
                'type': 'error',
                'title': 'API Key Issues Detected',
                'message': f'{failed_keys} API key(s) are not working properly. Check configuration and verify credentials.',
                'action': 'Review API keys in tool configurations'
            })
        
        if health_results['performance_metrics']['avg_response_time'] > 2000:
            health_results['recommendations'].append({
                'type': 'warning',
                'title': 'Slow Response Times',
                'message': f'Average response time is {health_results["performance_metrics"]["avg_response_time"]}ms. Consider optimizing requests.',
                'action': 'Monitor API usage and consider rate limiting'
            })
        
        if health_results['performance_metrics']['total_assistants'] == 0:
            health_results['recommendations'].append({
                'type': 'info',
                'title': 'No Assistants Found',
                'message': 'No assistants were discovered. Create assistants to start using the system.',
                'action': 'Create new assistants via OpenAI API'
            })
        
        # Determine overall status
        if failed_keys == 0 and health_results['performance_metrics']['avg_response_time'] < 1000:
            health_results['overall_status'] = 'healthy'
        elif failed_keys == 0:
            health_results['overall_status'] = 'warning'
        else:
            health_results['overall_status'] = 'error'
        
        return render_template('assistants/health.html', health=health_results)
        
    except Exception as e:
        flash(f'Error during health check: {str(e)}', 'error')
        return render_template('assistants/health.html', health={'overall_status': 'error', 'error': str(e)})

@assistants_bp.route('/chat/<assistant_id>')
def chat_interface(assistant_id):
    """Assistant Chat Interface"""
    try:
        # Get API key using our helper function
        api_key = get_openai_api_key()
        
        if not api_key:
            flash('No API key found', 'error')
            return redirect(url_for('assistants.list_assistants'))
        
        # Get assistant info
        client = openai.OpenAI(api_key=api_key)
        assistant = client.beta.assistants.retrieve(assistant_id)
        
        assistant_data = {
            'id': assistant.id,
            'name': assistant.name or 'Unnamed Assistant',
            'model': assistant.model,
            'instructions': assistant.instructions or '',
            'tools': [tool.type if hasattr(tool, 'type') else str(tool) for tool in assistant.tools] if assistant.tools else []
        }
        
        # Find associated agent
        agents = agents_manager.get_all()
        associated_agent = None
        for agent in agents:
            if agent.get('assistant_id') == assistant_id:
                associated_agent = agent
                break
        
        return render_template('assistants/chat.html', 
                             assistant=assistant_data,
                             agent=associated_agent)
                             
    except Exception as e:
        flash(f'Error loading chat interface: {str(e)}', 'error')
        return redirect(url_for('assistants.list_assistants'))

@assistants_bp.route('/api/chat/<assistant_id>', methods=['POST'])
def api_chat_with_assistant(assistant_id):
    """Send message to assistant using OpenAI Assistant API with persistent threads"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        thread_id = data.get('thread_id')  # Optional: use existing thread
        
        if not message:
            return jsonify({'success': False, 'message': 'Message is required'})
        
        # Get API key
        api_key = get_openai_api_key()
        if not api_key:
            return jsonify({'success': False, 'message': 'No OpenAI API key found'})
        
        client = openai.OpenAI(api_key=api_key)
        
        # Create or use existing thread
        if not thread_id:
            thread = client.beta.threads.create()
            thread_id = thread.id
        
        # Add user message to thread
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )
        
        # Create and poll run (disable tools for simple chat)
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            tools=[]  # Disable tools to avoid requires_action status
        )
        
        # Poll for completion
        max_attempts = 30  # 30 seconds timeout
        attempts = 0
        
        while run.status in ['queued', 'in_progress', 'cancelling'] and attempts < max_attempts:
            import time
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            attempts += 1
        
        if run.status == 'completed':
            # Get the assistant's response
            messages = client.beta.threads.messages.list(
                thread_id=thread_id,
                order='desc',
                limit=1
            )
            
            if messages.data:
                assistant_message = messages.data[0]
                if assistant_message.role == 'assistant':
                    # Extract text content from message
                    content = ''
                    for content_block in assistant_message.content:
                        if hasattr(content_block, 'text'):
                            content += content_block.text.value
                        elif hasattr(content_block, 'value'):
                            content += str(content_block.value)
                        else:
                            content += str(content_block)
                    
                    return jsonify({
                        'success': True,
                        'data': {
                            'message': content,
                            'assistant_id': assistant_id,
                            'thread_id': thread_id,
                            'timestamp': datetime.now().isoformat(),
                            'run_id': run.id
                        }
                    })
            
            return jsonify({'success': False, 'message': 'No response received from assistant'})
            
        elif run.status == 'failed':
            error_message = 'Assistant run failed'
            if hasattr(run, 'last_error') and run.last_error:
                error_message = f"Assistant run failed: {run.last_error.message}"
            return jsonify({'success': False, 'message': error_message})
            
        elif run.status == 'requires_action':
            # Handle tool calls
            try:
                # Get required actions
                required_actions = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                
                for tool_call in required_actions:
                    # For now, we'll provide a simple response for all tool calls
                    # In a full implementation, you would execute the actual tools
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": f"Tool '{tool_call.function.name}' executed successfully with arguments: {tool_call.function.arguments}"
                    })
                
                # Submit tool outputs
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
                
                # Continue polling for completion after tool execution
                attempts = 0
                while run.status in ['queued', 'in_progress'] and attempts < max_attempts:
                    import time
                    time.sleep(1)
                    run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
                    attempts += 1
                
                # Check final status after tool execution
                if run.status == 'completed':
                    # Get the assistant's response
                    messages = client.beta.threads.messages.list(
                        thread_id=thread_id,
                        order='desc',
                        limit=1
                    )
                    
                    if messages.data:
                        assistant_message = messages.data[0]
                        if assistant_message.role == 'assistant':
                            # Extract text content from message
                            content = ''
                            for content_block in assistant_message.content:
                                if hasattr(content_block, 'text'):
                                    content += content_block.text.value
                                elif hasattr(content_block, 'value'):
                                    content += str(content_block.value)
                                else:
                                    content += str(content_block)
                            
                            return jsonify({
                                'success': True,
                                'data': {
                                    'message': content,
                                    'assistant_id': assistant_id,
                                    'thread_id': thread_id,
                                    'timestamp': datetime.now().isoformat(),
                                    'run_id': run.id,
                                    'tool_calls_executed': len(tool_outputs)
                                }
                            })
                
                return jsonify({
                    'success': False, 
                    'message': f'Tool execution completed but run status is: {run.status}'
                })
                
            except Exception as tool_error:
                return jsonify({
                    'success': False, 
                    'message': f'Error handling tool calls: {str(tool_error)}'
                })
            
        else:
            return jsonify({
                'success': False, 
                'message': f'Assistant run timed out or unexpected status: {run.status}'
            })
        
    except openai.AuthenticationError:
        return jsonify({'success': False, 'message': 'Invalid OpenAI API key'})
    except openai.NotFoundError:
        return jsonify({'success': False, 'message': 'Assistant not found'})
    except openai.RateLimitError:
        return jsonify({'success': False, 'message': 'OpenAI API rate limit exceeded'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@assistants_bp.route('/api/chat/<assistant_id>/thread', methods=['POST'])
def create_new_thread(assistant_id):
    """Create a new conversation thread"""
    try:
        api_key = get_openai_api_key()
        if not api_key:
            return jsonify({'success': False, 'message': 'No OpenAI API key found'})
        
        client = openai.OpenAI(api_key=api_key)
        thread = client.beta.threads.create()
        
        return jsonify({
            'success': True,
            'data': {
                'thread_id': thread.id,
                'created_at': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@assistants_bp.route('/api/chat/<assistant_id>/history/<thread_id>')
def get_thread_history(assistant_id, thread_id):
    """Get conversation history for a thread"""
    try:
        api_key = get_openai_api_key()
        if not api_key:
            return jsonify({'success': False, 'message': 'No OpenAI API key found'})
        
        client = openai.OpenAI(api_key=api_key)
        
        # Get messages from thread
        messages = client.beta.threads.messages.list(
            thread_id=thread_id,
            order='asc'  # Chronological order
        )
        
        conversation_history = []
        for message in messages.data:
            content = ''
            for content_block in message.content:
                if hasattr(content_block, 'text'):
                    content += content_block.text.value
                elif hasattr(content_block, 'value'):
                    content += str(content_block.value)
                else:
                    content += str(content_block)
            
            conversation_history.append({
                'id': message.id,
                'role': message.role,
                'content': content,
                'created_at': message.created_at,
                'timestamp': datetime.fromtimestamp(message.created_at).isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': {
                'thread_id': thread_id,
                'messages': conversation_history
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@assistants_bp.route('/files')
def file_management():
    """File Management Dashboard for Assistant Files"""
    try:
        # Get all assistants and their files
        all_tools = tools_manager.get_all()
        api_keys_found = []
        all_files = []
        
        # Collect API keys
        for tool in all_tools:
            config = tool.get('config', {})
            for key, value in config.items():
                if 'api_key' in key.lower() and value and isinstance(value, str) and len(value) > 10:
                    api_keys_found.append({
                        'tool_name': tool.get('name'),
                        'api_key': value
                    })
        
        # Get unique API keys and fetch files
        unique_api_keys = {}
        for api_key_info in api_keys_found:
            api_key = api_key_info['api_key']
            if api_key not in unique_api_keys:
                unique_api_keys[api_key] = api_key_info
        
        for api_key, api_key_info in unique_api_keys.items():
            try:
                client = openai.OpenAI(api_key=api_key)
                
                # Get files
                files_response = client.files.list()
                for file_obj in files_response.data:
                    all_files.append({
                        'id': file_obj.id,
                        'filename': file_obj.filename,
                        'purpose': file_obj.purpose,
                        'size': file_obj.bytes,
                        'created_at': file_obj.created_at,
                        'api_source': api_key_info['tool_name'],
                        'status': getattr(file_obj, 'status', 'uploaded')
                    })
                
            except Exception as e:
                print(f"Error fetching files from {api_key_info['tool_name']}: {e}")
        
        # Statistics
        file_stats = {
            'total_files': len(all_files),
            'total_size': sum(f['size'] for f in all_files),
            'avg_size': sum(f['size'] for f in all_files) / len(all_files) if all_files else 0
        }
        
        return render_template('assistants/files.html', 
                             files=all_files,
                             stats=file_stats)
        
    except Exception as e:
        flash(f'Error loading file management: {str(e)}', 'error')
        return render_template('assistants/files.html', files=[], stats={})

@assistants_bp.route('/api/files/<file_id>/delete', methods=['POST'])
def api_delete_file(file_id):
    """Delete a file from OpenAI"""
    try:
        # Find which API key has this file
        all_tools = tools_manager.get_all()
        api_keys_found = []
        
        for tool in all_tools:
            config = tool.get('config', {})
            for key, value in config.items():
                if 'api_key' in key.lower() and value and isinstance(value, str) and len(value) > 10:
                    api_keys_found.append(value)
        
        file_deleted = False
        for api_key in set(api_keys_found):
            try:
                client = openai.OpenAI(api_key=api_key)
                client.files.delete(file_id)
                file_deleted = True
                break
            except:
                continue
        
        if not file_deleted:
            return jsonify({'success': False, 'message': 'File not found or could not be deleted'})
        
        return jsonify({'success': True, 'message': 'File deleted successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@assistants_bp.route('/api/create_agent/<assistant_id>', methods=['POST'])
def api_create_agent_from_assistant(assistant_id):
    """Create a new agent for an orphaned assistant"""
    try:
        # Get API key using our helper function
        api_key = get_openai_api_key()
        
        if not api_key:
            return jsonify({'success': False, 'message': 'No API key found'})
        
        # Get assistant info directly from OpenAI
        client = openai.OpenAI(api_key=api_key)
        assistant = client.beta.assistants.retrieve(assistant_id)
        
        # Create new agent
        agent_data = {
            'id': str(uuid.uuid4()),
            'name': assistant.name or f'Agent for {assistant_id[:8]}',
            'description': assistant.description or f'Auto-created agent for assistant {assistant_id}',
            'category': 'General',
            'status': 'active',
            'assistant_id': assistant_id,
            'ai_assistant_tool': 'tool:openai_assistant_api',
            'model': assistant.model,
            'instructions': assistant.instructions or '',
            'tasks': [],
            'knowledge_base': [],
            'files': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        agents_manager.save(agent_data)
        
        return jsonify({
            'success': True, 
            'message': f'Agent "{agent_data["name"]}" created successfully',
            'agent_id': agent_data['id']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error creating agent: {str(e)}'})

@assistants_bp.route('/api/chat/<assistant_id>/threads')
def list_threads(assistant_id):
    """List available threads for an assistant"""
    try:
        # Since OpenAI doesn't provide a direct way to list threads for an assistant,
        # we'll return a placeholder response. In a production system, you might
        # want to store thread information in your database
        return jsonify({
            'success': True,
            'data': {
                'threads': [],
                'message': 'Thread listing not available via OpenAI API. Create new threads as needed.'
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@assistants_bp.route('/api/chat/<assistant_id>/thread/<thread_id>/delete', methods=['POST'])
def delete_thread(assistant_id, thread_id):
    """Delete a conversation thread"""
    try:
        api_key = get_openai_api_key()
        if not api_key:
            return jsonify({'success': False, 'message': 'No OpenAI API key found'})
        
        client = openai.OpenAI(api_key=api_key)
        
        # Delete the thread
        response = client.beta.threads.delete(thread_id)
        
        return jsonify({
            'success': True,
            'message': 'Thread deleted successfully',
            'deleted': response.deleted if hasattr(response, 'deleted') else True
        })
        
    except openai.NotFoundError:
        return jsonify({'success': False, 'message': 'Thread not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
