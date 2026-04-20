# 🔧 Solución para Error de MCP de GitLab

## Problema
El MCP de GitLab está intentando conectarse a `your-gitlab-instance.com` (URL de ejemplo) en lugar de una URL real.

## Solución Rápida: Deshabilitar MCP de GitLab

### Opción 1: Desde la Interfaz de Cursor (Recomendado)

1. **Abre la configuración de Cursor:**
   - Presiona `Ctrl + Shift + P` (o `Cmd + Shift + P` en Mac)
   - Escribe: `Preferences: Open User Settings (JSON)`
   - O ve a: `File` → `Preferences` → `Settings`

2. **Busca la configuración de MCP:**
   - En la barra de búsqueda de Settings, escribe: `mcp`
   - Busca la sección "MCP Servers" o "Model Context Protocol"

3. **Deshabilita GitLab:**
   - Busca el servidor llamado "GitLab" o "user-GitLab"
   - Desactiva el toggle o elimina la entrada completa

4. **Reinicia Cursor:**
   - Cierra completamente Cursor
   - Vuelve a abrirlo

### Opción 2: Editar Archivo de Configuración Directamente

1. **Abre el archivo de configuración:**
   - Presiona `Ctrl + Shift + P`
   - Escribe: `Preferences: Open User Settings (JSON)`
   - O navega manualmente a:
     - Windows: `%APPDATA%\Cursor\User\settings.json`
     - Mac: `~/Library/Application Support/Cursor/User/settings.json`
     - Linux: `~/.config/Cursor/User/settings.json`

2. **Busca y elimina la configuración de GitLab MCP:**
   ```json
   {
     "mcp.servers": {
       "gitlab": {
         // Elimina toda esta sección
       }
     }
   }
   ```

3. **Reinicia Cursor**

## Solución Alternativa: Configurar GitLab Correctamente

Si necesitas usar GitLab, configura la URL correcta:

### Para GitLab.com (Público):
```json
{
  "mcp.servers": {
    "gitlab": {
      "url": "https://gitlab.com/api/v4/mcp",
      "token": "tu-personal-access-token-aqui"
    }
  }
}
```

### Para Instancia Privada de GitLab:
```json
{
  "mcp.servers": {
    "gitlab": {
      "url": "https://tu-instancia-gitlab.com/api/v4/mcp",
      "token": "tu-access-token-aqui"
    }
  }
}
```

### Cómo Obtener un Token de GitLab:

1. Ve a GitLab.com → Settings → Access Tokens
2. Crea un nuevo token con permisos `api`
3. Copia el token generado
4. Úsalo en la configuración de MCP

## Verificación

Después de deshabilitar o configurar correctamente:

1. Reinicia Cursor
2. Abre la consola de desarrollador (`Ctrl + Shift + I` o `Cmd + Option + I`)
3. Ve a la pestaña "Console"
4. Ya no deberías ver errores de `ENOTFOUND your-gitlab-instance.com`

## Nota

Este error no afecta el funcionamiento del proyecto. Es solo un servicio MCP opcional que intenta conectarse. Puedes trabajar normalmente en Supabase sin GitLab MCP.

