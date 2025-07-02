"""
Session management routes - Agent session creation and management
Handles new session creation and existing session opening for agents
"""

from flask import Blueprint, request, redirect, url_for, flash, current_app
from app.utils.data_manager import agents_manager

# Get blueprint from the parent module
from app.routes.agents import agents_bp

@agents_bp.route('/new_session/<agent_id>', methods=['POST'])
def new_session(agent_id):
    """Create a new session for an agent"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            flash('Agent not found', 'error')
            return redirect(url_for('agents.list_agents'))
        
        # For now, redirect to view agent - can be enhanced to create actual session
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
