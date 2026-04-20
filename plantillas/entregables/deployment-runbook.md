# Deployment Runbook

> **Fase:** Construir/Verificar
> **Agente:** nxt-devops
> **Version:** 3.8.0
> **Estado:** [Draft | Review | Approved]

## Informacion del Release

| Campo | Valor |
|-------|-------|
| Version | vX.Y.Z |
| Fecha planificada | YYYY-MM-DD |
| Responsable | [nombre] |
| Ambiente destino | [staging/production] |
| Rollback plan | [si/no] |

## Pre-requisitos

- [ ] Todos los tests pasan en CI
- [ ] Code review aprobado
- [ ] QA sign-off obtenido
- [ ] Changelog actualizado
- [ ] Variables de entorno configuradas
- [ ] Base de datos migrada (si aplica)
- [ ] Backups verificados

## Pasos de Deployment

### 1. Preparacion
```bash
# Verificar branch
git checkout main && git pull

# Verificar version
cat .nxt/version.txt

# Verificar tests
python -m pytest tests/ -v
```

### 2. Build
```bash
# Build de produccion
[comando de build]

# Verificar artefactos
[verificar que el build fue exitoso]
```

### 3. Deploy
```bash
# Deploy a staging primero
[comando deploy staging]

# Smoke tests en staging
[comandos de verificacion]

# Deploy a produccion
[comando deploy production]
```

### 4. Verificacion Post-Deploy
- [ ] Aplicacion responde en URL de produccion
- [ ] Health check endpoint OK
- [ ] Logs sin errores criticos
- [ ] Metricas dentro de rangos normales
- [ ] Funcionalidad principal verificada

## Rollback

### Trigger de Rollback
- Error rate > 5% en los primeros 15 minutos
- Health check falla 3 veces consecutivas
- Funcionalidad critica no disponible

### Pasos de Rollback
```bash
# Revertir a version anterior
[comando rollback]

# Verificar rollback
[comandos de verificacion]

# Notificar al equipo
[canal de comunicacion]
```

## Contactos de Emergencia

| Rol | Nombre | Contacto |
|-----|--------|----------|
| DevOps Lead | [nombre] | [slack/email] |
| Backend Lead | [nombre] | [slack/email] |
| QA Lead | [nombre] | [slack/email] |

## Historial de Deployments

| Fecha | Version | Resultado | Notas |
|-------|---------|-----------|-------|
| YYYY-MM-DD | vX.Y.Z | OK/Rollback | [detalles] |
