"""
Agent Run Manager for vntrai Data Management
Handles agent runs with Sprint 18 task execution
"""

import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from .base_manager import DataManager

class AgentRunManager(DataManager):
    """Manager for agent runs with Sprint 18 task execution"""
    
    def __init__(self):
        super().__init__('agentrun')
        self._save_locks = {}  # Track save operations to prevent concurrent writes
    
    def save(self, item: Dict[str, Any]) -> bool:
        """Save agent run using uuid instead of id"""
        uuid_val = item.get('uuid')
        if not uuid_val:
            uuid_val = str(uuid.uuid4())
            item['uuid'] = uuid_val
        
        # Remove id field if it exists to avoid duplication
        if 'id' in item:
            del item['id']
        
        # Update timestamp
        item['updated_at'] = datetime.now().isoformat()
        if 'created_at' not in item:
            item['created_at'] = item['updated_at']
        
        file_path = self.data_dir / f"{uuid_val}.json"
        
        # Safe write with temporary file to prevent corruption
        temp_path = file_path.with_suffix('.tmp')
        try:
            # Write to temporary file first
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(item, f, indent=2, ensure_ascii=False)
            
            # Validate JSON by reading it back
            with open(temp_path, 'r', encoding='utf-8') as f:
                json.load(f)  # This will raise an exception if JSON is invalid
            
            # If validation passes, move temp file to final location
            shutil.move(str(temp_path), str(file_path))
            return True
            
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error saving {self.data_type} {uuid_val}: {e}")
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            return False
    
    def load(self, uuid_val: str) -> Optional[Dict[str, Any]]:
        """Load agent run by uuid"""
        file_path = self.data_dir / f"{uuid_val}.json"
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Ensure uuid field exists and remove id field if present
            if 'uuid' not in data:
                data['uuid'] = uuid_val
            if 'id' in data:
                del data['id']
                
            return data
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading {self.data_type} {uuid_val}: {e}")
            return None
    
    def create_agent_run(self, agent_id: str, name: str = '') -> Dict[str, Any]:
        """Create new agent run with Sprint 18 task state structure"""
        agent_run = {
            'uuid': str(uuid.uuid4()),
            'agent_uuid': agent_id,
            'name': name or f"Run {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            'status': 'created',
            
            # Sprint 18: Task execution states stored in agentrun
            'task_states': [],  # Array of task execution states
            
            # Run context and inputs
            'inputs': {},
            'context': {},
            'outputs': {},
            
            # Metadata
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'started_at': None,
            'completed_at': None
        }
        
        # Initialize task states from agent's task definitions
        from .agents_manager import agents_manager
        agent = agents_manager.load(agent_id)
        if agent and 'tasks' in agent:
            for task_def in agent['tasks']:
                task_state = {
                    'task_uuid': task_def['uuid'],
                    'status': 'pending',
                    'inputs': {},
                    'outputs': {},
                    'results': {},
                    'error': None,
                    'started_at': None,
                    'completed_at': None,
                    'execution_time': None
                }
                agent_run['task_states'].append(task_state)
        
        if self.save(agent_run):
            return agent_run
        return None
    
    def get_task_state(self, run_id: str, task_uuid: str) -> Optional[Dict[str, Any]]:
        """Get task execution state from agent run (Sprint 18)"""
        agent_run = self.load(run_id)
        if not agent_run or 'task_states' not in agent_run:
            return None
        
        for task_state in agent_run['task_states']:
            if task_state.get('task_uuid') == task_uuid:
                return task_state
        
        return None
    
    def update_task_state(self, run_id: str, task_uuid: str, state_data: Dict[str, Any]) -> bool:
        """Update task execution state in agent run (Sprint 18)"""
        print(f"[DEBUG] update_task_state called with run_id={run_id}, task_uuid={task_uuid}, state_data={state_data}")
        
        # Prevent concurrent modifications of the same run
        if run_id in self._save_locks:
            print(f"[DEBUG] Save operation already in progress for run_id={run_id}, skipping")
            return False
            
        self._save_locks[run_id] = True
        
        try:
            agent_run = self.load(run_id)
            if not agent_run:
                print(f"[DEBUG] Agent run not found: {run_id}")
                return False
                
            if 'task_states' not in agent_run:
                print(f"[DEBUG] No task_states in agent run: {run_id}, creating empty list")
                agent_run['task_states'] = []
            
            print(f"[DEBUG] Found {len(agent_run['task_states'])} task states")
            
            # Look for existing task state
            for i, task_state in enumerate(agent_run['task_states']):
                print(f"[DEBUG] Checking task state {i}: task_uuid={task_state.get('task_uuid')}")
                if task_state.get('task_uuid') == task_uuid:
                    print(f"[DEBUG] Found matching task state at index {i}")
                    # Update state data while preserving task_uuid
                    updated_state = {**task_state, **state_data}
                    updated_state['task_uuid'] = task_uuid
                    updated_state['updated_at'] = datetime.now().isoformat()
                    
                    agent_run['task_states'][i] = updated_state
                    agent_run['updated_at'] = datetime.now().isoformat()
                    
                    result = self.save(agent_run)
                    print(f"[DEBUG] Save result: {result}")
                    return result
            
            # No existing task state found, create a new one
            print(f"[DEBUG] No matching task state found for task_uuid: {task_uuid}, creating new one")
            new_task_state = {
                'task_uuid': task_uuid,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                **state_data  # Add the provided state data
            }
            
            agent_run['task_states'].append(new_task_state)
            agent_run['updated_at'] = datetime.now().isoformat()
            
            result = self.save(agent_run)
            print(f"[DEBUG] Created new task state, save result: {result}")
            return result
            
        finally:
            # Always release the lock
            if run_id in self._save_locks:
                del self._save_locks[run_id]
    
    def set_task_status(self, run_id: str, task_uuid: str, status: str, error: str = None) -> bool:
        """Set task status (Sprint 18)"""
        state_data = {'status': status}
        
        if status == 'running' and not self.get_task_state(run_id, task_uuid).get('started_at'):
            state_data['started_at'] = datetime.now().isoformat()
        elif status in ['completed', 'error', 'skipped']:
            state_data['completed_at'] = datetime.now().isoformat()
            
            # Calculate execution time if started
            task_state = self.get_task_state(run_id, task_uuid)
            if task_state and task_state.get('started_at'):
                started = datetime.fromisoformat(task_state['started_at'].replace('Z', '+00:00'))
                completed = datetime.now()
                execution_time = (completed - started).total_seconds()
                state_data['execution_time'] = execution_time
        
        if error:
            state_data['error'] = error
        
        return self.update_task_state(run_id, task_uuid, state_data)
    
    def set_task_inputs(self, run_id: str, task_uuid: str, inputs: Dict[str, Any]) -> bool:
        """Set task inputs (Sprint 18)"""
        return self.update_task_state(run_id, task_uuid, {'inputs': inputs})
    
    def set_task_outputs(self, run_id: str, task_uuid: str, outputs: Dict[str, Any]) -> bool:
        """Set task outputs (Sprint 18)"""
        return self.update_task_state(run_id, task_uuid, {'outputs': outputs})
    
    def set_task_results(self, run_id: str, task_uuid: str, results: Dict[str, Any]) -> bool:
        """Set task results (Sprint 18)"""
        return self.update_task_state(run_id, task_uuid, {'results': results})
    
    def get_task_progress(self, run_id: str) -> Dict[str, Any]:
        """Get overall task progress for agent run (Sprint 18)"""
        agent_run = self.load(run_id)
        if not agent_run or 'task_states' not in agent_run:
            return {
                'total': 0,
                'pending': 0,
                'running': 0,
                'completed': 0,
                'error': 0,
                'skipped': 0,
                'progress_percent': 0
            }
        
        task_states = agent_run['task_states']
        total = len(task_states)
        
        status_counts = {
            'pending': 0,
            'running': 0,
            'completed': 0,
            'error': 0,
            'skipped': 0
        }
        
        for task_state in task_states:
            status = task_state.get('status', 'pending')
            if status in status_counts:
                status_counts[status] += 1
        
        completed_count = status_counts['completed'] + status_counts['error'] + status_counts['skipped']
        progress_percent = (completed_count / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'progress_percent': round(progress_percent, 1),
            **status_counts
        }
    
    def get_task_definitions_with_states(self, run_id: str) -> List[Dict[str, Any]]:
        """Get task definitions combined with their execution states (Sprint 18)"""
        try:
            from flask import current_app
            
            agent_run = self.load(run_id)
            if not agent_run:
                return []
            
            from .agents_manager import agents_manager
            agent = agents_manager.load(agent_run['agent_uuid'])
            if not agent or 'tasks' not in agent:
                return []
            
            # Combine task definitions with their states
            combined_tasks = []
            task_states_dict = {ts['task_uuid']: ts for ts in agent_run.get('task_states', [])}
            
            for task_def in sorted(agent['tasks'], key=lambda x: x.get('order', 0)):
                try:
                    task_uuid = task_def.get('uuid', '')
                    if not task_uuid:
                        current_app.logger.warning(f"Task without UUID found in agent {agent_run['agent_uuid']}")
                        continue
                        
                    task_state = task_states_dict.get(task_uuid, {
                        'task_uuid': task_uuid,
                        'status': 'pending',
                        'inputs': {},
                        'outputs': {},
                        'results': {},
                        'error': None
                    })
                    
                    combined_task = {
                        'definition': task_def,
                        'state': task_state,
                        'uuid': task_uuid,
                        'name': task_def.get('name', 'Unnamed Task'),
                        'type': task_def.get('type', 'ai'),
                        'status': task_state.get('status', 'pending')
                    }
                    combined_tasks.append(combined_task)
                except Exception as task_error:
                    if current_app:
                        current_app.logger.error(f"Error processing task {task_def}: {str(task_error)}")
                    else:
                        print(f"Error processing task {task_def}: {str(task_error)}")
                    continue
            
            return combined_tasks
        except Exception as e:
            try:
                from flask import current_app
                if current_app:
                    current_app.logger.error(f"Error in get_task_definitions_with_states: {str(e)}")
                else:
                    print(f"Error in get_task_definitions_with_states: {str(e)}")
            except:
                print(f"Error in get_task_definitions_with_states: {str(e)}")
            return []
    
    def sync_task_definitions(self, run_id: str) -> bool:
        """Sync task definitions from agent to agent run (Sprint 18)"""
        agent_run = self.load(run_id)
        if not agent_run:
            return False
        
        from .agents_manager import agents_manager
        agent = agents_manager.load(agent_run['agent_uuid'])
        if not agent or 'tasks' not in agent:
            return False
        
        # Get existing task states
        existing_states = {ts['task_uuid']: ts for ts in agent_run.get('task_states', [])}
        
        # Create new task states based on current agent task definitions
        new_task_states = []
        for task_def in agent['tasks']:
            task_uuid = task_def['uuid']
            
            # Preserve existing state if it exists, otherwise create new
            if task_uuid in existing_states:
                new_task_states.append(existing_states[task_uuid])
            else:
                new_task_states.append({
                    'task_uuid': task_uuid,
                    'status': 'pending',
                    'inputs': {},
                    'outputs': {},
                    'results': {},
                    'error': None,
                    'started_at': None,
                    'completed_at': None,
                    'execution_time': None
                })
        
        agent_run['task_states'] = new_task_states
        agent_run['updated_at'] = datetime.now().isoformat()
        return self.save(agent_run)

    def get_agent_runs(self, agent_uuid: str) -> List[Dict[str, Any]]:
        """Get all agent runs for a specific agent"""
        all_runs = self.get_all()
        agent_runs = [run for run in all_runs if run.get('agent_uuid') == agent_uuid]
        # Sort by created_at timestamp (newest first)
        return sorted(agent_runs, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def get_most_recent_run(self, agent_uuid: str) -> Optional[Dict[str, Any]]:
        """Get the most recent agent run for a specific agent"""
        agent_runs = self.get_agent_runs(agent_uuid)
        return agent_runs[0] if agent_runs else None
    
    def set_language_preference(self, run_id: str, language: str) -> bool:
        """Set language preference for an agent run"""
        try:
            agent_run = self.load(run_id)
            if not agent_run:
                return False
            
            # Set language preference in agent run
            agent_run['language_preference'] = language
            agent_run['updated_at'] = datetime.now().isoformat()
            
            return self.save(agent_run)
            
        except Exception as e:
            print(f"Error setting language preference for run {run_id}: {e}")
            return False
    
    def get_language_preference(self, run_id: str) -> str:
        """Get language preference for an agent run"""
        try:
            agent_run = self.load(run_id)
            if not agent_run:
                return 'auto'
            
            return agent_run.get('language_preference', 'auto')
            
        except Exception as e:
            print(f"Error getting language preference for run {run_id}: {e}")
            return 'auto'

# Global instance
agent_run_manager = AgentRunManager()
