"""
OpenAI Thread Management
Handles thread locking and cleanup operations
"""

import threading
import requests
import time
from .api_utils import log_error, log_info

# Global locks for OpenAI thread management to prevent concurrent access
_thread_locks = {}
_thread_locks_lock = threading.Lock()


def get_thread_lock(thread_id):
    """Get or create a lock for a specific OpenAI thread"""
    with _thread_locks_lock:
        if thread_id not in _thread_locks:
            _thread_locks[thread_id] = threading.Lock()
        return _thread_locks[thread_id]


def force_cancel_all_active_runs(thread_id, headers):
    """Force cancel all active runs on a thread - last resort cleanup"""
    try:
        log_info(f"Force cancelling all active runs on thread {thread_id}")
        runs_response = requests.get(
            f'https://api.openai.com/v1/threads/{thread_id}/runs?limit=20',
            headers=headers,
            timeout=30
        )
        
        if runs_response.status_code == 200:
            runs_data = runs_response.json()
            active_runs = []
            
            for run in runs_data.get('data', []):
                if run.get('status') in ['queued', 'in_progress', 'requires_action']:
                    active_runs.append(run['id'])
            
            log_info(f"Found {len(active_runs)} active runs to cancel")
            
            # Cancel all active runs
            for run_id in active_runs:
                try:
                    cancel_response = requests.post(
                        f'https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}/cancel',
                        headers=headers,
                        timeout=30
                    )
                    log_info(f"Force cancelled run {run_id}: {cancel_response.status_code}")
                except Exception as e:
                    log_error(f"Failed to force cancel run {run_id}: {e}")
            
            # Wait a bit for cancellations to take effect
            if active_runs:
                time.sleep(5)
                
        return True
        
    except Exception as e:
        log_error(f"Error in force_cancel_all_active_runs: {e}")
        return False


def ensure_thread_is_clean(thread_id, headers):
    """Ensure OpenAI thread has no active runs before starting new execution"""
    log_info(f"Checking for active runs on thread {thread_id}")
    
    # First, get list of all runs to check for active ones
    runs_response = requests.get(
        f'https://api.openai.com/v1/threads/{thread_id}/runs?limit=20',
        headers=headers,
        timeout=30
    )
    
    if runs_response.status_code != 200:
        log_error(f"Failed to get runs list: {runs_response.status_code}")
        return False, "Failed to check thread status"
    
    runs_data = runs_response.json()
    active_runs = []
    for run in runs_data.get('data', []):
        if run.get('status') in ['queued', 'in_progress', 'requires_action']:
            active_runs.append({'id': run['id'], 'status': run.get('status')})
    
    if not active_runs:
        log_info("No active runs found on thread")
        return True, None
    
    log_info(f"Found {len(active_runs)} active runs: {active_runs}")
    
    # Use comprehensive force cancel function
    if not force_cancel_all_active_runs(thread_id, headers):
        error_msg = "Failed to cancel active runs on thread"
        log_error(error_msg)
        return False, error_msg
    
    # Verify the thread is now clean after force cancellation
    log_info("Verifying thread is clean after force cancellation")
    verify_response = requests.get(
        f'https://api.openai.com/v1/threads/{thread_id}/runs?limit=10',
        headers=headers,
        timeout=30
    )
    
    if verify_response.status_code == 200:
        verify_data = verify_response.json()
        remaining_active = []
        for run in verify_data.get('data', []):
            if run.get('status') in ['queued', 'in_progress', 'requires_action']:
                remaining_active.append({'id': run['id'], 'status': run.get('status')})
        
        if remaining_active:
            error_msg = f"Thread still has {len(remaining_active)} active runs after force cancellation: {remaining_active}"
            log_error(error_msg)
            return False, error_msg
        else:
            log_info("Thread verified clean after force cancellation")
            return True, None
    else:
        log_error(f"Failed to verify thread cleanliness: {verify_response.status_code}")
        return False, "Failed to verify thread status"
