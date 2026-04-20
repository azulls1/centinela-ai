#!/usr/bin/env python3
"""
NXT AI Development - Validador de Setup
Verifica que el entorno este correctamente configurado.

Uso:
    python herramientas/validate_setup.py
"""

import os
import sys
from pathlib import Path

# Configurar encoding UTF-8 para Windows (evita errores con caracteres especiales)
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Colores ANSI para terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    """Imprime el header del validador."""
    print(f"\n{Colors.CYAN}{'═' * 62}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'NXT AI Development - Validacion de Setup':^62}{Colors.END}")
    print(f"{Colors.CYAN}{'═' * 62}{Colors.END}\n")

def print_section(title: str):
    """Imprime un titulo de seccion."""
    print(f"\n{Colors.BOLD}[{title}]{Colors.END}")

def print_ok(message: str):
    """Imprime mensaje de exito."""
    print(f"  {Colors.GREEN}✅{Colors.END} {message}")

def print_warn(message: str):
    """Imprime mensaje de advertencia."""
    print(f"  {Colors.YELLOW}⚠️ {Colors.END} {message}")

def print_error(message: str):
    """Imprime mensaje de error."""
    print(f"  {Colors.RED}❌{Colors.END} {message}")

def get_project_root() -> Path:
    """Obtiene la raiz del proyecto."""
    # Intentar encontrar la raiz buscando CLAUDE.md o .nxt/
    current = Path.cwd()

    # Si estamos en herramientas/, subir un nivel
    if current.name == 'herramientas':
        current = current.parent

    # Verificar si es la raiz del proyecto
    if (current / 'CLAUDE.md').exists() or (current / '.nxt').exists():
        return current

    # Buscar hacia arriba
    for parent in current.parents:
        if (parent / 'CLAUDE.md').exists() or (parent / '.nxt').exists():
            return parent

    return current

def validate_structure(root: Path) -> tuple[int, int]:
    """Valida la estructura de carpetas."""
    print_section("ESTRUCTURA")

    ok_count = 0
    warn_count = 0

    required_paths = [
        ('.nxt/nxt.config.yaml', 'Configuracion principal'),
        ('.claude/commands/nxt', 'Slash commands'),
        ('agentes', 'Agentes NXT'),
        ('herramientas', 'Herramientas CLI'),
        ('skills', 'Skills de Claude'),
        ('workflows', 'Workflows por fase'),
        ('CLAUDE.md', 'Archivo de contexto'),
    ]

    optional_paths = [
        ('plantillas', 'Plantillas de documentos'),
        ('ejemplos', 'Ejemplos de uso'),
        ('.claude/mcp.json', 'Configuracion MCP'),
    ]

    for path, desc in required_paths:
        full_path = root / path
        if full_path.exists():
            print_ok(f"{path}")
            ok_count += 1
        else:
            print_error(f"{path} - {desc} NO ENCONTRADO")
            warn_count += 1

    for path, desc in optional_paths:
        full_path = root / path
        if full_path.exists():
            print_ok(f"{path} (opcional)")
            ok_count += 1
        else:
            print_warn(f"{path} no existe (opcional)")

    return ok_count, warn_count

def validate_env_vars(root: Path) -> tuple[int, int, int]:
    """Valida las variables de entorno."""
    print_section("API KEYS")

    ok_count = 0
    warn_count = 0
    error_count = 0

    # Cargar .env si existe
    env_file = root / '.env'
    env_vars = {}

    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()

    # Combinar con variables de entorno del sistema
    for key in ['GEMINI_API_KEY', 'OPENAI_API_KEY', 'GITHUB_TOKEN', 'ANTHROPIC_API_KEY']:
        if key in os.environ:
            env_vars[key] = os.environ[key]

    # Validar GEMINI_API_KEY (requerida)
    if env_vars.get('GEMINI_API_KEY'):
        key = env_vars['GEMINI_API_KEY']
        if key.startswith('AIza') and len(key) > 30:
            print_ok("GEMINI_API_KEY configurada")
            ok_count += 1
        else:
            print_warn("GEMINI_API_KEY parece invalida (debe empezar con AIza)")
            warn_count += 1
    else:
        print_error("GEMINI_API_KEY no configurada (REQUERIDA para /nxt/search)")
        error_count += 1

    # Validar OPENAI_API_KEY (opcional)
    if env_vars.get('OPENAI_API_KEY'):
        key = env_vars['OPENAI_API_KEY']
        if key.startswith('sk-') and len(key) > 20:
            print_ok("OPENAI_API_KEY configurada")
            ok_count += 1
        else:
            print_warn("OPENAI_API_KEY parece invalida (debe empezar con sk-)")
            warn_count += 1
    else:
        print_warn("OPENAI_API_KEY no configurada (multimedia no disponible)")
        warn_count += 1

    # Validar GITHUB_TOKEN (opcional)
    if env_vars.get('GITHUB_TOKEN'):
        print_ok("GITHUB_TOKEN configurado")
        ok_count += 1
    else:
        print_warn("GITHUB_TOKEN no configurado (GitHub MCP no disponible)")
        warn_count += 1

    # Nota sobre ANTHROPIC_API_KEY
    print(f"\n  {Colors.BLUE}ℹ️ {Colors.END} ANTHROPIC_API_KEY no es necesaria - Claude Code usa sesion autenticada")

    return ok_count, warn_count, error_count

def validate_python_deps() -> tuple[int, int]:
    """Valida las dependencias de Python."""
    print_section("DEPENDENCIAS PYTHON")

    ok_count = 0
    warn_count = 0

    # Dependencias requeridas
    deps = [
        ('google.genai', 'google-genai', True),
        ('openai', 'openai', False),
    ]

    for module, package, required in deps:
        try:
            __import__(module.split('.')[0])
            print_ok(f"{package} instalado")
            ok_count += 1
        except ImportError:
            if required:
                print_error(f"{package} no instalado (pip install {package})")
                warn_count += 1
            else:
                print_warn(f"{package} no instalado (pip install {package})")
                warn_count += 1

    # Version de Python
    py_version = sys.version_info
    if py_version >= (3, 10):
        print_ok(f"Python {py_version.major}.{py_version.minor} (>= 3.10 requerido)")
        ok_count += 1
    else:
        print_error(f"Python {py_version.major}.{py_version.minor} (>= 3.10 requerido)")
        warn_count += 1

    return ok_count, warn_count

def validate_commands(root: Path) -> tuple[int, int]:
    """Valida que los comandos slash existan."""
    print_section("SLASH COMMANDS")

    ok_count = 0
    warn_count = 0

    commands_dir = root / '.claude' / 'commands' / 'nxt'

    if not commands_dir.exists():
        print_error("Carpeta de comandos no encontrada")
        return 0, 1

    required_commands = [
        'init.md',
        'orchestrator.md',
        'help.md',
        'status.md',
        'analyst.md',
        'pm.md',
        'architect.md',
        'dev.md',
        'qa.md',
    ]

    optional_commands = [
        'ux.md',
        'search.md',
        'media.md',
        'docs.md',
        'scrum.md',
        'devops.md',
    ]

    found = list(commands_dir.glob('*.md'))
    found_names = [f.name for f in found]

    for cmd in required_commands:
        if cmd in found_names:
            print_ok(f"/nxt/{cmd.replace('.md', '')}")
            ok_count += 1
        else:
            print_error(f"/nxt/{cmd.replace('.md', '')} no encontrado")
            warn_count += 1

    # Contar opcionales encontrados
    optional_found = sum(1 for cmd in optional_commands if cmd in found_names)
    if optional_found > 0:
        print(f"  {Colors.BLUE}ℹ️ {Colors.END} +{optional_found} comandos opcionales disponibles")

    return ok_count, warn_count

def validate_agents(root: Path) -> tuple[int, int]:
    """Valida que los agentes existan."""
    print_section("AGENTES NXT")

    ok_count = 0
    warn_count = 0

    agents_dir = root / 'agentes'

    if not agents_dir.exists():
        print_error("Carpeta de agentes no encontrada")
        return 0, 1

    found = list(agents_dir.glob('nxt-*.md'))

    if len(found) >= 9:
        print_ok(f"{len(found)} agentes encontrados")
        ok_count += 1
    elif len(found) >= 5:
        print_warn(f"Solo {len(found)} agentes encontrados (esperados 9+)")
        warn_count += 1
    else:
        print_error(f"Solo {len(found)} agentes encontrados (minimo 5)")
        warn_count += 1

    # Listar agentes
    for agent in sorted(found)[:5]:
        print(f"    • {agent.stem}")
    if len(found) > 5:
        print(f"    • ... y {len(found) - 5} mas")

    return ok_count, warn_count

def print_result(total_ok: int, total_warn: int, total_error: int):
    """Imprime el resultado final."""
    print(f"\n{Colors.CYAN}{'═' * 62}{Colors.END}")

    if total_error == 0 and total_warn == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}RESULTADO: ✅ LISTO PARA USAR{Colors.END}")
    elif total_error == 0:
        print(f"{Colors.YELLOW}{Colors.BOLD}RESULTADO: ⚠️  LISTO CON ADVERTENCIAS{Colors.END}")
        print(f"  {total_warn} advertencias menores")
    else:
        print(f"{Colors.RED}{Colors.BOLD}RESULTADO: ❌ REQUIERE CONFIGURACION{Colors.END}")
        print(f"  {total_error} errores criticos, {total_warn} advertencias")

    print(f"{Colors.CYAN}{'═' * 62}{Colors.END}")

    if total_error > 0 or total_warn > 0:
        print(f"\n{Colors.BOLD}Proximos pasos:{Colors.END}")
        if total_error > 0:
            print("  1. Corregir errores criticos arriba")
            print("  2. Ejecutar este script nuevamente")
        print("  3. Iniciar con: /nxt/orchestrator")
    else:
        print(f"\n{Colors.BOLD}Listo! Inicia con:{Colors.END}")
        print("  claude")
        print("  /nxt/orchestrator")

def main():
    """Funcion principal."""
    print_header()

    root = get_project_root()
    print(f"  {Colors.BLUE}📁{Colors.END} Proyecto: {root}\n")

    total_ok = 0
    total_warn = 0
    total_error = 0

    # Validar estructura
    ok, warn = validate_structure(root)
    total_ok += ok
    total_warn += warn

    # Validar variables de entorno
    ok, warn, err = validate_env_vars(root)
    total_ok += ok
    total_warn += warn
    total_error += err

    # Validar dependencias Python
    ok, warn = validate_python_deps()
    total_ok += ok
    total_warn += warn

    # Validar comandos
    ok, warn = validate_commands(root)
    total_ok += ok
    total_warn += warn

    # Validar agentes
    ok, warn = validate_agents(root)
    total_ok += ok
    total_warn += warn

    # Resultado final
    print_result(total_ok, total_warn, total_error)

    # Exit code
    sys.exit(1 if total_error > 0 else 0)

if __name__ == '__main__':
    main()
