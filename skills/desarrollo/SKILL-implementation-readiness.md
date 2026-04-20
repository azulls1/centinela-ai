# SKILL Implementation Readiness Check

> **Version:** 3.8.0
> **Fuente:** BMAD v6 Phase 3 Gate
> **Trigger:** ANTES de empezar a codear (entre Planificar y Construir)

## Proposito
Gate de calidad que verifica que todo esta listo para implementar.
Resultado: PASS / CONCERNS / FAIL

## Checklist de Readiness

### 1. Requisitos (obligatorio)
- [ ] PRD existe y esta aprobado
- [ ] User stories tienen criterios de aceptacion
- [ ] Scope esta definido (que SI y que NO)

### 2. Arquitectura (obligatorio para nivel 2+)
- [ ] Architecture doc existe
- [ ] Tech stack definido
- [ ] Modelo de datos disenado
- [ ] APIs definidas (endpoints, contracts)
- [ ] ADRs documentados para decisiones clave

### 3. Infraestructura (obligatorio para nivel 3+)
- [ ] Ambiente de desarrollo disponible
- [ ] Base de datos provisionada
- [ ] CI/CD pipeline configurado
- [ ] Variables de entorno definidas

### 4. Dependencias (siempre verificar)
- [ ] Dependencias externas identificadas
- [ ] APIs de terceros accesibles
- [ ] Permisos y accesos configurados
- [ ] No hay blockers conocidos

## Resultado

### PASS
Todos los checks obligatorios pasaron. Proceder con implementacion.

### CONCERNS
Checks menores faltan pero no bloquean. Documentar y proceder con precaucion.
Ejemplo: "Architecture doc existe pero falta diagrama de deployment"

### FAIL
Checks obligatorios faltan. NO proceder hasta resolver.
Ejemplo: "No hay PRD. No hay criterios de aceptacion."

## Decision Tree
```
Esta listo para implementar?
|-- Hay PRD/requisitos claros?
|   +-- NO -> FAIL (crear PRD primero con /nxt/pm)
|-- Nivel BMAD >= 2 y no hay architecture doc?
|   +-- SI -> FAIL (crear architecture con /nxt/architect)
|-- Hay dependencias externas sin verificar?
|   +-- SI -> CONCERNS (documentar y verificar antes de sprint)
|-- Todo listo?
|   +-- SI -> PASS (proceder con /nxt/dev)
```

## Resolución de CONCERNS

> Si el resultado es CONCERNS, alguien debe resolver antes de avanzar:

| CONCERN | Quién Resuelve | Cuándo |
|---------|---------------|--------|
| Falta diagrama de deployment | /nxt/architect | Antes de empezar sprint |
| TLS/certs no configurados | /nxt/devops | Antes de deploy (no bloquea dev) |
| API de tercero sin verificar | /nxt/integrations | Antes de implementar integración |
| Falta test plan | /nxt/qa | Paralelo al desarrollo |
| Schema no validado | /nxt/database | Antes de crear migraciones |

## Verificación de Dependencias (comandos concretos)

```bash
# Verificar dependencias externas en el código
grep -rn "fetch\|axios\|http\|request" src/ --include="*.ts" --include="*.py" | head -10

# Verificar variables de entorno requeridas
grep -rn "process.env\|os.environ\|getenv" src/ --include="*.ts" --include="*.py" | head -10

# Verificar que .env tiene todas las vars necesarias
comm -23 <(grep -ohP '(?:process\.env\.|os\.environ\.get\()["'"'"']\K[^"'"'"']+' src/**/*.{ts,py} 2>/dev/null | sort -u) <(grep -oP '^[A-Z_]+' .env 2>/dev/null | sort -u)
```

## Cuando Ejecutar
- SIEMPRE antes de nivel 2+ tasks
- Opcional para nivel 0-1 (trivial/simple)
- Obligatorio despues de /nxt/architect y antes de /nxt/dev
