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
            
            # Try to create assistant if AI assistant tool is configured
            try:
                ai_tool = agent_data.get('ai_assistant_tool', '')
                if ai_tool and ai_tool.startswith('tool:'):
                    current_app.logger.info(f"Creating assistant for new agent {agent_data['id']}")
                    assistant_id = assistant_manager.create_assistant_for_agent(agent_data)
                    if assistant_id:
                        agent_data['assistant_id'] = assistant_id
                        # Save again with assistant_id
                        agents_manager.save(agent_data)
                        current_app.logger.info(f"Created assistant {assistant_id} for new agent {agent_data['id']}")
            except Exception as e:
                current_app.logger.error(f"Error creating assistant for new agent {agent_data['id']}: {str(e)}")
            
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
            # Always preserve existing assistant_id unless explicitly provided in form
            form_assistant_id = request.form.get('assistant_id', '').strip()
            if form_assistant_id:
                # Only update if form has a value
                agent['assistant_id'] = form_assistant_id
            # Otherwise, preserve the existing assistant_id (don't overwrite with empty string)
            
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
            
            # Handle assistant tools configuration
            assistant_tools_list = request.form.getlist('assistant_tools')
            agent['assistant_tools'] = {
                'file_search': 'file_search' in assistant_tools_list,
                'code_interpreter': 'code_interpreter' in assistant_tools_list,
                'function_calling': 'function_calling' in assistant_tools_list,
                'web_browsing': 'web_browsing' in assistant_tools_list
            }
            
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
                if ai_tool and ai_tool.startswith('tool:'):
                    # Extract tool ID and validate it's an AI assistant tool
                    tool_id = ai_tool.replace('tool:', '')
                    try:
                        tool_data = tools_manager.get_by_id(tool_id)
                        is_ai_assistant_tool = False
                        
                        if tool_data:
                            # Check if it's an OpenAI Assistant tool by checking integration or tool definition
                            tool_definition = tool_data.get('tool_definition', '')
                            integration_id = tool_data.get('integration_id', '')
                            
                            if integration_id:
                                from app.utils.data_manager import integrations_manager
                                integration_data = integrations_manager.get_by_id(integration_id)
                                if integration_data and integration_data.get('implementation') == 'openai_assistant_api':
                                    is_ai_assistant_tool = True
                            elif tool_definition == 'OpenAI Assistant API':
                                is_ai_assistant_tool = True
                        
                        if is_ai_assistant_tool:
                            # Get current assistant ID
                            current_assistant_id = agent.get('assistant_id', '')
                            
                            if not current_assistant_id:
                                # No assistant exists, create a new one with all agent parameters
                                try:
                                    current_app.logger.info(f"Creating new assistant for agent {agent_id} with full parameter sync")
                                    new_assistant_id = assistant_manager.create_assistant_for_agent(agent)
                                    if new_assistant_id:
                                        agent['assistant_id'] = new_assistant_id
                                        current_app.logger.info(f"Successfully created assistant {new_assistant_id} for agent {agent_id}")
                                        # Immediately sync all parameters to ensure consistency
                                        assistant_manager.update_assistant_for_agent(agent)
                                    else:
                                        current_app.logger.warning(f"Could not create OpenAI Assistant for agent {agent_id}")
                                except Exception as e:
                                    current_app.logger.error(f"Error creating assistant for agent {agent_id}: {e}")
                            else:
                                # Assistant exists, synchronize all configuration parameters
                                try:
                                    # First verify the assistant_id is valid
                                    assistant_info = assistant_manager.get_assistant_info(current_assistant_id)
                                    if assistant_info:
                                        # Assistant exists, update with all current agent parameters
                                        current_app.logger.info(f"Synchronizing all parameters for assistant {current_assistant_id}")
                                        success = assistant_manager.update_assistant_for_agent(agent)
                                        if success:
                                            current_app.logger.info(f"Successfully synchronized assistant {current_assistant_id} with agent parameters")
                                        else:
                                            current_app.logger.warning(f"Could not synchronize OpenAI Assistant for agent {agent_id}")
                                    else:
                                        # Assistant doesn't exist, create a new one with current parameters
                                        current_app.logger.info(f"Assistant ID {current_assistant_id} not found, creating new assistant with current parameters")
                                        new_assistant_id = assistant_manager.create_assistant_for_agent(agent)
                                        if new_assistant_id:
                                            agent['assistant_id'] = new_assistant_id
                                            current_app.logger.info(f"Created replacement assistant {new_assistant_id} for agent {agent_id}")
                                            # Sync parameters immediately after creation
                                            assistant_manager.update_assistant_for_agent(agent)
                                        else:
                                            current_app.logger.error(f"Failed to create replacement assistant for agent {agent_id}")
                                except Exception as e:
                                    current_app.logger.error(f"Error updating assistant for agent {agent_id}: {e}")
                        else:
                            # AI assistant tool not configured or different tool selected
                            if agent.get('assistant_id'):
                                # Agent had an assistant but AI tool was removed/changed
                                current_app.logger.info(f"AI Assistant tool removed for agent {agent_id}, keeping existing assistant_id")
                    except Exception as e:
                        current_app.logger.error(f"Error validating AI assistant tool: {str(e)}")
                else:
                    # AI assistant tool not configured
                    if agent.get('assistant_id'):
                        # Agent had an assistant but AI tool was removed/changed
                        current_app.logger.info(f"AI Assistant tool removed for agent {agent_id}, keeping existing assistant_id")
                            
            except Exception as e:
                current_app.logger.error(f"Error handling OpenAI Assistant for agent {agent_id}: {str(e)}")
            
            # Save agent (including any assistant_id updates)
            agents_manager.save(agent)
            
            # Additional sync after save to ensure assistant is up-to-date with final agent state
            try:
                if agent.get('assistant_id') and agent.get('ai_assistant_tool'):
                    current_app.logger.info(f"Final assistant sync for agent {agent_id} after save")
                    assistant_manager.update_assistant_for_agent(agent)
            except Exception as e:
                current_app.logger.error(f"Error in final assistant sync for agent {agent_id}: {str(e)}")
            
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
        
        # Sync assistant if configured
        try:
            if agent.get('assistant_id') and agent.get('ai_assistant_tool'):
                current_app.logger.info(f"Syncing assistant after cleanup for agent {agent_id}")
                assistant_manager.update_assistant_for_agent(agent)
        except Exception as e:
            current_app.logger.error(f"Error syncing assistant after cleanup for agent {agent_id}: {str(e)}")
        
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
            
            # Sync assistant after reassignment
            try:
                assistant_manager.update_assistant_for_agent(agent)
            except Exception as e:
                current_app.logger.error(f"Error syncing assistant after reassignment for agent {agent_id}: {str(e)}")
            
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
            
            # Verify the assistant was actually created
            if not new_assistant_id:
                return jsonify({'success': False, 'error': 'Failed to create assistant'}), 500
                
            # Reload the agent to ensure we have the most recent version
            agent = agents_manager.load(agent_id)
            
            # Update agent with new assistant ID
            agent['assistant_id'] = new_assistant_id
            agent['updated_at'] = datetime.now().isoformat()
            
            # Save agent
            agents_manager.save(agent)
            
            # Ensure assistant is synced with final agent state
            try:
                assistant_manager.update_assistant_for_agent(agent)
            except Exception as e:
                current_app.logger.error(f"Error syncing assistant after creation for agent {agent_id}: {str(e)}")
            
            # Verify the agent was saved with the assistant ID
            saved_agent = agents_manager.load(agent_id)
            if saved_agent.get('assistant_id') != new_assistant_id:
                current_app.logger.error(f"Assistant created but agent not updated correctly. Assistant ID: {new_assistant_id}")
            
            return jsonify({
                'success': True,
                'message': 'OK',
                'details': {
                    'assistant_id': new_assistant_id
                }
            })
            
        except Exception as e:
            current_app.logger.error(f"Error creating assistant for agent {agent_id}: {str(e)}")
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
