"""
API routes for agents - Legacy and general agent API functions
Handles remaining API endpoints for quick actions and data management.

NOTE: Most functionality has been moved to specialized modules:
- assistant_api.py - Assistant management API endpoints  
- agent_run_api.py - Agent run API endpoints
- streaming_api.py - Streaming API endpoints
- task_api.py - Task-related API endpoints
- knowledge_api.py - Knowledge base API endpoints  
- tools_api.py - Tools API endpoints (including quick actions and data clearing)
- session_api.py - Session management API endpoints

This module is now essentially empty - all functionality has been moved to specialized modules.
"""

from flask import Blueprint
from app.routes.agents import agents_bp

# This module now serves as a placeholder - all API functions have been moved to specialized modules










