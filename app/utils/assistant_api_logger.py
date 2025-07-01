"""
Assistant API Call Logging
Logs all Assistant API calls for monitoring and debugging
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from functools import wraps
import time

def setup_assistant_logger(agent_uuid: str) -> logging.Logger:
    """
    Setup a dedicated logger for assistant API calls for a specific agent
    """
    log_dir = '/home/ga/fb1/age/data/agentlogs'
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'{agent_uuid}.log')
    
    # Create logger
    logger = logging.getLogger(f'assistant_{agent_uuid}')
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplication
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(file_handler)
    logger.propagate = False  # Prevent propagation to root logger
    
    return logger

def log_assistant_api_call(agent_uuid: str, endpoint: str, method: str, 
                          request_data: Optional[Dict[str, Any]] = None, 
                          response_data: Optional[Dict[str, Any]] = None,
                          status_code: Optional[int] = None,
                          error: Optional[str] = None,
                          execution_time: Optional[float] = None):
    """
    Log an Assistant API call with full details
    """
    try:
        logger = setup_assistant_logger(agent_uuid)
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'execution_time_ms': round(execution_time * 1000, 2) if execution_time else None,
            'request_data': request_data,
            'response_data': response_data,
            'error': error
        }
        
        # Create readable log message
        if error:
            log_message = f"ERROR | {method} {endpoint} | {error}"
            if execution_time:
                log_message += f" | {execution_time*1000:.2f}ms"
            logger.error(log_message)
        else:
            log_message = f"SUCCESS | {method} {endpoint}"
            if status_code:
                log_message += f" | {status_code}"
            if execution_time:
                log_message += f" | {execution_time*1000:.2f}ms"
            logger.info(log_message)
        
        # Also log detailed JSON for debugging
        logger.debug(f"DETAILS | {json.dumps(log_entry, indent=2)}")
        
    except Exception as e:
        # Fallback logging if main logging fails
        print(f"Failed to log Assistant API call: {e}")

def get_assistant_logs(agent_uuid: str, lines: int = 100) -> List[str]:
    """
    Retrieve recent logs for a specific agent
    """
    log_file = f'/home/ga/fb1/age/data/agentlogs/{agent_uuid}.log'
    
    if not os.path.exists(log_file):
        return []
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return [line.strip() for line in all_lines[-lines:]]
    except Exception as e:
        return [f"Error reading logs: {e}"]

def clear_assistant_logs(agent_uuid: str) -> bool:
    """
    Clear logs for a specific agent
    """
    log_file = f'/home/ga/fb1/age/data/agentlogs/{agent_uuid}.log'
    
    try:
        if os.path.exists(log_file):
            os.remove(log_file)
        return True
    except Exception:
        return False

def get_all_agent_logs() -> Dict[str, Dict[str, Any]]:
    """
    Get summary of all agent logs
    """
    log_dir = '/home/ga/fb1/age/data/agentlogs'
    
    if not os.path.exists(log_dir):
        return {}
    
    logs_summary = {}
    
    for filename in os.listdir(log_dir):
        if filename.endswith('.log'):
            agent_uuid = filename[:-4]  # Remove .log extension
            log_file = os.path.join(log_dir, filename)
            
            try:
                stat = os.stat(log_file)
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                logs_summary[agent_uuid] = {
                    'file_size': stat.st_size,
                    'line_count': len(lines),
                    'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'last_entry': lines[-1].strip() if lines else None
                }
            except Exception as e:
                logs_summary[agent_uuid] = {
                    'error': str(e)
                }
    
    return logs_summary
