"""
Implementation Module Manager für VNTRAI
Verwaltet das Laden und Ausführen von Implementation Modules
"""

import os
import importlib
import inspect
from typing import Dict, Any, List, Optional, Type
import asyncio
import time
import traceback
from datetime import datetime

from .base_implementation import BaseImplementation, ImplementationError, ImplementationRegistry

# Explizite Imports der Implementation Module um sicherzustellen, dass sie registriert werden
try:
    from . import openai_chatcompletion
    print("✓ OpenAI ChatCompletion module imported")
except ImportError as e:
    print(f"⚠ Failed to import openai_chatcompletion: {e}")

try:
    from . import google_sheets
    print("✓ Google Sheets module imported")
except ImportError as e:
    print(f"⚠ Failed to import google_sheets: {e}")


class ImplementationManager:
    """
    Manager für Implementation Modules.
    Lädt, verwaltet und führt Implementation Modules aus.
    """
    
    def __init__(self, modules_dir: str = "app/implementation_modules"):
        """
        Initialisiert den ImplementationManager.
        
        Args:
            modules_dir: Verzeichnis mit Implementation Modules
        """
        self.modules_dir = modules_dir
        self.loaded_implementations: Dict[str, BaseImplementation] = {}
        
        # Lade Module automatisch beim Start
        try:
            self.load_all_implementations()
        except Exception as e:
            print(f"Warning: Could not auto-load implementation modules: {e}")

    def load_all_implementations(self) -> Dict[str, Any]:
        """
        Lädt alle verfügbaren Implementation Modules.
        
        Returns:
            Dictionary mit Ladergebnissen
        """
        results = {
            'loaded': [],
            'failed': [],
            'total': 0
        }
        
        try:
            # Lade alle Python-Dateien im Modules-Verzeichnis
            if not os.path.exists(self.modules_dir):
                return results
            
            for filename in os.listdir(self.modules_dir):
                if filename.endswith('.py') and not filename.startswith('__') and filename != 'base_implementation.py':
                    module_name = filename[:-3]  # Remove .py extension
                    
                    try:
                        self._load_implementation_module(module_name)
                        results['loaded'].append(module_name)
                    except Exception as e:
                        results['failed'].append({
                            'module': module_name,
                            'error': str(e)
                        })
                    
                    results['total'] += 1
            
            return results
            
        except Exception as e:
            results['failed'].append({
                'module': 'loader',
                'error': f"Failed to scan modules directory: {str(e)}"
            })
            return results
    
    def _load_implementation_module(self, module_name: str):
        """
        Lädt ein einzelnes Implementation Module.
        
        Args:
            module_name: Name des Moduls (ohne .py)
        """
        try:
            # Import des Moduls
            module_path = f"app.implementation_modules.{module_name}"
            module = importlib.import_module(module_path)
            
            # Finde Implementation-Klassen im Modul
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseImplementation) and 
                    obj != BaseImplementation):
                    
                    # Registriere Implementation
                    ImplementationRegistry.register(obj)
                    
        except Exception as e:
            raise ImplementationError(f"Failed to load module {module_name}: {str(e)}")
    
    def get_implementation(self, name: str, config: Dict[str, Any] = None) -> Optional[BaseImplementation]:
        """
        Holt eine konfigurierte Implementation-Instanz.
        
        Args:
            name: Name der Implementation
            config: Konfigurationsparameter
            
        Returns:
            Konfigurierte Implementation-Instanz oder None
        """
        try:
            # Prüfe ob Implementation verfügbar ist
            impl_class = ImplementationRegistry.get_implementation(name)
            if not impl_class:
                return None
            
            # Erstelle Instanz mit Konfiguration
            implementation = impl_class(config or {})
            
            # Validiere Konfiguration
            validation = implementation.validate_config()
            if not validation['valid']:
                raise ImplementationError(
                    f"Invalid configuration for {name}: {'; '.join(validation['errors'])}"
                )
            
            return implementation
            
        except Exception as e:
            raise ImplementationError(f"Failed to get implementation {name}: {str(e)}")
    
    async def execute_implementation(self, name: str, config: Dict[str, Any], 
                                   inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führt eine Implementation aus.
        
        Args:
            name: Name der Implementation
            config: Konfigurationsparameter
            inputs: Eingabeparameter
            
        Returns:
            Dictionary mit Ausführungsergebnissen
        """
        start_time = time.time()
        implementation = None
        
        try:
            # Hole Implementation
            implementation = self.get_implementation(name, config)
            if not implementation:
                raise ImplementationError(f"Implementation '{name}' not found")
            
            # Validiere Eingaben
            input_validation = implementation.validate_inputs(inputs)
            if not input_validation['valid']:
                raise ImplementationError(
                    f"Invalid inputs: {'; '.join(input_validation['errors'])}"
                )
            
            # Führe Implementation aus
            outputs = await implementation.execute(inputs)
            execution_time = time.time() - start_time
            
            # Logge erfolgreiche Ausführung
            implementation.log_execution(inputs, outputs, execution_time)
            
            return {
                'success': True,
                'outputs': outputs,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            # Logge Fehler
            if implementation:
                implementation.log_execution(inputs, None, execution_time, error_msg)
            
            return {
                'success': False,
                'error': error_msg,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat(),
                'traceback': traceback.format_exc()
            }
    
    async def test_implementation(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Testet eine Implementation.
        
        Args:
            name: Name der Implementation
            config: Konfigurationsparameter
            
        Returns:
            Dictionary mit Test-Ergebnissen
        """
        try:
            # Hole Implementation
            implementation = self.get_implementation(name, config)
            if not implementation:
                return {
                    'success': False,
                    'error': f"Implementation '{name}' not found"
                }
            
            # Führe Connection-Test aus
            test_result = await implementation.test_connection()
            
            return {
                'success': test_result.get('success', False),
                'message': test_result.get('message', 'No message'),
                'details': test_result.get('details', {}),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'traceback': traceback.format_exc()
            }
    
    def list_available_implementations(self) -> List[Dict[str, Any]]:
        """
        Gibt eine Liste aller verfügbaren Implementations zurück.
        
        Returns:
            Liste mit Implementation-Metadaten
        """
        implementations = []
        
        for name in ImplementationRegistry.list_implementations():
            try:
                impl_class = ImplementationRegistry.get_implementation(name)
                temp_instance = impl_class()
                implementations.append(temp_instance.get_metadata())
            except Exception as e:
                implementations.append({
                    'name': name,
                    'error': f"Failed to load metadata: {str(e)}"
                })
        
        return implementations
    
    def get_implementation_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Gibt Metadaten für eine spezifische Implementation zurück.
        
        Args:
            name: Name der Implementation
            
        Returns:
            Dictionary mit Metadaten oder None
        """
        try:
            impl_class = ImplementationRegistry.get_implementation(name)
            if not impl_class:
                return None
            
            temp_instance = impl_class()
            return temp_instance.get_metadata()
            
        except Exception as e:
            return {
                'name': name,
                'error': f"Failed to load metadata: {str(e)}"
            }
    
    def reload_implementations(self) -> Dict[str, Any]:
        """
        Lädt alle Implementation Modules neu.
        
        Returns:
            Dictionary mit Reload-Ergebnissen
        """
        # Clear registry
        ImplementationRegistry._implementations.clear()
        self.loaded_implementations.clear()
        
        # Reload all modules
        return self.load_all_implementations()


# Globale Manager-Instanz
implementation_manager = ImplementationManager()
