# BAGO Framework v4.0.0 MVP

**Centro de mando local con sesión persistente**

---

## Descripción

BAGO es un centro de mando local, en terminal, con:

- ✅ Sesión persistente
- ✅ Proveedores intercambiables
- ✅ Herramientas conectables
- ✅ Control por nodos
- ✅ Trazabilidad obligatoria
- ✅ Seguridad antes que autonomía

---

## Instalación

1. Clonar o copiar a `C:\Users\<usuario>\bago_fw`
2. Verificar Python 3.10+
3. Ejecutar `.\bootstrap.ps1`

---

## Uso

```powershell
# Arrancar
.\bootstrap.ps1 start

# Ver estado
.\bootstrap.ps1 status

# Ejecutar comando con trazabilidad
.\bootstrap.ps1 exec "dir"

# Ver evidencias
.\bootstrap.ps1 evidence --recent

# Cerrar
.\bootstrap.ps1 stop
```

---

## Estructura

```
bago_fw/
├── .bago/
│   ├── core/           # Runtime esencial
│   ├── config/         # Configuración
│   ├── sessions/       # Sesiones
│   ├── connectors/     # Puentes CLI
│   ├── tools/          # Herramientas
│   ├── logs/           # Logs
│   ├── evidences/      # Evidencias
│   ├── nodes/          # Nodos
│   └── docs/           # Documentación
└── bootstrap.ps1       # Arranque
```

---

## Documentación

- `docs/BOOTSTRAP.md` — Instrucciones de arranque
- `docs/SECURITY.md` — Políticas de seguridad
- `docs/MVP.md` — Definición del MVP

---

## Requisitos

- Python 3.10+
- Git (opcional)
- Proveedor LLM (Ollama local por defecto)

---

## Licencia

MIT

---

**Versión:** 4.0.0 MVP  
**Fecha:** 2026-06-05
