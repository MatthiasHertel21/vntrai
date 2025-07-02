"""
Agent Routes für vntrai Agent System
Handles CRUD operations for AI agents
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response, current_app
from app.utils.data_manager import agents_manager, tools_manager
from app.utils.validation import DataValidator
import uuid
import os
from datetime import datetime
import json
from datetime import datetime
from datetime import datetime

agents_bp = Blueprint('agents', __name__)

@agents_bp.route('/')
def list_agents():
    """Agent overview page with card grid layout"""
    try:
        # Get all agents
        agents = agents_manager.load_all()
        
        # Get filter parameters
        category_filter = request.args.get('category', '')
        status_filter = request.args.get('status', '')
        search_query = request.args.get('search', '')
        
        # Apply filters
        if category_filter:
            agents = [a for a in agents if a.get('category', '').lower() == category_filter.lower()]
        
        if status_filter:
            agents = [a for a in agents if a.get('status') == status_filter]
        
        if search_query:
            search_lower = search_query.lower()
            agents = [a for a in agents if 
                     search_lower in a.get('name', '').lower() or 
                     search_lower in a.get('description', '').lower()]
        
        # Get statistics
        total_agents = len(agents_manager.load_all())
        active_agents = len([a for a in agents_manager.load_all() if a.get('status') == 'active'])
        inactive_agents = len([a for a in agents_manager.load_all() if a.get('status') == 'inactive'])
        
        # Get unique categories for filter
        all_agents = agents_manager.load_all()
        categories = list(set([a.get('category', 'General') for a in all_agents if a.get('category')]))
        categories.sort()
        
        # Add statistics to each agent
        for agent in agents:
            agent_stats = agents_manager.get_single_agent_statistics(agent['id'])
            agent.update(agent_stats)
        
        stats = {
            'total': total_agents,
            'active': active_agents,
            'inactive': inactive_agents,
            'other': total_agents - active_agents - inactive_agents
        }
        
        return render_template('agents/list.html', 
                             agents=agents,
                             stats=stats,
                             categories=categories,
                             category_filter=category_filter,
                             status_filter=status_filter,
                             search_query=search_query)
                             
    except Exception as e:
        flash(f'Error loading agents: {str(e)}', 'error')
        return render_template('agents/list.html', 
                             agents=[],
                             stats={'total': 0, 'active': 0, 'inactive': 0, 'other': 0},
                             categories=[],
                             category_filter='',
                             status_filter='',
                             search_query='')

@agents_bp.route('/create', methods=['GET', 'POST'])
def create_agent():
    """Create new agent"""
    if request.method == 'GET':
        return render_template('agents/create.html')
    
    try:
        # Extract form data
        name = request.form.get('name', '').strip()
        category = request.form.get('category', 'General').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Agent name is required', 'error')
            return render_template('agents/create.html')
        
        # Create agent
        agent = agents_manager.create_agent(name, category, description)
        if agent:
            flash(f'Agent "{name}" created successfully', 'success')
            return redirect(url_for('agents.edit_agent', agent_id=agent['id']))
        else:
            flash('Failed to create agent', 'error')
            
    except Exception as e:
        flash(f'Error creating agent: {str(e)}', 'error')
    
    return render_template('agents/create.html')

@agents_bp.route('/view/<agent_id>')
def view_agent(agent_id):
    """View agent details"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            flash('Agent not found', 'error')
            return redirect(url_for('agents.list_agents'))
        
        # Get agent statistics
        stats = agents_manager.get_single_agent_statistics(agent_id)
        agent.update(stats)
        
        return render_template('agents/view.html', agent=agent)
        
    except Exception as e:
        flash(f'Error loading agent: {str(e)}', 'error')
        return redirect(url_for('agents.list_agents'))

@agents_bp.route('/edit/<agent_id>', methods=['GET', 'POST'])
def edit_agent(agent_id):
    """Edit agent with two-column layout"""
    if request.method == 'GET':
        try:
            agent = agents_manager.load(agent_id)
            if not agent:
                flash('Agent not found', 'error')
                return redirect(url_for('agents.list_agents'))
            
            # Ensure migration of use_as fields for display
            if 'use_as_agent' not in agent:
                agent['use_as_agent'] = True
            if 'use_as_insight' not in agent:
                agent['use_as_insight'] = False
            if 'quick_actions' not in agent:
                agent['quick_actions'] = []
            
            # Get available tools with assistant functionality enabled
            available_tools = tools_manager.load_all()
            assistant_tools = []
            for tool in available_tools:
                assistant_options = tool.get('options', {}).get('assistant', {})
                if assistant_options.get('enabled', False):
                    assistant_tools.append(tool)
            
            return render_template('agents/edit.html', 
                                 agent=agent,
                                 assistant_tools=assistant_tools)
                                 
        except Exception as e:
            flash(f'Error loading agent: {str(e)}', 'error')
            return redirect(url_for('agents.list_agents'))
    
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            flash('Agent not found', 'error')
            return redirect(url_for('agents.list_agents'))
        
        # Migrate old agents to have use_as fields if they don't exist
        if 'use_as_agent' not in agent:
            agent['use_as_agent'] = True  # Default for existing agents
        if 'use_as_insight' not in agent:
            agent['use_as_insight'] = False  # Default for existing agents
        if 'quick_actions' not in agent:
            agent['quick_actions'] = []  # Default empty quick actions
        
        # Update basic information
        if 'name' in request.form:
            agent['name'] = request.form.get('name', '').strip()
        if 'category' in request.form:
            category = request.form.get('category', 'General').strip()
            # Handle custom categories
            if category == '__NEW__':
                category = 'General'  # Fallback if somehow __NEW__ is submitted
            elif request.form.get('custom_category', '').strip():
                category = request.form.get('custom_category', '').strip()
            agent['category'] = category
        if 'description' in request.form:
            agent['description'] = request.form.get('description', '').strip()
        if 'status' in request.form:
            agent['status'] = request.form.get('status', 'inactive')
        if 'ai_assistant_tool' in request.form:
            agent['ai_assistant_tool'] = request.form.get('ai_assistant_tool', '')
        if 'model' in request.form:
            agent['model'] = request.form.get('model', 'gpt-4-turbo-preview')
        if 'instructions' in request.form:
            agent['instructions'] = request.form.get('instructions', '')
        
        # Update "use as" options - handle checkbox behavior
        # Checkboxes are only sent when checked, so we need to check for presence
        agent['use_as_agent'] = 'use_as_agent' in request.form
        agent['use_as_insight'] = 'use_as_insight' in request.form
        
        # Debug: Log the form data and resulting values
        print(f"DEBUG: Form data: use_as_agent={'use_as_agent' in request.form}, use_as_insight={'use_as_insight' in request.form}")
        print(f"DEBUG: Agent values: use_as_agent={agent['use_as_agent']}, use_as_insight={agent['use_as_insight']}")
        
        # Debug: Log the form data
        print(f"DEBUG: Form data contains use_as_agent: {'use_as_agent' in request.form}")
        print(f"DEBUG: Form data contains use_as_insight: {'use_as_insight' in request.form}")
        print(f"DEBUG: Agent use_as_agent set to: {agent.get('use_as_agent')}")
        print(f"DEBUG: Agent use_as_insight set to: {agent.get('use_as_insight')}")
        
        # Sanitize and validate agent data
        sanitized_agent = DataValidator.sanitize_agent_data(agent)
        
        # Debug: Log the agent state after sanitization
        print(f"DEBUG: After sanitize - use_as_agent={sanitized_agent.get('use_as_agent')}, use_as_insight={sanitized_agent.get('use_as_insight')}")
        
        # Validate the data
        is_valid, validation_errors = DataValidator.validate_agent_data(sanitized_agent)
        if not is_valid:
            for error in validation_errors:
                flash(error, 'error')
            return redirect(url_for('agents.edit_agent', agent_id=agent_id))
        
        # Debug: Log the agent state before saving
        print(f"DEBUG: Before save - use_as_agent={sanitized_agent.get('use_as_agent')}, use_as_insight={sanitized_agent.get('use_as_insight')}")
        
        if agents_manager.save(sanitized_agent):
            # Verify the saved data
            saved_agent = agents_manager.load(agent_id)
            print(f"DEBUG: After save - use_as_agent={saved_agent.get('use_as_agent')}, use_as_insight={saved_agent.get('use_as_insight')}")
            flash('Agent updated successfully', 'success')
        else:
            flash('Failed to update agent', 'error')
        
        return redirect(url_for('agents.edit_agent', agent_id=agent_id))
        
    except Exception as e:
        flash(f'Error updating agent: {str(e)}', 'error')
        return redirect(url_for('agents.edit_agent', agent_id=agent_id))

@agents_bp.route('/delete/<agent_id>', methods=['POST'])
def delete_agent(agent_id):
    """Delete agent"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            if request.content_type == 'application/json':
                return jsonify({'error': 'Agent not found'}), 404
            flash('Agent not found', 'error')
            return redirect(url_for('agents.list_agents'))
        
        agent_name = agent.get('name', 'Unknown')
        
        if agents_manager.delete(agent_id):
            if request.content_type == 'application/json':
                return jsonify({'success': True, 'message': f'Agent "{agent_name}" deleted successfully'})
            flash(f'Agent "{agent_name}" deleted successfully', 'success')
        else:
            if request.content_type == 'application/json':
                return jsonify({'error': 'Failed to delete agent'}), 500
            flash('Failed to delete agent', 'error')
            
    except Exception as e:
        if request.content_type == 'application/json':
            return jsonify({'error': str(e)}), 500
        flash(f'Error deleting agent: {str(e)}', 'error')
    
    return redirect(url_for('agents.list_agents'))

@agents_bp.route('/duplicate/<agent_id>', methods=['POST'])
def duplicate_agent(agent_id):
    """Duplicate agent"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            flash('Agent not found', 'error')
            return redirect(url_for('agents.list_agents'))
        
        # Create copy with new ID and name
        new_agent = agent.copy()
        new_agent['id'] = str(uuid.uuid4())
        new_agent['name'] = f"{agent['name']} (Copy)"
        new_agent['created_at'] = datetime.now().isoformat()
        new_agent['updated_at'] = datetime.now().isoformat()
        new_agent['assistant_id'] = None  # Reset assistant connection
        
        # Reset task and knowledge IDs
        for task in new_agent.get('tasks', []):
            task['id'] = str(uuid.uuid4())
        
        for knowledge_item in new_agent.get('knowledge_base', []):
            knowledge_item['id'] = str(uuid.uuid4())
        
        if agents_manager.save(new_agent):
            flash(f'Agent duplicated successfully', 'success')
            return redirect(url_for('agents.edit_agent', agent_id=new_agent['id']))
        else:
            flash('Failed to duplicate agent', 'error')
            
    except Exception as e:
        flash(f'Error duplicating agent: {str(e)}', 'error')
    
    return redirect(url_for('agents.list_agents'))

@agents_bp.route('/export/<agent_id>')
def export_agent(agent_id):
    """Export agent configuration as JSON"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            flash('Agent not found', 'error')
            return redirect(url_for('agents.list_agents'))
        
        # Create clean export data
        export_data = {
            'name': agent.get('name', ''),
            'category': agent.get('category', 'General'),
            'description': agent.get('description', ''),
            'ai_assistant_tool': agent.get('ai_assistant_tool', ''),
            'model': agent.get('model', 'gpt-4-turbo-preview'),
            'instructions': agent.get('instructions', ''),
            'tasks': agent.get('tasks', []),
            'knowledge_base': agent.get('knowledge_base', []),
            'exported_at': datetime.now().isoformat(),
            'export_version': '1.0'
        }
        
        response = make_response(json.dumps(export_data, indent=2))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename="agent_{agent["name"].replace(" ", "_")}.json"'
        return response
        
    except Exception as e:
        flash(f'Error exporting agent: {str(e)}', 'error')
        return redirect(url_for('agents.list_agents'))

@agents_bp.route('/reconnect/<agent_id>', methods=['POST'])
def reconnect_agent(agent_id):
    """Reconnect agent's AI assistant"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        # Reset assistant connection and generate new system prompt
        agent['assistant_id'] = None
        agent['updated_at'] = datetime.now().isoformat()
        
        # Save changes
        if agents_manager.save(agent):
            return jsonify({'success': True, 'message': 'Assistant reconnected successfully'})
        else:
            return jsonify({'error': 'Failed to reconnect assistant'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/cleanup/<agent_id>', methods=['POST'])
def cleanup_agent(agent_id):
    """Clean up agent's temporary files"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        # Clean up agent directory (temporary files, caches, etc.)
        agent_dir = f"data/agents/{agent_id}"
        temp_files_cleaned = 0
        
        if os.path.exists(agent_dir):
            # Remove temporary files (you can extend this logic)
            for root, dirs, files in os.walk(agent_dir):
                for file in files:
                    if file.endswith('.tmp') or file.startswith('temp_'):
                        os.remove(os.path.join(root, file))
                        temp_files_cleaned += 1
        
        return jsonify({
            'success': True, 
            'message': f'Cleanup completed. {temp_files_cleaned} temporary files removed.'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API Routes for AJAX operations

@agents_bp.route('/api/task', methods=['POST'])
def api_create_task():
    """Create new task for agent via API"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        task_data = data.get('task', {})
        
        if not agent_id or not task_data:
            return jsonify({'error': 'Missing agent_id or task data'}), 400
        
        success = agents_manager.add_task(agent_id, task_data)
        if success:
            return jsonify({'message': 'Task created successfully'})
        else:
            return jsonify({'error': 'Failed to create task'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/api/task/<task_id>', methods=['PUT'])
def api_update_task(task_id):
    """Update task via API"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        task_data = data.get('task', {})
        
        if not agent_id:
            return jsonify({'error': 'Missing agent_id'}), 400
        
        success = agents_manager.update_task(agent_id, task_id, task_data)
        if success:
            return jsonify({'message': 'Task updated successfully'})
        else:
            return jsonify({'error': 'Failed to update task'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/api/task/<task_id>', methods=['DELETE'])
def api_delete_task(task_id):
    """Delete task via API"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return jsonify({'error': 'Missing agent_id'}), 400
        
        success = agents_manager.remove_task(agent_id, task_id)
        if success:
            return jsonify({'message': 'Task deleted successfully'})
        else:
            return jsonify({'error': 'Failed to delete task'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/api/tasks/reorder', methods=['POST'])
def api_reorder_tasks():
    """DEPRECATED: Legacy task reorder API - use Sprint 18 Task Management API instead"""
    return jsonify({
        'error': 'This API endpoint has been deprecated. Please use the Sprint 18 Task Management API: /api/task_management/agent/<agent_uuid>/tasks/reorder',
        'deprecated': True,
        'migration_url': '/api/task_management/agent/<agent_uuid>/tasks/reorder'
    }), 410  # HTTP 410 Gone

@agents_bp.route('/api/knowledge', methods=['POST'])
def api_create_knowledge():
    """Create knowledge item via API"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        knowledge_data = data.get('knowledge', {})
        
        if not agent_id or not knowledge_data:
            return jsonify({'error': 'Missing agent_id or knowledge data'}), 400
        
        success = agents_manager.add_knowledge_item(agent_id, knowledge_data)
        if success:
            return jsonify({'message': 'Knowledge item created successfully'})
        else:
            return jsonify({'error': 'Failed to create knowledge item'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/api/knowledge/<knowledge_id>', methods=['PUT'])
def api_update_knowledge(knowledge_id):
    """Update knowledge item via API"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        knowledge_data = data.get('knowledge', {})
        
        if not agent_id:
            return jsonify({'error': 'Missing agent_id'}), 400
        
        success = agents_manager.update_knowledge_item(agent_id, knowledge_id, knowledge_data)
        if success:
            return jsonify({'message': 'Knowledge item updated successfully'})
        else:
            return jsonify({'error': 'Failed to update knowledge item'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/api/knowledge/<knowledge_id>', methods=['DELETE'])
def api_delete_knowledge(knowledge_id):
    """Delete knowledge item via API"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return jsonify({'error': 'Missing agent_id'}), 400
        
        success = agents_manager.remove_knowledge_item(agent_id, knowledge_id)
        if success:
            return jsonify({'message': 'Knowledge item deleted successfully'})
        else:
            return jsonify({'error': 'Failed to delete knowledge item'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/create_from_assistant/<assistant_id>')
def create_from_assistant(assistant_id):
    """Create a new agent from an existing OpenAI Assistant"""
    try:
        # Find API key from tools
        all_tools = tools_manager.get_all()
        api_key = None
        
        for tool in all_tools:
            config = tool.get('config', {})
            for key, value in config.items():
                if 'api_key' in key.lower() and value and isinstance(value, str) and len(value) > 10:
                    api_key = value
                    break
            if api_key:
                break
        
        if not api_key:
            flash('No API key found for assistant access', 'error')
            return redirect(url_for('assistants.list_assistants'))
        
        # Get assistant info directly from OpenAI
        import openai
        client = openai.OpenAI(api_key=api_key)
        assistant = client.beta.assistants.retrieve(assistant_id)
        
        # Get tools list
        tools_list = []
        if hasattr(assistant, 'tools') and assistant.tools:
            tools_list = [tool.type if hasattr(tool, 'type') else str(tool) for tool in assistant.tools]
        
        # Get file_ids
        file_ids = []
        if hasattr(assistant, 'file_ids'):
            file_ids = assistant.file_ids or []
        elif hasattr(assistant, 'tool_resources'):
            if hasattr(assistant.tool_resources, 'file_search') and hasattr(assistant.tool_resources.file_search, 'vector_store_ids'):
                file_ids = assistant.tool_resources.file_search.vector_store_ids or []
        
        # Create new agent with assistant data
        agent_data = {
            'id': str(uuid.uuid4()),
            'name': assistant.name or f'Agent for {assistant_id[:8]}',
            'description': assistant.description or f'Agent created from OpenAI Assistant {assistant_id[:8]}',
            'category': 'AI Assistant',
            'status': 'active',
            'assistant_id': assistant_id,
            'ai_assistant_tool': 'tool:openai_assistant_api',
            'model': assistant.model,
            'instructions': assistant.instructions or '',
            'tools': tools_list,
            'file_ids': file_ids,
            'metadata': assistant.metadata or {} if hasattr(assistant, 'metadata') else {},
            'use_as_agent': True,  # Can be used as agent
            'use_as_insight': True,  # Also enable as insight since it's from assistant
            'quick_actions': [],  # Empty quick actions list
            'tasks': [],
            'knowledge_base': [],
            'global_variables': {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Save agent
        agents_manager.save(agent_data)
        
        flash(f'Agent "{agent_data["name"]}" created successfully from Assistant {assistant_id[:8]}', 'success')
        return redirect(url_for('agents.edit_agent', agent_id=agent_data['id']))
        
    except Exception as e:
        flash(f'Error creating agent from assistant: {str(e)}', 'error')
        return redirect(url_for('assistants.list_assistants'))

@agents_bp.route('/api/quick-actions/<agent_id>', methods=['GET', 'POST'])
def api_quick_actions(agent_id):
    """Manage quick actions for an agent"""
    try:
        if request.method == 'GET':
            # Load agent and return quick actions
            agent = agents_manager.load(agent_id)
            if not agent:
                return jsonify({'error': 'Agent not found'}), 404
            
            quick_actions = agent.get('quick_actions', [])
            return jsonify({'quick_actions': quick_actions})
        
        elif request.method == 'POST':
            # Save quick actions
            data = request.get_json()
            quick_actions = data.get('quick_actions', [])
            
            agent = agents_manager.load(agent_id)
            if not agent:
                return jsonify({'error': 'Agent not found'}), 404
            
            agent['quick_actions'] = quick_actions
            
            if agents_manager.save(agent):
                return jsonify({'success': True, 'message': 'Quick actions saved successfully'})
            else:
                return jsonify({'error': 'Failed to save quick actions'}), 500
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/api/clear-data/<agent_id>', methods=['POST'])
def api_clear_agent_data(agent_id):
    """Clear all data for an agent (threads, messages, etc.)"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        # Clear assistant thread if exists
        if agent.get('assistant_id'):
            from app.implementation_modules.openai_assistant_api import OpenAIAssistantAPI
            assistant_api = OpenAIAssistantAPI()
            
            # Get thread ID from agent
            thread_id = agent.get('thread_id')
            if thread_id:
                try:
                    # Delete the thread
                    assistant_api.client.beta.threads.delete(thread_id)
                    # Clear thread_id from agent
                    agent['thread_id'] = None
                except Exception as e:
                    print(f"Warning: Could not delete thread {thread_id}: {e}")
        
        # Clear conversation history and reset statistics
        agent['conversation_history'] = []
        agent['total_runs'] = 0
        agent['last_run'] = None
        
        # Save the updated agent
        if agents_manager.save(agent):
            return jsonify({'success': True, 'message': 'Agent data cleared successfully'})
        else:
            return jsonify({'error': 'Failed to save agent data'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Sprint 18: Task Management API Routes

@agents_bp.route('/api/<agent_id>/tasks', methods=['GET'])
def api_get_agent_tasks(agent_id):
    """API endpoint to get agent tasks (Sprint 18)"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return jsonify({'success': False, 'error': 'Agent not found'}), 404
        
        tasks = agents_manager.get_task_definitions(agent_id)
        
        return jsonify({
            'success': True,
            'tasks': tasks,
            'count': len(tasks)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@agents_bp.route('/api/<agent_id>/tasks', methods=['POST'])
def api_create_agent_task(agent_id):
    """API endpoint to create agent task (Sprint 18)"""
    try:
        # Validate agent exists first
        agent = agents_manager.load(agent_id)
        if not agent:
            return jsonify({'success': False, 'error': 'Agent not found'}), 404
        
        # Parse JSON data with better error handling
        try:
            data = request.get_json(force=True)
        except Exception as e:
            current_app.logger.error(f"JSON parsing error: {str(e)}")
            return jsonify({'success': False, 'error': f'Invalid JSON data: {str(e)}'}), 400
            
        if not data:
            current_app.logger.error("No data provided in request")
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        current_app.logger.info(f"Creating task with data: {data}")
        
        # Validate required fields
        if not data.get('name', '').strip():
            return jsonify({'success': False, 'error': 'Task name is required'}), 400
            
        if data.get('type') not in ['ai', 'tool']:
            return jsonify({'success': False, 'error': 'Task type must be "ai" or "tool"'}), 400
        
        # Create task definition with Sprint 18 structure
        task_def = {
            'uuid': str(uuid.uuid4()),
            'name': data.get('name', 'New Task').strip(),
            'type': data.get('type', 'ai'),
            'description': data.get('description', '').strip(),
            'order': data.get('order', len(agent.get('tasks', [])) + 1),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Add type-specific configuration
        if task_def['type'] == 'ai':
            task_def['ai_config'] = {
                'instructions': data.get('instructions', ''),
                'goals': data.get('goals', ''),
                'input_fields': data.get('input_fields', []),
                'output_type': data.get('output_type', 'text'),
                'output_description': data.get('output_description', '')
            }
        elif task_def['type'] == 'tool':
            task_def['tool_config'] = {
                'tool_uuid': data.get('tool_uuid', ''),
                'input_mapping': data.get('input_mapping', {}),
                'output_mapping': data.get('output_mapping', {})
            }
        
        # Add task to agent's tasks list directly
        if 'tasks' not in agent:
            agent['tasks'] = []
        
        agent['tasks'].append(task_def)
        agent['updated_at'] = datetime.now().isoformat()
        
        # Save agent with new task
        success = agents_manager.save(agent)
        
        if success:
            current_app.logger.info(f"Task created successfully: {task_def['uuid']}")
            return jsonify({
                'success': True,
                'task': task_def,
                'message': 'Task created successfully'
            })
        else:
            current_app.logger.error("Failed to save agent with new task")
            return jsonify({'success': False, 'error': 'Failed to save task'}), 500
    
    except Exception as e:
        current_app.logger.error(f"Error creating task: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Internal server error: {str(e)}'}), 500

@agents_bp.route('/api/<agent_id>/tasks/<task_uuid>', methods=['PUT'])
def api_update_agent_task(agent_id, task_uuid):
    """API endpoint to update agent task (Sprint 18)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        data['updated_at'] = datetime.now().isoformat()
        success = agents_manager.update_task_definition(agent_id, task_uuid, data)
        
        if success:
            task = agents_manager.get_task_definition(agent_id, task_uuid)
            return jsonify({
                'success': True,
                'task': task,
                'message': 'Task updated successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to update task'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@agents_bp.route('/api/<agent_id>/tasks/<task_uuid>', methods=['DELETE'])
def api_delete_agent_task(agent_id, task_uuid):
    """API endpoint to delete agent task (Sprint 18)"""
    try:
        success = agents_manager.remove_task_definition(agent_id, task_uuid)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Task deleted successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to delete task'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@agents_bp.route('/api/<agent_id>/tasks/reorder', methods=['POST'])
def api_reorder_agent_tasks(agent_id):
    """API endpoint to reorder agent tasks (Sprint 18)"""
    try:
        data = request.get_json()
        if not data or 'task_uuids' not in data:
            return jsonify({'success': False, 'error': 'task_uuids array required'}), 400
        
        success = agents_manager.reorder_task_definitions(agent_id, data['task_uuids'])
        
        if success:
            tasks = agents_manager.get_task_definitions(agent_id)
            return jsonify({
                'success': True,
                'tasks': tasks,
                'message': 'Tasks reordered successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to reorder tasks'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@agents_bp.route('/api/tools/assistant-enabled', methods=['GET'])
def api_get_assistant_enabled_tools():
    """API endpoint to get tools with assistant option enabled (Sprint 18)"""
    try:
        tools = tools_manager.get_assistant_enabled_tools()
        
        return jsonify({
            'success': True,
            'tools': tools,
            'count': len(tools)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@agents_bp.errorhandler(404)
def agents_not_found(error):
    """Custom 404 handler for agents blueprint"""
    return render_template('errors/404.html'), 404

@agents_bp.errorhandler(500)
def agents_internal_error(error):
    """Custom 500 handler for agents blueprint"""
    return render_template('errors/500.html'), 500

# Debug route for task creation troubleshooting
@agents_bp.route('/api/<agent_id>/tasks/debug', methods=['POST'])
def debug_create_agent_task(agent_id):
    """Debug endpoint for task creation issues"""
    try:
        # Log all request details
        current_app.logger.info(f"Debug task creation for agent: {agent_id}")
        current_app.logger.info(f"Request method: {request.method}")
        current_app.logger.info(f"Request headers: {dict(request.headers)}")
        current_app.logger.info(f"Request content type: {request.content_type}")
        current_app.logger.info(f"Request data: {request.get_data()}")
        
        # Simple response for debugging
        return jsonify({
            'success': True,
            'debug': True,
            'agent_id': agent_id,
            'method': request.method,
            'content_type': request.content_type,
            'has_data': bool(request.get_data()),
            'message': 'Debug endpoint reached successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Debug endpoint error: {str(e)}")
        return jsonify({
            'success': False,
            'debug': True,
            'error': str(e)
        }), 500

# Session Management Routes (Expected by templates)

@agents_bp.route('/new_session/<agent_id>', methods=['POST'])
def new_session(agent_id):
    """Create a new session/run for an agent"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            flash('Agent not found', 'error')
            return redirect(url_for('agents.list_agents'))
        
        # For now, redirect to view agent - can be enhanced to create actual sessions
        flash('New session created', 'success')
        return redirect(url_for('agents.view_agent', agent_id=agent_id))
        
    except Exception as e:
        flash(f'Error creating new session: {str(e)}', 'error')
        return redirect(url_for('agents.view_agent', agent_id=agent_id))

@agents_bp.route('/open_session/<agent_id>', methods=['POST'])
def open_session(agent_id):
    """Open existing session for an agent"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            flash('Agent not found', 'error')
            return redirect(url_for('agents.list_agents'))
        
        # For now, redirect to view agent - can be enhanced to open latest session
        flash('Session opened', 'success')
        return redirect(url_for('agents.view_agent', agent_id=agent_id))
        
    except Exception as e:
        flash(f'Error opening session: {str(e)}', 'error')
        return redirect(url_for('agents.view_agent', agent_id=agent_id))

# Task reordering endpoints
@agents_bp.route('/api/<agent_id>/tasks/<task_uuid>/move-up', methods=['POST'])
def move_task_up(agent_id, task_uuid):
    """Move a task up in the order"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return jsonify({'success': False, 'error': 'Agent not found'}), 404
        
        tasks = agent.get('tasks', [])
        if not tasks:
            return jsonify({'success': False, 'error': 'No tasks found'}), 400
        
        # Find the task index
        task_index = None
        for i, task in enumerate(tasks):
            if task.get('uuid') == task_uuid:
                task_index = i
                break
        
        if task_index is None:
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        if task_index == 0:
            return jsonify({'success': False, 'error': 'Task is already at the top'}), 400
        
        # Swap tasks
        tasks[task_index], tasks[task_index - 1] = tasks[task_index - 1], tasks[task_index]
        
        # Update order numbers
        for i, task in enumerate(tasks):
            task['order'] = i + 1
        
        # Save agent
        agent['tasks'] = tasks
        agents_manager.save(agent)
        
        return jsonify({'success': True, 'message': 'Task moved up successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Error moving task up: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@agents_bp.route('/api/<agent_id>/tasks/<task_uuid>/move-down', methods=['POST'])
def move_task_down(agent_id, task_uuid):
    """Move a task down in the order"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return jsonify({'success': False, 'error': 'Agent not found'}), 404
        
        tasks = agent.get('tasks', [])
        if not tasks:
            return jsonify({'success': False, 'error': 'No tasks found'}), 400
        
        # Find the task index
        task_index = None
        for i, task in enumerate(tasks):
            if task.get('uuid') == task_uuid:
                task_index = i
                break
        
        if task_index is None:
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        if task_index == len(tasks) - 1:
            return jsonify({'success': False, 'error': 'Task is already at the bottom'}), 400
        
        # Swap tasks
        tasks[task_index], tasks[task_index + 1] = tasks[task_index + 1], tasks[task_index]
        
        # Update order numbers
        for i, task in enumerate(tasks):
            task['order'] = i + 1
        
        # Save agent
        agent['tasks'] = tasks
        agents_manager.save(agent)
        
        return jsonify({'success': True, 'message': 'Task moved down successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Error moving task down: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Task CRUD endpoints
@agents_bp.route('/api/<agent_id>/tasks/<task_uuid>', methods=['PUT'])
def update_task(agent_id, task_uuid):
    """Update a specific task"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return jsonify({'success': False, 'error': 'Agent not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        tasks = agent.get('tasks', [])
        if not tasks:
            return jsonify({'success': False, 'error': 'No tasks found'}), 404
        
        # Find the task to update
        task_index = None
        for i, task in enumerate(tasks):
            if task.get('uuid') == task_uuid:
                task_index = i
                break
        
        if task_index is None:
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        # Update task fields
        task = tasks[task_index]
        if 'name' in data:
            task['name'] = data['name']
        if 'description' in data:
            task['description'] = data['description']
        if 'type' in data:
            task['type'] = data['type']
        if 'ai_config' in data:
            task['ai_config'] = data['ai_config']
        if 'tool_config' in data:
            task['tool_config'] = data['tool_config']
        
        # Update modified timestamp
        task['modified_at'] = datetime.utcnow().isoformat()
        
        # Save agent
        agent['tasks'] = tasks
        agents_manager.save(agent)
        
        return jsonify({
            'success': True,
            'message': 'Task updated successfully',
            'task': task
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating task: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@agents_bp.route('/api/<agent_id>/tasks/<task_uuid>', methods=['DELETE'])
def delete_task(agent_id, task_uuid):
    """Delete a specific task"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return jsonify({'success': False, 'error': 'Agent not found'}), 404
        
        tasks = agent.get('tasks', [])
        if not tasks:
            return jsonify({'success': False, 'error': 'No tasks found'}), 404
        
        # Find and remove the task
        task_index = None
        for i, task in enumerate(tasks):
            if task.get('uuid') == task_uuid:
                task_index = i
                break
        
        if task_index is None:
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        # Remove the task
        removed_task = tasks.pop(task_index)
        
        # Reorder remaining tasks
        for i, task in enumerate(tasks):
            task['order'] = i + 1
        
        # Save agent
        agent['tasks'] = tasks
        agents_manager.save(agent)
        
        return jsonify({
            'success': True,
            'message': 'Task deleted successfully',
            'deleted_task': removed_task,
            'remaining_count': len(tasks)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error deleting task: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
