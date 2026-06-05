# Políticas de Seguridad de BAGO

**Versión:** 4.0.0 MVP  
**Principio:** Seguridad antes que autonomía

---

## 1. No Romper BAGO

- No modificar archivos críticos sin backup automático
- No borrar directorios esenciales (`.bago/core`, `.bago/config`, `.bago/sessions`)
- No sobrescribir configuración sin registrar evidencia

**Verificación:** El sistema debe mantenerse funcional después de cualquier operación.

---

## 2. No Romper Comunicación con el Usuario

- No bloquear stdin/stdout/stderr
- No silenciar errores críticos
- Siempre informar cambios de estado relevantes
- Mantener el canal de comunicación abierto

**Verificación:** El usuario siempre puede interrumpir y recibir feedback.

---

## 3. No Borrar Sin Evidencia

- Cada borrado debe registrar:
  - **Qué** se borró
  - **Cuándo** se borró
  - **Por qué** se borró
- La evidencia debe ser consultable vía `bago evidence <id>`
- Backup automático antes de borrar archivos críticos

**Verificación:** `bago evidence <id>` siempre devuelve información de borrados.

---

## 4. Clasificación de Comandos

| Nivel | Ejemplos | Requiere Confirmación | Acción |
|-------|----------|----------------------|--------|
| **Seguro** | `dir`, `cat`, `echo`, `ls`, `pwd` | No | Ejecutar y registrar |
| **Moderado** | `mkdir`, `cp`, `mv`, `touch` | No | Ejecutar, registrar y generar evidencia |
| **Peligroso** | `rm`, `del`, `rmdir`, `erase` | Sí (explícita) | Confirmar, luego ejecutar con evidencia |
| **Crítico** | `diskpart`, `format`, `rd /s`, `rm -rf /` | Bloqueado | Rechazar con explicación |

**Verificación:** Comandos críticos nunca se ejecutan. Peligrosos requieren confirmación explícita.

---

## 5. No Decir "Hecho" Sin Prueba

- Cada afirmación de completitud requiere evidencia adjunta
- Evidencia válida:
  - Archivo creado/modificado (ruta + hash)
  - Output de comando (captura)
  - Screenshot (para cambios visuales)
  - Log de ejecución (timestamp + resultado)
- Sin evidencia = tarea marcada como "incompleta"

**Verificación:** `bago status` nunca muestra tareas completadas sin evidencia asociada.

---

## 6. Auto Allow Tools — Política Dura

El modo `auto_allow_tools` solo puede activarse si:

1. ✅ No romper el propio BAGO (verificado por tests)
2. ✅ No romper el canal de comunicación con el usuario (verificado)
3. ✅ No borrar ni sobrescribir sin evidencia (verificado)
4. ✅ No ejecutar comandos peligrosos sin clasificación (verificado)
5. ✅ No decir "hecho" si no hay prueba (verificado)

**Verificación:** Las 5 verificaciones deben pasar antes de activar auto_allow_tools.

---

## 7. Aislamiento de Proveedores

Cada proveedor (Copilot, Codex, Ollama, etc.) debe:

- Tener su propio puente CLI independiente
- Tener sus permisos específicos
- Tener su canal de entrada/salida aislado
- No interferir con otros proveedores

**Verificación:** Desactivar un proveedor no afecta a los demás.

---

## 8. Trazabilidad Obligatoria

Toda acción debe seguir el patrón:

```
1. AFIRMACIÓN: "Voy a ejecutar X"
2. ACCIÓN: Comando o acción ejecutada
3. EVIDENCIA: Archivo, log, hash, output
4. CONCLUSIÓN: "X se completó con resultado Y"
```

**Verificación:** Cada entrada en el log de sesión tiene los 4 componentes.

---

## 9. Auditoría

- Logs se guardan en `.bago/logs/runtime.log`
- Evidencias se guardan en `.bago/evidences/`
- Sesiones se guardan en `.bago/sessions/`
- Todo es consultable y exportable

---

## 10. Verificación de Cumplimiento

Para verificar que las políticas se cumplen:

```powershell
# Ejecutar health check de seguridad
python .bago\core\security.py --verify

# Ver evidencias recientes
bago evidence --recent

# Ver logs de auditoría
cat .bago\logs\runtime.log
```

---

**Firma de Aceptación:**

Las políticas anteriores son obligatorias para el MVP v4.0.
