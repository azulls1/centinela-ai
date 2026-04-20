# SKILL: API Documentation

> **Version:** 3.8.0
> **Trigger:** Generacion de documentacion de API
> **Agente:** nxt-docs
> **Track:** shared

## Proposito
Generar documentacion de API completa y profesional usando OpenAPI/Swagger,
incluyendo ejemplos, esquemas y colecciones de testing.

## Cuando se Activa
- Documentar endpoints REST
- Generar OpenAPI spec
- Crear colecciones Postman
- Documentar webhooks
- Generar SDK docs

## Instrucciones

### 1. OpenAPI 3.0 Specification

#### Estructura Base
```yaml
openapi: 3.0.3
info:
  title: API Name
  description: |
    # Introduccion
    Descripcion detallada de la API.

    ## Autenticacion
    Esta API usa Bearer tokens para autenticacion.

    ## Rate Limiting
    - 100 requests/minuto para usuarios free
    - 1000 requests/minuto para usuarios premium

  version: 1.0.0
  contact:
    name: API Support
    email: api@company.com
    url: https://docs.company.com
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: https://api.company.com/v1
    description: Production
  - url: https://staging-api.company.com/v1
    description: Staging
  - url: http://localhost:3000/v1
    description: Development

tags:
  - name: Users
    description: User management endpoints
  - name: Products
    description: Product catalog endpoints
  - name: Orders
    description: Order management endpoints
```

### 2. Endpoints

#### GET Endpoint
```yaml
paths:
  /users:
    get:
      tags:
        - Users
      summary: List all users
      description: |
        Returns a paginated list of users.
        Supports filtering and sorting.
      operationId: listUsers
      parameters:
        - name: page
          in: query
          description: Page number
          schema:
            type: integer
            default: 1
            minimum: 1
        - name: limit
          in: query
          description: Items per page
          schema:
            type: integer
            default: 20
            minimum: 1
            maximum: 100
        - name: sort
          in: query
          description: Sort field
          schema:
            type: string
            enum: [created_at, name, email]
            default: created_at
        - name: order
          in: query
          schema:
            type: string
            enum: [asc, desc]
            default: desc
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'
              example:
                data:
                  - id: "usr_123"
                    email: "john@example.com"
                    name: "John Doe"
                    created_at: "2024-01-15T10:30:00Z"
                meta:
                  total: 100
                  page: 1
                  limit: 20
        '401':
          $ref: '#/components/responses/Unauthorized'
```

#### POST Endpoint
```yaml
  /users:
    post:
      tags:
        - Users
      summary: Create a new user
      operationId: createUser
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
            examples:
              basic:
                summary: Basic user
                value:
                  email: "john@example.com"
                  name: "John Doe"
                  password: "SecurePass123!"
              withRole:
                summary: User with role
                value:
                  email: "admin@example.com"
                  name: "Admin User"
                  password: "SecurePass123!"
                  role: "admin"
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          $ref: '#/components/responses/BadRequest'
        '409':
          description: User already exists
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              example:
                code: "USER_EXISTS"
                message: "A user with this email already exists"
```

### 3. Components (Schemas)

```yaml
components:
  schemas:
    User:
      type: object
      required:
        - id
        - email
        - created_at
      properties:
        id:
          type: string
          description: Unique identifier
          example: "usr_123abc"
        email:
          type: string
          format: email
          example: "john@example.com"
        name:
          type: string
          example: "John Doe"
        avatar_url:
          type: string
          format: uri
          nullable: true
        role:
          type: string
          enum: [user, admin, moderator]
          default: user
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time

    CreateUserRequest:
      type: object
      required:
        - email
        - password
      properties:
        email:
          type: string
          format: email
        name:
          type: string
          minLength: 2
          maxLength: 100
        password:
          type: string
          format: password
          minLength: 8
          description: Must contain uppercase, lowercase, and number
        role:
          type: string
          enum: [user, admin]
          default: user

    UserList:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/User'
        meta:
          $ref: '#/components/schemas/PaginationMeta'

    PaginationMeta:
      type: object
      properties:
        total:
          type: integer
        page:
          type: integer
        limit:
          type: integer
        total_pages:
          type: integer

    Error:
      type: object
      required:
        - code
        - message
      properties:
        code:
          type: string
          description: Error code for programmatic handling
        message:
          type: string
          description: Human-readable error message
        details:
          type: array
          items:
            type: object
            properties:
              field:
                type: string
              message:
                type: string
```

### 4. Security Schemes

```yaml
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: |
        JWT token obtained from /auth/login.
        Include in header: `Authorization: Bearer <token>`

    apiKey:
      type: apiKey
      in: header
      name: X-API-Key
      description: API key for server-to-server communication

    oauth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://auth.company.com/authorize
          tokenUrl: https://auth.company.com/token
          scopes:
            read:users: Read user information
            write:users: Create and update users
            admin: Full admin access

# Apply globally
security:
  - bearerAuth: []
```

### 5. Reusable Responses

```yaml
components:
  responses:
    Unauthorized:
      description: Authentication required
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            code: "UNAUTHORIZED"
            message: "Invalid or expired token"

    BadRequest:
      description: Invalid request
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            code: "VALIDATION_ERROR"
            message: "Request validation failed"
            details:
              - field: "email"
                message: "Invalid email format"

    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            code: "NOT_FOUND"
            message: "Resource not found"

    RateLimited:
      description: Rate limit exceeded
      headers:
        X-RateLimit-Limit:
          schema:
            type: integer
          description: Request limit per minute
        X-RateLimit-Remaining:
          schema:
            type: integer
          description: Remaining requests
        X-RateLimit-Reset:
          schema:
            type: integer
          description: Unix timestamp when limit resets
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
```

### 6. Postman Collection

```json
{
  "info": {
    "name": "API Collection",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "baseUrl",
      "value": "https://api.company.com/v1"
    },
    {
      "key": "token",
      "value": ""
    }
  ],
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "{{token}}"
      }
    ]
  },
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "url": "{{baseUrl}}/auth/login",
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"test@example.com\",\n  \"password\": \"password123\"\n}",
              "options": {
                "raw": {
                  "language": "json"
                }
              }
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "if (pm.response.code === 200) {",
                  "  var json = pm.response.json();",
                  "  pm.collectionVariables.set('token', json.token);",
                  "}"
                ]
              }
            }
          ]
        }
      ]
    }
  ]
}
```

### 7. Herramientas

```bash
# Generar docs desde OpenAPI
npx @redocly/cli build-docs openapi.yaml -o docs/index.html

# Validar spec
npx @redocly/cli lint openapi.yaml

# Generar desde codigo (Express)
# swagger-jsdoc genera spec desde JSDoc comments

# Generar desde codigo (FastAPI)
# FastAPI genera OpenAPI automaticamente

# Preview interactivo
npx swagger-ui-watcher openapi.yaml
```

### 8. Checklist

- [ ] Info section completa
- [ ] Servers definidos (prod, staging, dev)
- [ ] Tags organizados
- [ ] Security schemes configurados
- [ ] Schemas con ejemplos
- [ ] Responses estandarizadas
- [ ] Error codes documentados
- [ ] Rate limits documentados
- [ ] Changelog mantenido

## Patrones Faltantes

### Error Catalog Estandar
```yaml
# En OpenAPI spec
components:
  responses:
    BadRequest:
      description: Datos de entrada invalidos
      content:
        application/json:
          schema:
            type: object
            properties:
              error: {type: string, example: "VALIDATION_ERROR"}
              message: {type: string, example: "Email format invalid"}
              details: {type: array, items: {type: object}}
    NotFound:
      description: Recurso no encontrado
      content:
        application/json:
          schema:
            type: object
            properties:
              error: {type: string, example: "NOT_FOUND"}
              message: {type: string, example: "User not found"}
```

### Paginacion (Cursor vs Offset)
```yaml
# Cursor-based (recomendado para datasets grandes)
/api/users?cursor=eyJpZCI6MTAwfQ&limit=20
# Response incluye: { data: [...], next_cursor: "eyJpZCI6MTIwfQ", has_more: true }

# Offset-based (simple, OK para datasets pequenos)
/api/users?page=3&per_page=20
# Response incluye: { data: [...], total: 500, page: 3, per_page: 20 }
```

### Decision Tree: Cursor o Offset?
```
├── Dataset < 10K items → Offset (mas simple)
├── Dataset > 10K items → Cursor (mas eficiente)
├── UI con "pagina 1, 2, 3..." → Offset
├── Infinite scroll / feed → Cursor
├── Datos que cambian frecuentemente → Cursor (offset salta items)
```

## Comandos de Ejemplo

```
"Genera OpenAPI spec para estos endpoints"
"Documenta el endpoint de autenticacion"
"Crea coleccion Postman para la API"
"Agrega ejemplos a los schemas"
"Genera documentacion HTML de la API"
```
