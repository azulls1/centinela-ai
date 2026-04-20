# SKILL: Diagramas Tecnicos

> **Version:** 3.8.0
> **Trigger:** Creacion de diagramas tecnicos y arquitectura
> **Agente:** nxt-architect, nxt-design
> **Track:** shared

## Proposito
Crear diagramas tecnicos claros y profesionales para documentar
arquitectura, flujos y estructuras del sistema.

## Cuando se Activa
- Crear diagramas de arquitectura
- Disenar flujos de datos
- Modelar base de datos
- Documentar secuencias
- Visualizar componentes

## Instrucciones

### 1. Tipos de Diagramas

| Tipo | Uso | Herramienta |
|------|-----|-------------|
| C4 Context | Vista general del sistema | Mermaid/PlantUML |
| C4 Container | Componentes principales | Mermaid/PlantUML |
| C4 Component | Detalle de un container | Mermaid/PlantUML |
| Secuencia | Flujo de mensajes | Mermaid |
| Flujo | Procesos y decisiones | Mermaid |
| ERD | Modelo de datos | Mermaid |
| Clase | Estructura OOP | Mermaid |
| Estado | Maquina de estados | Mermaid |

### 2. Diagramas C4

#### Level 1: Context Diagram
```mermaid
graph TB
    subgraph "Sistema"
        A[Mi Aplicacion]
    end

    U1[Usuario Web] -->|Usa| A
    U2[Usuario Mobile] -->|Usa| A
    A -->|Envia emails| E[Sistema de Email]
    A -->|Procesa pagos| P[Gateway de Pagos]
    A -->|Almacena| DB[(Base de Datos)]

    style A fill:#3B82F6,color:#fff
```

#### Level 2: Container Diagram
```mermaid
graph TB
    subgraph "Frontend"
        WEB[React SPA]
        MOB[React Native App]
    end

    subgraph "Backend"
        API[API Gateway]
        AUTH[Auth Service]
        CORE[Core Service]
        NOTIFY[Notification Service]
    end

    subgraph "Data"
        DB[(PostgreSQL)]
        CACHE[(Redis)]
        S3[S3 Storage]
    end

    WEB -->|HTTPS| API
    MOB -->|HTTPS| API
    API --> AUTH
    API --> CORE
    API --> NOTIFY
    CORE --> DB
    CORE --> CACHE
    NOTIFY --> S3

    style API fill:#3B82F6,color:#fff
```

#### Level 3: Component Diagram
```mermaid
graph TB
    subgraph "Auth Service"
        CTRL[Auth Controller]
        SVC[Auth Service]
        REPO[User Repository]
        JWT[JWT Provider]
    end

    CTRL --> SVC
    SVC --> REPO
    SVC --> JWT
    REPO --> DB[(Database)]

    style CTRL fill:#F97316,color:#fff
```

### 3. Diagrama de Secuencia

```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as Frontend
    participant A as API
    participant D as Database
    participant C as Cache

    U->>F: Click Login
    F->>A: POST /auth/login
    A->>D: Query user
    D-->>A: User data
    A->>A: Validate password
    A->>C: Store session
    A-->>F: JWT Token
    F->>F: Store token
    F-->>U: Redirect to Dashboard
```

### 4. Diagrama de Flujo

```mermaid
flowchart TD
    A[Inicio] --> B{Usuario autenticado?}
    B -->|Si| C[Mostrar Dashboard]
    B -->|No| D[Mostrar Login]
    D --> E[Ingresar credenciales]
    E --> F{Credenciales validas?}
    F -->|Si| G[Crear sesion]
    G --> C
    F -->|No| H[Mostrar error]
    H --> E
    C --> I[Fin]
```

### 5. Diagrama ERD

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    USER {
        int id PK
        string email UK
        string password_hash
        datetime created_at
    }
    ORDER ||--|{ ORDER_ITEM : contains
    ORDER {
        int id PK
        int user_id FK
        decimal total
        string status
        datetime created_at
    }
    ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal price
    }
    PRODUCT ||--o{ ORDER_ITEM : "is in"
    PRODUCT {
        int id PK
        string name
        decimal price
        int stock
    }
```

### 6. Diagrama de Clases

```mermaid
classDiagram
    class User {
        +int id
        +string email
        +string passwordHash
        +login(credentials)
        +logout()
    }

    class Order {
        +int id
        +User user
        +List~OrderItem~ items
        +decimal total
        +addItem(product, quantity)
        +calculateTotal()
    }

    class OrderItem {
        +int id
        +Product product
        +int quantity
        +decimal price
    }

    class Product {
        +int id
        +string name
        +decimal price
        +int stock
    }

    User "1" --> "*" Order
    Order "1" --> "*" OrderItem
    OrderItem "*" --> "1" Product
```

### 7. Diagrama de Estados

```mermaid
stateDiagram-v2
    [*] --> Pendiente
    Pendiente --> EnProceso : Pagar
    EnProceso --> Enviado : Despachar
    Enviado --> Entregado : Confirmar entrega
    Entregado --> [*]

    EnProceso --> Cancelado : Cancelar
    Pendiente --> Cancelado : Cancelar
    Cancelado --> [*]
```

### 8. Formato y Estilos

#### Colores NXT
```mermaid
%%{init: {'theme': 'base', 'themeVariables': {
  'primaryColor': '#3B82F6',
  'primaryTextColor': '#fff',
  'primaryBorderColor': '#1E40AF',
  'lineColor': '#6B7280',
  'secondaryColor': '#F97316',
  'tertiaryColor': '#8B5CF6'
}}}%%
```

#### Leyenda
- **Azul (#3B82F6)**: Componentes principales
- **Naranja (#F97316)**: Puntos de entrada
- **Purpura (#8B5CF6)**: Servicios externos
- **Verde (#10B981)**: Base de datos
- **Gris (#6B7280)**: Lineas de conexion

### 9. Proceso de Creacion

1. Identificar que se quiere comunicar
2. Elegir tipo de diagrama apropiado
3. Definir elementos principales
4. Establecer relaciones
5. Aplicar estilos NXT
6. Validar que sea comprensible
7. Exportar como SVG o PNG

## Comandos de Ejemplo

```
"Crea diagrama de arquitectura C4"
"Genera diagrama de secuencia para login"
"Crea ERD para el modulo de ordenes"
"Diagrama de flujo para checkout"
"Genera diagrama de componentes del API"
```

## Herramientas y Comandos

### Mermaid CLI (generar PNG/SVG)
```bash
# Instalar
npm install -g @mermaid-js/mermaid-cli

# Generar PNG desde .mmd
mmdc -i diagram.mmd -o diagram.png -t dark

# Generar SVG
mmdc -i diagram.mmd -o diagram.svg
```

### C4 Model con Mermaid (C4-PlantUML alternativa)
```mermaid
C4Context
    title Sistema NXT - Contexto (C4 Level 1)

    Person(dev, "Developer", "Usa Claude Code + NXT Framework")
    System(nxt, "NXT Framework", "32 agentes, 21 skills, telemetria")
    System_Ext(claude, "Claude API", "LLM principal")
    System_Ext(gemini, "Gemini API", "Busquedas y multimedia")
    System_Ext(supabase, "Supabase", "Telemetria del equipo")

    Rel(dev, nxt, "Usa via /nxt/ commands")
    Rel(nxt, claude, "Genera codigo, analiza")
    Rel(nxt, gemini, "Busca, genera media")
    Rel(nxt, supabase, "Envia telemetria")
```

### PlantUML (para diagramas complejos)
```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

Person(dev, "Developer")
System_Boundary(nxt, "NXT Framework") {
    Container(agents, "32 Agentes", "Markdown", "Instrucciones especializadas")
    Container(orchestrator, "Orchestrator", "Python", "Clasificacion y delegacion")
    Container(hooks, "Hooks", "Bash", "Telemetria automatica")
    ContainerDb(state, "State", "JSON", ".nxt/state.json")
}
Rel(dev, agents, "Activa via /nxt/")
Rel(orchestrator, agents, "Delega tareas")
Rel(hooks, state, "Actualiza")
@enduml
```

### Decision Tree: Que Tipo de Diagrama?
```
Que quieres visualizar?
├── Flujo de datos/proceso --> Mermaid flowchart
├── Arquitectura de sistema --> C4 Model (Mermaid C4Context)
├── Modelo de datos/ERD --> Mermaid erDiagram
├── Secuencia de llamadas --> Mermaid sequenceDiagram
├── Estados de un objeto --> Mermaid stateDiagram
├── Timeline/Gantt --> Mermaid gantt
├── Diagrama complejo con estilos --> PlantUML
├── Diagrama para docs/README --> Mermaid (renderiza en GitHub)
```

---

## Exportacion

Para exportar diagramas:

### Mermaid a SVG
```bash
npx mmdc -i diagram.mmd -o diagram.svg
```

### Mermaid a PNG
```bash
npx mmdc -i diagram.mmd -o diagram.png -w 1920 -H 1080
```

### PlantUML
```bash
java -jar plantuml.jar diagram.puml
```

## Ubicacion de Archivos

```
docs/
├── diagrams/
│   ├── architecture/
│   │   ├── c4-context.svg
│   │   ├── c4-container.svg
│   │   └── c4-component-auth.svg
│   ├── sequences/
│   │   ├── login-flow.svg
│   │   └── checkout-flow.svg
│   ├── data/
│   │   └── erd.svg
│   └── flows/
│       └── user-registration.svg
```
