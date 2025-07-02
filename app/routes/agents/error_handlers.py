"""
Error handlers for agents module
Centralized error handling for agent-related operations
"""

from flask import render_template, current_app

# Get blueprint from the parent module
from app.routes.agents import agents_bp

@agents_bp.errorhandler(404)
def agents_not_found(error):
    """Handle 404 errors in agents module"""
    current_app.logger.error(f"Agent not found: {error}")
    return render_template('errors/404.html', message="Agent not found"), 404

@agents_bp.errorhandler(500)
def agents_internal_error(error):
    """Handle 500 errors in agents module"""
    current_app.logger.error(f"Internal error in agents module: {error}")
    return render_template('errors/500.html', message="Internal server error"), 500
