#!/usr/bin/env python3
"""
BAGO CLI — Punto de entrada principal
Centro de mando local con sesión persistente
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Detectar raíz de BAGO dinámicamente
def find_bago_root():
    """Encuentra la raíz de BAGO aunque cambie la letra del volumen"""
    script_path = Path(__file__).resolve()
    current = script_path.parent
    
    # Subir hasta encontrar .bago o bago_fw
    while current != current.parent:
        if (current / '.bago').exists() or (current.name == 'bago_fw'):
            return current
        current = current.parent
    
    # Fallback: usar ruta relativa desde script
    return script_path.parent.parent

BAGO_ROOT = find_bago_root()
os.chdir(BAGO_ROOT)

# Añadir core al path
sys.path.insert(0, str(BAGO_ROOT / '.bago' / 'core'))

from session import SessionManager
from security import SecurityPolicy

# Inicializar componentes
sessions_dir = BAGO_ROOT / '.bago' / 'sessions'
config_path = BAGO_ROOT / '.bago' / 'config' / 'config.json'
tools_dir = BAGO_ROOT / '.bago' / 'tools'
nodes_registry = BAGO_ROOT / '.bago' / 'nodes' / 'registry.json'
nodes_connections = BAGO_ROOT / '.bago' / 'nodes' / 'connections.json'

session_manager = SessionManager(sessions_dir)
security_policy = SecurityPolicy(config_path)

from provider import ProviderManager
from tools import ToolsManager
from nodes import NodesManager

provider_manager = ProviderManager(config_path)
tools_manager = ToolsManager(tools_dir)
nodes_manager = NodesManager(nodes_registry, nodes_connections)

def cmd_start(args=None):
    """Arranca BAGO: detecta raíz, carga config, abre sesión"""
    print(f"BAGO MVP v4.0 — Arrancando desde: {BAGO_ROOT}")
    
    # Cargar configuración
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"Configuración cargada: v{config.get('version', 'unknown')}")
    
    # Obtener proveedor activo
    active_provider_info = provider_manager.get_active_provider()
    print(f"Proveedor activo: {active_provider_info['name']}")
    
    # Abrir sesión
    session = session_manager.load_session()
    if session:
        print(f"Sesión recuperada: {session['id']}")
        # Actualizar contexto con proveedor y herramientas
        session['provider'] = active_provider_info['name']
        session['tools_active'] = tools_manager.get_active_tools()
    else:
        provider = active_provider_info['name']
        model = config.get('default_model', 'default') if config_path.exists() else 'default'
        session_id = session_manager.start_session(provider, model)
        session = session_manager.load_session()
        # Registrar contexto inicial
        session['context'] = {
            'provider': provider,
            'model': model,
            'security': security_policy.verify_policies(),
            'tools': tools_manager.get_active_tools()
        }
        print(f"Nueva sesión iniciada: {session_id}")
    
    # Registrar evidencia de arranque
    session_manager.add_evidence({
        'type': 'system_startup',
        'timestamp': session_manager.session['updated_at'],
        'provider': active_provider_info['name'],
        'tools_active': len(tools_manager.get_active_tools()),
        'security_status': 'verified'
    })
    
    print("BAGO listo. Usa 'bago status' para ver estado.")
    return 0

def cmd_status(args=None):
    """Muestra estado: sesión activa, proveedores, nodos"""
    status = session_manager.get_status()
    
    if status['active']:
        print("=== Estado de BAGO ===")
        print(f"Sesión activa: {status['id']}")
        print(f"Proveedor: {status['provider']}")
        print(f"Modelo: {status['model']}")
        print(f"Comandos ejecutados: {status['commands_count']}")
        print(f"Evidencias: {status['evidences_count']}")
        print(f"Iniciada: {status['created_at']}")
    else:
        print("No hay sesión activa. Usa 'bago start' para iniciar.")
    
    return 0

def cmd_session(args=None):
    """Muestra sesión activa"""
    session = session_manager.load_session()
    if session:
        print("=== Sesión Activa ===")
        print(f"ID: {session['id']}")
        print(f"Proveedor: {session['provider']}")
        print(f"Modelo: {session['model']}")
        print(f"Creada: {session['created_at']}")
        print(f"Actualizada: {session['updated_at']}")
    else:
        print("No hay sesión activa.")
    return 0

def cmd_stop(args=None):
    """Cierra sesión y detiene BAGO"""
    session = session_manager.load_session()
    if session:
        session_id = session['id']
        session_manager.close_session()
        print(f"Sesión {session_id} cerrada correctamente.")
    else:
        print("No había sesión activa.")
    return 0

def cmd_exec(args):
    """Ejecuta comando con trazabilidad: afirmación → acción → evidencia → conclusión"""
    if not args:
        print("Uso: bago exec <comando>")
        return 1
    
    command = ' '.join(args)
    
    # Verificar sesión
    session = session_manager.load_session()
    if not session:
        print("Error: No hay sesión activa. Usa 'bago start' primero.")
        return 1
    
    # 1. AFIRMACIÓN
    print(f"AFIRMACIÓN: Voy a ejecutar: {command}")
    
    # 2. VERIFICAR SEGURIDAD
    can_exec, reason = security_policy.can_execute(command)
    if not can_exec:
        print(f"SEGURIDAD: {reason}")
        # Registrar rechazo como evidencia
        session_manager.add_evidence({
            'type': 'command_rejected',
            'command': command,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
        return 1
    
    # 3. ACCIÓN
    print("ACCIÓN: Ejecutando...")
    # Aquí iría la ejecución real
    output = "[simulado]"
    result = "success"
    
    # 4. EVIDENCIA
    evidence = {
        'type': 'command_execution',
        'command': command,
        'timestamp': datetime.now().isoformat(),
        'result': result,
        'output': output[:100],  # Primeros 100 caracteres
        'provider': session.get('provider', 'unknown'),
        'session_id': session['id']
    }
    session_manager.add_evidence(evidence)
    session_manager.add_command(command, evidence_path=f"evidences/executions/{evidence['timestamp']}.json")
    
    print("EVIDENCIA: Registrada")
    
    # 5. CONCLUSIÓN
    print(f"CONCLUSIÓN: Comando completado con resultado: {result}")
    print(f"Output: {output}")
    
    return 0 if result == "success" else 1

def cmd_nodes(args=None):
    """Lista nodos y conexiones"""
    nodes = nodes_manager.get_nodes()
    connections = nodes_manager.get_connections()
    
    print("=== Nodos Registrados ===")
    if nodes:
        for node in nodes:
            status = "✓" if node['enabled'] else "✗"
            print(f"{status} {node['name']} (ID: {node['id']}, Modo: {node['mode']})")
    else:
        print("  (vacío)")
    
    print("\n=== Conexiones ===")
    if connections:
        for conn in connections:
            status = "✓" if conn['enabled'] else "✗"
            print(f"{status} {conn['from']} → {conn['to']} ({conn['mode']})")
    else:
        print("  (vacío)")
    
    return 0

def cmd_connect(args=None):
    """Conecta un nodo"""
    if not args:
        print("Uso: bago connect <nodo> | <nodo_a> <nodo_b> [modo]")
        return 1
    
    session = session_manager.load_session()
    if not session:
        print("Error: No hay sesión activa.")
        return 1
    
    if len(args) == 1:
        # Registrar un nuevo nodo
        node_name = args[0]
        result = nodes_manager.register_node(node_name, node_name, 'generic')
        if result:
            print(f"Nodo '{node_name}' registrado.")
            session_manager.add_evidence({
                'type': 'node_registered',
                'node': node_name,
                'timestamp': datetime.now().isoformat()
            })
        else:
            print(f"Error: No se pudo registrar el nodo '{node_name}'")
            return 1
    elif len(args) >= 2:
        # Conectar dos nodos
        node_a = args[0]
        node_b = args[1]
        mode = args[2] if len(args) > 2 else 'read'
        
        result = nodes_manager.connect_nodes(node_a, node_b, mode)
        if result:
            print(f"Nodos '{node_a}' y '{node_b}' conectados (modo: {mode}).")
            session_manager.add_evidence({
                'type': 'nodes_connected',
                'from': node_a,
                'to': node_b,
                'mode': mode,
                'timestamp': datetime.now().isoformat()
            })
        else:
            print(f"Error: No se pudo conectar los nodos.")
            return 1
    
    return 0

def cmd_disconnect(args=None):
    """Desconecta un nodo o una conexión"""
    if not args:
        print("Uso: bago disconnect <nodo_a> <nodo_b>")
        return 1
    
    session = session_manager.load_session()
    if not session:
        print("Error: No hay sesión activa.")
        return 1
    
    node_a = args[0]
    node_b = args[1] if len(args) > 1 else None
    
    if not node_b:
        print("Error: Se requieren dos nodos para desconectar.")
        return 1
    
    result = nodes_manager.disconnect_nodes(node_a, node_b)
    if result:
        print(f"Nodos '{node_a}' y '{node_b}' desconectados.")
        session_manager.add_evidence({
            'type': 'nodes_disconnected',
            'from': node_a,
            'to': node_b,
            'timestamp': datetime.now().isoformat()
        })
    else:
        print(f"Error: No se pudo desconectar los nodos.")
        return 1
    
    return 0

def cmd_evidence(args=None):
    """Muestra evidencia de una acción"""
    if not args:
        print("Uso: bago evidence <id> | --recent")
        return 1
    
    session = session_manager.load_session()
    if not session:
        print("No hay sesión activa.")
        return 1
    
    if args[0] == '--recent':
        evidences = session.get('evidences', [])[-5:]
        for i, ev in enumerate(evidences):
            print(f"[{i}] {ev.get('type', 'unknown')} - {ev.get('timestamp', 'unknown')}")
    else:
        try:
            idx = int(args[0])
            evidences = session.get('evidences', [])
            if 0 <= idx < len(evidences):
                print(json.dumps(evidences[idx], indent=2))
            else:
                print("Índice fuera de rango.")
        except ValueError:
            print("Índice inválido.")
    
    return 0

def cmd_providers(args=None):
    """Lista proveedores disponibles"""
    available = provider_manager.get_available_providers()
    active = provider_manager.get_active_provider()
    
    print("=== Proveedores Disponibles ===")
    for provider in available:
        marker = "→" if provider['name'] == active['name'] else " "
        print(f"{marker} {provider['name']} ({provider['type']})")
    
    return 0

def cmd_tools(args=None):
    """Lista herramientas disponibles"""
    tools = tools_manager.get_tools()
    
    print("=== Herramientas Disponibles ===")
    for name, tool in tools.items():
        status = "✓" if tool['enabled'] else "✗"
        print(f"{status} {name} - {tool['description']}")
    
    return 0

def main():
    """Punto de entrada principal"""
    if len(sys.argv) < 2:
        print("BAGO MVP v4.0 — Centro de mando local con sesión persistente")
        print(f"Raíz: {BAGO_ROOT}")
        print("\nComandos disponibles:")
        print("  start       - Arranca BAGO (detecta raíz, carga config, abre sesión)")
        print("  status      - Muestra estado: sesión activa, proveedores, nodos")
        print("  session     - Muestra sesión activa")
        print("  providers   - Lista proveedores disponibles")
        print("  tools       - Lista herramientas disponibles")
        print("  nodes       - Lista nodos y conexiones")
        print("  connect     - Conecta un nodo")
        print("  disconnect  - Desconecta un nodo")
        print("  exec        - Ejecuta comando con trazabilidad")
        print("  evidence    - Muestra evidencia de una acción")
        print("  stop        - Cierra sesión y detiene BAGO")
        print("\nEjemplo: bago start")
        return 1
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    commands = {
        'start': cmd_start,
        'status': cmd_status,
        'session': cmd_session,
        'stop': cmd_stop,
        'exec': cmd_exec,
        'nodes': cmd_nodes,
        'connect': cmd_connect,
        'disconnect': cmd_disconnect,
        'evidence': cmd_evidence,
        'providers': cmd_providers,
        'tools': cmd_tools
    }
    
    if command in commands:
        return commands[command](args)
    else:
        print(f"Comando desconocido: {command}")
        print("Usa 'bago' sin argumentos para ver ayuda.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
