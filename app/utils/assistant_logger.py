"""
Assistant API Call Logger für vntrai Agent System
Logs all Assistant API calls per agent for tracking and monitoring
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class AssistantLogger:
    """Handles logging of all Assistant API calls per agent"""
    
    def __init__(self):
        # Try to use Flask app config if available, otherwise use relative path
        try:
            from flask import current_app
            self.logs_dir = Path(current_app.config.get('DATA_DIR', '/app/data')) / 'agentlogs'
        except (ImportError, RuntimeError):
            # Fallback for when not in Flask app context
            self.logs_dir = Path(__file__).parent.parent.parent / "data" / "agentlogs"
            
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def log_assistant_call(self, 
                          agent_id: str, 
                          endpoint: str, 
                          request_data: Dict[str, Any], 
                          response_status: str,
                          response_data: Optional[Dict[str, Any]] = None,
                          error_msg: Optional[str] = None) -> None:
        """
        Log an Assistant API call for a specific agent
        
        Args:
            agent_id: UUID of the agent making the call
            endpoint: API endpoint called (e.g., 'create_assistant', 'send_message')
            request_data: Data sent in the request
            response_status: HTTP status or 'success'/'error'
            response_data: Response data from API (optional)
            error_msg: Error message if call failed (optional)
        """
        
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "agent_id": agent_id,
            "endpoint": endpoint,
            "request_data": self._sanitize_data(request_data),
            "response_status": response_status
        }
        
        # Add optional fields
        if response_data:
            log_entry["response_data"] = self._sanitize_data(response_data)
        
        if error_msg:
            log_entry["error_message"] = error_msg
        
        # Create log file path
        log_file = self.logs_dir / f"{agent_id}.log"
        
        # Append to log file
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            # If logging fails, try to log to a fallback file
            fallback_log = self.logs_dir / "logging_errors.log"
            with open(fallback_log, 'a', encoding='utf-8') as f:
                f.write(f"{timestamp} - Failed to log for agent {agent_id}: {str(e)}\n")
    
    def get_agent_logs(self, agent_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get logs for a specific agent
        
        Args:
            agent_id: UUID of the agent
            limit: Maximum number of recent logs to return (None = all)
            
        Returns:
            List of log entries, most recent first
        """
        log_file = self.logs_dir / f"{agent_id}.log"
        
        if not log_file.exists():
            return []
        
        logs = []
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            log_entry = json.loads(line)
                            logs.append(log_entry)
                        except json.JSONDecodeError:
                            continue
            
            # Sort by timestamp (most recent first)
            logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Apply limit if specified
            if limit:
                logs = logs[:limit]
                
            return logs
            
        except Exception as e:
            return []
    
    def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """
        Get statistics for an agent's API calls
        
        Args:
            agent_id: UUID of the agent
            
        Returns:
            Dictionary with call statistics
        """
        logs = self.get_agent_logs(agent_id)
        
        stats = {
            'total_calls': len(logs),
            'successful_calls': 0,
            'failed_calls': 0,
            'endpoints': {},
            'latest_call': None,
            'error_rate': 0.0
        }
        
        if not logs:
            return stats
        
        stats['latest_call'] = logs[0].get('timestamp')
        
        for log in logs:
            # Count successes and failures
            status = log.get('response_status', '')
            if status in ['200', 'success', 'ok']:
                stats['successful_calls'] += 1
            else:
                stats['failed_calls'] += 1
            
            # Count endpoint usage
            endpoint = log.get('endpoint', 'unknown')
            stats['endpoints'][endpoint] = stats['endpoints'].get(endpoint, 0) + 1
        
        # Calculate error rate
        if stats['total_calls'] > 0:
            stats['error_rate'] = stats['failed_calls'] / stats['total_calls']
        
        return stats
    
    def _sanitize_data(self, data: Any) -> Any:
        """
        Sanitize data for logging (remove sensitive information)
        
        Args:
            data: Data to sanitize
            
        Returns:
            Sanitized data
        """
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                # Remove sensitive keys
                if key.lower() in ['api_key', 'password', 'token', 'secret', 'authorization']:
                    sanitized[key] = '***REDACTED***'
                elif isinstance(value, (dict, list)):
                    sanitized[key] = self._sanitize_data(value)
                else:
                    sanitized[key] = value
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        else:
            return data

# Global instance
assistant_logger = AssistantLogger()
