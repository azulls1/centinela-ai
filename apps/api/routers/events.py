"""
Router para endpoints de eventos
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from models import Event, EventCreate, EventStats
from supabase_client import get_supabase_client, Client

logger = logging.getLogger(__name__)

router = APIRouter()


def get_supabase() -> Client:
    """Dependency para obtener cliente de Supabase"""
    return get_supabase_client()


@router.post("/", response_model=Event)
async def create_event(
    event: EventCreate,
    supabase: Client = Depends(get_supabase),
):
    """
    Crear un nuevo evento
    """
    try:
        # Insertar evento en Supabase
        result = supabase.table("vishum_events").insert({
            "user_id": event.user_id or "anonymous",
            "event_type": event.event_type,
            "camera_id": event.camera_id or "default_camera",
            "payload": event.payload,
        }).execute()

        if not result.data:
            raise HTTPException(status_code=400, detail="Error creando evento")

        return Event(**result.data[0])
    except Exception as e:
        logger.exception("Error creating event")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=List[Event])
async def get_events(
    limit: int = Query(100, ge=1, le=1000, description="Límite de eventos"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    event_type: Optional[str] = Query(None, description="Filtrar por tipo de evento"),
    user_id: Optional[str] = Query(None, description="Filtrar por usuario"),
    camera_id: Optional[str] = Query(None, description="Filtrar por cámara"),
    session_id: Optional[str] = Query(None, description="Filtrar por sesión (payload.session_id)"),
    supabase: Client = Depends(get_supabase),
):
    """
    Obtener lista de eventos con filtros opcionales
    """
    try:
        query = supabase.table("vishum_events").select("*")

        # Aplicar filtros
        if event_type:
            query = query.eq("event_type", event_type)
        if user_id:
            query = query.eq("user_id", user_id)
        if camera_id:
            query = query.eq("camera_id", camera_id)
        if session_id:
            query = query.contains("payload", {"session_id": session_id})

        # Ordenar y paginar
        result = (
            query.order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        return [Event(**item) for item in result.data]
    except Exception as e:
        logger.exception("Error fetching events")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{event_id}", response_model=Event)
async def get_event(
    event_id: str,
    supabase: Client = Depends(get_supabase),
):
    """
    Obtener un evento específico por ID
    """
    try:
        result = supabase.table("vishum_events").select("*").eq("id", event_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Evento no encontrado")

        return Event(**result.data[0])
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error fetching event by ID")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{event_id}")
async def delete_event(
    event_id: str,
    supabase: Client = Depends(get_supabase),
):
    """
    Eliminar un evento por ID
    """
    try:
        result = supabase.table("vishum_events").delete().eq("id", event_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Evento no encontrado")

        return {"message": "Evento eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error deleting event")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats/summary", response_model=EventStats)
async def get_event_stats(
    hours: int = Query(24, ge=1, le=168, description="Horas hacia atrás"),
    user_id: Optional[str] = Query(None, description="Filtrar por usuario"),
    camera_id: Optional[str] = Query(None, description="Filtrar por cámara"),
    session_id: Optional[str] = Query(None, description="Filtrar por sesión (payload.session_id)"),
    supabase: Client = Depends(get_supabase),
):
    """
    Obtener estadísticas de eventos en un período
    """
    try:
        # Calcular fechas
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(hours=hours)

        # Construir query
        query = (
            supabase.table("vishum_events")
            .select("event_type, camera_id, created_at, payload")
            .gte("created_at", start_date.isoformat())
            .lte("created_at", end_date.isoformat())
        )

        if user_id:
            query = query.eq("user_id", user_id)
        if camera_id:
            query = query.eq("camera_id", camera_id)
        if session_id:
            query = query.contains("payload", {"session_id": session_id})

        result = query.execute()

        # Agrupar por tipo
        by_type: dict[str, int] = {}
        by_camera: dict[str, int] = {}
        hourly_buckets: dict[str, int] = {}
        total = len(result.data)

        for item in result.data:
            event_type = item["event_type"]
            by_type[event_type] = by_type.get(event_type, 0) + 1
            cam_key = item.get("camera_id") or "default_camera"
            by_camera[cam_key] = by_camera.get(cam_key, 0) + 1
            created_at = item.get("created_at")
            if created_at:
                try:
                    timestamp = datetime.fromisoformat(
                        created_at.replace("Z", "+00:00")
                    )
                    bucket = timestamp.replace(minute=0, second=0, microsecond=0)
                    bucket_key = bucket.isoformat()
                    hourly_buckets[bucket_key] = hourly_buckets.get(bucket_key, 0) + 1
                except ValueError:
                    pass

        return EventStats(
            total=total,
            by_type=by_type,
            by_camera=by_camera,
            period_hours=hours,
            start_date=start_date,
            end_date=end_date,
            hourly=[
                {"bucket": bucket, "count": count}
                for bucket, count in sorted(hourly_buckets.items())
            ],
        )
    except Exception as e:
        logger.exception("Error fetching event stats")
        raise HTTPException(status_code=500, detail="Internal server error")

