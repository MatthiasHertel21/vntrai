"""
OpenAI Chat Completion Implementation für VNTRAI
Basierend auf v036 ChatGPT Implementation, aber für neue Architektur optimiert
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_implementation import BaseImplementation, ImplementationError


class OpenAIChatCompletionImplementation(BaseImplementation):
    """
    Implementation für OpenAI Chat Completion API.
    Unterstützt GPT-3.5-turbo, GPT-4 und andere Chat-Modelle.
    """
    
    @property
    def name(self) -> str:
        return "openai_chatcompletion"
    
    @property
    def description(self) -> str:
        return "OpenAI Chat Completion API integration for GPT models"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def author(self) -> str:
        return "VNTRAI Team"
    
    @property
    def required_config_params(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'api_key',
                'type': 'text',
                'required': True,
                'label': 'OpenAI API Key',
                'description': 'Your OpenAI API key from https://platform.openai.com/api-keys',
                'placeholder': 'sk-...'
            },
            {
                'name': 'base_url',
                'type': 'text',
                'required': False,
                'label': 'Base URL',
                'description': 'Custom base URL for OpenAI API (optional)',
                'default': 'https://api.openai.com/v1'
            },
            {
                'name': 'organization',
                'type': 'text',
                'required': False,
                'label': 'Organization ID',
                'description': 'OpenAI Organization ID (optional)'
            },
            {
                'name': 'timeout',
                'type': 'number',
                'required': False,
                'label': 'Timeout (seconds)',
                'description': 'Request timeout in seconds',
                'default': 30.0
            }
        ]
    
    @property
    def input_params(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'model',
                'type': 'select',
                'required': True,
                'label': 'Model',
                'description': 'The OpenAI model to use',
                'options': [
                    'gpt-4',
                    'gpt-4-turbo-preview',
                    'gpt-4-vision-preview',
                    'gpt-3.5-turbo',
                    'gpt-3.5-turbo-16k'
                ],
                'default': 'gpt-3.5-turbo'
            },
            {
                'name': 'prompt',
                'type': 'textarea',
                'required': False,
                'label': 'Prompt (Simple)',
                'description': 'Simple text prompt for basic queries (alternative to messages)',
                'placeholder': 'Enter your question or request here...'
            },
            {
                'name': 'messages',
                'type': 'json',
                'required': False,
                'label': 'Messages (Advanced)',
                'description': 'Array of message objects for the conversation (for advanced use)',
                'example': [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello, how are you?"}
                ]
            },
            {
                'name': 'temperature',
                'type': 'number',
                'required': False,
                'label': 'Temperature',
                'description': 'Controls randomness (0.0 to 2.0)',
                'default': 1.0,
                'min': 0.0,
                'max': 2.0
            },
            {
                'name': 'max_tokens',
                'type': 'number',
                'required': False,
                'label': 'Max Tokens',
                'description': 'Maximum number of tokens to generate',
                'default': 1000,
                'min': 1,
                'max': 4096
            },
            {
                'name': 'top_p',
                'type': 'number',
                'required': False,
                'label': 'Top P',
                'description': 'Nucleus sampling parameter (0.0 to 1.0)',
                'default': 1.0,
                'min': 0.0,
                'max': 1.0
            },
            {
                'name': 'frequency_penalty',
                'type': 'number',
                'required': False,
                'label': 'Frequency Penalty',
                'description': 'Penalty for frequent tokens (-2.0 to 2.0)',
                'default': 0.0,
                'min': -2.0,
                'max': 2.0
            },
            {
                'name': 'presence_penalty',
                'type': 'number',
                'required': False,
                'label': 'Presence Penalty',
                'description': 'Penalty for new tokens (-2.0 to 2.0)',
                'default': 0.0,
                'min': -2.0,
                'max': 2.0
            },
            {
                'name': 'stop',
                'type': 'text',
                'required': False,
                'label': 'Stop Sequences',
                'description': 'Comma-separated stop sequences',
                'placeholder': '\\n,.,!'
            },
            {
                'name': 'stream',
                'type': 'boolean',
                'required': False,
                'label': 'Stream Response',
                'description': 'Whether to stream the response',
                'default': False
            }
        ]
    
    @property
    def output_params(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'content',
                'type': 'text',
                'label': 'Generated Content',
                'description': 'The generated text response'
            },
            {
                'name': 'role',
                'type': 'text',
                'label': 'Response Role',
                'description': 'Role of the response (usually "assistant")'
            },
            {
                'name': 'finish_reason',
                'type': 'text',
                'label': 'Finish Reason',
                'description': 'Why the generation stopped'
            },
            {
                'name': 'usage',
                'type': 'json',
                'label': 'Token Usage',
                'description': 'Information about token usage'
            },
            {
                'name': 'model',
                'type': 'text',
                'label': 'Model Used',
                'description': 'The actual model used for generation'
            },
            {
                'name': 'created',
                'type': 'number',
                'label': 'Created Timestamp',
                'description': 'Unix timestamp when the response was created'
            }
        ]
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führt eine Chat Completion Anfrage aus.
        
        Args:
            inputs: Dictionary mit Eingabeparametern
            
        Returns:
            Dictionary mit Antwortdaten
        """
        try:
            # Bereite API-Request vor
            headers = {
                'Authorization': f"Bearer {self.config['api_key']}",
                'Content-Type': 'application/json'
            }
            
            # Füge Organization-Header hinzu falls konfiguriert
            if 'organization' in self.config and self.config['organization']:
                headers['OpenAI-Organization'] = self.config['organization']
            
            # Bereite Request-Body vor
            payload = {
                'model': inputs['model'],
                'messages': inputs['messages']
            }
            
            # Füge optionale Parameter hinzu
            optional_params = [
                'temperature', 'max_tokens', 'top_p', 'frequency_penalty',
                'presence_penalty', 'stream'
            ]
            
            for param in optional_params:
                if param in inputs and inputs[param] is not None:
                    payload[param] = inputs[param]
            
            # Verarbeite Stop-Sequences
            if 'stop' in inputs and inputs['stop']:
                stop_sequences = [s.strip() for s in inputs['stop'].split(',') if s.strip()]
                if stop_sequences:
                    payload['stop'] = stop_sequences
            
            # API-URL
            base_url = self.config.get('base_url', 'https://api.openai.com/v1')
            url = f"{base_url}/chat/completions"
            
            # Timeout
            timeout = self.config.get('timeout', 30.0)
            
            # Führe API-Request aus
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    response_data = await response.json()
                    
                    if response.status != 200:
                        error_msg = response_data.get('error', {}).get('message', 'Unknown API error')
                        raise ImplementationError(f"OpenAI API error: {error_msg}")
                    
                    # Extrahiere Antwortdaten
                    choice = response_data['choices'][0]
                    message = choice['message']
                    
                    return {
                        'content': message.get('content', ''),
                        'role': message.get('role', 'assistant'),
                        'finish_reason': choice.get('finish_reason'),
                        'usage': response_data.get('usage', {}),
                        'model': response_data.get('model'),
                        'created': response_data.get('created'),
                        'raw_response': response_data
                    }
            
        except aiohttp.ClientError as e:
            raise ImplementationError(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            raise ImplementationError(f"Invalid JSON response: {str(e)}")
        except KeyError as e:
            raise ImplementationError(f"Unexpected response format: missing {str(e)}")
        except Exception as e:
            raise ImplementationError(f"Execution failed: {str(e)}")
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Testet die Verbindung zur OpenAI API.
        
        Returns:
            Dictionary mit Test-Ergebnissen
        """
        try:
            # Teste mit einer einfachen Anfrage
            test_inputs = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {'role': 'user', 'content': 'Hello, this is a connection test.'}
                ],
                'max_tokens': 10
            }
            
            result = await self.execute(test_inputs)
            
            return {
                'success': True,
                'message': 'Connection successful',
                'details': {
                    'model_used': result.get('model'),
                    'tokens_used': result.get('usage', {}).get('total_tokens', 0),
                    'response_preview': result.get('content', '')[:50] + '...' if len(result.get('content', '')) > 50 else result.get('content', '')
                }
            }
            
        except ImplementationError as e:
            return {
                'success': False,
                'message': f"Connection test failed: {e.message}",
                'details': e.details
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Connection test failed: {str(e)}",
                'details': {}
            }
    
    def get_example_inputs(self) -> Dict[str, Any]:
        """
        Gibt Beispiel-Eingabeparameter zurück.
        
        Returns:
            Dictionary mit Beispielwerten
        """
        return {
            'model': 'gpt-3.5-turbo',
            'prompt': 'Explain quantum computing in simple terms.',
            'temperature': 0.7,
            'max_tokens': 150,
            'top_p': 1.0,
            'frequency_penalty': 0.0,
            'presence_penalty': 0.0,
            'stream': False
        }
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Validiert die Konfiguration und mappt openai_api_key zu api_key für Kompatibilität.
        
        Returns:
            Dictionary mit Validierungsergebnis
        """
        errors = []
        
        # Prüfe API Key (unterstützt sowohl 'api_key' als auch 'openai_api_key' für v036 Kompatibilität)
        api_key = self.config.get('api_key') or self.config.get('openai_api_key')
        if not api_key:
            errors.append("Required parameter 'api_key' is missing")
        else:
            # Normalisiere API Key zu 'api_key' für interne Verwendung
            self.config['api_key'] = api_key
            # Entferne alte Key falls vorhanden
            if 'openai_api_key' in self.config and 'api_key' not in self.config:
                del self.config['openai_api_key']
        
        # Prüfe API Key Format
        if api_key and not api_key.startswith('sk-'):
            errors.append("API key must start with 'sk-'")
        
        # Validiere optionale Parameter
        if 'timeout' in self.config:
            try:
                timeout = float(self.config['timeout'])
                if timeout <= 0:
                    errors.append("Timeout must be a positive number")
            except (ValueError, TypeError):
                errors.append("Timeout must be a valid number")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validiert die Eingabeparameter und mappt 'prompt' zu 'messages' für Kompatibilität.
        
        Args:
            inputs: Dictionary mit Eingabeparametern
            
        Returns:
            Dictionary mit Validierungsergebnis
        """
        errors = []
        
        # Prüfe erforderliche Parameter
        if not inputs.get('model'):
            errors.append("Parameter 'model' is required")
        
        # Handle prompt to messages mapping für v036 Kompatibilität
        if not inputs.get('messages') and inputs.get('prompt'):
            # Konvertiere prompt zu messages Format
            inputs['messages'] = [
                {'role': 'user', 'content': str(inputs['prompt'])}
            ]
            # Entferne prompt Parameter nach der Konvertierung
            if 'prompt' in inputs:
                del inputs['prompt']
        
        if not inputs.get('messages'):
            errors.append("Either 'messages' (for advanced conversation) or 'prompt' (for simple queries) is required")
        elif not isinstance(inputs['messages'], list):
            errors.append("Parameter 'messages' must be a list")
        elif len(inputs['messages']) == 0:
            errors.append("Parameter 'messages' cannot be empty")
        
        # Validiere Messages-Format
        if isinstance(inputs.get('messages'), list):
            for i, message in enumerate(inputs['messages']):
                if not isinstance(message, dict):
                    errors.append(f"Message {i} must be a dictionary")
                    continue
                
                if 'role' not in message:
                    errors.append(f"Message {i} must have a 'role' field")
                
                if 'content' not in message:
                    errors.append(f"Message {i} must have a 'content' field")
                
                if message.get('role') not in ['system', 'user', 'assistant']:
                    errors.append(f"Message {i} role must be 'system', 'user', or 'assistant'")
        
        # Validiere numerische Parameter
        numeric_params = {
            'temperature': (0.0, 2.0),
            'max_tokens': (1, 4096),
            'top_p': (0.0, 1.0),
            'frequency_penalty': (-2.0, 2.0),
            'presence_penalty': (-2.0, 2.0)
        }
        
        for param, (min_val, max_val) in numeric_params.items():
            if param in inputs and inputs[param] is not None:
                try:
                    value = float(inputs[param])
                    if not (min_val <= value <= max_val):
                        errors.append(f"Parameter '{param}' must be between {min_val} and {max_val}")
                except (ValueError, TypeError):
                    errors.append(f"Parameter '{param}' must be a valid number")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
