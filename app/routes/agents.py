"""
Agent Routes für vntrai Agent System
Handles CRUD operations for AI agents
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from app.utils.data_manager import agents_manager, tools_manager
from app.utils.validation import DataValidator
import uuid
import os
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
            agent_stats = agents_manager.get_agent_statistics(agent['id'])
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
        stats = agents_manager.get_agent_statistics(agent_id)
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
        
        # Update basic information
        if 'name' in request.form:
            agent['name'] = request.form.get('name', '').strip()
        if 'category' in request.form:
            agent['category'] = request.form.get('category', 'General').strip()
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
        
        # Sanitize and validate agent data
        sanitized_agent = DataValidator.sanitize_agent_data(agent)
        
        # Validate the data
        is_valid, validation_errors = DataValidator.validate_agent_data(sanitized_agent)
        if not is_valid:
            for error in validation_errors:
                flash(error, 'error')
            return redirect(url_for('agents.edit_agent', agent_id=agent_id))
        
        if agents_manager.save(sanitized_agent):
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
    """Reorder tasks via API"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        task_ids = data.get('task_ids', [])
        
        if not agent_id or not task_ids:
            return jsonify({'error': 'Missing agent_id or task_ids'}), 400
        
        success = agents_manager.reorder_tasks(agent_id, task_ids)
        if success:
            return jsonify({'message': 'Tasks reordered successfully'})
        else:
            return jsonify({'error': 'Failed to reorder tasks'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        from app.utils.openai_assistant_wrapper import OpenAIAssistantAPI
        
        # Get assistant details
        openai_api = OpenAIAssistantAPI()
        assistant_result = openai_api.get_assistant(assistant_id)
        
        if not assistant_result.get('success'):
            flash(f'Assistant not found: {assistant_result.get("message", "Unknown error")}', 'error')
            return redirect(url_for('assistants.list_assistants'))
        
        assistant = assistant_result['data']
        
        # Create new agent with assistant data
        agent_data = {
            'id': str(uuid.uuid4()),
            'name': assistant.get('name', f'Agent for {assistant_id[:8]}'),
            'description': assistant.get('description', f'Agent created from OpenAI Assistant {assistant_id[:8]}'),
            'category': 'AI Assistant',
            'status': 'active',
            'assistant_id': assistant_id,
            'model': assistant.get('model', 'gpt-4-turbo-preview'),
            'instructions': assistant.get('instructions', ''),
            'tools': assistant.get('tools', []),
            'file_ids': assistant.get('file_ids', []),
            'metadata': assistant.get('metadata', {}),
            'tasks': [],
            'knowledge_base': [],
            'global_variables': {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Save agent
        agents_manager.save(agent_data['id'], agent_data)
        
        flash(f'Agent "{agent_data["name"]}" created successfully from Assistant {assistant_id[:8]}', 'success')
        return redirect(url_for('agents.edit_agent', agent_id=agent_data['id']))
        
    except Exception as e:
        flash(f'Error creating agent from assistant: {str(e)}', 'error')
        return redirect(url_for('assistants.list_assistants'))
