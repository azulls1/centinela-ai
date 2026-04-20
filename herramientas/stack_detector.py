#!/usr/bin/env python3
"""
NXT Stack Detector - Detección Inteligente de Stack Tecnológico
Basado en: BMAD v6 Alpha - Context-Aware Stack Detection

Detecta automáticamente el stack tecnológico de un proyecto
analizando archivos de configuración, dependencias y estructura.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class StackInfo:
    """Información detectada del stack"""
    languages: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    databases: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    cloud: List[str] = field(default_factory=list)
    testing: List[str] = field(default_factory=list)
    ci_cd: List[str] = field(default_factory=list)
    project_type: str = "unknown"
    is_monorepo: bool = False
    is_brownfield: bool = False
    confidence: float = 0.0


class StackDetector:
    """Detector inteligente de stack tecnológico"""

    # Patrones de detección
    LANGUAGE_PATTERNS = {
        "typescript": ["tsconfig.json", "*.ts", "*.tsx"],
        "javascript": ["*.js", "*.jsx", "*.mjs"],
        "python": ["*.py", "requirements.txt", "pyproject.toml", "setup.py"],
        "go": ["go.mod", "go.sum", "*.go"],
        "rust": ["Cargo.toml", "*.rs"],
        "java": ["pom.xml", "build.gradle", "*.java"],
        "kotlin": ["*.kt", "*.kts"],
        "swift": ["*.swift", "Package.swift"],
        "ruby": ["Gemfile", "*.rb"],
        "php": ["composer.json", "*.php"],
        "csharp": ["*.cs", "*.csproj"],
    }

    FRAMEWORK_PATTERNS = {
        # Frontend
        "next.js": ["next.config.js", "next.config.mjs", "next.config.ts"],
        "react": ["react", "react-dom"],  # Package deps
        "vue": ["vue.config.js", "nuxt.config.js", "vite.config.ts"],
        "angular": ["angular.json", "@angular/core"],
        "svelte": ["svelte.config.js", "svelte"],
        "astro": ["astro.config.mjs", "astro"],

        # Backend
        "express": ["express"],
        "fastify": ["fastify"],
        "nestjs": ["@nestjs/core"],
        "fastapi": ["fastapi"],
        "django": ["django"],
        "flask": ["flask"],
        "rails": ["rails"],
        "spring": ["spring-boot"],
        "gin": ["gin-gonic"],

        # Mobile
        "react-native": ["react-native"],
        "flutter": ["pubspec.yaml"],
        "expo": ["expo"],
    }

    DATABASE_PATTERNS = {
        "postgresql": ["pg", "postgres", "prisma"],
        "mysql": ["mysql", "mysql2"],
        "mongodb": ["mongodb", "mongoose"],
        "redis": ["redis", "ioredis"],
        "sqlite": ["sqlite", "better-sqlite3"],
        "supabase": ["@supabase/supabase-js"],
        "firebase": ["firebase"],
        "prisma": ["@prisma/client"],
        "drizzle": ["drizzle-orm"],
    }

    TOOL_PATTERNS = {
        "docker": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
        "kubernetes": ["*.yaml:kind: Deployment", "k8s/", "kubernetes/"],
        "terraform": ["*.tf", "terraform/"],
        "eslint": [".eslintrc", ".eslintrc.js", ".eslintrc.json", "eslint.config.js"],
        "prettier": [".prettierrc", "prettier.config.js"],
        "tailwind": ["tailwind.config.js", "tailwind.config.ts"],
        "webpack": ["webpack.config.js"],
        "vite": ["vite.config.ts", "vite.config.js"],
        "turbo": ["turbo.json"],
    }

    TESTING_PATTERNS = {
        "jest": ["jest.config.js", "jest.config.ts", "jest"],
        "vitest": ["vitest.config.ts", "vitest"],
        "playwright": ["playwright.config.ts", "@playwright/test"],
        "cypress": ["cypress.config.js", "cypress"],
        "pytest": ["pytest.ini", "conftest.py", "pytest"],
        "mocha": ["mocha", ".mocharc"],
        "rspec": ["spec/", "rspec"],
    }

    CI_CD_PATTERNS = {
        "github-actions": [".github/workflows/"],
        "gitlab-ci": [".gitlab-ci.yml"],
        "jenkins": ["Jenkinsfile"],
        "circleci": [".circleci/config.yml"],
        "azure-pipelines": ["azure-pipelines.yml"],
        "vercel": ["vercel.json"],
        "netlify": ["netlify.toml"],
    }

    CLOUD_PATTERNS = {
        "aws": ["aws-cdk", "serverless.yml", "sam.yaml"],
        "gcp": ["app.yaml", "cloudbuild.yaml"],
        "azure": ["azure-pipelines.yml", "host.json"],
        "vercel": ["vercel.json"],
        "cloudflare": ["wrangler.toml"],
        "supabase": ["supabase/"],
        "firebase": ["firebase.json"],
    }

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.stack = StackInfo()

    def detect(self) -> StackInfo:
        """Ejecuta detección completa del stack"""
        self._detect_languages()
        self._detect_frameworks()
        self._detect_databases()
        self._detect_tools()
        self._detect_testing()
        self._detect_ci_cd()
        self._detect_cloud()
        self._detect_project_type()
        self._detect_brownfield()
        self._calculate_confidence()

        return self.stack

    def _file_exists(self, pattern: str) -> bool:
        """Verifica si existe un archivo que matchea el patrón"""
        if "*" in pattern:
            # Glob pattern
            return bool(list(self.project_path.glob(pattern)))
        elif pattern.endswith("/"):
            # Directory
            return (self.project_path / pattern.rstrip("/")).is_dir()
        else:
            # Exact file
            return (self.project_path / pattern).exists()

    def _check_package_json(self, dep: str) -> bool:
        """Verifica si una dependencia existe en package.json"""
        pkg_path = self.project_path / "package.json"
        if not pkg_path.exists():
            return False

        try:
            with open(pkg_path) as f:
                pkg = json.load(f)
                deps = pkg.get("dependencies", {})
                dev_deps = pkg.get("devDependencies", {})
                return dep in deps or dep in dev_deps
        except:
            return False

    def _check_requirements(self, dep: str) -> bool:
        """Verifica si una dependencia existe en requirements.txt o pyproject.toml"""
        req_path = self.project_path / "requirements.txt"
        if req_path.exists():
            content = req_path.read_text().lower()
            return dep.lower() in content

        pyproject = self.project_path / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text().lower()
            return dep.lower() in content

        return False

    def _detect_languages(self):
        """Detecta lenguajes de programación"""
        for lang, patterns in self.LANGUAGE_PATTERNS.items():
            for pattern in patterns:
                if self._file_exists(pattern):
                    if lang not in self.stack.languages:
                        self.stack.languages.append(lang)
                    break

    def _detect_frameworks(self):
        """Detecta frameworks"""
        for framework, indicators in self.FRAMEWORK_PATTERNS.items():
            for indicator in indicators:
                if indicator.endswith(".js") or indicator.endswith(".ts") or indicator.endswith(".mjs"):
                    if self._file_exists(indicator):
                        self.stack.frameworks.append(framework)
                        break
                elif indicator.endswith(".yaml"):
                    if self._file_exists(indicator):
                        self.stack.frameworks.append(framework)
                        break
                else:
                    # Package dependency
                    if self._check_package_json(indicator) or self._check_requirements(indicator):
                        if framework not in self.stack.frameworks:
                            self.stack.frameworks.append(framework)
                        break

    def _detect_databases(self):
        """Detecta bases de datos"""
        for db, indicators in self.DATABASE_PATTERNS.items():
            for indicator in indicators:
                if self._check_package_json(indicator) or self._check_requirements(indicator):
                    if db not in self.stack.databases:
                        self.stack.databases.append(db)
                    break

    def _detect_tools(self):
        """Detecta herramientas de desarrollo"""
        for tool, patterns in self.TOOL_PATTERNS.items():
            for pattern in patterns:
                if ":" in pattern:
                    # Content pattern (file:content)
                    file_pattern, content = pattern.split(":", 1)
                    for f in self.project_path.glob(file_pattern):
                        if content in f.read_text():
                            self.stack.tools.append(tool)
                            break
                elif self._file_exists(pattern):
                    if tool not in self.stack.tools:
                        self.stack.tools.append(tool)
                    break

    def _detect_testing(self):
        """Detecta frameworks de testing"""
        for test_fw, patterns in self.TESTING_PATTERNS.items():
            for pattern in patterns:
                if pattern.endswith(".js") or pattern.endswith(".ts"):
                    if self._file_exists(pattern):
                        self.stack.testing.append(test_fw)
                        break
                elif self._file_exists(pattern):
                    if test_fw not in self.stack.testing:
                        self.stack.testing.append(test_fw)
                    break
                elif self._check_package_json(pattern) or self._check_requirements(pattern):
                    if test_fw not in self.stack.testing:
                        self.stack.testing.append(test_fw)
                    break

    def _detect_ci_cd(self):
        """Detecta CI/CD pipelines"""
        for cicd, patterns in self.CI_CD_PATTERNS.items():
            for pattern in patterns:
                if self._file_exists(pattern):
                    if cicd not in self.stack.ci_cd:
                        self.stack.ci_cd.append(cicd)
                    break

    def _detect_cloud(self):
        """Detecta servicios cloud"""
        for cloud, patterns in self.CLOUD_PATTERNS.items():
            for pattern in patterns:
                if self._file_exists(pattern) or self._check_package_json(pattern):
                    if cloud not in self.stack.cloud:
                        self.stack.cloud.append(cloud)
                    break

    def _detect_project_type(self):
        """Detecta el tipo de proyecto"""
        frameworks = self.stack.frameworks

        # Monorepo detection
        if self._file_exists("turbo.json") or self._file_exists("pnpm-workspace.yaml"):
            self.stack.is_monorepo = True
        if self._file_exists("packages/") or self._file_exists("apps/"):
            self.stack.is_monorepo = True

        # Project type
        if "next.js" in frameworks or "react" in frameworks:
            if "react-native" in frameworks or "expo" in frameworks:
                self.stack.project_type = "mobile"
            else:
                self.stack.project_type = "frontend"
        elif "express" in frameworks or "fastify" in frameworks or "nestjs" in frameworks:
            self.stack.project_type = "backend"
        elif "fastapi" in frameworks or "django" in frameworks or "flask" in frameworks:
            self.stack.project_type = "backend"
        elif "flutter" in frameworks:
            self.stack.project_type = "mobile"
        elif self.stack.databases:
            self.stack.project_type = "fullstack"
        elif "typescript" in self.stack.languages or "javascript" in self.stack.languages:
            self.stack.project_type = "library"
        elif "python" in self.stack.languages:
            self.stack.project_type = "tool"

    def _detect_brownfield(self):
        """Detecta si es un proyecto existente (brownfield)"""
        # Check git history
        git_dir = self.project_path / ".git"
        if git_dir.exists():
            try:
                objects_dir = git_dir / "objects"
                if objects_dir.exists():
                    # Count objects as proxy for history
                    obj_count = sum(1 for _ in objects_dir.glob("**/*") if _.is_file())
                    if obj_count > 50:  # Arbitrary threshold
                        self.stack.is_brownfield = True
            except:
                pass

        # Check for existing source files
        src_patterns = ["src/", "lib/", "app/", "pages/"]
        for pattern in src_patterns:
            if self._file_exists(pattern):
                dir_path = self.project_path / pattern.rstrip("/")
                if dir_path.is_dir():
                    file_count = sum(1 for _ in dir_path.rglob("*") if _.is_file())
                    if file_count > 10:
                        self.stack.is_brownfield = True
                        break

    def _calculate_confidence(self):
        """Calcula nivel de confianza de la detección"""
        total_detections = (
            len(self.stack.languages) +
            len(self.stack.frameworks) +
            len(self.stack.databases) +
            len(self.stack.tools) +
            len(self.stack.testing) +
            len(self.stack.ci_cd) +
            len(self.stack.cloud)
        )

        # More detections = higher confidence
        if total_detections >= 10:
            self.stack.confidence = 0.95
        elif total_detections >= 7:
            self.stack.confidence = 0.85
        elif total_detections >= 4:
            self.stack.confidence = 0.70
        elif total_detections >= 2:
            self.stack.confidence = 0.50
        else:
            self.stack.confidence = 0.30

    def to_dict(self) -> Dict:
        """Convierte a diccionario"""
        return {
            "languages": self.stack.languages,
            "frameworks": self.stack.frameworks,
            "databases": self.stack.databases,
            "tools": self.stack.tools,
            "testing": self.stack.testing,
            "ci_cd": self.stack.ci_cd,
            "cloud": self.stack.cloud,
            "project_type": self.stack.project_type,
            "is_monorepo": self.stack.is_monorepo,
            "is_brownfield": self.stack.is_brownfield,
            "confidence": self.stack.confidence,
        }

    def to_markdown(self) -> str:
        """Genera reporte en markdown"""
        lines = [
            "# Stack Detection Report",
            "",
            f"**Project Type:** {self.stack.project_type}",
            f"**Monorepo:** {'Yes' if self.stack.is_monorepo else 'No'}",
            f"**Brownfield:** {'Yes' if self.stack.is_brownfield else 'No'}",
            f"**Confidence:** {self.stack.confidence * 100:.0f}%",
            "",
        ]

        if self.stack.languages:
            lines.extend([
                "## Languages",
                ", ".join(self.stack.languages),
                "",
            ])

        if self.stack.frameworks:
            lines.extend([
                "## Frameworks",
                ", ".join(self.stack.frameworks),
                "",
            ])

        if self.stack.databases:
            lines.extend([
                "## Databases",
                ", ".join(self.stack.databases),
                "",
            ])

        if self.stack.tools:
            lines.extend([
                "## Tools",
                ", ".join(self.stack.tools),
                "",
            ])

        if self.stack.testing:
            lines.extend([
                "## Testing",
                ", ".join(self.stack.testing),
                "",
            ])

        if self.stack.ci_cd:
            lines.extend([
                "## CI/CD",
                ", ".join(self.stack.ci_cd),
                "",
            ])

        if self.stack.cloud:
            lines.extend([
                "## Cloud",
                ", ".join(self.stack.cloud),
                "",
            ])

        return "\n".join(lines)

    def suggest_agents(self) -> List[str]:
        """Sugiere agentes NXT basados en el stack detectado"""
        agents = ["nxt-orchestrator"]

        # Based on project type
        if self.stack.project_type == "frontend":
            agents.extend(["nxt-design"])
        elif self.stack.project_type == "backend":
            agents.extend(["nxt-api", "nxt-database"])
        elif self.stack.project_type == "fullstack":
            agents.extend(["nxt-dev", "nxt-api", "nxt-design", "nxt-database"])
        elif self.stack.project_type == "mobile":
            agents.extend(["nxt-mobile", "nxt-ux"])

        # Based on tools
        if "docker" in self.stack.tools or "kubernetes" in self.stack.tools:
            agents.append("nxt-devops")
        if "terraform" in self.stack.tools:
            agents.append("nxt-infra")

        # Based on CI/CD
        if self.stack.ci_cd:
            agents.append("nxt-devops")

        # Testing
        if self.stack.testing:
            agents.append("nxt-qa")

        # Always useful
        agents.extend(["nxt-docs", "nxt-cybersec"])

        # Remove duplicates while preserving order
        seen = set()
        unique_agents = []
        for agent in agents:
            if agent not in seen:
                seen.add(agent)
                unique_agents.append(agent)

        return unique_agents


def main():
    """CLI para stack detection"""
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "."
    output = sys.argv[2] if len(sys.argv) > 2 else "text"

    detector = StackDetector(path)
    stack = detector.detect()

    if output == "json":
        print(json.dumps(detector.to_dict(), indent=2))
    elif output == "markdown":
        print(detector.to_markdown())
    else:
        print("=" * 50)
        print("NXT STACK DETECTOR")
        print("=" * 50)
        print(f"\nProject: {detector.project_path}")
        print(f"Type: {stack.project_type}")
        print(f"Monorepo: {stack.is_monorepo}")
        print(f"Brownfield: {stack.is_brownfield}")
        print(f"Confidence: {stack.confidence * 100:.0f}%")
        print(f"\nLanguages: {', '.join(stack.languages) or 'None detected'}")
        print(f"Frameworks: {', '.join(stack.frameworks) or 'None detected'}")
        print(f"Databases: {', '.join(stack.databases) or 'None detected'}")
        print(f"Tools: {', '.join(stack.tools) or 'None detected'}")
        print(f"Testing: {', '.join(stack.testing) or 'None detected'}")
        print(f"CI/CD: {', '.join(stack.ci_cd) or 'None detected'}")
        print(f"Cloud: {', '.join(stack.cloud) or 'None detected'}")
        print(f"\nSuggested Agents: {', '.join(detector.suggest_agents())}")


if __name__ == "__main__":
    main()
