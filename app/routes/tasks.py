"""
Task Routes - Placeholder for task-related routes
Tasks are now integrated into Agents system (data/agents/*.json)
This blueprint exists to prevent routing errors during transition.
"""

from flask import Blueprint, jsonify

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/create_task', methods=['POST'])
def create_task():
    """
    Placeholder route - Tasks are now handled by agents.api_task
    This exists to prevent routing errors during transition.
    """
    return jsonify({
        'success': False,
        'message': 'Tasks are now handled through the Agent system. Use agents.api_task instead.',
        'redirect': '/agents'
    }), 410  # Gone - resource no longer available