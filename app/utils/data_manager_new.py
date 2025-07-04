"""
Data Manager for vntrai Data Management
Backward compatibility file that imports all manager instances
"""

# Import all manager classes and their global instances
from .base_manager import DataManager
from .integrations_manager import IntegrationsManager, integrations_manager
from .tools_manager import ToolsManager, tools_manager
from .agents_manager import AgentsManager, agents_manager
from .agent_run_manager import AgentRunManager, agent_run_manager
from .icon_manager import IconManager, icon_manager

# Export all instances for backward compatibility
__all__ = [
    'DataManager',
    'IntegrationsManager', 'integrations_manager',
    'ToolsManager', 'tools_manager', 
    'AgentsManager', 'agents_manager',
    'AgentRunManager', 'agent_run_manager',
    'IconManager', 'icon_manager'
]

# Legacy aliases - these were the original global instances in the old file
# Keep these for backward compatibility with existing imports
