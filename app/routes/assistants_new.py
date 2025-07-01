"""
Assistant Discovery and Management Routes
Provides comprehensive assistant management functionality
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app.utils.data_manager import agents_manager, tools_manager
import json
from datetime import datetime
import uuid

assistants_bp = Blueprint('assistants', __name__, url_prefix='/assistants')

@assistants_bp.route('/test')
def test_route():
    """Simple test route to check if routing works"""
    return "<h1>Test Route Works!</h1><p>If you see this, the routing is working.</p>"

@assistants_bp.route('/simple')
def simple_list():
    """Simplified version without complex logic"""
    try:
        all_tools = tools_manager.get_all()
        return f"<h1>Simple Assistants Debug</h1><p>Found {len(all_tools)} tools</p><pre>{json.dumps([t.get('name', 'No name') for t in all_tools], indent=2)}</pre>"
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p><p>Type: {type(e).__name__}</p>"

@assistants_bp.route('/')
def list_assistants():
    """Enhanced Assistant Discovery Dashboard with detailed debugging"""
    debug_info = {
        'step': 'starting',
        'tools_found': 0,
        'tools_with_assistant_options': 0,
        'api_keys_found': 0,
        'api_requests': [],
        'errors': []
    }
    
    try:
        # Step 1: Get all tools
        debug_info['step'] = 'loading_all_tools'
        all_tools = tools_manager.get_all()
        debug_info['tools_found'] = len(all_tools)
        
        # Step 2: Find tools with assistant options
        debug_info['step'] = 'filtering_assistant_tools'
        tools_with_assistants = []
        
        for tool in all_tools:
            tool_debug = {
                'id': tool.get('id'),
                'name': tool.get('name'),
                'has_options': 'options' in tool,
                'has_assistant_options': False,
                'assistant_enabled': False,
                'assistant_id': None,
                'config_keys': list(tool.get('config', {}).keys())
            }
            
            if 'options' in tool and 'assistant' in tool['options']:
                tool_debug['has_assistant_options'] = True
                assistant_options = tool['options']['assistant']
                tool_debug['assistant_enabled'] = assistant_options.get('enabled', False)
                tool_debug['assistant_id'] = assistant_options.get('assistant_id', '')
                
                if assistant_options.get('enabled', False):
                    tool['debug_info'] = tool_debug
                    tools_with_assistants.append(tool)
            
            debug_info[f'tool_{tool.get("id", "unknown")}'] = tool_debug
        
        debug_info['tools_with_assistant_options'] = len(tools_with_assistants)
        
        # Step 3: Extract API keys and test them
        debug_info['step'] = 'extracting_api_keys'
        api_keys_info = []
        all_assistants = []
        
        for tool in tools_with_assistants:
            config = tool.get('config', {})
            
            # Try multiple possible API key field names
            api_key = None
            api_key_field = None
            for field in ['openai_api_key', 'api_key', 'OPENAI_API_KEY']:
                if field in config and config[field]:
                    api_key = config[field]
                    api_key_field = field
                    break
            
            if api_key:
                debug_info['api_keys_found'] += 1
                
                # Create hash for display
                api_key_hash = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else api_key
                
                api_request_debug = {
                    'tool_name': tool.get('name'),
                    'tool_id': tool.get('id'),
                    'api_key_field': api_key_field,
                    'api_key_hash': api_key_hash,
                    'api_key_length': len(api_key),
                    'api_key_starts_with': api_key[:10] if len(api_key) > 10 else api_key,
                    'request_successful': False,
                    'response_data': None,
                    'error': None
                }
                
                # Try to get assistants from this API key
                try:
                    from app.implementation_modules.openai_assistant_api import OpenAIAssistantAPIImplementation
                    api_impl = OpenAIAssistantAPIImplementation()
                    
                    # Test the configuration
                    config_params = {'openai_api_key': api_key, 'api_key': api_key}
                    input_params = {'action': 'list_assistants'}
                    
                    api_request_debug['config_params'] = {k: v[:20] + "..." if len(str(v)) > 20 else v for k, v in config_params.items()}
                    api_request_debug['input_params'] = input_params
                    
                    # Add more debug info about the API call
                    api_request_debug['base_url'] = 'https://api.openai.com/v1'
                    api_request_debug['endpoint'] = '/assistants'
                    api_request_debug['headers_preview'] = f"Bearer {api_key[:8]}..."
                    
                    result = api_impl.execute(
                        config_params=config_params,
                        input_params=input_params,
                        output_params={}
                    )
                    
                    api_request_debug['raw_result'] = result
                    
                    assistants_for_key = []
                    error_for_key = None
                    
                    if result.get('success'):
                        api_request_debug['request_successful'] = True
                        assistants_data = result.get('data', {})
                        assistants_for_key = assistants_data.get('assistants', [])
                        
                        # Add detailed info to each assistant
                        for assistant in assistants_for_key:
                            assistant['api_key_hash'] = api_key_hash
                            assistant['source_tool'] = tool.get('name', 'Unknown')
                            assistant['source_tool_id'] = tool.get('id')
                            assistant['debug_info'] = {
                                'retrieved_via_tool': tool.get('name'),
                                'api_key_field_used': api_key_field
                            }
                        
                        all_assistants.extend(assistants_for_key)
                        api_request_debug['assistants_count'] = len(assistants_for_key)
                    else:
                        error_for_key = result.get('message', 'Unknown error')
                        api_request_debug['error'] = error_for_key
                        debug_info['errors'].append(f"API Error for {tool.get('name')}: {error_for_key}")
                    
                    api_keys_info.append({
                        'hash': api_key_hash,
                        'tool_name': tool.get('name', 'Unknown'),
                        'tool_id': tool.get('id'),
                        'assistants_count': len(assistants_for_key),
                        'assistants': assistants_for_key,
                        'error': error_for_key,
                        'debug': api_request_debug
                    })
                    
                except Exception as e:
                    error_msg = f'Exception: {str(e)}'
                    api_request_debug['error'] = error_msg
                    api_request_debug['exception_type'] = type(e).__name__
                    debug_info['errors'].append(f"Exception for {tool.get('name')}: {error_msg}")
                    
                    api_keys_info.append({
                        'hash': api_key_hash,
                        'tool_name': tool.get('name', 'Unknown'),
                        'tool_id': tool.get('id'),
                        'assistants_count': 0,
                        'assistants': [],
                        'error': error_msg,
                        'debug': api_request_debug
                    })
                
                debug_info['api_requests'].append(api_request_debug)
        
        debug_info['step'] = 'completed'
        debug_info['total_assistants_found'] = len(all_assistants)
        
        return render_template('assistants/list.html',
                             tools_with_assistants=tools_with_assistants,
                             api_keys_info=api_keys_info,
                             all_assistants=all_assistants,
                             total_assistants=len(all_assistants),
                             total_api_keys=len(api_keys_info),
                             debug_info=debug_info)
                             
    except Exception as e:
        debug_info['step'] = 'error'
        debug_info['main_error'] = str(e)
        debug_info['exception_type'] = type(e).__name__
        
        flash(f'Error loading assistants data: {str(e)}', 'error')
        return render_template('assistants/list.html', 
                             tools_with_assistants=[],
                             api_keys_info=[],
                             all_assistants=[],
                             total_assistants=0,
                             total_api_keys=0,
                             debug_info=debug_info)
