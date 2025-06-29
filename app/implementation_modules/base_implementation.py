"""
Base Implementation Class für VNTRAI Implementation Modules
Basierend auf v036 base.py, aber für Implementation-Modules optimiert
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import json
import traceback
from datetime import datetime
import logging

class BaseImplementation(ABC):
    """
    Abstract base class für alle Implementation Modules.
    Jede Implementation muss diese Klasse erweitern und die abstrakten Methoden implementieren.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialisiert die Implementation mit Konfiguration.
        
        Args:
            config: Dictionary mit Konfigurationsparametern
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.last_error = None
        self.last_execution = None
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Der Name der Implementation (z.B. 'openai_chatcompletion')"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Beschreibung der Implementation"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Version der Implementation"""
        pass
    
    @property
    @abstractmethod
    def author(self) -> str:
        """Autor der Implementation"""
        pass
    
    @property
    @abstractmethod
    def required_config_params(self) -> List[Dict[str, Any]]:
        """
        Liste der erforderlichen Konfigurationsparameter.
        
        Returns:
            List[Dict] mit Parameter-Definitionen:
            [
                {
                    'name': 'api_key',
                    'type': 'text',
                    'required': True,
                    'label': 'API Key',
                    'description': 'Your OpenAI API key'
                }
            ]
        """
        pass
    
    @property
    @abstractmethod
    def input_params(self) -> List[Dict[str, Any]]:
        """
        Liste der Eingabeparameter für die Ausführung.
        
        Returns:
            List[Dict] mit Parameter-Definitionen
        """
        pass
    
    @property
    @abstractmethod
    def output_params(self) -> List[Dict[str, Any]]:
        """
        Liste der Ausgabeparameter.
        
        Returns:
            List[Dict] mit Parameter-Definitionen
        """
        pass
    
    @abstractmethod
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führt die Implementation mit den gegebenen Eingaben aus.
        
        Args:
            inputs: Dictionary mit Eingabeparametern
            
        Returns:
            Dictionary mit Ausgabedaten
            
        Raises:
            ImplementationError: Wenn die Ausführung fehlschlägt
        """
        pass
    
    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """
        Testet die Verbindung mit den konfigurierten Parametern.
        
        Returns:
            Dictionary mit Test-Ergebnissen:
            {
                'success': True/False,
                'message': 'Test message',
                'details': {...}
            }
        """
        pass
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Validiert die Konfiguration der Implementation.
        
        Returns:
            Dictionary mit Validierungsergebnissen
        """
        try:
            errors = []
            warnings = []
            
            # Prüfe erforderliche Parameter
            for param in self.required_config_params:
                if param.get('required', False):
                    param_name = param['name']
                    if param_name not in self.config or not self.config[param_name]:
                        errors.append(f"Required parameter '{param_name}' is missing")
            
            # Typ-Validierung
            for param in self.required_config_params:
                param_name = param['name']
                if param_name in self.config:
                    expected_type = param.get('type', 'text')
                    value = self.config[param_name]
                    
                    if expected_type == 'number' and not isinstance(value, (int, float)):
                        try:
                            float(value)
                        except (ValueError, TypeError):
                            errors.append(f"Parameter '{param_name}' must be a number")
                    
                    elif expected_type == 'boolean' and not isinstance(value, bool):
                        if str(value).lower() not in ['true', 'false', '1', '0']:
                            errors.append(f"Parameter '{param_name}' must be a boolean")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Config validation failed: {str(e)}"],
                'warnings': []
            }
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validiert die Eingabeparameter für die Ausführung.
        
        Args:
            inputs: Dictionary mit Eingabeparametern
            
        Returns:
            Dictionary mit Validierungsergebnissen
        """
        try:
            errors = []
            warnings = []
            
            # Prüfe erforderliche Eingabeparameter
            for param in self.input_params:
                if param.get('required', False):
                    param_name = param['name']
                    if param_name not in inputs or inputs[param_name] is None:
                        errors.append(f"Required input parameter '{param_name}' is missing")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Input validation failed: {str(e)}"],
                'warnings': []
            }
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Gibt Metadaten der Implementation zurück.
        
        Returns:
            Dictionary mit Metadaten
        """
        return {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'author': self.author,
            'required_config_params': self.required_config_params,
            'input_params': self.input_params,
            'output_params': self.output_params,
            'last_execution': self.last_execution,
            'last_error': self.last_error
        }
    
    def log_execution(self, inputs: Dict[str, Any], outputs: Dict[str, Any], 
                     execution_time: float = None, error: str = None):
        """
        Loggt eine Ausführung der Implementation.
        
        Args:
            inputs: Eingabeparameter
            outputs: Ausgabedaten 
            execution_time: Ausführungszeit in Sekunden
            error: Fehlermeldung falls aufgetreten
        """
        execution_log = {
            'timestamp': datetime.now().isoformat(),
            'inputs': inputs,
            'outputs': outputs if not error else None,
            'execution_time': execution_time,
            'error': error,
            'success': error is None
        }
        
        self.last_execution = execution_log
        if error:
            self.last_error = error
            self.logger.error(f"Execution failed: {error}")
        else:
            self.logger.info(f"Execution successful in {execution_time:.2f}s")
    
    def get_example_inputs(self) -> Dict[str, Any]:
        """
        Gibt Beispiel-Eingabeparameter zurück.
        
        Returns:
            Dictionary mit Beispielwerten
        """
        examples = {}
        for param in self.input_params:
            param_name = param['name']
            param_type = param.get('type', 'text')
            
            if 'example' in param:
                examples[param_name] = param['example']
            elif param_type == 'text':
                examples[param_name] = f"Example {param_name}"
            elif param_type == 'number':
                examples[param_name] = 1.0
            elif param_type == 'boolean':
                examples[param_name] = True
            elif param_type == 'json':
                examples[param_name] = {}
            else:
                examples[param_name] = ""
        
        return examples


class ImplementationError(Exception):
    """Custom Exception für Implementation-Fehler"""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'error': self.message,
            'details': self.details,
            'timestamp': self.timestamp
        }


class ImplementationRegistry:
    """Registry für alle verfügbaren Implementation Modules"""
    
    _implementations: Dict[str, type] = {}
    
    @classmethod
    def register(cls, implementation_class: type):
        """
        Registriert eine Implementation-Klasse.
        
        Args:
            implementation_class: Klasse die BaseImplementation erweitert
        """
        if not issubclass(implementation_class, BaseImplementation):
            raise ValueError("Implementation must inherit from BaseImplementation")
        
        # Erstelle temporäre Instanz um Namen zu bekommen
        temp_instance = implementation_class()
        cls._implementations[temp_instance.name] = implementation_class
    
    @classmethod
    def get_implementation(cls, name: str) -> Optional[type]:
        """
        Holt eine Implementation-Klasse anhand des Namens.
        
        Args:
            name: Name der Implementation
            
        Returns:
            Implementation-Klasse oder None
        """
        return cls._implementations.get(name)
    
    @classmethod
    def list_implementations(cls) -> List[str]:
        """
        Gibt eine Liste aller registrierten Implementation-Namen zurück.
        
        Returns:
            Liste der Implementation-Namen
        """
        return list(cls._implementations.keys())
    
    @classmethod
    def get_all_metadata(cls) -> Dict[str, Dict[str, Any]]:
        """
        Gibt Metadaten aller registrierten Implementations zurück.
        
        Returns:
            Dictionary mit Metadaten aller Implementations
        """
        metadata = {}
        for name, impl_class in cls._implementations.items():
            try:
                temp_instance = impl_class()
                metadata[name] = temp_instance.get_metadata()
            except Exception as e:
                metadata[name] = {
                    'name': name,
                    'error': f"Failed to load metadata: {str(e)}"
                }
        return metadata
