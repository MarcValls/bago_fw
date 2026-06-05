#!/usr/bin/env python3
"""
Tools Manager — Sistema de herramientas conectables
"""

import json
from pathlib import Path
from typing import Dict, List, Any

class ToolsManager:
    """Gestiona herramientas conectables"""
    
    def __init__(self, tools_dir: Path):
        self.tools_dir = tools_dir
        self.tools_dir.mkdir(parents=True, exist_ok=True)
        self.tools = {}
    
    def register_tool(self, tool_name: str, tool_config: Dict) -> bool:
        """Registra una herramienta"""
        self.tools[tool_name] = {
            'name': tool_name,
            'enabled': tool_config.get('enabled', True),
            'description': tool_config.get('description', ''),
            'risk_level': tool_config.get('risk_level', 'moderate'),
            'config': tool_config
        }
        return True
    
    def get_tools(self) -> Dict:
        """Devuelve todas las herramientas registradas"""
        return self.tools
    
    def get_tool(self, tool_name: str) -> Optional[Dict]:
        """Devuelve una herramienta específica"""
        return self.tools.get(tool_name)
    
    def enable_tool(self, tool_name: str) -> bool:
        """Habilita una herramienta"""
        if tool_name in self.tools:
            self.tools[tool_name]['enabled'] = True
            return True
        return False
    
    def disable_tool(self, tool_name: str) -> bool:
        """Deshabilita una herramienta"""
        if tool_name in self.tools:
            self.tools[tool_name]['enabled'] = False
            return True
        return False
    
    def get_active_tools(self) -> List[Dict]:
        """Devuelve herramientas activas"""
        return [t for t in self.tools.values() if t['enabled']]
