#!/usr/bin/env python3
"""
SessionManager — Centro operativo de BAGO
Todo pasa por sesión: contexto, proveedor, herramienta, evidencia, resultado
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

class SessionManager:
    """Gestiona sesiones persistentes de BAGO"""
    
    def __init__(self, sessions_dir: Path):
        self.sessions_dir = sessions_dir
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.active_session_file = self.sessions_dir / 'active.json'
        self.session = None
    
    def start_session(self, provider: str = 'default', model: str = 'default'):
        """Abre una nueva sesión"""
        session_id = str(uuid.uuid4())[:8]
        self.session = {
            'id': session_id,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'provider': provider,
            'model': model,
            'context': {},
            'tools_active': [],
            'commands_executed': [],
            'evidences': []
        }
        self._save_session()
        return session_id
    
    def _save_session(self):
        """Guarda la sesión activa"""
        if self.session:
            self.session['updated_at'] = datetime.now().isoformat()
            with open(self.active_session_file, 'w', encoding='utf-8') as f:
                json.dump(self.session, f, indent=2, ensure_ascii=False)
    
    def load_session(self):
        """Carga la sesión activa si existe"""
        if self.active_session_file.exists():
            with open(self.active_session_file, 'r', encoding='utf-8') as f:
                self.session = json.load(f)
            return self.session
        return None
    
    def add_command(self, command: str, evidence_path: str = None):
        """Registra un comando ejecutado"""
        if self.session:
            self.session['commands_executed'].append({
                'command': command,
                'timestamp': datetime.now().isoformat(),
                'evidence': evidence_path
            })
            self._save_session()
    
    def add_evidence(self, evidence: dict):
        """Añade una evidencia a la sesión"""
        if self.session:
            self.session['evidences'].append(evidence)
            self._save_session()
    
    def close_session(self):
        """Cierra la sesión activa"""
        if self.session:
            self.session['closed_at'] = datetime.now().isoformat()
            # Mover a archivo histórico
            history_file = self.sessions_dir / f"{self.session['id']}.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.session, f, indent=2, ensure_ascii=False)
            
            # Limpiar active
            if self.active_session_file.exists():
                self.active_session_file.unlink()
            
            self.session = None
    
    def get_status(self):
        """Devuelve el estado de la sesión"""
        # Intentar cargar la sesión si no está en memoria
        if not self.session:
            self.load_session()
        
        if self.session:
            return {
                'active': True,
                'id': self.session['id'],
                'provider': self.session['provider'],
                'model': self.session['model'],
                'commands_count': len(self.session['commands_executed']),
                'evidences_count': len(self.session['evidences']),
                'created_at': self.session['created_at']
            }
        return {'active': False}
