# Configuración de Supabase - Solución de Error 401

## Problema: Error 401 "Invalid authentication credentials"

Este error ocurre cuando las políticas RLS (Row Level Security) de Supabase bloquean las inserciones.

## Soluciones

### Opción 1: Verificar que las políticas RLS permitan inserciones anónimas

Asegúrate de que en Supabase, la política de INSERT permite `user_id = 'anonymous'`:

```sql
-- Verificar y actualizar la política si es necesario
DROP POLICY IF EXISTS "Users can insert events" ON events;

CREATE POLICY "Users can insert events"
    ON events
    FOR INSERT
    WITH CHECK (
        auth.uid()::text = user_id 
        OR user_id = 'anonymous'  -- Permitir inserciones anónimas
    );
```

### Opción 2: Desactivar RLS temporalmente (solo para desarrollo)

```sql
ALTER TABLE events DISABLE ROW LEVEL SECURITY;
```

**⚠️ ADVERTENCIA**: Solo hacer esto en desarrollo, nunca en producción.

### Opción 3: Usar el backend para insertar eventos

El backend tiene la `service_role_key` que bypassa RLS. Puedes configurar el frontend para enviar eventos al backend en lugar de directamente a Supabase.

## Verificación

1. Ve a Supabase Dashboard > Table Editor > events
2. Ve a la pestaña "Policies" o "RLS"
3. Verifica que la política "Users can insert events" permita `user_id = 'anonymous'`

## Estado Actual

El código ahora:
- ✅ Maneja errores de autenticación silenciosamente
- ✅ Usa throttling para evitar demasiadas inserciones
- ✅ Solo intenta insertar cuando hay cambios significativos
- ✅ No bloquea la aplicación si hay errores de autenticación

Si los eventos no se guardan, la aplicación seguirá funcionando normalmente, solo que no se registrarán en Supabase hasta que se configuren correctamente las políticas.

