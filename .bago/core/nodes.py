#!/usr/bin/env python3
"""
Nodes Manager — Gestor de nodos y conexiones
Conectores como nodos con modos: lectura, escritura, bloqueo, aislamiento
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime

class NodeMode(Enum):
    """Modos de conexión de nodos"""
    READ = "read"           # Solo lectura
    WRITE = "write"         # Lectura y escritura
    BLOCKED = "blocked"     # Bloqueado
    ISOLATED = "isolated"   # Aislado

class NodesManager:
    """Gestiona registro de nodos y sus conexiones"""
    
    def __init__(self, registry_path: Path, connections_path: Path):
        self.registry_path = registry_path
        self.connections_path = connections_path
        self.nodes = {}
        self.connections = []
        self.load()
    
    def load(self):
        """Carga registro de nodos y conexiones"""
        if self.registry_path.exists():
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.nodes = {n['id']: n for n in data.get('nodes', [])}
        
        if self.connections_path.exists():
            with open(self.connections_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.connections = data.get('connections', [])
    
    def register_node(self, node_id: str, node_name: str, node_type: str) -> bool:
        """Registra un nuevo nodo"""
        if node_id in self.nodes:
            return False
        
        self.nodes[node_id] = {
            'id': node_id,
            'name': node_name,
            'type': node_type,
            'registered_at': datetime.now().isoformat(),
            'mode': NodeMode.READ.value,
            'enabled': True
        }
        self._save_registry()
        return True
    
    def connect_nodes(self, node_a: str, node_b: str, mode: str = NodeMode.READ.value) -> bool:
        """Conecta dos nodos"""
        if node_a not in self.nodes or node_b not in self.nodes:
            return False
        
        # Verificar que no estén aislados
        if self.nodes[node_a]['mode'] == NodeMode.ISOLATED.value:
            return False
        if self.nodes[node_b]['mode'] == NodeMode.ISOLATED.value:
            return False
        
        connection = {
            'from': node_a,
            'to': node_b,
            'mode': mode,
            'connected_at': datetime.now().isoformat(),
            'enabled': True
        }
        self.connections.append(connection)
        self._save_connections()
        return True
    
    def disconnect_nodes(self, node_a: str, node_b: str) -> bool:
        """Desconecta dos nodos"""
        initial_count = len(self.connections)
        self.connections = [
            c for c in self.connections
            if not (c['from'] == node_a and c['to'] == node_b)
        ]
        if len(self.connections) < initial_count:
            self._save_connections()
            return True
        return False
    
    def set_node_mode(self, node_id: str, mode: str) -> bool:
        """Cambia el modo de un nodo"""
        if node_id not in self.nodes:
            return False
        
        if mode not in [m.value for m in NodeMode]:
            return False
        
        self.nodes[node_id]['mode'] = mode
        
        # Si es aislado, desconectar todas sus conexiones
        if mode == NodeMode.ISOLATED.value:
            self.connections = [
                c for c in self.connections
                if c['from'] != node_id and c['to'] != node_id
            ]
        
        self._save_registry()
        self._save_connections()
        return True
    
    def get_node(self, node_id: str) -> Optional[Dict]:
        """Devuelve información de un nodo"""
        return self.nodes.get(node_id)
    
    def get_nodes(self) -> List[Dict]:
        """Devuelve todos los nodos"""
        return list(self.nodes.values())
    
    def get_connections(self) -> List[Dict]:
        """Devuelve todas las conexiones"""
        return self.connections
    
    def get_node_connections(self, node_id: str) -> List[Dict]:
        """Devuelve conexiones de un nodo específico"""
        return [c for c in self.connections if c['from'] == node_id or c['to'] == node_id]
    
    def _save_registry(self):
        """Guarda el registro de nodos"""
        data = {
            'nodes': list(self.nodes.values()),
            'last_updated': datetime.now().isoformat()
        }
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_connections(self):
        """Guarda las conexiones"""
        data = {
            'connections': self.connections,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.connections_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
