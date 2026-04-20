#!/usr/bin/env python3
"""
NXT AI Development - Herramientas de OpenAI
Proporciona acceso a las capacidades de OpenAI: imagenes, video, audio, etc.
"""

import os
import sys
import json
import base64
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Advertencia: openai no instalado. Ejecuta: pip install openai")


class OpenAITools:
    """Cliente para interactuar con OpenAI API."""

    def __init__(self, api_key: Optional[str] = None):
        """Inicializa el cliente de OpenAI."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY no configurada")

        if OPENAI_AVAILABLE:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None

        self.voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    def image(self, prompt: str, output_path: str, size: str = "1024x1024") -> Dict[str, Any]:
        """
        Generar imagen con GPT-Image-1 (mejor para texto/logos).

        Args:
            prompt: Descripcion de la imagen
            output_path: Ruta donde guardar la imagen
            size: Tamano de la imagen

        Returns:
            Diccionario con resultado
        """
        if not self.client:
            return {"error": "Cliente no disponible"}

        try:
            response = self.client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                n=1,
                size=size,
            )

            # Obtener imagen (puede ser URL o base64)
            image_data = response.data[0]

            if hasattr(image_data, 'b64_json') and image_data.b64_json:
                # Decodificar base64 y guardar
                image_bytes = base64.b64decode(image_data.b64_json)
                with open(output_path, 'wb') as f:
                    f.write(image_bytes)
            elif hasattr(image_data, 'url') and image_data.url:
                # Descargar desde URL
                import urllib.request
                urllib.request.urlretrieve(image_data.url, output_path)

            return {
                "success": True,
                "output": output_path,
                "prompt": prompt,
                "model": "gpt-image-1",
                "size": size,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}

    def dalle(self, prompt: str, output_path: str, size: str = "1024x1024", quality: str = "standard") -> Dict[str, Any]:
        """
        Generar imagen con DALL-E 3 (mejor para arte/ilustraciones).

        Args:
            prompt: Descripcion de la imagen
            output_path: Ruta donde guardar la imagen
            size: Tamano (1024x1024, 1792x1024, 1024x1792)
            quality: Calidad (standard, hd)

        Returns:
            Diccionario con resultado
        """
        if not self.client:
            return {"error": "Cliente no disponible"}

        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size=size,
                quality=quality,
            )

            image_url = response.data[0].url
            revised_prompt = response.data[0].revised_prompt

            # Descargar imagen
            import urllib.request
            urllib.request.urlretrieve(image_url, output_path)

            return {
                "success": True,
                "output": output_path,
                "prompt": prompt,
                "revised_prompt": revised_prompt,
                "model": "dall-e-3",
                "size": size,
                "quality": quality,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}

    def video(self, prompt: str, output_path: str, duration: int = 5) -> Dict[str, Any]:
        """
        Generar video con Sora 2.

        Args:
            prompt: Descripcion del video
            output_path: Ruta donde guardar el video
            duration: Duracion en segundos (max 60)

        Returns:
            Diccionario con resultado
        """
        if not self.client:
            return {"error": "Cliente no disponible"}

        try:
            # Nota: Sora 2 puede no estar disponible en todas las cuentas
            response = self.client.videos.generate(
                model="sora-2",
                prompt=prompt,
                duration=min(duration, 60),
            )

            # Esperar a que el video este listo y descargarlo
            video_url = response.url

            import urllib.request
            urllib.request.urlretrieve(video_url, output_path)

            return {
                "success": True,
                "output": output_path,
                "prompt": prompt,
                "duration": duration,
                "model": "sora-2",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "error": str(e),
                "note": "Sora 2 puede no estar disponible en tu cuenta. Verifica acceso en platform.openai.com"
            }

    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribir audio con Whisper.

        Args:
            audio_path: Ruta al archivo de audio
            language: Codigo de idioma (opcional, ej: "es", "en")

        Returns:
            Diccionario con transcripcion
        """
        if not self.client:
            return {"error": "Cliente no disponible"}

        try:
            with open(audio_path, 'rb') as audio_file:
                kwargs = {
                    "model": "whisper-1",
                    "file": audio_file,
                    "response_format": "verbose_json",
                }
                if language:
                    kwargs["language"] = language

                response = self.client.audio.transcriptions.create(**kwargs)

            return {
                "text": response.text,
                "language": response.language if hasattr(response, 'language') else language,
                "duration": response.duration if hasattr(response, 'duration') else None,
                "segments": [
                    {"start": s.start, "end": s.end, "text": s.text}
                    for s in (response.segments if hasattr(response, 'segments') else [])
                ],
                "file": audio_path,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}

    def translate(self, audio_path: str) -> Dict[str, Any]:
        """
        Traducir audio a ingles con Whisper.

        Args:
            audio_path: Ruta al archivo de audio

        Returns:
            Diccionario con traduccion
        """
        if not self.client:
            return {"error": "Cliente no disponible"}

        try:
            with open(audio_path, 'rb') as audio_file:
                response = self.client.audio.translations.create(
                    model="whisper-1",
                    file=audio_file,
                )

            return {
                "text": response.text,
                "target_language": "en",
                "file": audio_path,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}

    def tts(self, text: str, output_path: str, voice: str = "nova", model: str = "tts-1") -> Dict[str, Any]:
        """
        Generar audio narrado con Text-to-Speech.

        Args:
            text: Texto a narrar
            output_path: Ruta donde guardar el audio
            voice: Voz a usar (alloy, echo, fable, onyx, nova, shimmer)
            model: Modelo (tts-1, tts-1-hd)

        Returns:
            Diccionario con resultado
        """
        if not self.client:
            return {"error": "Cliente no disponible"}

        if voice not in self.voices:
            return {"error": f"Voz invalida. Opciones: {', '.join(self.voices)}"}

        try:
            response = self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
            )

            # Guardar audio
            response.stream_to_file(output_path)

            return {
                "success": True,
                "output": output_path,
                "text": text[:100] + "..." if len(text) > 100 else text,
                "voice": voice,
                "model": model,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}

    def analyze(self, image_path: str, question: str) -> Dict[str, Any]:
        """
        Analizar imagen con GPT-4o Vision.

        Args:
            image_path: Ruta a la imagen
            question: Pregunta sobre la imagen

        Returns:
            Diccionario con analisis
        """
        if not self.client:
            return {"error": "Cliente no disponible"}

        try:
            # Leer y codificar imagen
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            # Determinar tipo MIME
            ext = Path(image_path).suffix.lower()
            mime_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp',
            }.get(ext, 'image/jpeg')

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": question
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
            )

            return {
                "text": response.choices[0].message.content,
                "image": image_path,
                "question": question,
                "model": "gpt-4o",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}

    def compare(self, image1_path: str, image2_path: str, question: str) -> Dict[str, Any]:
        """
        Comparar dos imagenes con GPT-4o Vision.

        Args:
            image1_path: Ruta a la primera imagen
            image2_path: Ruta a la segunda imagen
            question: Pregunta de comparacion

        Returns:
            Diccionario con comparacion
        """
        if not self.client:
            return {"error": "Cliente no disponible"}

        try:
            images = []
            for path in [image1_path, image2_path]:
                with open(path, 'rb') as f:
                    data = base64.b64encode(f.read()).decode('utf-8')
                ext = Path(path).suffix.lower()
                mime = 'image/png' if ext == '.png' else 'image/jpeg'
                images.append(f"data:{mime};base64,{data}")

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {"type": "image_url", "image_url": {"url": images[0]}},
                            {"type": "image_url", "image_url": {"url": images[1]}},
                        ]
                    }
                ],
                max_tokens=1000,
            )

            return {
                "text": response.choices[0].message.content,
                "images": [image1_path, image2_path],
                "question": question,
                "model": "gpt-4o",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}


def main():
    """Punto de entrada principal para CLI."""
    parser = argparse.ArgumentParser(
        description="NXT AI Development - Herramientas de OpenAI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python openai_tools.py image "logo minimalista para app" logo.png
  python openai_tools.py dalle "ciudad futurista" ciudad.png
  python openai_tools.py video "demo de app movil" demo.mp4 10
  python openai_tools.py transcribe reunion.mp3 es
  python openai_tools.py translate audio_espanol.mp3
  python openai_tools.py tts "Bienvenidos" bienvenida.mp3 nova
  python openai_tools.py analyze screenshot.png "que ves?"
  python openai_tools.py compare img1.png img2.png "diferencias?"

Voces TTS disponibles: alloy, echo, fable, onyx, nova, shimmer
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")

    # image
    image_parser = subparsers.add_parser("image", help="Generar imagen (GPT-Image-1)")
    image_parser.add_argument("prompt", help="Descripcion de la imagen")
    image_parser.add_argument("output", help="Ruta de salida")
    image_parser.add_argument("--size", default="1024x1024", help="Tamano")

    # dalle
    dalle_parser = subparsers.add_parser("dalle", help="Generar imagen (DALL-E 3)")
    dalle_parser.add_argument("prompt", help="Descripcion de la imagen")
    dalle_parser.add_argument("output", help="Ruta de salida")
    dalle_parser.add_argument("--size", default="1024x1024", help="Tamano")
    dalle_parser.add_argument("--quality", default="standard", help="Calidad")

    # video
    video_parser = subparsers.add_parser("video", help="Generar video (Sora 2)")
    video_parser.add_argument("prompt", help="Descripcion del video")
    video_parser.add_argument("output", help="Ruta de salida")
    video_parser.add_argument("duration", nargs="?", type=int, default=5, help="Duracion")

    # transcribe
    trans_parser = subparsers.add_parser("transcribe", help="Transcribir audio")
    trans_parser.add_argument("audio", help="Ruta al audio")
    trans_parser.add_argument("language", nargs="?", help="Codigo de idioma")

    # translate
    translate_parser = subparsers.add_parser("translate", help="Traducir audio a ingles")
    translate_parser.add_argument("audio", help="Ruta al audio")

    # tts
    tts_parser = subparsers.add_parser("tts", help="Text-to-Speech")
    tts_parser.add_argument("text", help="Texto a narrar")
    tts_parser.add_argument("output", help="Ruta de salida")
    tts_parser.add_argument("voice", nargs="?", default="nova", help="Voz")

    # analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analizar imagen")
    analyze_parser.add_argument("image", help="Ruta a la imagen")
    analyze_parser.add_argument("question", help="Pregunta")

    # compare
    compare_parser = subparsers.add_parser("compare", help="Comparar imagenes")
    compare_parser.add_argument("image1", help="Primera imagen")
    compare_parser.add_argument("image2", help="Segunda imagen")
    compare_parser.add_argument("question", help="Pregunta")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        tools = OpenAITools()

        if args.command == "image":
            result = tools.image(args.prompt, args.output, args.size)
        elif args.command == "dalle":
            result = tools.dalle(args.prompt, args.output, args.size, args.quality)
        elif args.command == "video":
            result = tools.video(args.prompt, args.output, args.duration)
        elif args.command == "transcribe":
            result = tools.transcribe(args.audio, args.language)
        elif args.command == "translate":
            result = tools.translate(args.audio)
        elif args.command == "tts":
            result = tools.tts(args.text, args.output, args.voice)
        elif args.command == "analyze":
            result = tools.analyze(args.image, args.question)
        elif args.command == "compare":
            result = tools.compare(args.image1, args.image2, args.question)
        else:
            parser.print_help()
            sys.exit(1)

        print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
