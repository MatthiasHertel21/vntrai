"""
Session Management API Routes
Handles session CRUD operations and cleanup for agents
"""

from flask import request, jsonify, current_app
from app.routes.agents import agents_bp
from app.utils.data_manager import agent_run_manager
from .api_utils import (validate_json_request, success_response, error_response, 
                        get_agent_or_404, current_timestamp, log_error, log_info)
from app import csrf
from datetime import datetime


@agents_bp.route('/api/<agent_id>/sessions', methods=['GET'])
@csrf.exempt
def get_agent_sessions(agent_id):
    """Get all sessions/runs for an agent"""
    try:
        # Get agent runs from agent_run_manager
        agent_runs = agent_run_manager.get_agent_runs(agent_id)
        
        # Format sessions for frontend display
        sessions = []
        for run_data in agent_runs:
            try:
                run_id = run_data.get('id', run_data.get('uuid', 'unknown'))
                
                # Calculate session age in days
                created_at = run_data.get('created_at')
                if created_at:
                    if isinstance(created_at, str):
                        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        created_date = created_at
                    
                    age_days = (datetime.now() - created_date.replace(tzinfo=None)).days
                else:
                    age_days = 0
                
                # Get task completion status
                tasks = run_data.get('tasks', [])
                completed_tasks = len([t for t in tasks if t.get('status') == 'completed'])
                total_tasks = len(tasks)
                
                session = {
                    'id': run_id,
                    'status': run_data.get('status', 'unknown'),
                    'created_at': created_at,
                    'updated_at': run_data.get('updated_at'),
                    'age_days': age_days,
                    'completed_tasks': completed_tasks,
                    'total_tasks': total_tasks,
                    'last_activity': run_data.get('updated_at', created_at)
                }
                sessions.append(session)
                
            except Exception as session_error:
                log_error(f"Error processing session {run_id}: {str(session_error)}")
                continue
        
        # Sort sessions by last activity (newest first)
        sessions.sort(key=lambda x: x.get('last_activity', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'sessions': sessions,
            'total_count': len(sessions)
        })
        
    except Exception as e:
        log_error(f"Error loading sessions for agent {agent_id}: {str(e)}")
        return error_response(str(e), 500)


@agents_bp.route('/api/<agent_id>/sessions/<session_id>', methods=['DELETE'])
@csrf.exempt
def delete_agent_session(agent_id, session_id):
    """Delete a specific session"""
    try:
        # Delete the session using agent_run_manager
        success = agent_run_manager.delete(session_id)
        
        if success:
            return success_response('Session deleted successfully')
        else:
            return error_response('Failed to delete session', 500)
            
    except Exception as e:
        log_error(f"Error deleting session {session_id} for agent {agent_id}: {str(e)}")
        return error_response(str(e), 500)


@agents_bp.route('/api/<agent_id>/sessions/cleanup', methods=['POST'])
@csrf.exempt
def cleanup_agent_sessions(agent_id):
    """Clean up closed and error sessions for an agent"""
    try:
        data = request.get_json() or {}
        cleanup_types = data.get('types', ['closed', 'error'])
        
        # Get all agent runs
        agent_runs = agent_run_manager.get_agent_runs(agent_id)
        
        deleted_count = 0
        for run_data in agent_runs:
            run_id = run_data.get('id', run_data.get('uuid'))
            status = run_data.get('status', 'unknown')
            if status in cleanup_types:
                if agent_run_manager.delete(run_id):
                    deleted_count += 1
        
        return success_response(
            f'Cleaned up {deleted_count} sessions',
            {'deleted_count': deleted_count}
        )
        
    except Exception as e:
        log_error(f"Error cleaning up sessions for agent {agent_id}: {str(e)}")
        return error_response(str(e), 500)
