# SKILL Testing

> **Version:** 3.8.0
> **Trigger:** Testing automatizado (unit, integration, E2E)
> **Agente:** nxt-qa, nxt-dev, nxt-mobile
> **Track:** shared (web + mobile)

## Proposito
Generar tests automatizados de alta calidad para garantizar la estabilidad
y confiabilidad del codigo.

## Cuando se Activa
- Crear tests unitarios
- Crear tests de integracion
- Crear tests e2e
- Generar test plan
- Analizar cobertura

## Instrucciones

### 1. Filosofia de Testing NXT

#### Piramide de Tests
```
         /\
        /  \
       / E2E\        <- Pocos, criticos
      /______\
     /        \
    /Integration\    <- Moderados, flujos
   /______________\
  /                \
 /    Unit Tests    \  <- Muchos, rapidos
/_____________________\
```

#### Cobertura Objetivo
- **Unit**: 80%+ de cobertura
- **Integration**: Flujos criticos
- **E2E**: Happy paths principales

### 2. Estructura de Tests

#### Organizacion de Archivos
```
tests/
├── unit/
│   ├── components/
│   │   └── Button.test.ts
│   ├── services/
│   │   └── AuthService.test.ts
│   └── utils/
│       └── helpers.test.ts
├── integration/
│   ├── api/
│   │   └── auth.integration.test.ts
│   └── database/
│       └── users.integration.test.ts
├── e2e/
│   ├── auth.e2e.test.ts
│   └── checkout.e2e.test.ts
├── fixtures/
│   └── users.json
├── mocks/
│   └── api.mock.ts
└── setup.ts
```

### 3. Patron AAA (Arrange-Act-Assert)

```typescript
describe('AuthService', () => {
  describe('login', () => {
    it('should return user when credentials are valid', async () => {
      // Arrange
      const credentials = {
        email: 'test@example.com',
        password: 'validPassword123'
      };
      const mockUser = { id: 1, email: credentials.email };
      mockRepository.findByEmail.mockResolvedValue(mockUser);

      // Act
      const result = await authService.login(credentials);

      // Assert
      expect(result).toEqual(mockUser);
      expect(mockRepository.findByEmail).toHaveBeenCalledWith(credentials.email);
    });

    it('should throw error when credentials are invalid', async () => {
      // Arrange
      const credentials = {
        email: 'test@example.com',
        password: 'wrongPassword'
      };
      mockRepository.findByEmail.mockResolvedValue(null);

      // Act & Assert
      await expect(authService.login(credentials))
        .rejects.toThrow('Invalid credentials');
    });
  });
});
```

### 4. Templates de Tests

#### Unit Test Template
```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { ComponentOrService } from '@/path/to/component';

describe('ComponentOrService', () => {
  let instance: ComponentOrService;

  beforeEach(() => {
    // Setup
    instance = new ComponentOrService();
  });

  describe('methodName', () => {
    it('should [expected behavior] when [condition]', () => {
      // Arrange
      const input = 'test';

      // Act
      const result = instance.methodName(input);

      // Assert
      expect(result).toBe('expected');
    });

    it('should throw when [error condition]', () => {
      // Arrange & Act & Assert
      expect(() => instance.methodName(null))
        .toThrow('Expected error message');
    });
  });
});
```

#### Integration Test Template
```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { createTestApp, TestDatabase } from '@/test/setup';

describe('Auth API Integration', () => {
  let app: TestApp;
  let db: TestDatabase;

  beforeAll(async () => {
    db = await TestDatabase.create();
    app = await createTestApp(db);
  });

  afterAll(async () => {
    await db.cleanup();
    await app.close();
  });

  describe('POST /api/auth/login', () => {
    it('should return 200 and token for valid credentials', async () => {
      // Arrange
      await db.seed('users', [{ email: 'test@test.com', password: 'hashed' }]);

      // Act
      const response = await app.request()
        .post('/api/auth/login')
        .send({ email: 'test@test.com', password: 'password' });

      // Assert
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('token');
    });

    it('should return 401 for invalid credentials', async () => {
      const response = await app.request()
        .post('/api/auth/login')
        .send({ email: 'wrong@test.com', password: 'wrong' });

      expect(response.status).toBe(401);
    });
  });
});
```

#### E2E Test Template (Playwright)
```typescript
import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('user can login successfully', async ({ page }) => {
    // Navigate
    await page.goto('/login');

    // Fill form
    await page.fill('[data-testid="email-input"]', 'user@example.com');
    await page.fill('[data-testid="password-input"]', 'password123');

    // Submit
    await page.click('[data-testid="login-button"]');

    // Assert redirect
    await expect(page).toHaveURL('/dashboard');

    // Assert user info visible
    await expect(page.locator('[data-testid="user-name"]'))
      .toContainText('John Doe');
  });

  test('shows error for invalid credentials', async ({ page }) => {
    await page.goto('/login');
    await page.fill('[data-testid="email-input"]', 'wrong@example.com');
    await page.fill('[data-testid="password-input"]', 'wrongpass');
    await page.click('[data-testid="login-button"]');

    await expect(page.locator('[data-testid="error-message"]'))
      .toContainText('Invalid credentials');
  });
});
```

### 5. Herramientas por Stack

| Stack | Unit | Integration | E2E |
|-------|------|-------------|-----|
| React | Jest/Vitest + RTL | MSW | Playwright |
| Vue | Vitest + VTU | MSW | Cypress |
| Node | Jest/Vitest | Supertest | - |
| Python | Pytest | Pytest | Playwright |
| Go | testing pkg | - | - |

### 6. Mocking Best Practices

#### Cuando Mockear
- Dependencias externas (APIs, DBs)
- Tiempo (dates, timers)
- Aleatoridad
- Filesystem

#### Cuando NO Mockear
- La unidad bajo test
- Utilidades internas simples
- Logica de negocio pura

### 7. Proceso de Generacion

1. Analizar componente/servicio a testear
2. Identificar casos (happy path, edge cases, errors)
3. Crear archivo de test con estructura AAA
4. Implementar mocks necesarios
5. Ejecutar y verificar cobertura
6. Documentar casos especiales

## Comandos de Ejemplo

```
"Genera tests unitarios para AuthService"
"Crea test de integracion para la API de usuarios"
"Genera test e2e para el flujo de checkout"
"Analiza cobertura de tests"
"Crea mocks para el servicio de pagos"
```

## Configuraciones Reales

### Vitest Config (vitest.config.ts)
```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      thresholds: { lines: 80, branches: 75, functions: 80 },
    },
    include: ['tests/**/*.test.{ts,tsx}'],
  },
});
```

### MSW Setup (tests/setup.ts)
```typescript
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/users', () => {
    return HttpResponse.json([
      { id: '1', name: 'Test User', email: 'test@example.com' },
    ]);
  }),
  http.post('/api/users', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ id: '2', ...body }, { status: 201 });
  }),
];

export const server = setupServer(...handlers);
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### Pytest Config (pyproject.toml)
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --tb=short --cov=src --cov-report=term-missing"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks integration tests",
]
```

## Configuracion de Cobertura (Legacy)

```json
// vitest.config.ts (formato JSON alternativo)
{
  "test": {
    "coverage": {
      "provider": "v8",
      "reporter": ["text", "html", "lcov"],
      "exclude": ["node_modules", "tests"],
      "thresholds": {
        "statements": 80,
        "branches": 80,
        "functions": 80,
        "lines": 80
      }
    }
  }
}
```
