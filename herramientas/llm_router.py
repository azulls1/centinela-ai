#!/usr/bin/env python3
"""
NXT AI Development - Router Inteligente de LLMs
Enruta tareas al LLM mas apropiado basado en el tipo de tarea.
"""

import os
import sys
import json
import argparse
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass


class LLMProvider(Enum):
    """Proveedores de LLM disponibles."""
    CLAUDE = "claude"
    GEMINI = "gemini"
    OPENAI = "openai"


class TaskType(Enum):
    """Tipos de tareas soportadas."""
    # Tareas para Gemini
    WEB_SEARCH = "web_search"
    MAPS_SEARCH = "maps_search"
    FACT_CHECK = "fact_check"
    CODE_EXECUTION = "code_execution"
    LARGE_DOCUMENT = "large_document"
    URL_ANALYSIS = "url_analysis"
    DEEP_REASONING = "deep_reasoning"

    # Tareas para OpenAI
    IMAGE_WITH_TEXT = "image_with_text"
    IMAGE_CREATIVE = "image_creative"
    VIDEO_GENERATION = "video_generation"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    TEXT_TO_SPEECH = "text_to_speech"
    IMAGE_ANALYSIS = "image_analysis"

    # Tareas para Claude (default)
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DOCUMENT_CREATION = "document_creation"
    COMPLEX_REASONING = "complex_reasoning"
    PLANNING = "planning"
    GENERAL = "general"


@dataclass
class RoutingRule:
    """Regla de enrutamiento."""
    task_type: TaskType
    provider: LLMProvider
    priority: int
    keywords: List[str]
    description: str


class LLMRouter:
    """Router inteligente que decide que LLM usar para cada tarea."""

    def __init__(self):
        """Inicializa el router con las reglas de enrutamiento."""
        self.rules = self._initialize_rules()
        self.keyword_map = self._build_keyword_map()

    def _initialize_rules(self) -> List[RoutingRule]:
        """Define las reglas de enrutamiento."""
        return [
            # Reglas para Gemini
            RoutingRule(
                TaskType.WEB_SEARCH,
                LLMProvider.GEMINI,
                1,
                ["buscar", "search", "google", "web", "actual", "reciente", "noticias", "tendencias"],
                "Busquedas web con fuentes verificadas"
            ),
            RoutingRule(
                TaskType.MAPS_SEARCH,
                LLMProvider.GEMINI,
                1,
                ["mapa", "maps", "ubicacion", "lugar", "restaurante", "cerca", "direccion", "hotel"],
                "Busquedas de ubicaciones y lugares"
            ),
            RoutingRule(
                TaskType.FACT_CHECK,
                LLMProvider.GEMINI,
                1,
                ["verificar", "fact", "check", "verdad", "cierto", "falso", "confirmar"],
                "Verificacion de hechos"
            ),
            RoutingRule(
                TaskType.LARGE_DOCUMENT,
                LLMProvider.GEMINI,
                1,
                ["documento grande", "pdf largo", "analizar documento", "1m tokens"],
                "Procesamiento de documentos muy grandes"
            ),
            RoutingRule(
                TaskType.URL_ANALYSIS,
                LLMProvider.GEMINI,
                1,
                ["url", "pagina web", "sitio web", "analizar sitio"],
                "Analisis de paginas web"
            ),

            # Reglas para Gemini - Multimedia (migrado de OpenAI en v3.1.0)
            RoutingRule(
                TaskType.IMAGE_WITH_TEXT,
                LLMProvider.GEMINI,
                1,
                ["logo", "imagen con texto", "banner", "cartel", "poster", "texto en imagen"],
                "Imagenes con texto/logos (Nano Banana Pro)"
            ),
            RoutingRule(
                TaskType.IMAGE_CREATIVE,
                LLMProvider.GEMINI,
                2,
                ["ilustracion", "arte", "imagen", "dibujo", "concepto visual", "diseño"],
                "Imagenes artisticas y creativas (Nano Banana Pro)"
            ),
            RoutingRule(
                TaskType.VIDEO_GENERATION,
                LLMProvider.GEMINI,
                1,
                ["video", "animacion", "clip", "demo video"],
                "Generacion de videos (Veo 3)"
            ),
            RoutingRule(
                TaskType.AUDIO_TRANSCRIPTION,
                LLMProvider.GEMINI,
                1,
                ["transcribir", "transcripcion", "audio a texto", "reunion grabada"],
                "Transcripcion de audio (Gemini Live)"
            ),
            RoutingRule(
                TaskType.TEXT_TO_SPEECH,
                LLMProvider.GEMINI,
                1,
                ["narrar", "voz", "tts", "leer en voz alta", "generar audio"],
                "Generacion de audio narrado (Gemini TTS - 30 voces)"
            ),
            RoutingRule(
                TaskType.IMAGE_ANALYSIS,
                LLMProvider.GEMINI,
                1,
                ["analizar imagen", "que hay en", "describir imagen", "vision"],
                "Analisis visual de imagenes (Gemini Vision)"
            ),

            # Reglas para Claude (default)
            RoutingRule(
                TaskType.CODE_GENERATION,
                LLMProvider.CLAUDE,
                1,
                ["codigo", "programar", "implementar", "desarrollar", "function", "clase", "api"],
                "Generacion de codigo"
            ),
            RoutingRule(
                TaskType.CODE_REVIEW,
                LLMProvider.CLAUDE,
                1,
                ["revisar codigo", "code review", "analizar codigo", "mejorar codigo"],
                "Revision de codigo"
            ),
            RoutingRule(
                TaskType.DOCUMENT_CREATION,
                LLMProvider.CLAUDE,
                1,
                ["docx", "word", "pptx", "powerpoint", "xlsx", "excel", "pdf", "documento"],
                "Creacion de documentos"
            ),
            RoutingRule(
                TaskType.PLANNING,
                LLMProvider.CLAUDE,
                1,
                ["planificar", "arquitectura", "diseñar", "prd", "requisitos", "stories"],
                "Planificacion y arquitectura"
            ),
            RoutingRule(
                TaskType.GENERAL,
                LLMProvider.CLAUDE,
                10,
                [],
                "Tareas generales (default)"
            ),
        ]

    def _build_keyword_map(self) -> Dict[str, RoutingRule]:
        """Construye un mapa de keywords a reglas."""
        keyword_map = {}
        for rule in self.rules:
            for keyword in rule.keywords:
                keyword_map[keyword.lower()] = rule
        return keyword_map

    def route(self, task_description: str) -> Dict[str, Any]:
        """
        Determina el mejor LLM para una tarea.

        Args:
            task_description: Descripcion de la tarea

        Returns:
            Diccionario con provider recomendado y justificacion
        """
        task_lower = task_description.lower()

        # Buscar matches de keywords
        matches = []
        for keyword, rule in self.keyword_map.items():
            if keyword in task_lower:
                matches.append(rule)

        if matches:
            # Ordenar por prioridad (menor = mayor prioridad)
            matches.sort(key=lambda r: r.priority)
            best_match = matches[0]

            return {
                "provider": best_match.provider.value,
                "task_type": best_match.task_type.value,
                "description": best_match.description,
                "confidence": "high" if len(matches) == 1 else "medium",
                "alternatives": [
                    {"provider": m.provider.value, "reason": m.description}
                    for m in matches[1:3]
                ]
            }

        # Default a Claude
        return {
            "provider": LLMProvider.CLAUDE.value,
            "task_type": TaskType.GENERAL.value,
            "description": "Tarea general procesada por Claude",
            "confidence": "low",
            "alternatives": []
        }

    def get_tool_command(self, routing_result: Dict[str, Any], task: str) -> Optional[str]:
        """
        Genera el comando de herramienta apropiado.

        Args:
            routing_result: Resultado del routing
            task: Descripcion de la tarea

        Returns:
            Comando sugerido o None
        """
        provider = routing_result["provider"]
        task_type = routing_result["task_type"]

        if provider == "gemini":
            if task_type == "web_search":
                return f'python herramientas/gemini_tools.py search "{task}"'
            elif task_type == "maps_search":
                return f'python herramientas/gemini_tools.py maps "{task}"'
            elif task_type == "fact_check":
                return f'python herramientas/gemini_tools.py fact_check "{task}"'
            elif task_type == "url_analysis":
                return f'python herramientas/gemini_tools.py url "[URL]" "{task}"'
            elif task_type == "deep_reasoning":
                return f'python herramientas/gemini_tools.py think "{task}"'

        # Multimedia ahora usa Gemini (migrado en v3.1.0)
        if task_type in ["image_with_text", "image_creative"]:
            return f'python herramientas/gemini_tools.py image "{task}" output.png'
        elif task_type == "video_generation":
            return f'python herramientas/gemini_tools.py video "{task}" output.mp4'
        elif task_type == "audio_transcription":
            return 'python herramientas/gemini_tools.py analyze [audio.mp3]'
        elif task_type == "text_to_speech":
            return f'python herramientas/gemini_tools.py tts "{task}" output.mp3 Puck'
        elif task_type == "image_analysis":
            return 'python herramientas/gemini_tools.py analyze [image.png]'

        return None

    def explain_routing(self) -> str:
        """Explica las reglas de routing disponibles."""
        explanation = """
# Reglas de Routing de LLM (v3.1.0)

## Claude (Opus 4.5) - LLM Principal
- Generacion y revision de codigo
- Creacion de documentos (Word, Excel, PPT)
- Planificacion y arquitectura
- Razonamiento de codigo y logica
- Tareas generales (default)

## Gemini (3 Pro Preview) - Busquedas + Multimedia
- Busquedas web con fuentes verificadas
- Busquedas de lugares y mapas
- Verificacion de hechos
- Procesamiento de documentos grandes (>200K tokens)
- Analisis de URLs y paginas web
- Razonamiento + informacion actual
- Generacion de imagenes (Nano Banana Pro)
- Generacion de videos con audio (Veo 3)
- Text-to-Speech (30 voces)
- Analisis visual de imagenes

## OpenAI (Deshabilitado)
- Backup opcional - usar solo si Gemini falla
"""
        return explanation


def main():
    """Punto de entrada principal para CLI."""
    parser = argparse.ArgumentParser(
        description="NXT AI Development - Router Inteligente de LLMs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python llm_router.py route "buscar tendencias de IA en 2025"
  python llm_router.py route "crear logo para mi empresa"
  python llm_router.py route "revisar este codigo Python"
  python llm_router.py explain
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Comando")

    # route
    route_parser = subparsers.add_parser("route", help="Determinar LLM para tarea")
    route_parser.add_argument("task", help="Descripcion de la tarea")

    # explain
    explain_parser = subparsers.add_parser("explain", help="Explicar reglas de routing")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    router = LLMRouter()

    if args.command == "route":
        result = router.route(args.task)
        command = router.get_tool_command(result, args.task)
        if command:
            result["suggested_command"] = command

        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "explain":
        print(router.explain_routing())


if __name__ == "__main__":
    main()
