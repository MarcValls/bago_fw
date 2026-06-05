# BAGO BOOTSTRAP — Instrucciones de Arranque

**Versión:** 4.0.0 MVP  
**Última actualización:** 2026-06-05

---

## 1. Arranque Rápido

```powershell
# Desde cualquier ubicación, BAGO detecta su raíz automáticamente
cd C:\Users\AMTEC_Terminal_1º\bago_fw
python .bago\core\cli.py start
```

---

## 2. Comandos Esenciales

| Comando | Descripción |
|---------|-------------|
| `bago start` | Arranca BAGO (detecta raíz, carga config, abre sesión) |
| `bago status` | Muestra estado: sesión activa, proveedores, nodos |
| `bago nodes` | Lista nodos y conexiones |
| `bago connect <node>` | Conecta un nodo |
| `bago disconnect <node>` | Desconecta un nodo |
| `bago exec <cmd>` | Ejecuta comando con trazabilidad |
| `bago evidence <id>` | Muestra evidencia de una acción |
| `bago session` | Muestra sesión activa |
| `bago stop` | Cierra sesión y detiene BAGO |

---

## 3. Flujo de Trabajo

1. **Arrancar:** `bago start`
2. **Verificar estado:** `bago status`
3. **Conectar herramientas:** `bago connect <nombre>`
4. **Ejecutar:** `bago exec <comando>`
5. **Ver evidencias:** `bago evidence <id>`
6. **Cerrar:** `bago stop`

---

## 4. Seguridad

- No ejecutar comandos peligrosos sin confirmación
- Toda acción genera evidencia
- No se cierra tarea sin evidencia

Ver `docs/SECURITY.md` para políticas completas.

---

## 5. Trazabilidad

Cada acción sigue el patrón:

```
AFIRMACIÓN → ACCIÓN → EVIDENCIA → CONCLUSIÓN
```

Sin evidencia, no hay completitud.

---

## 6. Estructura del Proyecto

```
bago_fw/
├── .bago/
│   ├── core/           # Runtime (cli.py, session.py)
│   ├── config/         # Configuración
│   ├── sessions/       # Sesiones persistentes
│   ├── connectors/     # Puentes CLI
│   ├── tools/          # Herramientas
│   ├── logs/           # Logs
│   ├── evidences/      # Evidencias
│   ├── nodes/          # Gestor de nodos
│   └── docs/           # Documentación
└── scripts/            # Scripts de soporte
```

---

## 7. Requisitos

- Python 3.10+
- Git (opcional)
- Proveedor de LLM configurado (Ollama local por defecto)

---

## 8. Soporte

Para issues o preguntas, revisar `docs/` o ejecutar `bago help`.
