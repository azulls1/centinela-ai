# SKILL: Database Migrations

> **Version:** 3.8.0
> **Trigger:** Gestion de migraciones de base de datos
> **Agente:** nxt-database, nxt-migrator
> **Track:** shared

## Proposito
Gestionar cambios de esquema de base de datos de forma segura, versionada
y con capacidad de rollback.

## Cuando se Activa
- Crear nuevas tablas
- Modificar esquemas existentes
- Agregar/eliminar columnas
- Crear indices
- Migraciones de datos

## Instrucciones

### 1. Principios de Migraciones

#### Reglas Fundamentales
- Cada migracion es **irreversible** en produccion (planificar bien)
- Siempre incluir **up** y **down** (rollback)
- Migraciones deben ser **idempotentes** cuando sea posible
- Nunca modificar migraciones ya ejecutadas
- Probar en staging antes de produccion

### 2. Herramientas por Stack

| Stack | Herramienta | Comando |
|-------|-------------|---------|
| Node.js | Prisma | `prisma migrate` |
| Node.js | Knex | `knex migrate` |
| Node.js | TypeORM | `typeorm migration` |
| Python | Alembic | `alembic` |
| Python | Django | `python manage.py migrate` |
| Go | golang-migrate | `migrate` |
| Ruby | ActiveRecord | `rails db:migrate` |

### 3. Templates de Migracion

#### Prisma Migration
```prisma
// prisma/schema.prisma
model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  posts     Post[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

model Post {
  id        Int      @id @default(autoincrement())
  title     String
  content   String?
  published Boolean  @default(false)
  author    User     @relation(fields: [authorId], references: [id])
  authorId  Int
  createdAt DateTime @default(now())
}
```

```bash
# Generar migracion
npx prisma migrate dev --name add_posts_table

# Aplicar en produccion
npx prisma migrate deploy

# Resetear (desarrollo)
npx prisma migrate reset
```

#### Knex Migration
```javascript
// migrations/20240115_create_users.js
exports.up = function(knex) {
  return knex.schema.createTable('users', (table) => {
    table.increments('id').primary();
    table.string('email').unique().notNullable();
    table.string('name');
    table.string('password_hash').notNullable();
    table.enum('role', ['user', 'admin']).defaultTo('user');
    table.boolean('is_active').defaultTo(true);
    table.timestamps(true, true); // created_at, updated_at
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('users');
};

// migrations/20240116_add_profile_to_users.js
exports.up = function(knex) {
  return knex.schema.alterTable('users', (table) => {
    table.string('avatar_url');
    table.text('bio');
    table.date('birth_date');
  });
};

exports.down = function(knex) {
  return knex.schema.alterTable('users', (table) => {
    table.dropColumn('avatar_url');
    table.dropColumn('bio');
    table.dropColumn('birth_date');
  });
};
```

#### Alembic (Python)
```python
# alembic/versions/001_create_users.py
"""Create users table

Revision ID: 001
Create Date: 2024-01-15
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('name', sa.String(255)),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])

def downgrade():
    op.drop_index('ix_users_email', 'users')
    op.drop_table('users')
```

### 4. Patrones Comunes

#### Agregar Columna NOT NULL
```javascript
// Paso 1: Agregar columna nullable
exports.up = async function(knex) {
  await knex.schema.alterTable('users', (table) => {
    table.string('phone'); // nullable primero
  });

  // Paso 2: Backfill datos existentes
  await knex('users').update({ phone: 'UNKNOWN' });

  // Paso 3: Hacer NOT NULL
  await knex.schema.alterTable('users', (table) => {
    table.string('phone').notNullable().alter();
  });
};
```

#### Renombrar Columna (Zero Downtime)
```javascript
// Migracion 1: Agregar nueva columna
exports.up = function(knex) {
  return knex.schema.alterTable('users', (table) => {
    table.string('full_name'); // nueva
  });
};

// Migracion 2: Copiar datos (puede ser script separado)
// UPDATE users SET full_name = name;

// Migracion 3: Eliminar columna vieja (despues de deploy de codigo)
exports.up = function(knex) {
  return knex.schema.alterTable('users', (table) => {
    table.dropColumn('name'); // vieja
  });
};
```

#### Crear Indice Sin Bloqueo (PostgreSQL)
```sql
-- Crear indice CONCURRENTLY para no bloquear tabla
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- En migracion, puede requerir raw SQL
exports.up = function(knex) {
  return knex.raw(
    'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email)'
  );
};
```

### 5. Data Migrations

```javascript
// migrations/20240120_migrate_user_roles.js
exports.up = async function(knex) {
  // Crear nueva tabla de roles
  await knex.schema.createTable('roles', (table) => {
    table.increments('id');
    table.string('name').unique();
  });

  // Insertar roles
  await knex('roles').insert([
    { name: 'user' },
    { name: 'admin' },
    { name: 'moderator' },
  ]);

  // Agregar foreign key
  await knex.schema.alterTable('users', (table) => {
    table.integer('role_id').unsigned().references('roles.id');
  });

  // Migrar datos
  const adminRole = await knex('roles').where('name', 'admin').first();
  const userRole = await knex('roles').where('name', 'user').first();

  await knex('users')
    .where('role', 'admin')
    .update({ role_id: adminRole.id });

  await knex('users')
    .where('role', 'user')
    .update({ role_id: userRole.id });

  // Eliminar columna vieja
  await knex.schema.alterTable('users', (table) => {
    table.dropColumn('role');
  });
};
```

### 6. Comandos de Migracion

```bash
# Knex
knex migrate:make create_users      # Crear migracion
knex migrate:latest                  # Ejecutar pendientes
knex migrate:rollback                # Revertir ultima
knex migrate:status                  # Ver estado

# Prisma
prisma migrate dev --name init       # Desarrollo
prisma migrate deploy                # Produccion
prisma migrate status                # Ver estado

# Alembic
alembic revision -m "create users"   # Crear
alembic upgrade head                 # Ejecutar
alembic downgrade -1                 # Revertir una
alembic history                      # Ver historial
```

### 7. Checklist de Migracion

#### Antes de Crear
- [ ] Revisar schema actual
- [ ] Planificar cambios necesarios
- [ ] Considerar impacto en datos existentes
- [ ] Evaluar tiempo de ejecucion

#### Antes de Ejecutar
- [ ] Backup de base de datos
- [ ] Probar en ambiente de staging
- [ ] Verificar rollback funciona
- [ ] Coordinar con equipo (si es breaking)

#### Despues de Ejecutar
- [ ] Verificar schema resultante
- [ ] Probar queries principales
- [ ] Monitorear performance
- [ ] Documentar cambios

### 8. Zero-Downtime Migrations

```
Estrategia de 3 fases:

Fase 1 - Expand
├── Agregar nuevas columnas/tablas
├── Columnas nuevas son nullable
└── Deploy: codigo lee viejo, escribe viejo

Fase 2 - Migrate
├── Backfill datos a nuevas columnas
├── Deploy: codigo lee viejo+nuevo, escribe ambos
└── Verificar consistencia

Fase 3 - Contract
├── Codigo solo usa nuevo schema
├── Deploy: codigo lee nuevo, escribe nuevo
└── Eliminar columnas/tablas viejas
```

## Zero-Downtime Migration (Expand-Migrate-Contract)

### Paso 1: Expand (agregar sin romper)
```sql
-- migration_001_expand.sql
ALTER TABLE users ADD COLUMN display_name VARCHAR(100);
-- La columna nueva es nullable, no rompe queries existentes
```

### Paso 2: Migrate (copiar datos)
```sql
-- migration_002_migrate.sql
UPDATE users SET display_name = name WHERE display_name IS NULL;
-- Backfill gradual para no bloquear tabla
```

### Paso 3: Contract (remover lo viejo)
```sql
-- migration_003_contract.sql (deploy en siguiente release)
ALTER TABLE users ALTER COLUMN display_name SET NOT NULL;
ALTER TABLE users DROP COLUMN name;
```

### Decision Tree: Necesito Zero-Downtime?
```
Que tipo de cambio es?
├── Agregar columna nullable → Directo (no rompe nada)
├── Renombrar columna → Expand-Migrate-Contract (3 pasos)
├── Cambiar tipo de columna → Expand-Migrate-Contract
├── Eliminar columna → Verificar que no se usa + Contract
├── Agregar indice en tabla grande → CREATE INDEX CONCURRENTLY
├── Cambiar constraint → Expand-Migrate-Contract
```

## Comandos de Ejemplo

```
"Crea una migracion para agregar tabla de productos"
"Genera migracion para agregar columna status a orders"
"Como hago un rename de columna sin downtime?"
"Crea migracion de datos para normalizar roles"
"Rollback de la ultima migracion"
```
