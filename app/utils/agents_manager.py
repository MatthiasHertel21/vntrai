"""
Agents Manager for vntrai Data Management
Handles agents data with Sprint 18 Task Management Revolution
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from .base_manager import DataManager

class AgentsManager(DataManager):
    """Manager for agents data with Sprint 18 Task Management Revolution"""
    
    def __init__(self):
        super().__init__('agents')
    
    def create_agent(self, name: str, category: str = 'general', description: str = '') -> Dict[str, Any]:
        """Create new agent with Sprint 18 task structure"""
        agent = {
            'uuid': str(uuid.uuid4()),  # Primary UUID
            'id': str(uuid.uuid4()),     # Secondary ID for compatibility
            'name': name,
            'category': category,
            'description': description,
            'status': 'active',
            
            # Sprint 18: Task definitions stored in agent
            'tasks': [],  # Array of task definitions
            
            # Knowledge base and files
            'knowledge_base': [],
            'files': [],
            
            # AI Assistant configuration
            'ai_assistant_tool': '',  # Tool ID with assistant option
            'assistant_id': '',
            'assistant_model': 'gpt-4-turbo-preview',
            'assistant_tools_retrieval': False,
            'assistant_tools_code_interpreter': False,
            'use_openai_assistant': False,
            
            # Agent usage modes (from Sprint 17.5)
            'use_as_agent': True,
            'use_as_insight': False,
            'quick_actions': [],
            
            # Metadata
            'metadata': {
                'color': 'blue',
                'tags': []
            },
            'version': '1.0.0',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        if self.save(agent):
            return agent
        return None

    # Sprint 18: Task Management Methods
    def add_task_definition(self, agent_id: str, task: Dict[str, Any]) -> bool:
        """Add task definition to agent (Sprint 18)"""
        agent = self.load(agent_id)
        if not agent:
            return False
        
        # Ensure task has required fields for Sprint 18
        if 'uuid' not in task:
            task['uuid'] = str(uuid.uuid4())
        # Ensure both id and uuid exist for compatibility
        if 'id' not in task:
            task['id'] = task['uuid']  # Use uuid as id for validator compatibility
        if 'type' not in task:
            task['type'] = 'ai'  # Default to AI task
        if 'name' not in task:
            task['name'] = f"Task {len(agent['tasks']) + 1}"
        if 'order' not in task:
            task['order'] = len(agent['tasks']) + 1
        if 'created_at' not in task:
            task['created_at'] = datetime.now().isoformat()
        
        task['updated_at'] = datetime.now().isoformat()
        
        if 'tasks' not in agent:
            agent['tasks'] = []
        
        agent['tasks'].append(task)
        agent['updated_at'] = datetime.now().isoformat()
        return self.save(agent)
    
    def update_task_definition(self, agent_id: str, task_uuid: str, task_data: Dict[str, Any]) -> bool:
        """Update task definition in agent (Sprint 18)"""
        agent = self.load(agent_id)
        if not agent or 'tasks' not in agent:
            return False
        
        for i, task in enumerate(agent['tasks']):
            if task.get('uuid') == task_uuid:
                task_data['uuid'] = task_uuid
                task_data['updated_at'] = datetime.now().isoformat()
                # Preserve order and creation time
                if 'order' not in task_data:
                    task_data['order'] = task.get('order', i + 1)
                if 'created_at' not in task_data:
                    task_data['created_at'] = task.get('created_at', datetime.now().isoformat())
                
                agent['tasks'][i] = {**task, **task_data}
                agent['updated_at'] = datetime.now().isoformat()
                return self.save(agent)
        
        return False
    
    def remove_task_definition(self, agent_id: str, task_uuid: str) -> bool:
        """Remove task definition from agent (Sprint 18)"""
        agent = self.load(agent_id)
        if not agent or 'tasks' not in agent:
            return False
        
        original_count = len(agent['tasks'])
        agent['tasks'] = [task for task in agent['tasks'] if task.get('uuid') != task_uuid]
        
        if len(agent['tasks']) < original_count:
            # Reorder remaining tasks
            for i, task in enumerate(agent['tasks']):
                task['order'] = i + 1
            agent['updated_at'] = datetime.now().isoformat()
            return self.save(agent)
        
        return False
    
    def reorder_task_definitions(self, agent_id: str, task_uuids: List[str]) -> bool:
        """Reorder task definitions in agent (Sprint 18)"""
        agent = self.load(agent_id)
        if not agent or 'tasks' not in agent:
            return False
        
        # Create task dictionary for quick lookup
        tasks_dict = {task['uuid']: task for task in agent['tasks']}
        
        # Reorder tasks and update order field
        reordered_tasks = []
        for i, task_uuid in enumerate(task_uuids):
            if task_uuid in tasks_dict:
                task = tasks_dict[task_uuid]
                task['order'] = i + 1
                task['updated_at'] = datetime.now().isoformat()
                reordered_tasks.append(task)
        
        # Add any tasks that weren't in the reorder list
        for task in agent['tasks']:
            if task['uuid'] not in task_uuids:
                task['order'] = len(reordered_tasks) + 1
                reordered_tasks.append(task)
        
        agent['tasks'] = reordered_tasks
        agent['updated_at'] = datetime.now().isoformat()
        return self.save(agent)
    
    def get_task_definition(self, agent_id: str, task_uuid: str) -> Optional[Dict[str, Any]]:
        """Get specific task definition from agent (Sprint 18)"""
        agent = self.load(agent_id)
        if not agent or 'tasks' not in agent:
            return None
        
        for task in agent['tasks']:
            if task.get('uuid') == task_uuid:
                return task
        
        return None
    
    def get_task_definitions(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all task definitions from agent (Sprint 18)"""
        agent = self.load(agent_id)
        if not agent or 'tasks' not in agent:
            return []
        
        # Sort by order field
        return sorted(agent['tasks'], key=lambda x: x.get('order', 0))

    # Assistant-enabled tools filtering for Sprint 18
    def get_assistant_enabled_tools(self) -> List[Dict[str, Any]]:
        """Get tools that have assistant option enabled (Sprint 18)"""
        # Import here to avoid circular imports
        from .tools_manager import tools_manager
        return tools_manager.get_tools_with_assistant_enabled()
    
    def validate_assistant_tool_selection(self, agent_id: str, tool_id: str) -> bool:
        """Validate that selected tool has assistant option enabled (Sprint 18)"""
        if not tool_id:
            return False
        
        # Import here to avoid circular imports
        from .tools_manager import tools_manager
        tool = tools_manager.get_by_id(tool_id)
        if not tool:
            return False
        
        return tools_manager.is_assistant_enabled(tool_id)

    def get_agent_statistics(self) -> Dict[str, Any]:
        """Get statistics about agents for overview page"""
        all_agents = self.load_all()
        
        # Count by status
        status_counts = {
            'active': 0,
            'inactive': 0,
            'draft': 0
        }
        
        # Count by category
        category_counts = {}
        
        # Count by use_as field (Sprint 17.5)
        use_as_counts = {
            'agent': 0,
            'insight': 0,
            'both': 0
        }
        
        # Task statistics (Sprint 18)
        total_tasks = 0
        agents_with_tasks = 0
        
        for agent in all_agents:
            # Status counts
            status = agent.get('status', 'inactive')
            if status in status_counts:
                status_counts[status] += 1
            
            # Category counts
            category = agent.get('category', 'general')
            category_counts[category] = category_counts.get(category, 0) + 1
            
            # Use as counts (Sprint 17.5)
            use_as_agent = agent.get('use_as_agent', True)
            use_as_insight = agent.get('use_as_insight', False)
            
            if use_as_agent and use_as_insight:
                use_as_counts['both'] += 1
            elif use_as_insight:
                use_as_counts['insight'] += 1
            else:
                use_as_counts['agent'] += 1
            
            # Task statistics (Sprint 18)
            tasks = agent.get('tasks', [])
            if tasks:
                agents_with_tasks += 1
                total_tasks += len(tasks)
        
        # Calculate averages
        total_agents = len(all_agents)
        avg_tasks_per_agent = round(total_tasks / total_agents, 1) if total_agents > 0 else 0
        
        return {
            'total_agents': total_agents,
            'status_counts': status_counts,
            'category_counts': category_counts,
            'use_as_counts': use_as_counts,
            'task_statistics': {
                'total_tasks': total_tasks,
                'agents_with_tasks': agents_with_tasks,
                'avg_tasks_per_agent': avg_tasks_per_agent
            }
        }

    def get_single_agent_statistics(self, agent_id: str) -> Dict[str, Any]:
        """Get statistics for a single agent"""
        agent = self.load(agent_id)
        if not agent:
            return {}
        
        # Count tasks (Sprint 18)
        tasks = agent.get('tasks', [])
        task_counts = {
            'total': len(tasks),
            'ai_tasks': len([t for t in tasks if t.get('type') == 'ai']),
            'tool_tasks': len([t for t in tasks if t.get('type') == 'tool'])
        }
        
        # Count files
        files = agent.get('files', [])
        file_count = len(files)
        
        # Count knowledge base items
        knowledge_base = agent.get('knowledge_base', [])
        knowledge_count = len(knowledge_base)
        
        # Assistant status
        has_assistant = bool(agent.get('assistant_id'))
        assistant_tool = agent.get('ai_assistant_tool')
        
        return {
            'task_counts': task_counts,
            'file_count': file_count,
            'knowledge_count': knowledge_count,
            'has_assistant': has_assistant,
            'assistant_tool': assistant_tool,
            'status': agent.get('status', 'inactive'),
            'category': agent.get('category', 'general'),
            'use_as_agent': agent.get('use_as_agent', True),
            'use_as_insight': agent.get('use_as_insight', False)
        }

    # Legacy task methods - maintained for backward compatibility but marked for removal
    def add_task(self, agent_id: str, task: Dict[str, Any]) -> bool:
        """Legacy method - use add_task_definition instead (Sprint 18)"""
        # Redirect to new method
        return self.add_task_definition(agent_id, task)
    
    def update_task(self, agent_id: str, task_id: str, task_data: Dict[str, Any]) -> bool:
        """Legacy method - use update_task_definition instead (Sprint 18)"""
        # Try to find by id or uuid
        agent = self.load(agent_id)
        if not agent or 'tasks' not in agent:
            return False
        
        # Find task by id or uuid
        task_uuid = None
        for task in agent['tasks']:
            if task.get('id') == task_id or task.get('uuid') == task_id:
                task_uuid = task.get('uuid', task.get('id'))
                break
        
        if task_uuid:
            return self.update_task_definition(agent_id, task_uuid, task_data)
        
        return False
    
    def remove_task(self, agent_id: str, task_id: str) -> bool:
        """Legacy method - use remove_task_definition instead (Sprint 18)"""
        # Try to find by id or uuid
        agent = self.load(agent_id)
        if not agent or 'tasks' not in agent:
            return False
        
        # Find task by id or uuid
        task_uuid = None
        for task in agent['tasks']:
            if task.get('id') == task_id or task.get('uuid') == task_id:
                task_uuid = task.get('uuid', task.get('id'))
                break
        
        if task_uuid:
            return self.remove_task_definition(agent_id, task_uuid)
        
        return False
    
    def reorder_tasks(self, agent_id: str, task_ids: List[str]) -> bool:
        """Legacy method - use reorder_task_definitions instead (Sprint 18)"""
        # Convert ids to uuids if needed
        agent = self.load(agent_id)
        if not agent or 'tasks' not in agent:
            return False
        
        task_uuids = []
        for task_id in task_ids:
            for task in agent['tasks']:
                if task.get('id') == task_id or task.get('uuid') == task_id:
                    task_uuids.append(task.get('uuid', task.get('id')))
                    break
        
        return self.reorder_task_definitions(agent_id, task_uuids)

# Global instance
agents_manager = AgentsManager()
