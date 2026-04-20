#!/usr/bin/env python3
"""
NXT AI Development - Utilidades Comunes
Funciones auxiliares para el framework.
"""

import os
import sys
import json
import yaml
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List


def get_project_root() -> Path:
    """
    Obtiene la raiz del proyecto NXT.

    Estrategia de resolución (multi-proyecto safe):
    1. NXT_PROJECT_ROOT env var (explicit override, máxima prioridad)
    2. CWD si tiene .nxt/ (el caso más común)
    3. Directorio del script que importó utils.py (para CLI tools)
    4. Buscar hacia arriba desde CWD (máximo 3 niveles para evitar cross-project)
    5. Fallback: CWD
    """
    # 1. Variable de entorno explícita (para docker, CI, multi-project)
    env_root = os.environ.get("NXT_PROJECT_ROOT")
    if env_root:
        env_path = Path(env_root)
        if (env_path / ".nxt").exists():
            return env_path

    # 2. CWD directo (caso más común: usuario está en el directorio del proyecto)
    cwd = Path.cwd()
    if (cwd / ".nxt").exists():
        return cwd

    # 3. Directorio del script que importó utils.py (para herramientas/*.py)
    script_dir = Path(__file__).resolve().parent
    # Si estamos en herramientas/, el root es el padre
    candidate = script_dir.parent
    if (candidate / ".nxt").exists():
        return candidate

    # 4. Buscar hacia arriba LIMITADO a 3 niveles (evita cross-project contamination)
    current = cwd
    max_depth = 3
    for _ in range(max_depth):
        if current == current.parent:
            break
        current = current.parent
        if (current / ".nxt").exists():
            # Validar que es el proyecto correcto verificando nxt.config.yaml
            config = current / ".nxt" / "nxt.config.yaml"
            if config.exists():
                return current

    # 5. Fallback: CWD (puede no tener .nxt/, pero es mejor que un proyecto ajeno)
    return cwd


def load_config() -> Dict[str, Any]:
    """Carga la configuracion del framework."""
    root = get_project_root()

    # Intentar cargar desde .nxt/nxt.config.yaml
    config_path = root / ".nxt" / "nxt.config.yaml"
    if not config_path.exists():
        # Fallback a nxt/_cfg/nxt.config.yaml
        config_path = root / "nxt" / "_cfg" / "nxt.config.yaml"

    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    return {}


def get_welcome_message() -> str:
    """Obtiene el mensaje de bienvenida."""
    root = get_project_root()
    welcome_path = root / ".nxt" / "welcome.txt"

    if welcome_path.exists():
        with open(welcome_path, 'r', encoding='utf-8') as f:
            return f.read()

    return "Bienvenido a NXT AI Development"


def get_version() -> str:
    """Obtiene la version del framework."""
    root = get_project_root()
    version_path = root / ".nxt" / "version.txt"

    if version_path.exists():
        with open(version_path, 'r', encoding='utf-8') as f:
            return f.read().strip()

    return "1.0.0"


def ensure_directory(path: str) -> Path:
    """Asegura que un directorio existe."""
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def generate_id(prefix: str = "") -> str:
    """Genera un ID unico."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    hash_part = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:6]
    return f"{prefix}{timestamp}-{hash_part}" if prefix else f"{timestamp}-{hash_part}"


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Formatea un timestamp."""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_date(dt: Optional[datetime] = None) -> str:
    """Formatea una fecha."""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d")


def load_json(path: str) -> Dict[str, Any]:
    """Carga un archivo JSON."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Dict[str, Any], path: str, indent: int = 2) -> None:
    """Guarda datos en un archivo JSON."""
    ensure_directory(str(Path(path).parent))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def load_yaml(path: str) -> Dict[str, Any]:
    """Carga un archivo YAML."""
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_yaml(data: Dict[str, Any], path: str) -> None:
    """Guarda datos en un archivo YAML."""
    ensure_directory(str(Path(path).parent))
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


def load_markdown(path: str) -> str:
    """Carga un archivo Markdown."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def save_markdown(content: str, path: str) -> None:
    """Guarda contenido en un archivo Markdown."""
    ensure_directory(str(Path(path).parent))
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Obtiene una variable de entorno."""
    return os.getenv(key, default)


def require_env(key: str) -> str:
    """Obtiene una variable de entorno requerida."""
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Variable de entorno requerida: {key}")
    return value


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Trunca texto a una longitud maxima."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def slugify(text: str) -> str:
    """Convierte texto a slug (kebab-case)."""
    import re
    # Convertir a minusculas
    text = text.lower()
    # Reemplazar espacios y caracteres especiales con guiones
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def count_tokens_estimate(text: str) -> int:
    """Estima el numero de tokens (aproximado)."""
    # Estimacion simple: ~4 caracteres por token
    return len(text) // 4


def format_file_size(size_bytes: int) -> str:
    """Formatea un tamano de archivo."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def get_file_extension(path: str) -> str:
    """Obtiene la extension de un archivo."""
    return Path(path).suffix.lower()


def is_binary_file(path: str) -> bool:
    """Determina si un archivo es binario."""
    binary_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.pdf',
                        '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                        '.zip', '.tar', '.gz', '.exe', '.dll', '.so',
                        '.mp3', '.mp4', '.wav', '.avi', '.mov'}
    return get_file_extension(path) in binary_extensions


def list_files(directory: str, pattern: str = "*") -> List[Path]:
    """Lista archivos en un directorio."""
    return list(Path(directory).glob(pattern))


def read_file_safe(path: str) -> Optional[str]:
    """Lee un archivo de forma segura."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return None


class NXTContext:
    """Contexto del proyecto NXT."""

    def __init__(self):
        self.root = get_project_root()
        self.config = load_config()
        self.version = get_version()

    @property
    def docs_dir(self) -> Path:
        return self.root / "docs"

    @property
    def agents_dir(self) -> Path:
        # Intentar nueva estructura primero
        if (self.root / "agentes").exists():
            return self.root / "agentes"
        return self.root / "nxt" / "method" / "agents"

    @property
    def skills_dir(self) -> Path:
        if (self.root / "skills").exists():
            return self.root / "skills"
        return self.root / "nxt" / "skills"

    @property
    def tools_dir(self) -> Path:
        if (self.root / "herramientas").exists():
            return self.root / "herramientas"
        return self.root / "tools"

    def get_agent(self, name: str) -> Optional[str]:
        """Carga el contenido de un agente."""
        # Buscar en agentes/
        agent_path = self.agents_dir / f"{name}.md"
        if agent_path.exists():
            return load_markdown(str(agent_path))

        # Buscar con prefijo nxt-
        agent_path = self.agents_dir / f"nxt-{name}.md"
        if agent_path.exists():
            return load_markdown(str(agent_path))

        return None

    def get_skill(self, name: str) -> Optional[str]:
        """Carga el contenido de un skill."""
        # Buscar en subdirectorios
        for subdir in self.skills_dir.iterdir():
            if subdir.is_dir():
                skill_path = subdir / f"SKILL-{name}.md"
                if skill_path.exists():
                    return load_markdown(str(skill_path))

                skill_path = subdir / "SKILL.md"
                if skill_path.exists() and name in subdir.name:
                    return load_markdown(str(skill_path))

        return None


# Instancia global del contexto
_context: Optional[NXTContext] = None


def get_context() -> NXTContext:
    """Obtiene el contexto global del proyecto."""
    global _context
    if _context is None:
        _context = NXTContext()
    return _context


def print_welcome():
    """Imprime el mensaje de bienvenida."""
    print(get_welcome_message())


if __name__ == "__main__":
    # Test de utilidades
    print(f"Raiz del proyecto: {get_project_root()}")
    print(f"Version: {get_version()}")
    print(f"Config: {json.dumps(load_config(), indent=2, default=str)[:500]}...")
