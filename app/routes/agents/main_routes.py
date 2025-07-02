"""
Main agent routes - Core CRUD operations for agents
Handles listing, creating, viewing, editing, and deleting agents
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response, current_app
from app.utils.data_manager import agents_manager, tools_manager
from app.utils.validation import DataValidator
from app.utils.assistant_manager import assistant_manager
import uuid
import os
from datetime import datetime
import json
import openai

# Get blueprint from the parent module
from app.routes.agents import agents_bp

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
        
        # Sort agents by created_at descending (newest first)
        agents.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return render_template('agents/list.html', 
                             agents=agents, 
                             categories=categories,
                             stats={
                                 'total': total_agents,
                                 'active': active_agents, 
                                 'inactive': inactive_agents
                             },
                             filters={
                                 'category': category_filter,
                                 'status': status_filter,
                                 'search': search_query
                             })
    except Exception as e:
        current_app.logger.error(f"Error loading agents: {str(e)}")
        flash(f'Error loading agents: {str(e)}', 'error')
        return render_template('agents/list.html', 
                             agents=[], 
                             categories=[],
                             stats={'total': 0, 'active': 0, 'inactive': 0},
                             filters={'category': '', 'status': '', 'search': ''})

@agents_bp.route('/create', methods=['GET', 'POST'])
def create_agent():
    """Create new agent"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            category = request.form.get('category', 'General')
            
            if not name:
                flash('Agent name is required', 'error')
                return redirect(url_for('agents.create_agent'))
            
            # Create agent data
            agent_data = {
                'id': str(uuid.uuid4()),
                'name': name,
                'description': description,
                'category': category,
                'status': 'active',
                'tasks': [],
                'knowledge_base': [],
                'global_variables': {},
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Save agent
            agents_manager.save(agent_data)
            
            flash(f'Agent "{name}" created successfully', 'success')
            return redirect(url_for('agents.view_agent', agent_id=agent_data['id']))
            
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
        
        # Get all tools for agent configuration
        all_tools = tools_manager.get_all()
        
        return render_template('agents/view.html', agent=agent, all_tools=all_tools)
        
    except Exception as e:
        current_app.logger.error(f"Error loading agent {agent_id}: {str(e)}")
        flash(f'Error loading agent: {str(e)}', 'error')
        return redirect(url_for('agents.list_agents'))

@agents_bp.route('/edit/<agent_id>', methods=['GET', 'POST'])
def edit_agent(agent_id):
    """Edit agent"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            flash('Agent not found', 'error')
            return redirect(url_for('agents.list_agents'))
        
        if request.method == 'POST':
            # Update agent data from form
            agent['name'] = request.form.get('name', agent.get('name', ''))
            agent['description'] = request.form.get('description', agent.get('description', ''))
            agent['category'] = request.form.get('category', agent.get('category', 'General'))
            agent['status'] = request.form.get('status', agent.get('status', 'active'))
            
            # Handle AI configuration
            agent['ai_assistant_tool'] = request.form.get('ai_assistant_tool', '')
            agent['model'] = request.form.get('model', '')
            agent['instructions'] = request.form.get('instructions', '')
            agent['assistant_id'] = request.form.get('assistant_id', '')
            
            # Handle tool configuration
            enabled_tools = request.form.getlist('enabled_tools')
            agent['enabled_tools'] = enabled_tools
            
            # Handle quick actions
            quick_actions_json = request.form.get('quick_actions', '[]')
            try:
                agent['quick_actions'] = json.loads(quick_actions_json)
            except json.JSONDecodeError:
                agent['quick_actions'] = []
            
            # Handle global variables
            global_vars_json = request.form.get('global_variables', '{}')
            try:
                agent['global_variables'] = json.loads(global_vars_json)
            except json.JSONDecodeError:
                agent['global_variables'] = {}
            
            # Handle checkboxes
            agent['use_as_agent'] = bool(request.form.get('use_as_agent'))
            agent['use_as_insight'] = bool(request.form.get('use_as_insight'))
            
            # Update timestamp
            agent['updated_at'] = datetime.now().isoformat()
            
            # Validate data
            validator = DataValidator()
            is_valid, validation_errors = validator.validate_agent_data(agent)
            if not is_valid:
                for error in validation_errors:
                    flash(error, 'error')
                # Filter assistant tools for the error case too
                all_tools = tools_manager.get_all()
                assistant_tools = []
                for tool in all_tools:
                    # Check if tool has AI Assistant Integration enabled in options
                    tool_options = tool.get('options', {})
                    assistant_options = tool_options.get('assistant', {})
                    if assistant_options.get('enabled', False):
                        assistant_tools.append(tool)
                return render_template('agents/edit.html', agent=agent, all_tools=all_tools, assistant_tools=assistant_tools)
            
            # Handle OpenAI Assistant creation/synchronization
            try:
                # Check if AI assistant tool is configured
                ai_tool = agent.get('ai_assistant_tool', '')
                if ai_tool and ai_tool.startswith('tool:openai_assistant'):
                    # Get current assistant ID
                    current_assistant_id = agent.get('assistant_id', '')
                    
                    if not current_assistant_id:
                        # No assistant exists, create a new one
                        try:
                            new_assistant_id = assistant_manager.create_assistant_for_agent(agent)
                            if new_assistant_id:
                                agent['assistant_id'] = new_assistant_id
                                flash(f'Created new OpenAI Assistant {new_assistant_id[:8]}... for agent', 'success')
                            else:
                                flash('Could not create OpenAI Assistant. Please check your configuration.', 'warning')
                        except Exception as e:
                            current_app.logger.error(f"Error creating assistant for agent {agent_id}: {e}")
                            flash(f'Warning: Could not create OpenAI Assistant: {str(e)}', 'warning')
                    else:
                        # Assistant exists, synchronize configuration
                        try:
                            success = assistant_manager.update_assistant_for_agent(agent)
                            if success:
                                flash(f'Synchronized agent configuration with OpenAI Assistant {current_assistant_id[:8]}...', 'info')
                            else:
                                flash('Could not synchronize with OpenAI Assistant. Please check the configuration.', 'warning')
                        except Exception as e:
                            current_app.logger.error(f"Error updating assistant for agent {agent_id}: {e}")
                            flash(f'Warning: Could not sync with OpenAI Assistant: {str(e)}', 'warning')
                else:
                    # AI assistant tool not configured or different tool selected
                    if agent.get('assistant_id'):
                        # Agent had an assistant but AI tool was removed/changed
                        flash('AI Assistant tool was removed. The existing Assistant connection remains but won\'t be updated.', 'info')
                            
            except Exception as e:
                current_app.logger.error(f"Error handling OpenAI Assistant for agent {agent_id}: {str(e)}")
                flash(f'Warning: Assistant management error: {str(e)}', 'warning')
            
            # Save agent
            agents_manager.save(agent)
            
            flash(f'Agent "{agent["name"]}" updated successfully', 'success')
            return redirect(url_for('agents.view_agent', agent_id=agent_id))
        
        # GET request - show edit form
        all_tools = tools_manager.get_all()
        
        # Filter tools that have AI Assistant Integration enabled
        assistant_tools = []
        for tool in all_tools:
            # Check if tool has AI Assistant Integration enabled in options
            tool_options = tool.get('options', {})
            assistant_options = tool_options.get('assistant', {})
            if assistant_options.get('enabled', False):
                assistant_tools.append(tool)
        
        return render_template('agents/edit.html', 
                             agent=agent, 
                             all_tools=all_tools, 
                             assistant_tools=assistant_tools)
        
    except Exception as e:
        current_app.logger.error(f"Error editing agent {agent_id}: {str(e)}")
        flash(f'Error editing agent: {str(e)}', 'error')
        return redirect(url_for('agents.list_agents'))

@agents_bp.route('/delete/<agent_id>', methods=['POST'])
def delete_agent(agent_id):
    """Delete agent"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            flash('Agent not found', 'error')
            return redirect(url_for('agents.list_agents'))
        
        # Delete agent
        if agents_manager.delete(agent_id):
            flash(f'Agent "{agent.get("name", "Unknown")}" deleted successfully', 'success')
        else:
            flash('Error deleting agent', 'error')
        
        return redirect(url_for('agents.list_agents'))
        
    except Exception as e:
        current_app.logger.error(f"Error deleting agent {agent_id}: {str(e)}")
        flash(f'Error deleting agent: {str(e)}', 'error')
        return redirect(url_for('agents.list_agents'))

@agents_bp.route('/duplicate/<agent_id>', methods=['POST'])
def duplicate_agent(agent_id):
    """Duplicate an existing agent"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            flash('Agent not found', 'error')
            return redirect(url_for('agents.list_agents'))
        
        # Create duplicate with new ID
        new_agent = agent.copy()
        new_agent['id'] = str(uuid.uuid4())
        new_agent['name'] = f"{agent['name']} (Copy)"
        new_agent['created_at'] = datetime.now().isoformat()
        new_agent['updated_at'] = datetime.now().isoformat()
        
        # Reset any session-specific data
        new_agent['tasks'] = []
        
        # Save duplicate
        agents_manager.save(new_agent)
        
        flash(f'Agent duplicated as "{new_agent["name"]}"', 'success')
        return redirect(url_for('agents.edit_agent', agent_id=new_agent['id']))
        
    except Exception as e:
        current_app.logger.error(f"Error duplicating agent {agent_id}: {str(e)}")
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
        
        # Create clean export data (remove internal fields)
        export_data = {k: v for k, v in agent.items() 
                      if k not in ['id', 'created_at', 'updated_at']}
        
        # Create response
        response = make_response(json.dumps(export_data, indent=2))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename=agent_{agent["name"]}.json'
        
        return response
        
    except Exception as e:
        current_app.logger.error(f"Error exporting agent {agent_id}: {str(e)}")
        flash(f'Error exporting agent: {str(e)}', 'error')
        return redirect(url_for('agents.list_agents'))

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
            'use_as_agent': True,
            'use_as_insight': True,
            'quick_actions': [],
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

@agents_bp.route('/reconnect/<agent_id>', methods=['POST'])
def reconnect_agent(agent_id):
    """Reconnect agent to assistant"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            flash('Agent not found', 'error')
            return redirect(url_for('agents.list_agents'))
        
        # Here you could add logic to re-sync with OpenAI Assistant
        # For now, just show success message
        flash(f'Agent "{agent.get("name", "Unknown")}" reconnected successfully', 'success')
        return redirect(url_for('agents.view_agent', agent_id=agent_id))
        
    except Exception as e:
        current_app.logger.error(f"Error reconnecting agent {agent_id}: {str(e)}")
        flash(f'Error reconnecting agent: {str(e)}', 'error')
        return redirect(url_for('agents.view_agent', agent_id=agent_id))

@agents_bp.route('/cleanup/<agent_id>', methods=['POST'])
def cleanup_agent(agent_id):
    """Clean up agent data"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            flash('Agent not found', 'error')
            return redirect(url_for('agents.list_agents'))
        
        # Reset tasks and knowledge base
        agent['tasks'] = []
        agent['knowledge_base'] = []
        agent['updated_at'] = datetime.now().isoformat()
        
        # Save agent
        agents_manager.save(agent)
        
        flash(f'Agent "{agent.get("name", "Unknown")}" cleaned up successfully', 'success')
        return redirect(url_for('agents.view_agent', agent_id=agent_id))
        
    except Exception as e:
        current_app.logger.error(f"Error cleaning up agent {agent_id}: {str(e)}")
        flash(f'Error cleaning up agent: {str(e)}', 'error')
        return redirect(url_for('agents.view_agent', agent_id=agent_id))

@agents_bp.route('/reassign_assistant/<agent_id>', methods=['POST'])
def reassign_assistant(agent_id):
    """Reassign agent to a different OpenAI assistant"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return jsonify({'success': False, 'error': 'Agent not found'}), 404
        
        data = request.get_json()
        new_assistant_id = data.get('assistant_id', '').strip()
        
        if not new_assistant_id:
            return jsonify({'success': False, 'error': 'Assistant ID is required'}), 400
        
        # Reassign the assistant
        try:
            assistant_manager.reassign_assistant(agent, new_assistant_id)
            
            # Update timestamp
            agent['updated_at'] = datetime.now().isoformat()
            
            # Save agent
            agents_manager.save(agent)
            
            return jsonify({
                'success': True,
                'message': f'Agent reassigned to assistant {new_assistant_id[:8]}...',
                'assistant_id': new_assistant_id
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
        
    except Exception as e:
        current_app.logger.error(f"Error reassigning assistant for agent {agent_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@agents_bp.route('/create_assistant/<agent_id>', methods=['POST'])
def create_assistant(agent_id):
    """Create a new OpenAI assistant for the agent"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return jsonify({'success': False, 'error': 'Agent not found'}), 404
        
        # Create new assistant
        try:
            new_assistant_id = assistant_manager.create_assistant_for_agent(agent)
            
            # Update agent with new assistant ID
            agent['assistant_id'] = new_assistant_id
            agent['updated_at'] = datetime.now().isoformat()
            
            # Save agent
            agents_manager.save(agent)
            
            return jsonify({
                'success': True,
                'message': f'Created new assistant {new_assistant_id[:8]}...',
                'assistant_id': new_assistant_id
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
        
    except Exception as e:
        current_app.logger.error(f"Error creating assistant for agent {agent_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@agents_bp.route('/sync_assistant/<agent_id>', methods=['POST'])
def sync_assistant(agent_id):
    """Synchronize agent configuration with OpenAI assistant"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return jsonify({'success': False, 'error': 'Agent not found'}), 404
        
        assistant_id = agent.get('assistant_id')
        if not assistant_id:
            return jsonify({'success': False, 'error': 'No assistant configured for this agent'}), 400
        
        # Sync assistant
        try:
            assistant_manager.update_assistant_for_agent(agent)
            
            return jsonify({
                'success': True,
                'message': f'Synchronized with assistant {assistant_id[:8]}...'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
        
    except Exception as e:
        current_app.logger.error(f"Error syncing assistant for agent {agent_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
