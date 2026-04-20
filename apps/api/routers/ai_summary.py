"""
Router para generar resúmenes y análisis con OpenAI
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import os
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

from openai import OpenAI

from models import HealthSummary
from supabase_client import get_supabase_client, Client

router = APIRouter()

@lru_cache(maxsize=1)
def get_openai_client() -> Optional[OpenAI]:
    """
    Devuelve el cliente de OpenAI sólo cuando es necesario.
    El cache evita recrearlo por petición.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        return OpenAI(api_key=api_key)
    except TypeError as exc:
        # Versiones antiguas del SDK pueden no aceptar ciertos parámetros (p. ej. proxies).
        # Para no tumbar toda la API, se registra el problema y se retorna None.
        print(f"[openai] No se pudo inicializar el cliente: {exc}")
        return None


def get_supabase() -> Client:
    """Dependency para obtener cliente de Supabase"""
    return get_supabase_client()


@router.post("/generate-summary")
async def generate_ai_summary(
    hours: int = Query(24, ge=1, le=168, description="Horas hacia atrás"),
    user_id: Optional[str] = Query(None, description="Filtrar por usuario"),
    language: str = Query("es", description="Idioma del resumen (es, en)"),
    supabase: Client = Depends(get_supabase),
):
    """
    Generar un resumen inteligente de los eventos usando OpenAI
    """
    openai_client = get_openai_client()
    if not openai_client:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key no configurada. Verifica OPENAI_API_KEY en .env"
        )

    try:
        # Calcular fechas
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(hours=hours)

        # Obtener eventos del período
        query = (
            supabase.table("vishum_events")
            .select("event_type, payload, created_at")
            .gte("created_at", start_date.isoformat())
            .lte("created_at", end_date.isoformat())
        )

        if user_id:
            query = query.eq("user_id", user_id)

        result = query.execute()

        if not result.data:
            return {
                "summary": "No hay eventos en el período seleccionado.",
                "language": language,
                "period": f"{hours} horas",
            }

        # Preparar datos para el prompt
        events_summary = []
        for item in result.data:
            event_type = item.get("event_type", "unknown")
            payload = item.get("payload", {})
            created_at = item.get("created_at", "")
            
            events_summary.append({
                "tipo": event_type,
                "timestamp": created_at,
                "emociones": payload.get("emotions", []),
                "actividad": payload.get("activity"),
                "estado_salud": payload.get("healthStatus"),
                "personas": payload.get("persons", 0),
            })

        # Crear prompt para OpenAI
        prompt = f"""Analiza los siguientes eventos de detección de visión por computadora y genera un resumen inteligente en {language}.

Eventos detectados (últimas {hours} horas):
{str(events_summary)}

Genera un resumen que incluya:
1. Resumen general de la actividad
2. Patrones de emociones detectadas
3. Tipos de actividad más comunes
4. Estado de salud general
5. Recomendaciones o observaciones

Responde SOLO en español, de forma clara y concisa."""

        # Llamar a OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Modelo más económico y rápido
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente experto en análisis de datos de visión por computadora y salud humana. Generas resúmenes claros y útiles.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.7,
            max_tokens=500,
        )

        summary_text = response.choices[0].message.content

        return {
            "summary": summary_text,
            "language": language,
            "period": f"{hours} horas",
            "events_analyzed": len(result.data),
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.exception("Error generating AI summary")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.post("/generate-voice-description")
async def generate_voice_description(
    text: str = Query(..., description="Texto a convertir a voz"),
    voice: str = Query("alloy", description="Voz a usar (alloy, echo, fable, onyx, nova, shimmer)"),
):
    """
    Generar descripción de audio usando OpenAI TTS (Text-to-Speech)
    Retorna la URL del audio generado
    """
    openai_client = get_openai_client()
    if not openai_client:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key no configurada"
        )

    try:
        # Generar audio con OpenAI TTS
        response = openai_client.audio.speech.create(
            model="tts-1",  # Modelo rápido y económico
            voice=voice,
            input=text,
        )

        # Guardar audio temporalmente (en producción, guardar en storage)
        audio_filename = f"audio_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp3"
        audio_path = f"/tmp/{audio_filename}"
        
        with open(audio_path, "wb") as f:
            f.write(response.content)

        return {
            "message": "Audio generado exitosamente",
            "filename": audio_filename,
            "path": audio_path,
            "note": "En producción, subir a storage y retornar URL pública",
        }

    except Exception as e:
        logger.exception("Error generating voice description")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


class DetectionValidationRequest(BaseModel):
    image_base64: str
    detections: List[Dict[str, Any]]


@router.post("/validate-detections")
async def validate_detections_with_openai(
    request: DetectionValidationRequest = Body(...),
):
    """
    Validar detecciones usando OpenAI Vision API
    Ayuda a filtrar falsos positivos y mejorar precisión
    
    Uso: Enviar imagen en base64 y lista de detecciones
    Retorna: detecciones válidas, falsos positivos y objetos faltantes
    """
    openai_client = get_openai_client()
    if not openai_client:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key no configurada"
        )

    try:
        # Preparar prompt para validar detecciones
        detection_list = ", ".join([
            f"{d.get('label', 'unknown')} ({d.get('confidence', 0)*100:.0f}%)" 
            for d in request.detections
        ])
        
        prompt = f"""Analiza esta imagen y valida si los siguientes objetos están realmente presentes:
        
Objetos detectados: {detection_list}

Responde SOLO con un JSON válido en este formato:
{{
  "valid_detections": ["cell phone", "cup"],
  "false_positives": ["laptop", "mouse"],
  "missing_objects": ["cell phone"],
  "confidence": 0.95
}}

Sé estricto: solo marca como válido un objeto si claramente está en la imagen.
Si hay objetos presentes que no están en la lista, agrégalos a missing_objects.
Para objetos como celular, vaso, lata, casco, zapato o bota, sé especialmente cuidadoso."""
        
        # Llamar a OpenAI Vision
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Modelo con visión
            messages=[
                {
                    "role": "system",
                    "content": "Eres un experto en análisis de imágenes. Validas detecciones de objetos con precisión. Responde SOLO con JSON válido.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{request.image_base64}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.1,  # Baja temperatura para respuestas más consistentes
            max_tokens=500,
        )

        import json
        result_text = response.choices[0].message.content
        
        # Parsear respuesta JSON
        try:
            validation_result = json.loads(result_text)
        except json.JSONDecodeError:
            # Si no es JSON válido, intentar extraer JSON del texto
            import re
            json_match = re.search(r'\{[^}]+\}', result_text)
            if json_match:
                validation_result = json.loads(json_match.group())
            else:
                raise ValueError("No se pudo parsear la respuesta de OpenAI")

        return {
            "validated": True,
            "valid_detections": validation_result.get("valid_detections", []),
            "false_positives": validation_result.get("false_positives", []),
            "missing_objects": validation_result.get("missing_objects", []),
            "confidence": validation_result.get("confidence", 0.8),
        }

    except Exception as e:
        logger.exception("Error validating detections")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
