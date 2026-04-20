# SKILL: Model Context Protocol (MCP)

> **Version:** 3.8.0
> **Trigger:** Configuracion y uso de MCP servers
> **Agente:** nxt-orchestrator, nxt-context
> **Track:** shared

## Proposito
Configurar y utilizar MCP servers para extender las capacidades de Claude
con herramientas externas, bases de datos y servicios.

## Cuando se Activa
- Configurar MCP servers
- Crear custom tools
- Integrar con servicios externos
- Acceder a bases de datos
- Automatizar workflows

## Instrucciones

### 1. Que es MCP

Model Context Protocol (MCP) es un protocolo abierto de Anthropic que permite
conectar LLMs con fuentes de datos externas y herramientas.

```
┌─────────────┐     MCP      ┌─────────────┐
│   Claude    │◄────────────►│ MCP Server  │
│   (Host)    │   Protocol   │  (Tools)    │
└─────────────┘              └──────┬──────┘
                                    │
                             ┌──────▼──────┐
                             │  External   │
                             │  Services   │
                             └─────────────┘
```

### 2. Configuracion en Claude Code

#### Archivo de Configuracion
```json
// .claude/mcp.json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${DATABASE_URL}"
      }
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}",
        "SLACK_TEAM_ID": "${SLACK_TEAM_ID}"
      }
    }
  }
}
```

### 3. MCP Servers Disponibles

#### Oficiales (Anthropic)
| Server | Proposito | Tools |
|--------|-----------|-------|
| filesystem | Acceso a archivos | read, write, list, search |
| github | GitHub API | repos, issues, PRs, files |
| postgres | PostgreSQL | query, schema, tables |
| sqlite | SQLite | query, tables |
| memory | Key-value store | get, set, delete |
| slack | Slack API | messages, channels, users |
| fetch | HTTP requests | fetch URLs |
| puppeteer | Browser automation | screenshot, navigate |

#### Comunidad Populares
| Server | Proposito |
|--------|-----------|
| notion | Notion API |
| linear | Linear issues |
| jira | Jira integration |
| sentry | Error tracking |
| vercel | Deployments |
| supabase | Supabase DB |

### 4. Crear Custom MCP Server

#### Estructura Basica (TypeScript)
```typescript
// src/index.ts
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

const server = new Server(
  {
    name: 'my-custom-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'get_weather',
        description: 'Get current weather for a location',
        inputSchema: {
          type: 'object',
          properties: {
            location: {
              type: 'string',
              description: 'City name or coordinates',
            },
          },
          required: ['location'],
        },
      },
      {
        name: 'send_notification',
        description: 'Send a notification to a user',
        inputSchema: {
          type: 'object',
          properties: {
            userId: { type: 'string' },
            message: { type: 'string' },
          },
          required: ['userId', 'message'],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case 'get_weather': {
      const weather = await fetchWeather(args.location);
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(weather, null, 2),
          },
        ],
      };
    }

    case 'send_notification': {
      await sendNotification(args.userId, args.message);
      return {
        content: [
          {
            type: 'text',
            text: `Notification sent to ${args.userId}`,
          },
        ],
      };
    }

    default:
      throw new Error(`Unknown tool: ${name}`);
  }
});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
```

#### Package.json
```json
{
  "name": "my-mcp-server",
  "version": "1.0.0",
  "type": "module",
  "bin": {
    "my-mcp-server": "./dist/index.js"
  },
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0"
  }
}
```

### 5. Resources (Datos Estructurados)

```typescript
// Exponer recursos que Claude puede leer
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: [
      {
        uri: 'config://app/settings',
        name: 'Application Settings',
        description: 'Current application configuration',
        mimeType: 'application/json',
      },
      {
        uri: 'db://users/schema',
        name: 'Users Table Schema',
        description: 'Database schema for users table',
        mimeType: 'application/json',
      },
    ],
  };
});

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  if (uri === 'config://app/settings') {
    return {
      contents: [
        {
          uri,
          mimeType: 'application/json',
          text: JSON.stringify(appSettings),
        },
      ],
    };
  }

  throw new Error(`Unknown resource: ${uri}`);
});
```

### 6. Prompts (Templates Reutilizables)

```typescript
server.setRequestHandler(ListPromptsRequestSchema, async () => {
  return {
    prompts: [
      {
        name: 'code_review',
        description: 'Review code for best practices',
        arguments: [
          {
            name: 'code',
            description: 'Code to review',
            required: true,
          },
          {
            name: 'language',
            description: 'Programming language',
            required: true,
          },
        ],
      },
    ],
  };
});

server.setRequestHandler(GetPromptRequestSchema, async (request) => {
  if (request.params.name === 'code_review') {
    return {
      messages: [
        {
          role: 'user',
          content: {
            type: 'text',
            text: `Review this ${request.params.arguments?.language} code:\n\n${request.params.arguments?.code}`,
          },
        },
      ],
    };
  }
});
```

### 7. Seguridad

#### Best Practices
```typescript
// Validar inputs
function validateInput(args: unknown): asserts args is ValidArgs {
  const schema = z.object({
    query: z.string().max(1000),
    limit: z.number().int().min(1).max(100),
  });
  schema.parse(args);
}

// Sanitizar queries SQL
const result = await db.query(
  'SELECT * FROM users WHERE id = $1',
  [args.userId]  // Parametrizado, NO concatenar
);

// Limitar acceso a archivos
const ALLOWED_DIRS = ['/app/data', '/app/config'];
function isPathAllowed(path: string): boolean {
  const resolved = path.resolve(path);
  return ALLOWED_DIRS.some(dir => resolved.startsWith(dir));
}

// Rate limiting
const rateLimiter = new RateLimiter({
  tokensPerInterval: 100,
  interval: 'minute',
});
```

### 8. Testing

```typescript
// test/server.test.ts
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { InMemoryTransport } from '@modelcontextprotocol/sdk/inMemory.js';

describe('MCP Server', () => {
  let client: Client;

  beforeEach(async () => {
    const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
    await server.connect(serverTransport);
    client = new Client({ name: 'test', version: '1.0' });
    await client.connect(clientTransport);
  });

  it('should list tools', async () => {
    const result = await client.listTools();
    expect(result.tools).toHaveLength(2);
  });

  it('should execute tool', async () => {
    const result = await client.callTool({
      name: 'get_weather',
      arguments: { location: 'London' },
    });
    expect(result.content[0].text).toContain('temperature');
  });
});
```

### 9. Checklist

#### Configuracion
- [ ] mcp.json configurado
- [ ] Variables de entorno set
- [ ] Servers testeados localmente
- [ ] Permisos verificados

#### Custom Server
- [ ] Tools documentados
- [ ] Input validation
- [ ] Error handling
- [ ] Rate limiting
- [ ] Tests escritos

#### Seguridad
- [ ] Secrets en env vars
- [ ] Inputs sanitizados
- [ ] Acceso restringido
- [ ] Logs de auditoria

## Comandos de Ejemplo

```
"Configura MCP server de GitHub"
"Crea un custom MCP server para nuestra API"
"Agrega MCP server de PostgreSQL"
"Como expongo resources en MCP?"
"Implementa rate limiting en el MCP server"
```

## Referencias

- Documentacion oficial: https://modelcontextprotocol.io
- Servers oficiales: https://github.com/modelcontextprotocol/servers
- SDK: https://github.com/modelcontextprotocol/sdk
