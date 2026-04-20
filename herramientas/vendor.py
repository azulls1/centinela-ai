#!/usr/bin/env python3
"""
NXT Workflow Vendoring Tool v3.8.0

Crea bundles standalone de workflows para distribución.

Uso:
    python vendor.py analyze <workflow>
    python vendor.py create <workflow> <output-dir>
    python vendor.py validate <bundle-path>
    python vendor.py install <bundle-path>
    python vendor.py list
"""

import argparse
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class BundleDependencies:
    """Dependencias detectadas de un workflow."""
    agents: Set[str] = field(default_factory=set)
    skills: Set[str] = field(default_factory=set)
    templates: Set[str] = field(default_factory=set)
    workflows: Set[str] = field(default_factory=set)
    config_keys: Set[str] = field(default_factory=set)


@dataclass
class BundleManifest:
    """Manifest de un bundle."""
    name: str
    version: str
    workflow: str
    framework_version: str
    created: str
    author: str
    description: str
    dependencies: Dict[str, List[str]]
    requirements: Dict[str, str]
    entry_point: str
    config: Dict[str, str]


class WorkflowVendor:
    """Herramienta para crear bundles de workflows."""

    # Patrones para detectar dependencias
    AGENT_PATTERNS = [
        r'/nxt/(\w+)',
        r'nxt-(\w+)\.md',
        r'agentes/nxt-(\w+)',
        r'@nxt-(\w+)',
    ]

    SKILL_PATTERNS = [
        r'SKILL-(\w+)',
        r'skills/\w+/SKILL-(\w+)',
        r'\*(\w+)',  # Comandos de skill
    ]

    TEMPLATE_PATTERNS = [
        r'plantillas/\w+/(\w+\.md)',
        r'templates/(\w+\.md)',
    ]

    def __init__(self, project_root: Optional[Path] = None):
        """Inicializa el vendor con la raíz del proyecto."""
        self.project_root = project_root or Path.cwd()
        self.agents_dir = self.project_root / "agentes"
        self.skills_dir = self.project_root / "skills"
        self.templates_dir = self.project_root / "plantillas"
        self.workflows_dir = self.project_root / "workflows"
        self.bundles_dir = self.project_root / "bundles"
        self.framework_version = self._get_framework_version()

    def _get_framework_version(self) -> str:
        """Obtiene la versión del framework."""
        version_file = self.project_root / ".nxt" / "version.txt"
        if version_file.exists():
            return version_file.read_text().strip()
        return "3.8.0"

    def analyze(self, workflow_path: str) -> BundleDependencies:
        """Analiza un workflow y detecta sus dependencias."""
        path = self._resolve_workflow_path(workflow_path)

        if not path.exists():
            raise FileNotFoundError(f"Workflow no encontrado: {workflow_path}")

        content = path.read_text(encoding='utf-8')
        deps = BundleDependencies()

        # Detectar agentes
        for pattern in self.AGENT_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                agent_name = f"nxt-{match.lower()}"
                if self._agent_exists(agent_name):
                    deps.agents.add(agent_name)

        # Detectar skills
        for pattern in self.SKILL_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                skill_name = f"SKILL-{match.lower()}"
                if self._skill_exists(skill_name):
                    deps.skills.add(skill_name)

        # Detectar templates
        for pattern in self.TEMPLATE_PATTERNS:
            matches = re.findall(pattern, content)
            for match in matches:
                if self._template_exists(match):
                    deps.templates.add(match)

        # Detectar referencias a configuración
        config_patterns = [
            r'escala\.(\w+)',
            r'config\.(\w+)',
            r'nxt\.config\.(\w+)',
        ]
        for pattern in config_patterns:
            matches = re.findall(pattern, content)
            deps.config_keys.update(matches)

        return deps

    def _resolve_workflow_path(self, workflow_path: str) -> Path:
        """Resuelve la ruta de un workflow."""
        path = Path(workflow_path)

        # Si es ruta absoluta
        if path.is_absolute():
            return path

        # Si es ruta relativa desde el proyecto
        full_path = self.project_root / path
        if full_path.exists():
            return full_path

        # Buscar en workflows/
        workflow_path_in_dir = self.workflows_dir / path
        if workflow_path_in_dir.exists():
            return workflow_path_in_dir

        # Buscar por nombre
        for wf in self.workflows_dir.rglob("*.md"):
            if wf.stem == path.stem or wf.name == path.name:
                return wf

        return full_path

    def _agent_exists(self, agent_name: str) -> bool:
        """Verifica si un agente existe."""
        agent_file = self.agents_dir / f"{agent_name}.md"
        return agent_file.exists()

    def _skill_exists(self, skill_name: str) -> bool:
        """Verifica si un skill existe."""
        for skill_file in self.skills_dir.rglob(f"{skill_name}.md"):
            return True
        return False

    def _template_exists(self, template_name: str) -> bool:
        """Verifica si una plantilla existe."""
        for template_file in self.templates_dir.rglob(template_name):
            return True
        return False

    def create(
        self,
        workflow_path: str,
        output_dir: str,
        include_all: bool = False,
        minimal: bool = False,
        author: str = "NXT Grupo",
        description: str = ""
    ) -> Path:
        """Crea un bundle de un workflow."""
        path = self._resolve_workflow_path(workflow_path)
        deps = self.analyze(workflow_path)

        # Nombre del bundle
        bundle_name = path.stem
        bundle_dir = Path(output_dir) / f"{bundle_name}.bundle"

        # Crear estructura
        bundle_dir.mkdir(parents=True, exist_ok=True)
        (bundle_dir / "agents").mkdir(exist_ok=True)
        (bundle_dir / "skills").mkdir(exist_ok=True)
        (bundle_dir / "templates").mkdir(exist_ok=True)
        (bundle_dir / "config").mkdir(exist_ok=True)

        # Copiar workflow principal
        shutil.copy2(path, bundle_dir / "workflow.md")

        # Copiar agentes
        for agent in deps.agents:
            agent_file = self.agents_dir / f"{agent}.md"
            if agent_file.exists():
                shutil.copy2(agent_file, bundle_dir / "agents" / f"{agent}.md")

        # Copiar skills
        for skill in deps.skills:
            for skill_file in self.skills_dir.rglob(f"{skill}.md"):
                shutil.copy2(skill_file, bundle_dir / "skills" / skill_file.name)
                break

        # Copiar templates
        for template in deps.templates:
            for template_file in self.templates_dir.rglob(template):
                shutil.copy2(template_file, bundle_dir / "templates" / template_file.name)
                break

        # Crear config defaults
        defaults = {
            "framework_version": self.framework_version,
            "config_keys": list(deps.config_keys),
        }
        (bundle_dir / "config" / "defaults.yaml").write_text(
            self._dict_to_yaml(defaults),
            encoding='utf-8'
        )

        # Crear manifest
        manifest = {
            "$schema": "https://nxt.dev/schemas/bundle-v1.json",
            "name": f"{bundle_name}-bundle",
            "version": "1.0.0",
            "workflow": bundle_name,
            "framework_version": self.framework_version,
            "created": datetime.now().isoformat(),
            "author": author,
            "description": description or f"Bundle para workflow {bundle_name}",
            "dependencies": {
                "agents": list(deps.agents),
                "skills": list(deps.skills),
                "templates": list(deps.templates),
            },
            "requirements": {
                "claude_code": ">=1.0.0",
                "features": ["slash_commands"],
            },
            "entry_point": "workflow.md",
            "config": {
                "defaults": "config/defaults.yaml",
                "overridable": ["empresa.nombre", "desarrollador.nombre"],
            },
        }
        (bundle_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

        # Crear README
        readme = self._generate_bundle_readme(bundle_name, deps, manifest)
        (bundle_dir / "README.md").write_text(readme, encoding='utf-8')

        return bundle_dir

    def _dict_to_yaml(self, data: dict, indent: int = 0) -> str:
        """Convierte un dict simple a YAML."""
        lines = []
        prefix = "  " * indent
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(self._dict_to_yaml(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}:")
                for item in value:
                    lines.append(f"{prefix}  - {item}")
            else:
                lines.append(f"{prefix}{key}: {value}")
        return "\n".join(lines)

    def _generate_bundle_readme(
        self,
        name: str,
        deps: BundleDependencies,
        manifest: dict
    ) -> str:
        """Genera README para el bundle."""
        return f"""# Bundle: {name}

> Generado por NXT Workflow Vendoring v{self.framework_version}
> Fecha: {manifest['created']}

## Descripción

{manifest['description']}

## Contenido

### Workflow Principal
- `workflow.md`

### Agentes Incluidos ({len(deps.agents)})
{chr(10).join(f'- {a}' for a in deps.agents) or '- Ninguno'}

### Skills Incluidos ({len(deps.skills)})
{chr(10).join(f'- {s}' for s in deps.skills) or '- Ninguno'}

### Templates Incluidos ({len(deps.templates)})
{chr(10).join(f'- {t}' for t in deps.templates) or '- Ninguno'}

## Instalación

```bash
# Copiar a tu proyecto
cp -r {name}.bundle/ /tu/proyecto/bundles/

# O usar el CLI de NXT
python herramientas/vendor.py install ./{name}.bundle/
```

## Uso

1. Asegúrate de tener NXT Framework >= {self.framework_version}
2. Instala el bundle en tu proyecto
3. Ejecuta el workflow: `*{name}`

## Requisitos

- Claude Code >= 1.0.0
- NXT Framework >= {self.framework_version}

---

*Bundle generado con NXT Workflow Vendoring*
"""

    def validate(self, bundle_path: str) -> Dict[str, any]:
        """Valida un bundle."""
        path = Path(bundle_path)
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "info": {},
        }

        # Verificar estructura
        required_files = ["manifest.json", "workflow.md", "README.md"]
        required_dirs = ["agents", "skills", "templates", "config"]

        for f in required_files:
            if not (path / f).exists():
                results["errors"].append(f"Archivo requerido faltante: {f}")
                results["valid"] = False

        for d in required_dirs:
            if not (path / d).is_dir():
                results["warnings"].append(f"Directorio faltante: {d}")

        # Verificar manifest
        manifest_path = path / "manifest.json"
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
                results["info"]["name"] = manifest.get("name", "unknown")
                results["info"]["version"] = manifest.get("version", "unknown")
                results["info"]["framework_version"] = manifest.get("framework_version", "unknown")

                # Verificar dependencias
                deps = manifest.get("dependencies", {})
                for agent in deps.get("agents", []):
                    agent_file = path / "agents" / f"{agent}.md"
                    if not agent_file.exists():
                        results["errors"].append(f"Agente declarado pero no incluido: {agent}")
                        results["valid"] = False

            except json.JSONDecodeError as e:
                results["errors"].append(f"Manifest JSON inválido: {e}")
                results["valid"] = False

        # Calcular tamaño
        total_size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
        results["info"]["size_kb"] = round(total_size / 1024, 2)

        if total_size > 500 * 1024:  # 500KB
            results["warnings"].append(f"Bundle grande: {results['info']['size_kb']}KB (recomendado < 500KB)")

        return results

    def install(self, bundle_path: str, target_dir: Optional[str] = None) -> bool:
        """Instala un bundle en el proyecto."""
        path = Path(bundle_path)

        # Validar primero
        validation = self.validate(bundle_path)
        if not validation["valid"]:
            print("❌ Bundle inválido:")
            for error in validation["errors"]:
                print(f"   - {error}")
            return False

        # Directorio destino
        target = Path(target_dir) if target_dir else self.project_root

        # Copiar agentes
        agents_src = path / "agents"
        if agents_src.exists():
            for agent in agents_src.glob("*.md"):
                dest = target / "agentes" / agent.name
                if not dest.exists():
                    shutil.copy2(agent, dest)
                    print(f"✓ Instalado agente: {agent.name}")

        # Copiar skills
        skills_src = path / "skills"
        if skills_src.exists():
            for skill in skills_src.glob("*.md"):
                # Detectar categoría
                dest_dir = target / "skills" / "custom"
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest = dest_dir / skill.name
                if not dest.exists():
                    shutil.copy2(skill, dest)
                    print(f"✓ Instalado skill: {skill.name}")

        # Copiar workflow
        workflow_src = path / "workflow.md"
        if workflow_src.exists():
            manifest = json.loads((path / "manifest.json").read_text(encoding='utf-8'))
            workflow_name = manifest.get("workflow", path.stem)
            dest = target / "workflows" / "bundles" / f"{workflow_name}.md"
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(workflow_src, dest)
            print(f"✓ Instalado workflow: {workflow_name}.md")

        print(f"\n✅ Bundle instalado correctamente")
        return True

    def list_bundles(self) -> List[Dict[str, str]]:
        """Lista bundles instalados."""
        bundles = []

        if not self.bundles_dir.exists():
            return bundles

        for bundle_dir in self.bundles_dir.iterdir():
            if bundle_dir.is_dir() and bundle_dir.suffix == ".bundle":
                manifest_path = bundle_dir / "manifest.json"
                if manifest_path.exists():
                    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
                    bundles.append({
                        "name": manifest.get("name", bundle_dir.stem),
                        "version": manifest.get("version", "unknown"),
                        "path": str(bundle_dir),
                    })

        return bundles


def print_analysis(deps: BundleDependencies, workflow_name: str):
    """Imprime análisis de dependencias."""
    print(f"\n📦 Análisis de Dependencias: {workflow_name}\n")

    print(f"Agentes ({len(deps.agents)}):")
    for agent in deps.agents:
        print(f"  ✓ {agent}")
    if not deps.agents:
        print("  - Ninguno detectado")

    print(f"\nSkills ({len(deps.skills)}):")
    for skill in deps.skills:
        print(f"  ✓ {skill}")
    if not deps.skills:
        print("  - Ninguno detectado")

    print(f"\nTemplates ({len(deps.templates)}):")
    for template in deps.templates:
        print(f"  ✓ {template}")
    if not deps.templates:
        print("  - Ninguno detectado")

    print(f"\nConfig keys ({len(deps.config_keys)}):")
    for key in deps.config_keys:
        print(f"  ✓ {key}")
    if not deps.config_keys:
        print("  - Ninguno detectado")

    total = len(deps.agents) + len(deps.skills) + len(deps.templates)
    print(f"\n✅ Total dependencias: {total}")


def print_validation(results: Dict[str, any]):
    """Imprime resultados de validación."""
    status = "✅ VÁLIDO" if results["valid"] else "❌ INVÁLIDO"
    print(f"\n📦 Validación de Bundle: {status}\n")

    if results["info"]:
        print("Información:")
        for key, value in results["info"].items():
            print(f"  {key}: {value}")

    if results["errors"]:
        print("\nErrores:")
        for error in results["errors"]:
            print(f"  ❌ {error}")

    if results["warnings"]:
        print("\nAdvertencias:")
        for warning in results["warnings"]:
            print(f"  ⚠️  {warning}")


def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="NXT Workflow Vendoring Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python vendor.py analyze workflows/create-prd.md
  python vendor.py create workflows/create-prd.md ./bundles/
  python vendor.py validate ./bundles/create-prd.bundle/
  python vendor.py install ./bundles/create-prd.bundle/
  python vendor.py list
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")

    # Analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analizar dependencias")
    analyze_parser.add_argument("workflow", help="Ruta al workflow")

    # Create
    create_parser = subparsers.add_parser("create", help="Crear bundle")
    create_parser.add_argument("workflow", help="Ruta al workflow")
    create_parser.add_argument("output", help="Directorio de salida")
    create_parser.add_argument("--author", default="NXT Grupo", help="Autor del bundle")
    create_parser.add_argument("--description", default="", help="Descripción")
    create_parser.add_argument("--include-all", action="store_true", help="Incluir todo")
    create_parser.add_argument("--minimal", action="store_true", help="Solo esencial")

    # Validate
    validate_parser = subparsers.add_parser("validate", help="Validar bundle")
    validate_parser.add_argument("bundle", help="Ruta al bundle")

    # Install
    install_parser = subparsers.add_parser("install", help="Instalar bundle")
    install_parser.add_argument("bundle", help="Ruta al bundle")
    install_parser.add_argument("--target", help="Directorio destino")

    # List
    subparsers.add_parser("list", help="Listar bundles instalados")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    vendor = WorkflowVendor()

    try:
        if args.command == "analyze":
            deps = vendor.analyze(args.workflow)
            print_analysis(deps, args.workflow)

        elif args.command == "create":
            bundle_path = vendor.create(
                args.workflow,
                args.output,
                include_all=args.include_all,
                minimal=args.minimal,
                author=args.author,
                description=args.description,
            )
            print(f"\n✅ Bundle creado: {bundle_path}")

        elif args.command == "validate":
            results = vendor.validate(args.bundle)
            print_validation(results)

        elif args.command == "install":
            success = vendor.install(args.bundle, args.target)
            if not success:
                sys.exit(1)

        elif args.command == "list":
            bundles = vendor.list_bundles()
            if bundles:
                print("\n📦 Bundles Instalados:\n")
                for bundle in bundles:
                    print(f"  {bundle['name']} v{bundle['version']}")
                    print(f"    {bundle['path']}")
            else:
                print("\nNo hay bundles instalados.")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
