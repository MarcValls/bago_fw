#!/usr/bin/env python3
"""
BAGO MVP Acceptance Test — Prueba final de aceptación
Flujo completo: arranque → sesión → nodos → acciones → evidencia → conclusión
"""

import subprocess
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime

CORE_DIR = Path(__file__).resolve().parent / ".bago" / "core"
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

from paths import source_base_dir

class BagoAcceptanceTest:
    """Prueba de aceptación del MVP de BAGO"""
    
    def __init__(self, bago_root: Path):
        self.bago_root = bago_root
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def log(self, message: str, status: str = "INFO"):
        """Registra un mensaje de prueba"""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] [{status}] {message}")
        
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
    
    def run_bago_command(self, cmd: str) -> tuple:
        """Ejecuta un comando de BAGO"""
        try:
            result = subprocess.run(
                f'python .bago\\core\\cli.py {cmd}',
                shell=True,
                cwd=str(self.bago_root),
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Timeout"
    
    def test_1_arranque(self) -> bool:
        """Test 1: Arranque detectable"""
        print("\n=== TEST 1: Arranque detectable ===")
        
        # Limpiar sesión anterior
        sessions_dir = self.bago_root / '.bago' / 'sessions'
        if sessions_dir.exists():
            for f in sessions_dir.glob('*'):
                f.unlink()
        
        code, stdout, stderr = self.run_bago_command("start")
        
        if code == 0 and "Nueva sesión iniciada" in stdout:
            self.log("Arranque exitoso", "PASS")
            return True
        else:
            self.log(f"Arranque fallido: {stderr}", "FAIL")
            return False
    
    def test_2_sesion_persistente(self) -> bool:
        """Test 2: Sesión persistente"""
        print("\n=== TEST 2: Sesión persistente ===")
        
        # Obtener ID de sesión activa
        code, stdout, stderr = self.run_bago_command("session")
        
        if code == 0 and "ID:" in stdout:
            self.log("Sesión recuperada", "PASS")
            return True
        else:
            self.log(f"No se pudo recuperar sesión: {stderr}", "FAIL")
            return False
    
    def test_3_status(self) -> bool:
        """Test 3: Estado de BAGO"""
        print("\n=== TEST 3: Estado de BAGO ===")
        
        code, stdout, stderr = self.run_bago_command("status")
        
        if code == 0 and "Sesión activa:" in stdout:
            self.log("Estado visible", "PASS")
            return True
        else:
            self.log(f"No se pudo obtener estado: {stderr}", "FAIL")
            return False
    
    def test_4_proveedores(self) -> bool:
        """Test 4: Proveedores detectados"""
        print("\n=== TEST 4: Proveedores detectados ===")
        
        code, stdout, stderr = self.run_bago_command("providers")
        
        if code == 0 and "ollama-local" in stdout:
            self.log("Proveedores disponibles", "PASS")
            return True
        else:
            self.log(f"No se detectaron proveedores: {stderr}", "FAIL")
            return False
    
    def test_5_nodos(self) -> bool:
        """Test 5: Nodos y conexiones"""
        print("\n=== TEST 5: Nodos y conexiones ===")
        
        registry_path = self.bago_root / '.bago' / 'nodes' / 'registry.json'
        connections_path = self.bago_root / '.bago' / 'nodes' / 'connections.json'
        registry_before = registry_path.read_text(encoding='utf-8') if registry_path.exists() else None
        connections_before = connections_path.read_text(encoding='utf-8') if connections_path.exists() else None

        try:
            # Registrar nodo
            node_name = f"test-node-{uuid.uuid4().hex[:8]}"
            code1, _, _ = self.run_bago_command(f"connect {node_name}")

            # Listar nodos
            code2, stdout, stderr = self.run_bago_command("nodes")

            if code1 == 0 and code2 == 0 and node_name in stdout:
                self.log("Nodos registrados y visibles", "PASS")
                return True
            self.log(f"Error con nodos: {stderr}", "FAIL")
            return False
        finally:
            if registry_before is None:
                registry_path.unlink(missing_ok=True)
            else:
                registry_path.write_text(registry_before, encoding='utf-8')

            if connections_before is None:
                connections_path.unlink(missing_ok=True)
            else:
                connections_path.write_text(connections_before, encoding='utf-8')
    
    def test_6_ejecucion(self) -> bool:
        """Test 6: Ejecución con trazabilidad"""
        print("\n=== TEST 6: Ejecución con trazabilidad ===")
        
        code, stdout, stderr = self.run_bago_command('exec "echo test"')
        
        if code == 0 and "AFIRMACIÓN" in stdout and "CONCLUSIÓN" in stdout:
            self.log("Ejecución con patrón de trazabilidad", "PASS")
            return True
        else:
            self.log(f"Error en ejecución: {stderr}", "FAIL")
            return False
    
    def test_7_evidencia(self) -> bool:
        """Test 7: Evidencia registrada"""
        print("\n=== TEST 7: Evidencia registrada ===")
        
        code, stdout, stderr = self.run_bago_command("evidence --recent")
        
        if code == 0 and "command_execution" in stdout:
            self.log("Evidencias disponibles", "PASS")
            return True
        else:
            self.log(f"No se encontraron evidencias: {stderr}", "FAIL")
            return False
    
    def test_8_cierre_seguro(self) -> bool:
        """Test 8: Cierre sin romper estado"""
        print("\n=== TEST 8: Cierre sin romper estado ===")
        
        code, stdout, stderr = self.run_bago_command("stop")
        
        if code == 0 and "cerrada" in stdout:
            self.log("Cierre correcto", "PASS")
            return True
        else:
            self.log(f"Error al cerrar: {stderr}", "FAIL")
            return False
    
    def test_9_recuperacion(self) -> bool:
        """Test 9: Recuperación de sesión"""
        print("\n=== TEST 9: Recuperación de sesión ===")
        
        # Reiniciar
        code1, stdout1, _ = self.run_bago_command("start")
        
        # Verificar que recupera
        code2, stdout2, _ = self.run_bago_command("status")
        
        if code1 == 0 and code2 == 0 and ("recuperada" in stdout1 or "Sesión activa" in stdout2):
            self.log("Sesión recuperada exitosamente", "PASS")
            return True
        else:
            self.log("No se recuperó la sesión", "FAIL")
            return False
    
    def run_all(self) -> bool:
        """Ejecuta todas las pruebas"""
        print("╔══════════════════════════════════════════════════════════╗")
        print("║  BAGO MVP v4.0 — ACCEPTANCE TEST                         ║")
        print("╚══════════════════════════════════════════════════════════╝")
        
        tests = [
            self.test_1_arranque,
            self.test_2_sesion_persistente,
            self.test_3_status,
            self.test_4_proveedores,
            self.test_5_nodos,
            self.test_6_ejecucion,
            self.test_7_evidencia,
            self.test_8_cierre_seguro,
            self.test_9_recuperacion
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log(f"Exception: {e}", "FAIL")
        
        print("\n╔══════════════════════════════════════════════════════════╗")
        print(f"║  RESULTADOS: {self.passed} PASSED, {self.failed} FAILED            ")
        print("╚══════════════════════════════════════════════════════════╝")
        
        return self.failed == 0

def main():
    bago_root = source_base_dir()
    test = BagoAcceptanceTest(bago_root)
    success = test.run_all()
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
