#!/usr/bin/env python3
"""
NXT AI Development - Test de Integración
=========================================
Script para validar que toda la integración Claude CLI funciona correctamente.

Ejecutar: python herramientas/test_integration.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Agregar directorio al path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(title: str):
    """Imprime un header formateado."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_result(test_name: str, passed: bool, details: str = ""):
    """Imprime resultado de un test."""
    icon = "✓" if passed else "✗"
    status = "PASS" if passed else "FAIL"
    print(f"  {icon} [{status}] {test_name}")
    if details:
        print(f"           {details}")

def test_imports():
    """Test 1: Verificar que los imports funcionan."""
    print_header("TEST 1: Imports")

    results = []

    # Test utils
    try:
        from utils import get_project_root, load_config, NXTContext
        print_result("utils.py", True)
        results.append(True)
    except Exception as e:
        print_result("utils.py", False, str(e))
        results.append(False)

    # Test claude_cli_client
    try:
        from claude_cli_client import (
            ClaudeCLIClient, ClaudeCLIAgentRunner, ClaudeResponse,
            InvocationStatus, AgentConfig, CLAUDE_CLI_AVAILABLE
        )
        print_result("claude_cli_client.py", True, f"CLAUDE_CLI_AVAILABLE={CLAUDE_CLI_AVAILABLE if 'CLAUDE_CLI_AVAILABLE' in dir() else 'N/A'}")
        results.append(True)
    except Exception as e:
        print_result("claude_cli_client.py", False, str(e))
        results.append(False)

    # Test agent_executor
    try:
        from agent_executor import (
            AgentExecutor, ParallelExecutor, CLAUDE_CLI_AVAILABLE as EXEC_CLI_AVAILABLE
        )
        print_result("agent_executor.py", True, f"CLAUDE_CLI_AVAILABLE={EXEC_CLI_AVAILABLE}")
        results.append(True)
    except Exception as e:
        print_result("agent_executor.py", False, str(e))
        results.append(False)

    # Test nxt_orchestrator_v3
    try:
        from nxt_orchestrator_v3 import (
            NXTOrchestratorV3, TaskScale, AgentRole, CLAUDE_CLI_AVAILABLE as ORCH_CLI_AVAILABLE
        )
        print_result("nxt_orchestrator_v3.py", True, f"CLAUDE_CLI_AVAILABLE={ORCH_CLI_AVAILABLE}")
        results.append(True)
    except Exception as e:
        print_result("nxt_orchestrator_v3.py", False, str(e))
        results.append(False)

    return all(results)

def test_claude_cli_availability():
    """Test 2: Verificar que Claude CLI está disponible."""
    print_header("TEST 2: Claude CLI Disponibilidad")

    import shutil
    import subprocess

    # Verificar que el comando existe
    claude_path = shutil.which("claude") or shutil.which("claude.cmd")
    if claude_path:
        print_result("Claude CLI en PATH", True, claude_path)
    else:
        print_result("Claude CLI en PATH", False, "No encontrado")
        return False

    # Verificar versión
    try:
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print_result("Claude CLI versión", True, version)
            return True
        else:
            print_result("Claude CLI versión", False, result.stderr)
            return False
    except Exception as e:
        print_result("Claude CLI versión", False, str(e))
        return False

def test_client_initialization():
    """Test 3: Verificar inicialización del cliente."""
    print_header("TEST 3: Inicialización del Cliente")

    try:
        from claude_cli_client import ClaudeCLIClient, ClaudeCLIAgentRunner
        from utils import get_project_root

        root = get_project_root()

        # Test ClaudeCLIClient
        try:
            client = ClaudeCLIClient(working_dir=root)
            print_result("ClaudeCLIClient", True)
        except Exception as e:
            print_result("ClaudeCLIClient", False, str(e))
            return False

        # Test ClaudeCLIAgentRunner
        try:
            runner = ClaudeCLIAgentRunner(root)
            agents = runner.get_available_agents()
            print_result("ClaudeCLIAgentRunner", True, f"{len(agents)} agentes cargados")
        except Exception as e:
            print_result("ClaudeCLIAgentRunner", False, str(e))
            return False

        return True

    except Exception as e:
        print_result("Inicialización", False, str(e))
        return False

def test_orchestrator_initialization():
    """Test 4: Verificar inicialización del orquestador."""
    print_header("TEST 4: Inicialización del Orquestador")

    try:
        from nxt_orchestrator_v3 import NXTOrchestratorV3

        # Inicializar orquestador
        orchestrator = NXTOrchestratorV3(use_claude_cli=True)

        print_result("Orquestador creado", True)
        print_result("Claude CLI habilitado", orchestrator.use_claude_cli,
                    f"use_claude_cli={orchestrator.use_claude_cli}")

        if orchestrator.claude_runner:
            print_result("Claude Runner inicializado", True)
        else:
            print_result("Claude Runner inicializado", False, "claude_runner es None")

        # Verificar registries
        nxt_agents = orchestrator.agents.list_nxt()
        print_result("Agentes NXT cargados", len(nxt_agents) > 0, f"{len(nxt_agents)} agentes")

        skills = orchestrator.skills.list_all()
        print_result("Skills cargados", len(skills) > 0, f"{len(skills)} skills")

        return orchestrator.use_claude_cli

    except Exception as e:
        print_result("Orquestador", False, str(e))
        return False

def test_classification():
    """Test 5: Verificar clasificación de tareas."""
    print_header("TEST 5: Clasificación de Tareas")

    try:
        from nxt_orchestrator_v3 import NXTOrchestratorV3, TaskScale

        orchestrator = NXTOrchestratorV3(use_claude_cli=False)  # Sin CLI para este test

        # Test casos de clasificación
        test_cases = [
            ("fix typo in readme", TaskScale.NIVEL_0),
            ("add validation to form", TaskScale.NIVEL_1),
            ("implement user authentication", TaskScale.NIVEL_2),
            ("refactor entire codebase", TaskScale.NIVEL_3),
        ]

        all_passed = True
        for task, expected in test_cases:
            result = orchestrator.classify(task)
            passed = result == expected
            if not passed:
                all_passed = False
            print_result(f"'{task[:30]}...'", passed, f"got {result.value}, expected {expected.value}")

        return all_passed

    except Exception as e:
        print_result("Clasificación", False, str(e))
        return False

def test_dry_run_execution():
    """Test 6: Verificar ejecución en modo dry-run."""
    print_header("TEST 6: Ejecución Dry-Run")

    try:
        from nxt_orchestrator_v3 import NXTOrchestratorV3

        orchestrator = NXTOrchestratorV3(use_claude_cli=True)

        # Ejecutar en modo dry-run (simulación)
        agents = ["nxt-analyst", "nxt-dev"]
        task = "analizar estructura del proyecto"

        print(f"  Ejecutando {len(agents)} agentes en dry-run...")

        results = orchestrator.execute_parallel(
            agents=agents,
            task=task,
            max_workers=2,
            dry_run=True  # Simulación
        )

        print_result("Ejecución dry-run", True, f"mode={results.get('mode')}")
        print_result("Agentes ejecutados", results.get('completed', 0) > 0,
                    f"{results.get('completed', 0)}/{results.get('total_agents', 0)}")

        return True

    except Exception as e:
        print_result("Dry-run", False, str(e))
        return False

def test_agent_executor():
    """Test 7: Verificar AgentExecutor."""
    print_header("TEST 7: Agent Executor")

    try:
        from agent_executor import AgentExecutor, ParallelExecutor

        # Test AgentExecutor
        executor = AgentExecutor(use_claude_cli=True)
        print_result("AgentExecutor creado", True, f"claude_cli={executor.use_claude_cli}")

        # Test ParallelExecutor
        parallel = ParallelExecutor(use_claude_cli=True)
        print_result("ParallelExecutor creado", True, f"claude_cli={parallel.use_claude_cli}")

        return True

    except Exception as e:
        print_result("Agent Executor", False, str(e))
        return False

def run_all_tests():
    """Ejecuta todos los tests."""
    print("\n" + "="*60)
    print("  NXT AI DEVELOPMENT - TEST DE INTEGRACIÓN")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)

    results = {
        "imports": test_imports(),
        "claude_cli": test_claude_cli_availability(),
        "client_init": test_client_initialization(),
        "orchestrator_init": test_orchestrator_initialization(),
        "classification": test_classification(),
        "dry_run": test_dry_run_execution(),
        "agent_executor": test_agent_executor(),
    }

    # Resumen
    print_header("RESUMEN DE TESTS")

    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)

    for test_name, result in results.items():
        print_result(test_name, result)

    print(f"\n  Total: {passed} passed, {failed} failed")
    print(f"  Status: {'ALL TESTS PASSED' if failed == 0 else 'SOME TESTS FAILED'}")
    print("="*60 + "\n")

    # Información adicional si todo pasó
    if failed == 0:
        print("  Sistema listo para uso. Comandos disponibles:")
        print("  ")
        print("  # Ejecutar un agente individual")
        print("  python herramientas/nxt_orchestrator_v3.py run-agent nxt-dev 'tu tarea'")
        print("  ")
        print("  # Ejecutar agentes en paralelo")
        print("  python herramientas/nxt_orchestrator_v3.py parallel \\")
        print("    --agents 'nxt-analyst,nxt-dev' \\")
        print("    --task 'tu tarea'")
        print("  ")
        print("  # Dry-run (simulación)")
        print("  python herramientas/nxt_orchestrator_v3.py parallel \\")
        print("    --agents 'nxt-analyst,nxt-dev' \\")
        print("    --task 'tu tarea' --dry-run")
        print("")

    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
