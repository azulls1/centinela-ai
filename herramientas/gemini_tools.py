#!/usr/bin/env python3
"""
NXT AI Development - Herramientas de Google Gemini
Proporciona acceso a las capacidades de Gemini: busqueda, mapas, codigo, etc.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Optional, Dict, Any, List

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("Advertencia: google-genai no instalado. Ejecuta: pip install google-genai")


class GeminiTools:
    """Cliente para interactuar con Google Gemini API."""

    def __init__(self, api_key: Optional[str] = None):
        """Inicializa el cliente de Gemini."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY no configurada")

        if GENAI_AVAILABLE:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

        self.default_model = "gemini-3-pro-preview"
        self.thinking_model = "gemini-3-pro-preview"  # Razonamiento profundo (mas reciente)

    def search(self, query: str) -> Dict[str, Any]:
        """
        Busqueda web con Google Search Grounding.

        Args:
            query: Consulta de busqueda

        Returns:
            Diccionario con texto, fuentes y metadata
        """
        if not self.client:
            return {"error": "Cliente no disponible"}

        try:
            response = self.client.models.generate_content(
                model=self.default_model,
                contents=query,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.7,
                )
            )

            # Extraer fuentes si estan disponibles
            sources = []
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata'):
                    metadata = candidate.grounding_metadata
                    if hasattr(metadata, 'grounding_chunks'):
                        for chunk in metadata.grounding_chunks:
                            if hasattr(chunk, 'web'):
                                sources.append({
                                    "title": chunk.web.title if hasattr(chunk.web, 'title') else "Sin titulo",
                                    "url": chunk.web.uri if hasattr(chunk.web, 'uri') else ""
                                })

            return {
                "text": response.text,
                "sources": sources,
                "timestamp": datetime.now().isoformat(),
                "confidence": "high" if sources else "medium"
            }

        except Exception as e:
            return {"error": str(e)}

    def current(self, topic: str) -> Dict[str, Any]:
        """
        Obtener informacion actual sobre un tema.

        Args:
            topic: Tema a investigar

        Returns:
            Diccionario con informacion actual
        """
        query = f"Informacion actual y reciente sobre: {topic}. Proporciona datos actualizados con fuentes."
        return self.search(query)

    def maps(self, query: str, lat: Optional[float] = None, lon: Optional[float] = None) -> Dict[str, Any]:
        """
        Busqueda con Google Maps Grounding.

        Args:
            query: Consulta de busqueda (ej: "restaurantes italianos")
            lat: Latitud (opcional)
            lon: Longitud (opcional)

        Returns:
            Diccionario con lugares encontrados
        """
        if not self.client:
            return {"error": "Cliente no disponible"}

        try:
            location_context = ""
            if lat and lon:
                location_context = f" cerca de las coordenadas {lat}, {lon}"

            full_query = f"Busca {query}{location_context}. Incluye nombres, direcciones, ratings y horarios."

            response = self.client.models.generate_content(
                model=self.default_model,
                contents=full_query,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.3,
                )
            )

            return {
                "text": response.text,
                "query": query,
                "location": {"lat": lat, "lon": lon} if lat and lon else None,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}

    def fact_check(self, claim: str) -> Dict[str, Any]:
        """
        Verificar un hecho o afirmacion.

        Args:
            claim: Afirmacion a verificar

        Returns:
            Diccionario con veredicto y explicacion
        """
        query = f"""Verifica la siguiente afirmacion y proporciona un veredicto:

Afirmacion: "{claim}"

Responde con:
1. VERDADERO, FALSO o PARCIALMENTE VERDADERO
2. Explicacion breve
3. Fuentes que respaldan tu veredicto"""

        result = self.search(query)

        if "error" not in result:
            result["claim"] = claim
            # Intentar extraer veredicto del texto
            text_lower = result["text"].lower()
            if "verdadero" in text_lower and "parcialmente" not in text_lower:
                result["verdict"] = "TRUE"
            elif "falso" in text_lower:
                result["verdict"] = "FALSE"
            else:
                result["verdict"] = "PARTIALLY_TRUE"

        return result

    def code(self, task: str) -> Dict[str, Any]:
        """
        Ejecutar codigo Python para una tarea.

        Args:
            task: Descripcion de la tarea a realizar

        Returns:
            Diccionario con codigo y resultado
        """
        if not self.client:
            return {"error": "Cliente no disponible"}

        try:
            prompt = f"""Escribe y ejecuta codigo Python para: {task}

Requisitos:
- Codigo limpio y eficiente
- Muestra el resultado claramente
- Si hay errores, explica como solucionarlos"""

            response = self.client.models.generate_content(
                model=self.default_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(code_execution=types.ToolCodeExecution())],
                    temperature=0.2,
                )
            )

            return {
                "text": response.text,
                "task": task,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}

    def url(self, url: str, question: str) -> Dict[str, Any]:
        """
        Analizar una URL y responder preguntas sobre su contenido.

        Args:
            url: URL a analizar
            question: Pregunta sobre el contenido

        Returns:
            Diccionario con respuesta
        """
        if not self.client:
            return {"error": "Cliente no disponible"}

        try:
            prompt = f"""Analiza el contenido de esta URL: {url}

Pregunta: {question}

Proporciona una respuesta detallada basada en el contenido de la pagina."""

            response = self.client.models.generate_content(
                model=self.default_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(url_context=types.UrlContext(urls=[url]))],
                    temperature=0.3,
                )
            )

            return {
                "text": response.text,
                "url": url,
                "question": question,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}

    def think(self, problem: str) -> Dict[str, Any]:
        """
        Razonamiento profundo para problemas complejos.

        Args:
            problem: Problema a analizar

        Returns:
            Diccionario con analisis profundo
        """
        if not self.client:
            return {"error": "Cliente no disponible"}

        try:
            response = self.client.models.generate_content(
                model=self.thinking_model,
                contents=problem,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(
                        thinking_budget=10000
                    ),
                    temperature=0.7,
                )
            )

            # Extraer pensamiento si esta disponible
            thinking = ""
            answer = response.text
            if hasattr(response, 'candidates') and response.candidates:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'thought') and part.thought:
                        thinking = part.text
                    elif hasattr(part, 'text'):
                        answer = part.text

            return {
                "thinking": thinking,
                "answer": answer,
                "problem": problem,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}

    def analyze(self, file_path: str, question: str) -> Dict[str, Any]:
        """
        Analizar un documento grande.

        Args:
            file_path: Ruta al archivo
            question: Pregunta sobre el documento

        Returns:
            Diccionario con respuesta
        """
        if not self.client:
            return {"error": "Cliente no disponible"}

        try:
            # Subir archivo
            with open(file_path, 'rb') as f:
                uploaded_file = self.client.files.upload(file=f)

            response = self.client.models.generate_content(
                model=self.default_model,
                contents=[
                    uploaded_file,
                    f"Analiza este documento y responde: {question}"
                ],
                config=types.GenerateContentConfig(
                    temperature=0.3,
                )
            )

            return {
                "text": response.text,
                "file": file_path,
                "question": question,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}

    # =========================================================================
    # MULTIMEDIA - Nano Banana Pro, Veo 3, TTS (Opcion A - Todo Gemini)
    # =========================================================================

    def image(self, prompt: str, output_path: str, aspect_ratio: str = "1:1") -> Dict[str, Any]:
        """
        Generar imagen con Nano Banana Pro (Gemini 3 Pro Image).

        Args:
            prompt: Descripcion de la imagen
            output_path: Ruta donde guardar la imagen
            aspect_ratio: Ratio de aspecto (1:1, 16:9, 9:16, 4:3, 3:4)

        Returns:
            Diccionario con resultado
        """
        if not self.client:
            return {"error": "Cliente no disponible"}

        try:
            # Nano Banana Pro - el mejor modelo de imagen de Gemini
            response = self.client.models.generate_content(
                model="nano-banana-pro-preview",
                contents=f"Generate an image: {prompt}",
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                    temperature=0.7,
                )
            )

            # Extraer y guardar imagen
            if hasattr(response, 'candidates') and response.candidates:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        import base64
                        image_data = base64.b64decode(part.inline_data.data)
                        with open(output_path, 'wb') as f:
                            f.write(image_data)

                        return {
                            "success": True,
                            "output": output_path,
                            "prompt": prompt,
                            "model": "nano-banana-pro",
                            "aspect_ratio": aspect_ratio,
                            "timestamp": datetime.now().isoformat()
                        }

            return {"error": "No se genero ninguna imagen"}

        except Exception as e:
            return {"error": str(e)}

    def video(self, prompt: str, output_path: str, duration: int = 5) -> Dict[str, Any]:
        """
        Generar video con Veo 3.

        Args:
            prompt: Descripcion del video
            output_path: Ruta donde guardar el video
            duration: Duracion en segundos (max 8)

        Returns:
            Diccionario con resultado
        """
        if not self.client:
            return {"error": "Cliente no disponible"}

        try:
            # Veo 3 - genera video con audio nativo
            response = self.client.models.generate_videos(
                model="veo-3.0-generate-001",  # Veo 3 estable
                prompt=prompt,
                config=types.GenerateVideosConfig(
                    duration_seconds=min(duration, 8),
                    aspect_ratio="16:9",
                    generate_audio=True,  # Audio nativo sincronizado
                )
            )

            # Esperar y obtener resultado
            if hasattr(response, 'video') and response.video:
                video_data = response.video.video_bytes
                with open(output_path, 'wb') as f:
                    f.write(video_data)

                return {
                    "success": True,
                    "output": output_path,
                    "prompt": prompt,
                    "duration": duration,
                    "model": "veo-3",
                    "has_audio": True,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "processing",
                    "message": "Video en proceso. Puede tomar unos minutos.",
                    "prompt": prompt
                }

        except Exception as e:
            return {
                "error": str(e),
                "note": "Veo 3 requiere acceso a Vertex AI o Google AI Studio"
            }

    def tts(self, text: str, output_path: str, voice: str = "Puck") -> Dict[str, Any]:
        """
        Generar audio narrado con Text-to-Speech nativo de Gemini.

        Args:
            text: Texto a narrar
            output_path: Ruta donde guardar el audio
            voice: Voz a usar (Puck, Charon, Kore, Fenrir, Aoede, etc.)

        Returns:
            Diccionario con resultado
        """
        if not self.client:
            return {"error": "Cliente no disponible"}

        # Voces disponibles en Gemini
        available_voices = [
            "Puck", "Charon", "Kore", "Fenrir", "Aoede",
            "Leda", "Orus", "Zephyr", "Clio", "Calliope"
        ]

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-pro-preview-tts",  # Mejor calidad TTS
                contents=text,
                config=types.GenerateContentConfig(
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice
                            )
                        )
                    ),
                    response_modalities=["AUDIO"],
                )
            )

            # Guardar audio
            if hasattr(response, 'candidates') and response.candidates:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        import base64
                        audio_data = base64.b64decode(part.inline_data.data)
                        with open(output_path, 'wb') as f:
                            f.write(audio_data)

                        return {
                            "success": True,
                            "output": output_path,
                            "text": text[:100] + "..." if len(text) > 100 else text,
                            "voice": voice,
                            "model": "gemini-tts",
                            "available_voices": available_voices,
                            "timestamp": datetime.now().isoformat()
                        }

            return {"error": "No se genero audio"}

        except Exception as e:
            return {"error": str(e)}

    def analyze_image(self, image_path: str, question: str) -> Dict[str, Any]:
        """
        Analizar imagen con Gemini Vision.

        Args:
            image_path: Ruta a la imagen
            question: Pregunta sobre la imagen

        Returns:
            Diccionario con analisis
        """
        if not self.client:
            return {"error": "Cliente no disponible"}

        try:
            # Subir imagen
            with open(image_path, 'rb') as f:
                uploaded_file = self.client.files.upload(file=f)

            response = self.client.models.generate_content(
                model=self.default_model,
                contents=[
                    uploaded_file,
                    question
                ],
                config=types.GenerateContentConfig(
                    temperature=0.3,
                )
            )

            return {
                "text": response.text,
                "image": image_path,
                "question": question,
                "model": self.default_model,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}


def main():
    """Punto de entrada principal para CLI."""
    parser = argparse.ArgumentParser(
        description="NXT AI Development - Herramientas de Google Gemini",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Busquedas y analisis
  python gemini_tools.py search "tendencias IA 2025"
  python gemini_tools.py maps "restaurantes italianos" 40.4168 -3.7038
  python gemini_tools.py fact_check "Python es el lenguaje mas usado"
  python gemini_tools.py code "calcular fibonacci de 50"
  python gemini_tools.py url "https://ejemplo.com" "resume el articulo"
  python gemini_tools.py think "como disenar un sistema escalable"
  python gemini_tools.py analyze documento.pdf "puntos principales"

  # Multimedia (Nano Banana Pro, Veo 3, TTS)
  python gemini_tools.py image "logo minimalista para app de fitness" logo.png
  python gemini_tools.py video "demo de app movil con UI moderna" demo.mp4 8
  python gemini_tools.py tts "Bienvenidos a nuestra aplicacion" bienvenida.mp3 Puck
  python gemini_tools.py vision screenshot.png "que elementos UI ves?"

Voces TTS disponibles: Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, Zephyr, Clio, Calliope
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")

    # search
    search_parser = subparsers.add_parser("search", help="Busqueda web con fuentes")
    search_parser.add_argument("query", help="Consulta de busqueda")

    # current
    current_parser = subparsers.add_parser("current", help="Informacion actual")
    current_parser.add_argument("topic", help="Tema a investigar")

    # maps
    maps_parser = subparsers.add_parser("maps", help="Busqueda de lugares")
    maps_parser.add_argument("query", help="Consulta de busqueda")
    maps_parser.add_argument("lat", nargs="?", type=float, help="Latitud")
    maps_parser.add_argument("lon", nargs="?", type=float, help="Longitud")

    # fact_check
    fact_parser = subparsers.add_parser("fact_check", help="Verificar afirmacion")
    fact_parser.add_argument("claim", help="Afirmacion a verificar")

    # code
    code_parser = subparsers.add_parser("code", help="Ejecutar codigo Python")
    code_parser.add_argument("task", help="Tarea a realizar")

    # url
    url_parser = subparsers.add_parser("url", help="Analizar URL")
    url_parser.add_argument("url", help="URL a analizar")
    url_parser.add_argument("question", help="Pregunta sobre el contenido")

    # think
    think_parser = subparsers.add_parser("think", help="Razonamiento profundo")
    think_parser.add_argument("problem", help="Problema a analizar")

    # analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analizar documento")
    analyze_parser.add_argument("file", help="Ruta al archivo")
    analyze_parser.add_argument("question", help="Pregunta sobre el documento")

    # =========================================================================
    # MULTIMEDIA - Comandos CLI
    # =========================================================================

    # image (Nano Banana Pro)
    image_parser = subparsers.add_parser("image", help="Generar imagen (Nano Banana Pro)")
    image_parser.add_argument("prompt", help="Descripcion de la imagen")
    image_parser.add_argument("output", help="Ruta de salida")
    image_parser.add_argument("--ratio", default="1:1", help="Aspect ratio (1:1, 16:9, 9:16)")

    # video (Veo 3)
    video_parser = subparsers.add_parser("video", help="Generar video (Veo 3)")
    video_parser.add_argument("prompt", help="Descripcion del video")
    video_parser.add_argument("output", help="Ruta de salida")
    video_parser.add_argument("duration", nargs="?", type=int, default=5, help="Duracion (max 8)")

    # tts (Gemini TTS)
    tts_parser = subparsers.add_parser("tts", help="Text-to-Speech (30 voces)")
    tts_parser.add_argument("text", help="Texto a narrar")
    tts_parser.add_argument("output", help="Ruta de salida")
    tts_parser.add_argument("voice", nargs="?", default="Puck", help="Voz")

    # vision (analizar imagen)
    vision_parser = subparsers.add_parser("vision", help="Analizar imagen")
    vision_parser.add_argument("image", help="Ruta a la imagen")
    vision_parser.add_argument("question", help="Pregunta sobre la imagen")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        tools = GeminiTools()

        if args.command == "search":
            result = tools.search(args.query)
        elif args.command == "current":
            result = tools.current(args.topic)
        elif args.command == "maps":
            result = tools.maps(args.query, args.lat, args.lon)
        elif args.command == "fact_check":
            result = tools.fact_check(args.claim)
        elif args.command == "code":
            result = tools.code(args.task)
        elif args.command == "url":
            result = tools.url(args.url, args.question)
        elif args.command == "think":
            result = tools.think(args.problem)
        elif args.command == "analyze":
            result = tools.analyze(args.file, args.question)
        # Multimedia
        elif args.command == "image":
            result = tools.image(args.prompt, args.output, args.ratio)
        elif args.command == "video":
            result = tools.video(args.prompt, args.output, args.duration)
        elif args.command == "tts":
            result = tools.tts(args.text, args.output, args.voice)
        elif args.command == "vision":
            result = tools.analyze_image(args.image, args.question)
        else:
            parser.print_help()
            sys.exit(1)

        print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
