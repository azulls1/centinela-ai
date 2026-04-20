# SKILL Code Quality

> **Version:** 3.8.0
> **Trigger:** Code quality, refactoring, code smells, linting, formatting
> **Agente:** nxt-dev, nxt-qa, nxt-mobile
> **Track:** shared (web + mobile)

## Proposito
Garantizar la calidad del codigo mediante revision exhaustiva y refactorizacion
sistematica, manteniendo seguridad, legibilidad y mantenibilidad.

> **Unificado:** Combina Code Review + Refactoring en un solo skill

## Cuando se Activa
- Revisar Pull Request
- Analizar codigo existente
- Buscar vulnerabilidades
- Mejorar legibilidad del codigo
- Eliminar code smells
- Reducir deuda tecnica
- Preparar codigo para nuevas features

---

# PARTE 1: CODE REVIEW

## 1.1 Checklist de Code Review

### Funcionalidad
- [ ] El codigo hace lo que se supone que debe hacer
- [ ] Los edge cases estan manejados
- [ ] Los errores se manejan apropiadamente
- [ ] La logica es correcta

### Legibilidad
- [ ] Nombres de variables/funciones descriptivos
- [ ] Funciones pequenas y enfocadas
- [ ] Comentarios donde son necesarios
- [ ] Codigo autoexplicativo

### Seguridad
- [ ] No hay credenciales hardcodeadas
- [ ] Input validation presente
- [ ] Sin vulnerabilidades OWASP Top 10
- [ ] Datos sensibles protegidos

### Performance
- [ ] Sin queries N+1
- [ ] Algoritmos eficientes
- [ ] Memoria bien gestionada
- [ ] Sin loops innecesarios

### Testing
- [ ] Tests unitarios presentes
- [ ] Cobertura adecuada
- [ ] Tests son legibles
- [ ] Edge cases testeados

### Mantenibilidad
- [ ] Principios SOLID seguidos
- [ ] DRY (no repeticion)
- [ ] Acoplamiento bajo
- [ ] Codigo modular

## 1.2 Formato de Review

```markdown
## Code Review: PR #XXX

### Resumen
[Descripcion breve de los cambios]

### Veredicto
**APROBADO** / **CAMBIOS REQUERIDOS** / **BLOQUEADO**

### Hallazgos

#### Criticos (deben arreglarse)
1. **[Archivo:Linea]** - [Descripcion]
   ```[codigo problematico]```
   **Sugerencia:** [Como arreglarlo]

#### Importantes (deberian arreglarse)
1. **[Archivo:Linea]** - [Descripcion]

#### Menores (nice to have)
1. **[Archivo:Linea]** - [Descripcion]

#### Positivos
- [Que se hizo bien]

### Checklist
- [x] Funcionalidad correcta
- [x] Tests incluidos
- [ ] Documentacion actualizada
- [x] Sin vulnerabilidades de seguridad

### Notas Adicionales
[Comentarios generales, sugerencias de mejora]
```

## 1.3 Categorias de Hallazgos

| Categoria | Icono | Accion |
|-----------|-------|--------|
| **Critico** | BLOCKER | Bloquea merge |
| **Importante** | WARNING | Debe arreglarse |
| **Menor** | INFO | Sugerencia |
| **Positivo** | GOOD | Reconocimiento |
| **Pregunta** | QUESTION | Clarificacion |

## 1.4 Patrones Problematicos a Buscar

### Seguridad
```javascript
// MAL: SQL Injection
const query = `SELECT * FROM users WHERE id = ${userId}`;

// BIEN: Parametrizado
const query = 'SELECT * FROM users WHERE id = ?';
db.query(query, [userId]);
```

```javascript
// MAL: XSS
element.innerHTML = userInput;

// BIEN: Escapado
element.textContent = userInput;
```

### Performance
```javascript
// MAL: N+1 query
for (const user of users) {
  const posts = await db.query('SELECT * FROM posts WHERE user_id = ?', [user.id]);
}

// BIEN: Single query con JOIN
const usersWithPosts = await db.query(`
  SELECT u.*, p.* FROM users u
  LEFT JOIN posts p ON u.id = p.user_id
`);
```

## 1.5 Preguntas de Review

Al revisar, preguntate:

1. **Podria yo mantener este codigo en 6 meses?**
2. **Que pasa si esta funcion recibe null/undefined?**
3. **Hay algun caso donde esto podria fallar?**
4. **Esto escala si tenemos 10x mas usuarios?**
5. **Un atacante podria explotar esto?**

## 1.6 Feedback Constructivo

### Como DAR feedback
- Se especifico, no vago
- Explica el "por que"
- Ofrece alternativas
- Reconoce lo bueno
- Usa tono colaborativo

### Ejemplos
```
// BIEN
"Este loop podria ser un .map() para mayor claridad.
Ademas, si la lista es grande, considera usar .filter()
primero para reducir iteraciones."

// MAL
"Este codigo es ineficiente."
```

---

# PARTE 2: REFACTORING

## 2.1 Principios de Refactoring

### Regla de Oro
> "Refactoring es cambiar la estructura del codigo sin cambiar su comportamiento"

### Pre-requisitos
- Tests existentes que pasen
- Commits pequenos y frecuentes
- Cambios reversibles

## 2.2 Code Smells Comunes

| Smell | Descripcion | Refactoring |
|-------|-------------|-------------|
| Long Method | Metodo > 20 lineas | Extract Method |
| Large Class | Clase con muchas responsabilidades | Extract Class |
| Duplicate Code | Codigo repetido | Extract Method/Class |
| Long Parameter List | > 3 parametros | Parameter Object |
| Feature Envy | Metodo usa mas datos de otra clase | Move Method |
| Data Clumps | Grupos de datos que viajan juntos | Extract Class |
| Primitive Obsession | Uso excesivo de primitivos | Value Object |
| Switch Statements | Switch largos | Strategy/Polymorphism |
| Speculative Generality | Codigo "por si acaso" | Remove Dead Code |
| Dead Code | Codigo no usado | Delete |

## 2.3 Catalogo de Refactorings

### Extract Method
```javascript
// ANTES
function printOwing(invoice) {
  printBanner();
  // Print details
  console.log(`name: ${invoice.customer}`);
  console.log(`amount: ${invoice.amount}`);
  console.log(`due: ${invoice.dueDate}`);
}

// DESPUES
function printOwing(invoice) {
  printBanner();
  printDetails(invoice);
}

function printDetails(invoice) {
  console.log(`name: ${invoice.customer}`);
  console.log(`amount: ${invoice.amount}`);
  console.log(`due: ${invoice.dueDate}`);
}
```

### Guard Clauses
```javascript
// ANTES
function getPayAmount() {
  let result;
  if (isDead) {
    result = deadAmount();
  } else {
    if (isSeparated) {
      result = separatedAmount();
    } else {
      if (isRetired) {
        result = retiredAmount();
      } else {
        result = normalPayAmount();
      }
    }
  }
  return result;
}

// DESPUES
function getPayAmount() {
  if (isDead) return deadAmount();
  if (isSeparated) return separatedAmount();
  if (isRetired) return retiredAmount();
  return normalPayAmount();
}
```

### Replace Conditional with Polymorphism
```javascript
// ANTES
function getSpeed(vehicle) {
  switch (vehicle.type) {
    case 'car': return vehicle.baseSpeed * 1.0;
    case 'motorcycle': return vehicle.baseSpeed * 1.2;
    case 'bicycle': return vehicle.baseSpeed * 0.5;
  }
}

// DESPUES
class Vehicle {
  getSpeed() { return this.baseSpeed; }
}
class Car extends Vehicle {
  getSpeed() { return this.baseSpeed * 1.0; }
}
class Motorcycle extends Vehicle {
  getSpeed() { return this.baseSpeed * 1.2; }
}
```

### Replace Magic Numbers
```javascript
// ANTES
if (user.age >= 18) { ... }
const tax = price * 0.21;

// DESPUES
const LEGAL_AGE = 18;
const TAX_RATE = 0.21;

if (user.age >= LEGAL_AGE) { ... }
const tax = price * TAX_RATE;
```

## 2.4 Metricas de Calidad

| Metrica | Bueno | Aceptable | Malo |
|---------|-------|-----------|------|
| Cyclomatic Complexity | 1-5 | 6-10 | > 10 |
| Lines per Function | < 20 | 20-50 | > 50 |
| Parameters | 0-3 | 4-5 | > 5 |
| Nesting Depth | 1-2 | 3 | > 3 |
| Class Lines | < 200 | 200-500 | > 500 |

---

# PARTE 3: HERRAMIENTAS Y PROCESO

## 3.1 Herramientas Automaticas

| Herramienta | Proposito | Comando |
|-------------|-----------|---------|
| ESLint/Prettier | Estilo y formato | `npx eslint src/` |
| SonarQube | Calidad de codigo | `sonar-scanner` |
| Snyk | Vulnerabilidades | `snyk test` |
| CodeClimate | Mantenibilidad | `codeclimate analyze` |
| Codecov | Cobertura de tests | `codecov` |
| Plato | Metricas complejidad | `npx plato -r -d report src/` |

## 3.2 Proceso de Code Review

```
1. Entender el contexto (story, PR description)
2. Ejecutar el codigo localmente si es posible
3. Revisar diff linea por linea
4. Anotar hallazgos por categoria
5. Revisar tests incluidos
6. Verificar documentacion
7. Escribir resumen y veredicto
8. Discutir hallazgos si es necesario
```

## 3.3 Workflow de Refactoring

```
1. Verificar tests existentes
   -> Si no hay tests -> escribir tests primero

2. Identificar el smell
   -> Usar checklist de code smells

3. Seleccionar refactoring apropiado
   -> Consultar catalogo

4. Aplicar refactoring en pasos pequenos
   -> Commit despues de cada paso

5. Ejecutar tests
   -> Si fallan -> revertir

6. Repetir hasta satisfaccion
```

## 3.4 Checklists

### Pre-Refactoring
- [ ] Tests existentes y pasando
- [ ] Branch de feature creado
- [ ] Scope del refactoring definido
- [ ] Comportamiento actual documentado
- [ ] Metricas baseline capturadas

### Post-Refactoring
- [ ] Todos los tests pasan
- [ ] No hay regresiones
- [ ] Codigo mas legible
- [ ] Metricas mejoradas
- [ ] PR con descripcion clara

---

## Comandos de Ejemplo

```
"Revisa este PR/codigo"
"Busca vulnerabilidades de seguridad"
"Analiza performance del codigo"
"Refactoriza esta funcion para reducir complejidad"
"Extrae metodos de esta clase grande"
"Aplica guard clauses a estos condicionales"
"Elimina codigo duplicado entre estos archivos"
```

---

# PARTE 4: AUTOMATIZACIÓN CI/CD

## 4.1 GitHub Actions - Auto Lint

```yaml
# .github/workflows/lint.yml
name: Code Quality
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: {node-version: 20}
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
```

## 4.2 Pre-commit Hook (.husky/pre-commit)

```bash
#!/bin/sh
npx lint-staged
```

## 4.3 lint-staged Config (package.json)

```json
{
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{css,scss}": ["prettier --write"],
    "*.md": ["prettier --write"]
  }
}
```

## 4.4 Decision Tree: Que Herramienta de Calidad?

```
Que necesitas verificar?
├── Estilo de codigo → Prettier (formateo) + ESLint (reglas)
├── Types → TypeScript strict mode
├── Complejidad ciclomatica → ESLint complexity rule (max 10)
├── Codigo muerto → ts-prune o knip
├── Dependencias no usadas → depcheck o knip
├── Python → ruff (lint + format en uno)
```

---

## Referencias

- Martin Fowler - "Refactoring: Improving the Design of Existing Code"
- https://refactoring.guru/refactoring/catalog
