# SKILL Security Audit

> **Version:** 3.8.0
> **Trigger:** Auditoría de seguridad web, OWASP Top 10, vulnerabilidades
> **Agente:** nxt-cybersec, nxt-dev
> **Track:** web

## Propósito
Identificar y prevenir vulnerabilidades de seguridad en el código,
siguiendo estándares OWASP y mejores prácticas de seguridad.

## Cuando se Activa
- Revisar código por vulnerabilidades
- Implementar autenticación/autorización
- Manejar datos sensibles
- Configurar APIs seguras
- Auditar dependencias

---

## 1. OWASP Top 10 (2021)

| # | Vulnerabilidad | Descripción |
|---|----------------|-------------|
| A01 | Broken Access Control | Control de acceso mal implementado |
| A02 | Cryptographic Failures | Criptografía débil o ausente |
| A03 | Injection | SQL, NoSQL, OS, LDAP injection |
| A04 | Insecure Design | Diseño sin seguridad desde inicio |
| A05 | Security Misconfiguration | Configuraciones inseguras |
| A06 | Vulnerable Components | Dependencias con CVEs |
| A07 | Auth Failures | Autenticación/sesión débil |
| A08 | Data Integrity Failures | Deserialización insegura |
| A09 | Logging Failures | Logs insuficientes |
| A10 | SSRF | Server-Side Request Forgery |

---

## 2. Patrones Peligrosos

### SQL Injection
```javascript
// PELIGROSO
const query = `SELECT * FROM users WHERE id = ${userId}`;
db.query(query);

// SEGURO
const query = 'SELECT * FROM users WHERE id = ?';
db.query(query, [userId]);
```

### Command Injection
```python
# PELIGROSO
os.system(f"ls {user_input}")
subprocess.call(user_input, shell=True)

# SEGURO
subprocess.run(["ls", user_input], shell=False)
```

### XSS (Cross-Site Scripting)
```javascript
// PELIGROSO
element.innerHTML = userInput;
dangerouslySetInnerHTML={{ __html: userInput }}

// SEGURO
element.textContent = userInput;
DOMPurify.sanitize(userInput)
```

### Path Traversal
```python
# PELIGROSO
file_path = f"/uploads/{user_filename}"
open(file_path)

# SEGURO
import os
safe_path = os.path.basename(user_filename)
file_path = os.path.join("/uploads", safe_path)
```

### Eval Usage
```javascript
// PELIGROSO
eval(userCode);
new Function(userCode)();

// SEGURO
// Usar AST parsing o sandboxing
```

### Hardcoded Secrets
```python
# PELIGROSO
API_KEY = "sk-1234567890abcdef"
password = "admin123"

# SEGURO
import os
API_KEY = os.environ.get("API_KEY")
```

---

## 3. Checklist de Seguridad

### Input Validation
- [ ] Validar tipo de datos
- [ ] Validar longitud máxima
- [ ] Sanitizar caracteres especiales
- [ ] Usar allowlists, no blocklists
- [ ] Validar en servidor (no solo cliente)

### Autenticación
- [ ] Passwords hasheados (bcrypt, argon2)
- [ ] Rate limiting en login
- [ ] MFA disponible
- [ ] Tokens con expiración
- [ ] Logout invalida sesión

### Autorización
- [ ] Principio de menor privilegio
- [ ] Verificar permisos en cada request
- [ ] No confiar en IDs del cliente
- [ ] RBAC o ABAC implementado

### Datos Sensibles
- [ ] HTTPS everywhere
- [ ] Datos cifrados en reposo
- [ ] No loggear datos sensibles
- [ ] Headers de seguridad configurados
- [ ] CORS restrictivo

### Dependencias
- [ ] Auditar con `npm audit` / `pip-audit`
- [ ] Actualizar regularmente
- [ ] Usar lockfiles
- [ ] Escanear con Snyk/Dependabot

---

## 4. Headers de Seguridad

```
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=()
```

---

## 5. Herramientas de Escaneo

| Herramienta | Propósito | Comando |
|-------------|-----------|---------|
| **npm audit** | Node.js deps | `npm audit` |
| **pip-audit** | Python deps | `pip-audit` |
| **Snyk** | Multi-lenguaje | `snyk test` |
| **Trivy** | Containers | `trivy image` |
| **OWASP ZAP** | Web apps | GUI/CLI |
| **Bandit** | Python SAST | `bandit -r src/` |
| **ESLint security** | JS SAST | `eslint --plugin security` |
| **Semgrep** | Multi-lenguaje | `semgrep --config=auto` |

### Escaneo de Secretos
```bash
# Detectar secretos en codigo (pre-commit)
pip install detect-secrets
detect-secrets scan --all-files > .secrets.baseline

# GitHub Secret Scanning (automatico en repos publicos)
# Para repos privados: habilitar en Settings > Security

# Patterns a buscar manualmente
grep -rn "eyJhbGciOi" --include="*.sh" --include="*.py" --include="*.yaml" .
grep -rn "AKIA" --include="*.py" --include="*.yaml" .  # AWS keys
grep -rn "sk-" --include="*.py" --include="*.env" .     # OpenAI keys
```

### Escaneo de Dependencias
```bash
# Python
pip-audit                          # Detecta CVEs en dependencias
safety check -r requirements.txt   # Alternativa

# Node.js
npm audit                   # Built-in
npx better-npm-audit audit  # Mas detallado

# Docker
docker scout cves image:tag  # Escanea imagen
trivy image image:tag        # Alternativa open-source
```

---

## 6. Formato de Reporte de Vulnerabilidad

```markdown
## Security Finding

### Resumen
**Severidad:** CRÍTICA / ALTA / MEDIA / BAJA
**Tipo:** [OWASP Category]
**Archivo:** path/to/file.js:123

### Descripción
[Qué encontramos y por qué es problema]

### Código Vulnerable
```[lang]
[código problemático]
```

### Remediación
```[lang]
[código corregido]
```

### Referencias
- [OWASP link]
- [CWE link]
```

---

## 7. Secrets Management

### Qué NO commitear
```gitignore
# .gitignore
.env
.env.*
*.pem
*.key
credentials.json
secrets.yaml
*.secret
```

### .gitignore Seguro (template completo)
```gitignore
# Secrets - NUNCA commitear
.env
.env.local
.env.*.local
*.pem
*.key
*.crt
credentials.json
service-account.json
secrets.json

# Tokens de sesion
.nxt/telemetry-identity.json
.nxt/.turn-state.json
```

### Dónde guardar secrets
| Ambiente | Solución |
|----------|----------|
| Local | `.env` (no commitear) |
| CI/CD | GitHub Secrets, GitLab CI Variables |
| Prod | Vault, AWS Secrets Manager, GCP Secret Manager |

---

## Relación con Otros Elementos

| Elemento | Relación |
|----------|----------|
| `/security-check` | Plugin que usa este skill automáticamente |
| `nxt-cybersec` | Agente que aplica este skill manualmente |
| `SKILL-code-quality` | Complementario (seguridad en review) |

---

## 8. Decision Tree: Como Respondo a un Incidente de Seguridad?
```
Que paso?
├── Secret expuesto en git --> Rotar INMEDIATAMENTE + git filter-branch
├── Vulnerabilidad en dependencia --> npm audit fix / pip-audit --fix
├── SQL injection detectada --> Parameterizar query + WAF rule
├── XSS reportado --> Sanitizar input + CSP header
├── Acceso no autorizado --> Revocar tokens + audit log + incident response
```

---

*SKILL Security - La seguridad no es un producto, es un proceso*
