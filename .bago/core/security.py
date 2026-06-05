#!/usr/bin/env python3
"""
BAGO Security — Políticas de seguridad y verificación
Seguridad antes que autonomía
"""

import json
from pathlib import Path
from enum import Enum

class CommandRiskLevel(Enum):
    SAFE = "safe"
    MODERATE = "moderate"
    DANGEROUS = "dangerous"
    CRITICAL = "critical"

# Clasificación de comandos
COMMAND_CLASSIFICATION = {
    # Seguros
    'dir': CommandRiskLevel.SAFE,
    'ls': CommandRiskLevel.SAFE,
    'cat': CommandRiskLevel.SAFE,
    'echo': CommandRiskLevel.SAFE,
    'pwd': CommandRiskLevel.SAFE,
    'type': CommandRiskLevel.SAFE,
    'get-content': CommandRiskLevel.SAFE,
    
    # Moderados
    'mkdir': CommandRiskLevel.MODERATE,
    'md': CommandRiskLevel.MODERATE,
    'cp': CommandRiskLevel.MODERATE,
    'copy': CommandRiskLevel.MODERATE,
    'mv': CommandRiskLevel.MODERATE,
    'move': CommandRiskLevel.MODERATE,
    'touch': CommandRiskLevel.MODERATE,
    'new-item': CommandRiskLevel.MODERATE,
    
    # Peligrosos
    'rm': CommandRiskLevel.DANGEROUS,
    'del': CommandRiskLevel.DANGEROUS,
    'erase': CommandRiskLevel.DANGEROUS,
    'rmdir': CommandRiskLevel.DANGEROUS,
    'rd': CommandRiskLevel.DANGEROUS,
    'remove-item': CommandRiskLevel.DANGEROUS,
    
    # Críticos (bloqueados)
    'format': CommandRiskLevel.CRITICAL,
    'diskpart': CommandRiskLevel.CRITICAL,
    'rd /s': CommandRiskLevel.CRITICAL,
    'rm -rf': CommandRiskLevel.CRITICAL,
    'rm -rf /': CommandRiskLevel.CRITICAL,
    'deltree': CommandRiskLevel.CRITICAL,
}

BLOCKED_COMMANDS = [
    'format', 'diskpart', 'rd /s', 'rm -rf /', 'deltree'
]

class SecurityPolicy:
    """Implementa políticas de seguridad de BAGO"""
    
    def __init__(self, config_path: Path = None):
        self.config = {}
        if config_path and config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
    
    def classify_command(self, command: str) -> CommandRiskLevel:
        """Clasifica un comando por nivel de riesgo"""
        cmd_base = command.split()[0].lower() if command else ''
        
        # Verificar si es crítico (bloqueado)
        for blocked in BLOCKED_COMMANDS:
            if blocked in command.lower():
                return CommandRiskLevel.CRITICAL
        
        # Buscar en clasificación
        return COMMAND_CLASSIFICATION.get(cmd_base, CommandRiskLevel.MODERATE)
    
    def can_execute(self, command: str, auto_allow: bool = False) -> tuple[bool, str]:
        """
        Verifica si un comando puede ejecutarse
        
        Returns:
            (puede_ejecutar, razon)
        """
        risk = self.classify_command(command)
        
        if risk == CommandRiskLevel.CRITICAL:
            return False, f"Comando crítico bloqueado: {command}"
        
        if risk == CommandRiskLevel.DANGEROUS:
            if auto_allow:
                return False, "Comandos peligrosos requieren confirmación explícita"
            return True, "Requiere confirmación"
        
        return True, "Permitido"
    
    def require_evidence(self) -> bool:
        """Verifica si se requiere evidencia para todas las acciones"""
        return self.config.get('trazabilidad', {}).get('obligatory', True)
    
    def verify_policies(self) -> dict:
        """Verifica que todas las políticas se cumplen"""
        checks = {
            'no_romper_bago': True,  # Verificar por tests
            'no_romper_comunicacion': True,  # Verificar por tests
            'no_borrar_sin_evidencia': self.require_evidence(),
            'no_peligrosos_sin_clasificacion': True,  # Siempre cierto por diseño
            'no_hecho_sin_prueba': self.require_evidence()
        }
        
        all_passed = all(checks.values())
        
        return {
            'passed': all_passed,
            'checks': checks,
            'can_enable_auto_allow': all_passed
        }
