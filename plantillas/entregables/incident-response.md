# Incident Response Plan

> **Fase:** Verificar
> **Agente:** nxt-devops, nxt-cybersec
> **Version:** 3.8.0
> **Estado:** [Draft | Review | Approved]

## Clasificacion del Incidente

| Severidad | Descripcion | Tiempo de Respuesta | Ejemplo |
|-----------|-------------|--------------------|---------|
| **P0 - Critico** | Sistema caido, datos comprometidos | < 15 min | Produccion no responde |
| **P1 - Alto** | Feature critica no funciona | < 1 hora | Login roto |
| **P2 - Medio** | Funcionalidad degradada | < 4 horas | Lentitud en busquedas |
| **P3 - Bajo** | Issue menor, workaround existe | < 24 horas | Typo en UI |

## Datos del Incidente

| Campo | Valor |
|-------|-------|
| ID | INC-YYYY-NNN |
| Fecha deteccion | YYYY-MM-DD HH:MM |
| Severidad | P0/P1/P2/P3 |
| Reportado por | [nombre] |
| Componente afectado | [servicio/modulo] |
| Usuarios impactados | [numero/porcentaje] |

## Timeline del Incidente

| Hora | Evento | Responsable |
|------|--------|-------------|
| HH:MM | Incidente detectado | [quien] |
| HH:MM | Equipo notificado | [quien] |
| HH:MM | Investigacion iniciada | [quien] |
| HH:MM | Causa raiz identificada | [quien] |
| HH:MM | Fix implementado | [quien] |
| HH:MM | Verificacion completada | [quien] |
| HH:MM | Incidente resuelto | [quien] |

## Investigacion

### Sintomas Observados
- [Que se observo]
- [Errores en logs]
- [Metricas afectadas]

### Causa Raiz
[Descripcion de la causa raiz del problema]

### Impacto
- **Usuarios afectados:** [numero]
- **Duracion:** [minutos/horas]
- **Datos perdidos:** [si/no, detalles]
- **SLA impactado:** [si/no]

## Resolucion

### Acciones Tomadas
1. [Accion inmediata (mitigation)]
2. [Fix temporal (workaround)]
3. [Fix permanente (root cause)]

### Verificacion
- [ ] Servicio restaurado
- [ ] Metricas normalizadas
- [ ] Usuarios notificados
- [ ] Monitoring ajustado

## Post-Mortem

### Que Salio Bien
- [Deteccion rapida / Comunicacion efectiva / etc.]

### Que Salio Mal
- [Falta de monitoring / Documentacion insuficiente / etc.]

### Action Items

| # | Accion | Responsable | Fecha Limite | Estado |
|---|--------|-------------|-------------|--------|
| 1 | [Mejorar monitoring] | [nombre] | YYYY-MM-DD | Pendiente |
| 2 | [Agregar tests] | [nombre] | YYYY-MM-DD | Pendiente |
| 3 | [Actualizar runbook] | [nombre] | YYYY-MM-DD | Pendiente |

## Lecciones Aprendidas
[Resumen de lo aprendido para prevenir incidentes similares]
