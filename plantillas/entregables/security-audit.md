# Security Audit Report

> **Fase:** Verificar
> **Agente:** nxt-cybersec
> **Version:** 3.8.0
> **Estado:** [Draft | Review | Approved]

---

## Informacion General

| Campo | Valor |
|-------|-------|
| Proyecto | [nombre] |
| Fecha | YYYY-MM-DD |
| Auditor | [nombre/agente] |
| Scope | [modulos/endpoints auditados] |
| Nivel OWASP | [Top 10 / ASVS Level 1-3] |

## Hallazgos

| # | Severidad | Categoria OWASP | Descripcion | Ubicacion | Estado |
|---|-----------|-----------------|-------------|-----------|--------|
| 1 | CRITICO | A01 - Broken Access Control | [descripcion] | [archivo:linea] | Abierto |
| 2 | ALTO | A03 - Injection | [descripcion] | [archivo:linea] | Corregido |
| 3 | MEDIO | A07 - Auth Failures | [descripcion] | [archivo:linea] | Abierto |

## Resumen de Riesgos

| Severidad | Encontrados | Corregidos | Pendientes |
|-----------|-------------|------------|------------|
| Critico | 0 | 0 | 0 |
| Alto | 0 | 0 | 0 |
| Medio | 0 | 0 | 0 |
| Bajo | 0 | 0 | 0 |
| **Total** | 0 | 0 | 0 |

## Dependencias Vulnerables

| Paquete | Version Actual | CVE | Severidad | Version Fix |
|---------|---------------|-----|-----------|-------------|
| [paquete] | [x.y.z] | CVE-YYYY-NNNNN | ALTO | [x.y.z] |

## Configuracion de Seguridad

| Check | Estado | Notas |
|-------|--------|-------|
| HTTPS enforced | PASS/FAIL | [nota] |
| CORS configurado | PASS/FAIL | [nota] |
| Rate limiting activo | PASS/FAIL | [nota] |
| Headers de seguridad | PASS/FAIL | [nota] |
| Secrets en env vars | PASS/FAIL | [nota] |
| Logs sin datos sensibles | PASS/FAIL | [nota] |

## Recomendaciones

1. **Inmediato (P0):** [Accion critica requerida]
2. **Corto plazo (P1):** [Mejora en 1-2 sprints]
3. **Largo plazo (P2):** [Mejora arquitectonica]

## Herramientas y Comandos de Escaneo

```bash
# Secretos expuestos
grep -rn "eyJhbGciOi\|AKIA\|sk-\|password\s*=" --include="*.ts" --include="*.py" --include="*.yaml" src/ || echo "No secrets found"

# Dependencias vulnerables (Node.js)
npm audit --audit-level=high 2>/dev/null || echo "npm not available"

# Dependencias vulnerables (Python)
pip-audit 2>/dev/null || safety check -r requirements.txt 2>/dev/null || echo "pip-audit not available"

# Headers de seguridad (si hay URL)
curl -sI https://[TU-URL] | grep -iE "x-frame|x-content|strict-transport|content-security"

# SQL injection patterns
grep -rn "f\"\|f'\|%s\|\.format(" --include="*.py" src/ | grep -i "select\|insert\|update\|delete" || echo "No SQL concat found"
```

- [ ] Revision manual de codigo
- [ ] SAST (semgrep/SonarQube)
- [ ] DAST (OWASP ZAP)
- [ ] Dependency audit (npm audit/pip-audit)
- [ ] Secret scanning (detect-secrets)

## Aprobaciones

| Rol | Nombre | Fecha | Firma |
|-----|--------|-------|-------|
| Security Lead | [Nombre] | [Fecha] | [ ] |
| Tech Lead | [Nombre] | [Fecha] | [ ] |

---

*Generado con NXT AI Development v3.8.0*
