# 🔧 Configuración de Supabase - Guía Completa

Esta guía te ayudará a configurar tu proyecto Supabase con las credenciales proporcionadas.

## 📋 Credenciales de Tu Proyecto

```
URL del Proyecto: https://iagenteksupabase.iagentek.com.mx
Anon Key: eyJhbGciOiJlUzI1NilsInR5cCl6lkpXVCJ9.ewoglCJyb2xlljogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzE1MDUwODAwLAogICJleHAiOiAxODcyODE3MjAwCn0.23LYnOepZ9yTJObLFoTnszO5WdHpbekvgwMt8bn2o_k
Service Role Key: eyJhbGciOiJlUzI1NilsInR5cCl6IkpXVCJ9.ewoglCJyb2xlljogInNlcnZpY2Vfcm9sZSIsCiAglmlzcyI6ICJzdXBhYmFzZSIsCiAglmlhdC16IDE3MTUwNTA4MDAsCiAglmV4cCI6IDE4NzI4MTcyMDAKfQ.82nFc9RPC-OtzNOsvrqQrnHUHHe51bJkpCUiC_uTypo
```

## 🚀 Pasos Rápidos

### 1️⃣ Ejecutar Script SQL en Supabase

1. Ve a tu proyecto Supabase: https://supabase.com/dashboard
2. Selecciona tu proyecto
3. Abre el **SQL Editor** (menú lateral)
4. Haz clic en **"+ New Query"**
5. Abre el archivo `infra/supabase/setup.sql`
6. Copia TODO el contenido
7. Pégalo en el editor SQL de Supabase
8. Haz clic en **"Run"** (o presiona Ctrl+Enter)

**✅ Verificación:** Deberías ver mensajes de éxito sin errores.

### 2️⃣ Configurar Variables de Entorno

Los archivos `.env` ya están creados con tus credenciales. Solo verifica que existan:

#### Frontend (`apps/web/.env`)
```env
VITE_SUPABASE_URL=https://iagenteksupabase.iagentek.com.mx
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJlUzI1NilsInR5cCl6lkpXVCJ9.ewoglCJyb2xlljogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzE1MDUwODAwLAogICJleHAiOiAxODcyODE3MjAwCn0.23LYnOepZ9yTJObLFoTnszO5WdHpbekvgwMt8bn2o_k
VITE_API_URL=http://localhost:8000
```

#### Backend (`apps/api/.env`)
```env
SUPABASE_URL=https://iagenteksupabase.iagentek.com.mx
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJlUzI1NilsInR5cCl6IkpXVCJ9.ewoglCJyb2xlljogInNlcnZpY2Vfcm9sZSIsCiAglmlzcyI6ICJzdXBhYmFzZSIsCiAglmlhdC16IDE3MTUwNTA4MDAsCiAglmV4cCI6IDE4NzI4MTcyMDAKfQ.82nFc9RPC-OtzNOsvrqQrnHUHHe51bJkpCUiC_uTypo
OPENAI_API_KEY=
FRONTEND_URL=http://localhost:5173
```

**Nota:** Si los archivos `.env` no existen, créalos manualmente con el contenido de arriba.

### 3️⃣ Verificar Configuración

Ejecuta el script de verificación en Supabase:

1. Abre el **SQL Editor** en Supabase
2. Abre el archivo `infra/supabase/verificar.sql`
3. Copia y ejecuta el contenido
4. Deberías ver resultados sin errores

## 📁 Archivos Creados

He creado los siguientes archivos para ti:

### Scripts SQL

1. **`infra/supabase/setup.sql`** ⭐
   - Script principal de configuración
   - Crea tablas, índices, políticas RLS y funciones
   - **EJECUTA ESTE PRIMERO**

2. **`infra/supabase/verificar.sql`**
   - Script de verificación
   - Ejecuta después de `setup.sql` para confirmar que todo funciona

3. **`infra/supabase/limpiar.sql`** ⚠️
   - Script de limpieza (elimina todo)
   - Solo usar si necesitas empezar desde cero

### Documentación

4. **`infra/supabase/INSTRUCCIONES.md`**
   - Guía detallada paso a paso
   - Incluye solución de problemas

## ✅ Checklist de Configuración

- [ ] Ejecutado `setup.sql` en Supabase SQL Editor
- [ ] Verificado que la tabla `events` existe (Table Editor)
- [ ] Verificado que RLS está habilitado (Table Editor > Policies)
- [ ] Verificado que las funciones existen (Database > Functions)
- [ ] Creado/verificado `apps/web/.env` con credenciales
- [ ] Creado/verificado `apps/api/.env` con credenciales
- [ ] Ejecutado `verificar.sql` sin errores
- [ ] Frontend se conecta a Supabase (sin errores en consola)
- [ ] Backend se conecta a Supabase (`/api/health` responde correctamente)

## 🧪 Probar la Conexión

### Desde Supabase (SQL Editor):

```sql
-- Insertar evento de prueba
INSERT INTO events (event_type, payload, user_id) 
VALUES (
    'test_event',
    '{"test": true, "message": "Conexión exitosa"}'::jsonb,
    'anonymous'
);

-- Verificar
SELECT * FROM events ORDER BY created_at DESC LIMIT 1;
```

### Desde el Frontend:

1. Inicia el frontend: `cd apps/web && npm run dev`
2. Abre la consola del navegador (F12)
3. No deberías ver errores de conexión a Supabase

### Desde el Backend:

1. Inicia el backend: `cd apps/api && python main.py`
2. Visita: http://localhost:8000/api/health
3. Deberías ver: `{"status": "healthy", "database": "connected"}`

## 🔒 Seguridad

### ⚠️ IMPORTANTE:

- **Anon Key**: Segura para usar en el frontend (pública)
- **Service Role Key**: ⚠️ **NUNCA** exponer en el frontend o repositorios públicos
- Solo usar Service Role Key en el backend (FastAPI)

### Variables de Entorno:

- Los archivos `.env` están en `.gitignore` (no se suben a Git)
- Nunca commitees las credenciales
- Rota las keys periódicamente si es necesario

## 📚 Recursos

- **Scripts SQL**: `infra/supabase/`
- **Guía Detallada**: `infra/supabase/INSTRUCCIONES.md`
- **Documentación Supabase**: https://supabase.com/docs

## 🐛 Solución de Problemas

### Error: "relation already exists"
```sql
-- Ejecuta primero el script de limpieza (opcional)
-- O simplemente continúa, las declaraciones IF NOT EXISTS evitarán errores
```

### Error: "permission denied"
- Verifica que estás usando la cuenta correcta
- Asegúrate de tener permisos de administrador en el proyecto

### Error de conexión desde el frontend/backend
- Verifica que las variables de entorno están correctas
- Verifica que no hay espacios extra en las keys
- Reinicia el servidor después de cambiar `.env`

---

**¿Listo?** Una vez completados estos pasos, tu proyecto estará completamente configurado y listo para usar. 🚀

