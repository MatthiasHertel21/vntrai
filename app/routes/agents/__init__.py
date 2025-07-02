"""
Agents module - Refactored agent management system
Split into logical components for better maintainability
"""

from flask import Blueprint

# Create main blueprint
agents_bp = Blueprint('agents', __name__)

# Import all routes after blueprint creation to avoid circular imports
def register_routes():
    from . import main_routes
    from . import api_routes
    from . import task_routes
    from . import session_routes
    from . import error_handlers

# Register routes immediately
register_routes()
