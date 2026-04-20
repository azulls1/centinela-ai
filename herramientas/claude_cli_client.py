#!/usr/bin/env python3
"""
NXT AI Development - Claude CLI Client
=======================================
Cliente para invocar Claude CLI desde Python usando subprocess.

Permite ejecutar agentes NXT de forma programática aprovechando
la sesión de Claude Pro Max sin necesidad de API keys.

Características:
- Invocación via subprocess (sin API key)
- Output JSON para parsing estructurado
- Soporte para herramientas específicas
- Control de iteraciones (max-turns)
- Manejo de sesiones para contexto persistente
- Retry con backoff exponencial
- Logging estructurado

Versión: 3.8.0
"""

import subprocess
import json
import time
import logging
import threading
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import shutil

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("claude_cli_client")


class ClaudeOutputFormat(Enum):
    """Formatos de output soportados por Claude CLI."""
    TEXT = "text"
    JSON = "json"
    STREAM_JSON = "stream-json"


class InvocationStatus(Enum):
    """Estado de una invocación."""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ClaudeResponse:
    """Respuesta de una invocación a Claude CLI."""
    status: InvocationStatus
    response: str
    session_id: Optional[str] = None
    raw_output: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    tokens_used: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario."""
        return {
            "status": self.status.value,
            "response": self.response,
            "session_id": self.session_id,
            "error": self.error,
            "execution_time": self.execution_time,
            "tokens_used": self.tokens_used,
            "metadata": self.metadata
        }


@dataclass
class AgentConfig:
    """Configuración para un agente."""
    name: str
    prompt_file: Optional[str] = None
    system_prompt: Optional[str] = None
    allowed_tools: List[str] = field(default_factory=lambda: ["Read", "Edit", "Write", "Bash", "Glob", "Grep"])
    max_turns: int = 25
    timeout: int = 300  # 5 minutos


class ClaudeCLIClient:
    """
    Cliente para invocar Claude CLI desde Python.

    Usa subprocess para ejecutar Claude CLI aprovechando la sesión
    de Pro Max sin necesidad de API key.

    Ejemplo de uso:
        client = ClaudeCLIClient()
        response = client.invoke("Analiza este código y sugiere mejoras")
        print(response.response)
    """

    def __init__(
        self,
        working_dir: Optional[Path] = None,
        default_timeout: int = 300,
        default_max_turns: int = 25,
        default_tools: Optional[List[str]] = None
    ):
        """
        Inicializa el cliente.

        Args:
            working_dir: Directorio de trabajo para Claude CLI
            default_timeout: Timeout por defecto en segundos
            default_max_turns: Máximo de turnos por defecto
            default_tools: Herramientas permitidas por defecto
        """
        self.working_dir = working_dir or Path.cwd()
        self.default_timeout = default_timeout
        self.default_max_turns = default_max_turns
        self.default_tools = default_tools or ["Read", "Edit", "Write", "Bash", "Glob", "Grep"]

        # Verificar que Claude CLI está disponible
        self._verify_claude_cli()

        # Cache de sesiones
        self._sessions: Dict[str, str] = {}
        self._lock = threading.Lock()

        # Métricas
        self.total_invocations = 0
        self.successful_invocations = 0
        self.failed_invocations = 0
        self.total_execution_time = 0.0

    def _verify_claude_cli(self) -> bool:
        """Verifica que Claude CLI está instalado y disponible."""
        claude_path = shutil.which("claude")
        if not claude_path:
            logger.warning("Claude CLI no encontrado en PATH. Intentando con 'claude.cmd' para Windows...")
            claude_path = shutil.which("claude.cmd")

        if not claude_path:
            raise RuntimeError(
                "Claude CLI no está instalado o no está en PATH. "
                "Instálalo con: npm install -g @anthropic-ai/claude-code"
            )

        logger.info(f"Claude CLI encontrado en: {claude_path}")
        return True

    def _get_claude_command(self) -> str:
        """Obtiene el comando de Claude CLI según el sistema operativo."""
        # En Windows puede ser 'claude' o 'claude.cmd'
        claude_path = shutil.which("claude") or shutil.which("claude.cmd")
        return claude_path or "claude"

    def invoke(
        self,
        prompt: str,
        output_format: ClaudeOutputFormat = ClaudeOutputFormat.JSON,
        allowed_tools: Optional[List[str]] = None,
        max_turns: Optional[int] = None,
        timeout: Optional[int] = None,
        session_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        append_system_prompt: Optional[str] = None,
        working_dir: Optional[Path] = None
    ) -> ClaudeResponse:
        """
        Invoca Claude CLI con un prompt.

        Args:
            prompt: El prompt a enviar a Claude
            output_format: Formato de output (text, json, stream-json)
            allowed_tools: Lista de herramientas permitidas
            max_turns: Número máximo de turnos del agente
            timeout: Timeout en segundos
            session_id: ID de sesión para continuar conversación
            system_prompt: System prompt personalizado (reemplaza el default)
            append_system_prompt: System prompt adicional (se añade al default)
            working_dir: Directorio de trabajo específico

        Returns:
            ClaudeResponse con el resultado
        """
        start_time = time.time()
        self.total_invocations += 1

        # Construir comando
        cmd = self._build_command(
            prompt=prompt,
            output_format=output_format,
            allowed_tools=allowed_tools or self.default_tools,
            max_turns=max_turns or self.default_max_turns,
            session_id=session_id,
            system_prompt=system_prompt,
            append_system_prompt=append_system_prompt
        )

        logger.debug(f"Ejecutando comando: {' '.join(cmd)}")

        try:
            # Ejecutar Claude CLI
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout or self.default_timeout,
                cwd=str(working_dir or self.working_dir),
                encoding='utf-8',
                errors='replace'
            )

            execution_time = time.time() - start_time
            self.total_execution_time += execution_time

            # Procesar resultado
            if result.returncode == 0:
                self.successful_invocations += 1
                return self._parse_response(
                    result.stdout,
                    output_format,
                    execution_time
                )
            else:
                self.failed_invocations += 1
                return ClaudeResponse(
                    status=InvocationStatus.FAILED,
                    response="",
                    error=result.stderr or f"Exit code: {result.returncode}",
                    execution_time=execution_time,
                    raw_output=result.stdout
                )

        except subprocess.TimeoutExpired:
            self.failed_invocations += 1
            execution_time = time.time() - start_time
            return ClaudeResponse(
                status=InvocationStatus.TIMEOUT,
                response="",
                error=f"Timeout después de {timeout or self.default_timeout} segundos",
                execution_time=execution_time
            )

        except Exception as e:
            self.failed_invocations += 1
            execution_time = time.time() - start_time
            return ClaudeResponse(
                status=InvocationStatus.FAILED,
                response="",
                error=str(e),
                execution_time=execution_time
            )

    def _build_command(
        self,
        prompt: str,
        output_format: ClaudeOutputFormat,
        allowed_tools: List[str],
        max_turns: int,
        session_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        append_system_prompt: Optional[str] = None
    ) -> List[str]:
        """Construye el comando CLI."""
        claude_cmd = self._get_claude_command()

        cmd = [
            claude_cmd,
            "-p", prompt,  # Modo no interactivo con prompt
            "--output-format", output_format.value,
            "--max-turns", str(max_turns),
        ]

        # Herramientas permitidas
        if allowed_tools:
            cmd.extend(["--allowedTools", ",".join(allowed_tools)])

        # Sesión existente
        if session_id:
            cmd.extend(["--resume", session_id])

        # System prompt
        if system_prompt:
            cmd.extend(["--system-prompt", system_prompt])
        elif append_system_prompt:
            cmd.extend(["--append-system-prompt", append_system_prompt])

        return cmd

    def _parse_response(
        self,
        output: str,
        output_format: ClaudeOutputFormat,
        execution_time: float
    ) -> ClaudeResponse:
        """Parsea la respuesta de Claude CLI."""

        if output_format == ClaudeOutputFormat.JSON:
            try:
                # Intentar parsear como JSON
                data = json.loads(output)
                return ClaudeResponse(
                    status=InvocationStatus.SUCCESS,
                    response=data.get("result", data.get("response", output)),
                    session_id=data.get("session_id"),
                    execution_time=execution_time,
                    tokens_used=data.get("tokens_used"),
                    metadata=data,
                    raw_output=output
                )
            except json.JSONDecodeError:
                # Si falla el JSON, tratar como texto
                return ClaudeResponse(
                    status=InvocationStatus.SUCCESS,
                    response=output,
                    execution_time=execution_time,
                    raw_output=output
                )
        else:
            return ClaudeResponse(
                status=InvocationStatus.SUCCESS,
                response=output,
                execution_time=execution_time,
                raw_output=output
            )

    def invoke_agent(
        self,
        agent_config: AgentConfig,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ClaudeResponse:
        """
        Invoca un agente NXT específico.

        Args:
            agent_config: Configuración del agente
            task: Tarea a ejecutar
            context: Contexto adicional

        Returns:
            ClaudeResponse con el resultado
        """
        # Construir prompt con instrucciones del agente
        prompt_parts = []

        # Cargar instrucciones del agente si existe archivo
        if agent_config.prompt_file and Path(agent_config.prompt_file).exists():
            agent_instructions = Path(agent_config.prompt_file).read_text(encoding='utf-8')
            prompt_parts.append(f"# Instrucciones del Agente {agent_config.name}\n\n{agent_instructions}\n\n")

        # Agregar contexto
        if context:
            prompt_parts.append(f"# Contexto\n\n```json\n{json.dumps(context, indent=2, ensure_ascii=False)}\n```\n\n")

        # Agregar tarea
        prompt_parts.append(f"# Tarea\n\n{task}")

        full_prompt = "\n".join(prompt_parts)

        return self.invoke(
            prompt=full_prompt,
            allowed_tools=agent_config.allowed_tools,
            max_turns=agent_config.max_turns,
            timeout=agent_config.timeout,
            system_prompt=agent_config.system_prompt
        )

    def invoke_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        **kwargs
    ) -> ClaudeResponse:
        """
        Invoca con reintentos y backoff exponencial.

        Args:
            prompt: El prompt
            max_retries: Número máximo de reintentos
            backoff_factor: Factor de backoff
            **kwargs: Argumentos adicionales para invoke()

        Returns:
            ClaudeResponse
        """
        last_response = None

        for attempt in range(max_retries + 1):
            response = self.invoke(prompt, **kwargs)

            if response.status == InvocationStatus.SUCCESS:
                return response

            last_response = response

            if attempt < max_retries:
                wait_time = backoff_factor ** attempt
                logger.warning(
                    f"Intento {attempt + 1} falló: {response.error}. "
                    f"Reintentando en {wait_time}s..."
                )
                time.sleep(wait_time)

        return last_response

    def get_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas del cliente."""
        return {
            "total_invocations": self.total_invocations,
            "successful_invocations": self.successful_invocations,
            "failed_invocations": self.failed_invocations,
            "success_rate": (
                self.successful_invocations / self.total_invocations * 100
                if self.total_invocations > 0 else 0
            ),
            "total_execution_time": round(self.total_execution_time, 2),
            "avg_execution_time": (
                round(self.total_execution_time / self.total_invocations, 2)
                if self.total_invocations > 0 else 0
            )
        }


class ClaudeCLIAgentRunner:
    """
    Runner de alto nivel para ejecutar agentes NXT via Claude CLI.

    Proporciona una interfaz simplificada para ejecutar agentes
    con configuración automática basada en los archivos .md
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Inicializa el runner.

        Args:
            project_root: Raíz del proyecto NXT
        """
        self.project_root = project_root or Path.cwd()
        self.agents_dir = self.project_root / "agentes"
        self.client = ClaudeCLIClient(working_dir=self.project_root)

        # Cache de configuraciones de agentes
        self._agent_configs: Dict[str, AgentConfig] = {}
        self._load_agent_configs()

    def _load_agent_configs(self):
        """Carga configuraciones de agentes desde archivos .md"""
        if not self.agents_dir.exists():
            logger.warning(f"Directorio de agentes no encontrado: {self.agents_dir}")
            return

        for agent_file in self.agents_dir.glob("nxt-*.md"):
            agent_name = agent_file.stem
            self._agent_configs[agent_name] = AgentConfig(
                name=agent_name,
                prompt_file=str(agent_file),
                allowed_tools=self._get_tools_for_agent(agent_name),
                max_turns=self._get_max_turns_for_agent(agent_name)
            )

        logger.info(f"Cargados {len(self._agent_configs)} agentes")

    def _get_tools_for_agent(self, agent_name: str) -> List[str]:
        """Determina herramientas permitidas según el tipo de agente."""
        # Mapeo de agentes a herramientas
        tool_mappings = {
            "nxt-dev": ["Read", "Edit", "Write", "Bash", "Glob", "Grep"],
            "nxt-qa": ["Read", "Bash", "Glob", "Grep"],
            "nxt-architect": ["Read", "Glob", "Grep", "Write"],
            "nxt-analyst": ["Read", "Glob", "Grep", "WebSearch", "WebFetch"],
            "nxt-search": ["WebSearch", "WebFetch", "Read"],
            "nxt-devops": ["Read", "Edit", "Write", "Bash", "Glob"],
            "nxt-database": ["Read", "Edit", "Write", "Bash", "Glob"],
            "nxt-cybersec": ["Read", "Glob", "Grep", "Bash"],
        }

        return tool_mappings.get(agent_name, ["Read", "Edit", "Write", "Glob", "Grep"])

    def _get_max_turns_for_agent(self, agent_name: str) -> int:
        """Determina max_turns según el tipo de agente."""
        # Agentes que necesitan más iteraciones
        high_iteration_agents = ["nxt-dev", "nxt-qa", "nxt-devops", "nxt-ralph"]

        if agent_name in high_iteration_agents:
            return 50
        return 25

    def run_agent(
        self,
        agent_name: str,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ClaudeResponse:
        """
        Ejecuta un agente NXT.

        Args:
            agent_name: Nombre del agente (ej: "nxt-dev")
            task: Tarea a ejecutar
            context: Contexto adicional

        Returns:
            ClaudeResponse con el resultado
        """
        # Normalizar nombre
        if not agent_name.startswith("nxt-"):
            agent_name = f"nxt-{agent_name}"

        # Obtener configuración
        config = self._agent_configs.get(agent_name)
        if not config:
            logger.warning(f"Agente no encontrado: {agent_name}. Usando configuración default.")
            config = AgentConfig(name=agent_name)

        logger.info(f"Ejecutando agente: {agent_name}")
        logger.info(f"Tarea: {task[:100]}...")

        return self.client.invoke_agent(config, task, context)

    def run_agents_sequential(
        self,
        agents: List[str],
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, ClaudeResponse]]:
        """
        Ejecuta múltiples agentes secuencialmente.

        Args:
            agents: Lista de nombres de agentes
            task: Tarea común
            context: Contexto compartido

        Returns:
            Lista de tuplas (agent_name, response)
        """
        results = []
        accumulated_context = context or {}

        for agent_name in agents:
            response = self.run_agent(agent_name, task, accumulated_context)
            results.append((agent_name, response))

            # Agregar resultado al contexto para el siguiente agente
            if response.status == InvocationStatus.SUCCESS:
                accumulated_context[f"{agent_name}_result"] = response.response[:1000]

        return results

    def run_agents_parallel(
        self,
        agents: List[str],
        task: str,
        context: Optional[Dict[str, Any]] = None,
        max_workers: int = 5
    ) -> Dict[str, ClaudeResponse]:
        """
        Ejecuta múltiples agentes en paralelo.

        Args:
            agents: Lista de nombres de agentes
            task: Tarea común
            context: Contexto compartido
            max_workers: Número máximo de workers

        Returns:
            Diccionario {agent_name: response}
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results: Dict[str, ClaudeResponse] = {}

        logger.info(f"Ejecutando {len(agents)} agentes en paralelo (max_workers={max_workers})")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submeter tareas
            future_to_agent = {
                executor.submit(self.run_agent, agent, task, context): agent
                for agent in agents
            }

            # Recoger resultados
            for future in as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    response = future.result()
                    results[agent_name] = response
                    status = "OK" if response.status == InvocationStatus.SUCCESS else "FAIL"
                    logger.info(f"  [{status}] {agent_name}: {response.execution_time:.2f}s")
                except Exception as e:
                    logger.error(f"  [ERROR] {agent_name}: {e}")
                    results[agent_name] = ClaudeResponse(
                        status=InvocationStatus.FAILED,
                        response="",
                        error=str(e)
                    )

        return results

    def get_available_agents(self) -> List[str]:
        """Lista agentes disponibles."""
        return list(self._agent_configs.keys())

    def get_agent_info(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Obtiene información de un agente."""
        config = self._agent_configs.get(agent_name)
        if not config:
            return None

        return {
            "name": config.name,
            "prompt_file": config.prompt_file,
            "allowed_tools": config.allowed_tools,
            "max_turns": config.max_turns,
            "timeout": config.timeout
        }


# =============================================================================
# CLI
# =============================================================================

def main():
    """CLI del Claude CLI Client."""
    import argparse

    parser = argparse.ArgumentParser(
        description="NXT Claude CLI Client - Ejecuta agentes via Claude CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comando: invoke
    invoke_parser = subparsers.add_parser("invoke", help="Invocar Claude directamente")
    invoke_parser.add_argument("prompt", help="Prompt a enviar")
    invoke_parser.add_argument("--max-turns", type=int, default=25)
    invoke_parser.add_argument("--timeout", type=int, default=300)
    invoke_parser.add_argument("--tools", help="Herramientas permitidas (separadas por coma)")

    # Comando: agent
    agent_parser = subparsers.add_parser("agent", help="Ejecutar un agente NXT")
    agent_parser.add_argument("agent_name", help="Nombre del agente (ej: nxt-dev)")
    agent_parser.add_argument("task", help="Tarea a ejecutar")

    # Comando: parallel
    parallel_parser = subparsers.add_parser("parallel", help="Ejecutar agentes en paralelo")
    parallel_parser.add_argument("--agents", required=True, help="Agentes separados por coma")
    parallel_parser.add_argument("--task", required=True, help="Tarea común")
    parallel_parser.add_argument("--workers", type=int, default=5)

    # Comando: list
    subparsers.add_parser("list", help="Listar agentes disponibles")

    # Comando: metrics
    subparsers.add_parser("metrics", help="Ver métricas del cliente")

    # Comando: verify
    subparsers.add_parser("verify", help="Verificar instalación de Claude CLI")

    args = parser.parse_args()

    try:
        if args.command == "invoke":
            client = ClaudeCLIClient()
            tools = args.tools.split(",") if args.tools else None

            print(f"\n{'='*60}")
            print("  Invocando Claude CLI...")
            print(f"{'='*60}\n")

            response = client.invoke(
                args.prompt,
                allowed_tools=tools,
                max_turns=args.max_turns,
                timeout=args.timeout
            )

            print(f"Status: {response.status.value}")
            print(f"Tiempo: {response.execution_time:.2f}s")
            print(f"\nRespuesta:\n{'-'*40}")
            print(response.response)

        elif args.command == "agent":
            runner = ClaudeCLIAgentRunner()

            print(f"\n{'='*60}")
            print(f"  Ejecutando agente: {args.agent_name}")
            print(f"{'='*60}\n")

            response = runner.run_agent(args.agent_name, args.task)

            print(f"Status: {response.status.value}")
            print(f"Tiempo: {response.execution_time:.2f}s")
            print(f"\nRespuesta:\n{'-'*40}")
            print(response.response)

        elif args.command == "parallel":
            runner = ClaudeCLIAgentRunner()
            agents = [a.strip() for a in args.agents.split(",")]

            print(f"\n{'='*60}")
            print(f"  Ejecutando {len(agents)} agentes en paralelo")
            print(f"{'='*60}\n")

            results = runner.run_agents_parallel(
                agents, args.task, max_workers=args.workers
            )

            print(f"\n{'='*60}")
            print("  RESULTADOS")
            print(f"{'='*60}")
            for agent, response in results.items():
                status = "OK" if response.status == InvocationStatus.SUCCESS else "FAIL"
                print(f"  [{status}] {agent}: {response.execution_time:.2f}s")

        elif args.command == "list":
            runner = ClaudeCLIAgentRunner()
            agents = runner.get_available_agents()

            print(f"\n{'='*60}")
            print(f"  Agentes Disponibles ({len(agents)})")
            print(f"{'='*60}\n")

            for agent in sorted(agents):
                info = runner.get_agent_info(agent)
                tools_count = len(info["allowed_tools"]) if info else 0
                print(f"  - {agent} ({tools_count} tools, {info['max_turns'] if info else '?'} turns)")

        elif args.command == "metrics":
            client = ClaudeCLIClient()
            metrics = client.get_metrics()

            print(f"\n{'='*60}")
            print("  Métricas del Cliente")
            print(f"{'='*60}")
            print(json.dumps(metrics, indent=2))

        elif args.command == "verify":
            print(f"\n{'='*60}")
            print("  Verificando Claude CLI...")
            print(f"{'='*60}\n")

            try:
                client = ClaudeCLIClient()
                print("  Claude CLI está instalado y disponible")

                # Verificar versión
                result = subprocess.run(
                    ["claude", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    print(f"  Versión: {result.stdout.strip()}")

            except Exception as e:
                print(f"  Error: {e}")
                return 1

        else:
            parser.print_help()

    except Exception as e:
        print(f"\nError: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
