"""
Task management routes - Specialized endpoints for agent task operations
Handles CRUD operations for agent tasks, reordering, and task-specific API endpoints
"""

from flask import Blueprint, request, jsonify, current_app
from app.utils.data_manager import agents_manager
from datetime import datetime
import uuid

# Get blueprint from the parent module
from app.routes.agents import agents_bp

@agents_bp.route('/api/<agent_id>/tasks', methods=['GET'])
def api_get_agent_tasks(agent_id):
    """Get all tasks for a specific agent"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        tasks = agent.get('tasks', [])
        
        # Sort tasks by order
        tasks.sort(key=lambda x: x.get('order', 0))
        
        return jsonify({
            'agent_id': agent_id,
            'tasks': tasks,
            'count': len(tasks)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting tasks for agent {agent_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/<agent_id>/tasks', methods=['POST'])
def api_create_agent_task(agent_id):
    """Create a new task for a specific agent"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'error': 'Task name is required'}), 400
        
        # Get current tasks
        tasks = agent.get('tasks', [])
        
        # Create new task
        task_def = {
            'uuid': str(uuid.uuid4()),
            'name': name,
            'description': data.get('description', ''),
            'type': data.get('type', 'standard'),
            'output_variable': data.get('output_variable', ''),
            'output_type': data.get('output_type', 'text'),
            'output_description': data.get('output_description', ''),
            'output_rendering': data.get('output_rendering', 'text'),
            'order': len(tasks) + 1,
            'created_at': datetime.utcnow().isoformat(),
            'modified_at': datetime.utcnow().isoformat(),
            'ai_config': data.get('ai_config', {}),
            'tool_config': data.get('tool_config', {}),
            'status': 'pending'
        }
        
        # Add task to agent
        tasks.append(task_def)
        agent['tasks'] = tasks
        agent['updated_at'] = datetime.utcnow().isoformat()
        
        # Save agent
        agents_manager.save(agent)
        
        return jsonify({
            'success': True,
            'message': 'Task created successfully',
            'task': task_def
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating task for agent {agent_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/<agent_id>/tasks/<task_uuid>', methods=['PUT'])
def api_update_agent_task(agent_id, task_uuid):
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
        if 'output_variable' in data:
            task['output_variable'] = data['output_variable']
        if 'output_type' in data:
            task['output_type'] = data['output_type']
        if 'output_description' in data:
            task['output_description'] = data['output_description']
        if 'output_rendering' in data:
            task['output_rendering'] = data['output_rendering']
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

@agents_bp.route('/<agent_id>/tasks/<task_uuid>', methods=['DELETE'])
def api_delete_agent_task(agent_id, task_uuid):
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

@agents_bp.route('/<agent_id>/tasks/reorder', methods=['POST'])
def api_reorder_agent_tasks(agent_id):
    """Reorder tasks for a specific agent"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return jsonify({'success': False, 'error': 'Agent not found'}), 404
        
        data = request.get_json()
        if not data or 'task_order' not in data:
            return jsonify({'success': False, 'error': 'Task order not provided'}), 400
        
        task_order = data['task_order']  # List of task UUIDs in new order
        tasks = agent.get('tasks', [])
        
        if len(task_order) != len(tasks):
            return jsonify({'success': False, 'error': 'Task order length mismatch'}), 400
        
        # Create new ordered task list
        new_tasks = []
        for i, task_uuid in enumerate(task_order):
            # Find task by UUID
            task = next((t for t in tasks if t.get('uuid') == task_uuid), None)
            if not task:
                return jsonify({'success': False, 'error': f'Task {task_uuid} not found'}), 404
            
            # Update order
            task['order'] = i + 1
            new_tasks.append(task)
        
        # Save reordered tasks
        agent['tasks'] = new_tasks
        agent['updated_at'] = datetime.utcnow().isoformat()
        agents_manager.save(agent)
        
        return jsonify({
            'success': True,
            'message': 'Tasks reordered successfully',
            'task_count': len(new_tasks)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error reordering tasks: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@agents_bp.route('/<agent_id>/tasks/<task_uuid>/move-up', methods=['POST'])
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

@agents_bp.route('/<agent_id>/tasks/<task_uuid>/move-down', methods=['POST'])
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

# Legacy update and delete endpoints (maintain compatibility)
@agents_bp.route('/<agent_id>/tasks/<task_uuid>', methods=['PUT'])
def update_task(agent_id, task_uuid):
    """Update a specific task (alias for api_update_agent_task)"""
    return api_update_agent_task(agent_id, task_uuid)

@agents_bp.route('/<agent_id>/tasks/<task_uuid>', methods=['DELETE'])
def delete_task(agent_id, task_uuid):
    """Delete a specific task (alias for api_delete_agent_task)"""
    return api_delete_agent_task(agent_id, task_uuid)

# Debug endpoint for task creation
@agents_bp.route('/debug/<agent_id>/tasks', methods=['POST'])
def debug_create_agent_task(agent_id):
    """Debug endpoint for creating agent tasks with detailed logging"""
    try:
        current_app.logger.info(f"Debug: Creating task for agent {agent_id}")
        
        agent = agents_manager.load(agent_id)
        if not agent:
            current_app.logger.error(f"Debug: Agent {agent_id} not found")
            return jsonify({'error': 'Agent not found', 'debug': True}), 404
        
        data = request.get_json()
        current_app.logger.info(f"Debug: Received data: {data}")
        
        if not data:
            current_app.logger.error("Debug: No data provided")
            return jsonify({'error': 'No data provided', 'debug': True}), 400
        
        # Continue with regular task creation logic...
        return api_create_agent_task(agent_id)
        
    except Exception as e:
        current_app.logger.error(f"Debug: Error creating task: {str(e)}")
        return jsonify({'error': str(e), 'debug': True}), 500
