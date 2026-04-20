# ============================================================
# Script para Deshabilitar MCP de GitLab en Cursor
# Vision Human Insight - IAGENTEK
# ============================================================

Write-Host "🔧 Deshabilitando MCP de GitLab en Cursor..." -ForegroundColor Cyan

# Ruta del archivo de configuración de Cursor
$settingsPath = Join-Path $env:APPDATA "Cursor\User\settings.json"

# Verificar si existe el archivo
if (-not (Test-Path $settingsPath)) {
    Write-Host "❌ No se encontró el archivo de configuración de Cursor en:" -ForegroundColor Red
    Write-Host "   $settingsPath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💡 Intenta:" -ForegroundColor Cyan
    Write-Host "   1. Abre Cursor" -ForegroundColor White
    Write-Host "   2. Presiona Ctrl+Shift+P" -ForegroundColor White
    Write-Host "   3. Escribe: Preferences: Open User Settings (JSON)" -ForegroundColor White
    Write-Host "   4. Sigue las instrucciones en SOLUCION_MCP_GITLAB.md" -ForegroundColor White
    exit 1
}

Write-Host "✅ Archivo de configuración encontrado" -ForegroundColor Green
Write-Host "   $settingsPath" -ForegroundColor Gray

# Leer el archivo JSON
try {
    $settingsContent = Get-Content $settingsPath -Raw -ErrorAction Stop
    $settings = $settingsContent | ConvertFrom-Json -ErrorAction Stop
} catch {
    Write-Host "❌ Error al leer el archivo de configuración:" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💡 El archivo podría estar corrupto o no ser JSON válido." -ForegroundColor Cyan
    exit 1
}

# Verificar si existe configuración de MCP
$mcpModified = $false
$gitlabRemoved = $false

if ($settings.'mcp.servers') {
    Write-Host "📋 Configuración de MCP encontrada" -ForegroundColor Yellow
    
    # Convertir a hashtable para modificar
    $mcpServers = @{}
    if ($settings.'mcp.servers'.PSObject.Properties) {
        foreach ($server in $settings.'mcp.servers'.PSObject.Properties) {
            $serverName = $server.Name
            $serverValue = $server.Value
            
            # Verificar si es GitLab
            if ($serverName -like "*gitlab*" -or $serverName -like "*GitLab*") {
                Write-Host "   🗑️  Eliminando servidor: $serverName" -ForegroundColor Yellow
                $gitlabRemoved = $true
                # No agregar este servidor a la nueva configuración
            } else {
                # Mantener otros servidores MCP
                $mcpServers[$serverName] = $serverValue
            }
        }
    }
    
    if ($gitlabRemoved) {
        if ($mcpServers.Count -eq 0) {
            # Si no quedan servidores, eliminar la sección completa
            $settings.PSObject.Properties.Remove('mcp.servers')
            Write-Host "   ✅ Sección MCP eliminada (no quedan servidores)" -ForegroundColor Green
        } else {
            # Actualizar con los servidores restantes
            $settings.'mcp.servers' = $mcpServers
            Write-Host "   ✅ Servidor GitLab eliminado" -ForegroundColor Green
        }
        $mcpModified = $true
    } else {
        Write-Host "   ℹ️  No se encontró servidor GitLab en la configuración" -ForegroundColor Gray
    }
} else {
    Write-Host "ℹ️  No se encontró configuración de MCP" -ForegroundColor Gray
    Write-Host "   (Esto es normal si no has configurado MCP)" -ForegroundColor Gray
}

# Guardar cambios si se modificó algo
if ($mcpModified) {
    try {
        # Crear backup del archivo original
        $backupPath = "$settingsPath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Copy-Item $settingsPath $backupPath -ErrorAction Stop
        Write-Host "💾 Backup creado: $backupPath" -ForegroundColor Green
        
        # Convertir a JSON y guardar
        $jsonContent = $settings | ConvertTo-Json -Depth 10
        [System.IO.File]::WriteAllText($settingsPath, $jsonContent, [System.Text.Encoding]::UTF8)
        
        Write-Host ""
        Write-Host "✅ Configuración actualizada correctamente" -ForegroundColor Green
        Write-Host ""
        Write-Host "🔄 Siguiente paso:" -ForegroundColor Cyan
        Write-Host "   1. Cierra completamente Cursor" -ForegroundColor White
        Write-Host "   2. Vuelve a abrir Cursor" -ForegroundColor White
        Write-Host "   3. El error de MCP de GitLab debería desaparecer" -ForegroundColor White
    } catch {
        Write-Host "❌ Error al guardar la configuración:" -ForegroundColor Red
        Write-Host "   $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "💡 Puedes restaurar el backup desde:" -ForegroundColor Cyan
        if (Test-Path $backupPath) {
            Write-Host "   $backupPath" -ForegroundColor Yellow
        }
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "ℹ️  No se realizaron cambios" -ForegroundColor Gray
    Write-Host "   (El MCP de GitLab ya estaba deshabilitado o no existe)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "✨ Proceso completado" -ForegroundColor Green

