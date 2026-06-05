#!/usr/bin/env python3
"""
Provider Manager — Gestión de proveedores intercambiables
"""

import json
from pathlib import Path
from typing import Dict, Optional

class ProviderManager:
    """Gestiona múltiples proveedores LLM"""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = {}
        self.active_provider = None
        self.load_config()
    
    def load_config(self):
        """Carga la configuración de proveedores"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        self.active_provider = self.config.get('default_provider', 'ollama-local')
    
    def get_active_provider(self) -> Dict:
        """Devuelve el proveedor activo"""
        providers = self.config.get('providers', {})
        active_config = providers.get(self.active_provider, {})
        return {
            'name': self.active_provider,
            'enabled': active_config.get('enabled', False),
            'type': active_config.get('type', 'unknown'),
            'config': active_config
        }
    
    def switch_provider(self, provider_name: str) -> bool:
        """Cambia el proveedor activo"""
        providers = self.config.get('providers', {})
        if provider_name not in providers:
            return False
        
        if not providers[provider_name].get('enabled', False):
            return False
        
        self.active_provider = provider_name
        return True
    
    def get_available_providers(self) -> list:
        """Lista proveedores disponibles"""
        providers = self.config.get('providers', {})
        available = []
        for name, config in providers.items():
            if config.get('enabled', False):
                available.append({
                    'name': name,
                    'type': config.get('type', 'unknown')
                })
        return available
    
    def get_security_config(self) -> Dict:
        """Devuelve configuración de seguridad"""
        return self.config.get('security', {})
