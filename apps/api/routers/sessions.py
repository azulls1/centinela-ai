"""
Router para sesiones de demo: inicio, heartbeats y panel administrativo.
"""

import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List

import bcrypt
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request

from models import (
    AdminSessionsResponse,
    AdminSessionsSummary,
    DemoSessionRecord,
    SessionInitRequest,
    SessionHeartbeatRequest,
    SessionAdminActionRequest,
    AdminAlert,
    AdminBannedSessionsResponse,
    AdminLoginRequest,
    AdminLoginResponse,
)
from supabase_client import Client, get_supabase_client


router = APIRouter()

ADMIN_API_TOKEN = os.getenv("ADMIN_API_TOKEN", "")
SESSION_LIMIT_MINUTES = int(os.getenv("SESSION_LIMIT_MINUTES", "45"))
SESSION_TOKEN_LIMIT = int(os.getenv("SESSION_TOKEN_LIMIT", "15000"))
SESSION_CAMERA_LIMIT = int(os.getenv("SESSION_CAMERA_LIMIT", "3"))
SESSION_INACTIVITY_ALERT_MINUTES = int(os.getenv("SESSION_INACTIVITY_ALERT_MINUTES", "5"))
DEFAULT_BANNED_LIMIT = int(os.getenv("ADMIN_BANNED_LIMIT_DEFAULT", "5"))


def get_supabase() -> Client:
    return get_supabase_client()


@router.post("/admin/auth/login", response_model=AdminLoginResponse)
def admin_auth_login(
    payload: AdminLoginRequest,
    supabase: Client = Depends(get_supabase),
) -> AdminLoginResponse:
    if not payload.username or not payload.password:
        raise HTTPException(status_code=400, detail="Usuario y contraseña son obligatorios.")

    try:
        result = (
            supabase.table("vishum_admin_users")
            .select("password_hash")
            .eq("username", payload.username)
            .limit(1)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"No se pudo validar credenciales: {exc}") from exc

    data = getattr(result, "data", None) or []
    if not data:
        raise HTTPException(status_code=401, detail="Credenciales inválidas.")

    password_hash = data[0].get("password_hash")
    if not password_hash:
        raise HTTPException(status_code=401, detail="Credenciales inválidas.")

    if not bcrypt.checkpw(payload.password.encode("utf-8"), password_hash.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Credenciales inválidas.")

    if not ADMIN_API_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="ADMIN_API_TOKEN no está configurado en el servidor.",
        )

    return AdminLoginResponse(token=ADMIN_API_TOKEN, username=payload.username)


def require_admin_token(x_admin_token: str = Header(..., alias="x-admin-token")) -> str:
    if not ADMIN_API_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="ADMIN_API_TOKEN no está configurado en el servidor.",
        )
    if x_admin_token != ADMIN_API_TOKEN:
        raise HTTPException(status_code=401, detail="Token administrativo inválido.")
    return x_admin_token


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _compute_duration_minutes(started_at: Optional[str], last_ping_at: Optional[str]) -> float:
    if not started_at or not last_ping_at:
        return 0.0
    try:
        start_dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        last_dt = datetime.fromisoformat(last_ping_at.replace("Z", "+00:00"))
        return round((last_dt - start_dt).total_seconds() / 60.0, 2)
    except Exception:
        return 0.0


def _normalize_record(row: dict) -> DemoSessionRecord:
    metadata = row.get("metadata") or {}
    organization = metadata.get("organization")
    return DemoSessionRecord(
        session_id=row.get("session_id"),
        name=row.get("name"),
        email=row.get("email"),
        plan=row.get("plan"),
        organization=organization,
        ip_address=row.get("ip_address"),
        user_agent=row.get("user_agent"),
        referer=row.get("referer"),
        cameras_active=row.get("cameras_active"),
        fps_average=row.get("fps_average"),
        tokens_used=row.get("tokens_used"),
        status=row.get("status"),
        started_at=row.get("started_at"),
        last_ping_at=row.get("last_ping_at"),
        admin_note=row.get("admin_note"),
        metadata=metadata,
    )


def _insert_session_event(
    supabase: Client,
    session_id: str,
    event_type: str,
    payload: Optional[dict] = None,
) -> None:
    try:
        supabase.table("vishum_session_events").insert(
            {
                "session_id": session_id,
                "event_type": event_type,
                "payload": payload or {},
            }
        ).execute()
    except Exception:
        pass


def _fetch_session_by_id(supabase: Client, session_id: str) -> Optional[dict]:
    """Consulta Supabase y devuelve la fila de sesión asociada al ID."""
    result = (
        supabase.table("vishum_sessions")
        .select("*")
        .eq("session_id", session_id)
        .limit(1)
        .execute()
    )

    data = result.data
    if isinstance(data, list):
        return data[0] if data else None
    return data


def _identifier_is_banned(
    supabase: Client,
    *,
    ip_address: Optional[str] = None,
    email: Optional[str] = None,
) -> bool:
    if not ip_address and not email:
        return False

    if ip_address:
        try:
            result = (
                supabase.table("vishum_sessions")
                .select("session_id")
                .eq("status", "banned")
                .eq("ip_address", ip_address)
                .limit(1)
                .execute()
            )
            if result.data:
                return True
        except Exception:
            pass

    if email:
        normalized_email = email.strip().lower()
        if normalized_email:
            try:
                result = (
                    supabase.table("vishum_sessions")
                    .select("session_id")
                    .eq("status", "banned")
                    .eq("email", normalized_email)
                    .limit(1)
                    .execute()
                )
                if result.data:
                    return True
            except Exception:
                pass

    return False


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


@router.post("/init", response_model=DemoSessionRecord, status_code=201)
async def init_session(
    payload: SessionInitRequest,
    request: Request,
    supabase: Client = Depends(get_supabase),
) -> DemoSessionRecord:
    session_id = payload.session_id or str(uuid.uuid4())
    now = _utc_now().isoformat()
    ip_address = request.headers.get("x-forwarded-for")
    if not ip_address and request.client:
        ip_address = request.client.host

    referer = request.headers.get("referer")
    user_agent = request.headers.get("user-agent")

    if _identifier_is_banned(
        supabase,
        ip_address=ip_address,
        email=payload.email,
    ):
        raise HTTPException(
            status_code=403,
            detail="El acceso está bloqueado para esta IP o correo electrónico. Contacta al administrador.",
        )

    insert_payload = {
        "session_id": session_id,
        "name": payload.name,
        "email": payload.email.strip().lower() if payload.email else None,
        "plan": payload.plan,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "referer": referer,
        "status": "active",
        "metadata": payload.metadata or {},
        "started_at": now,
        "last_ping_at": now,
    }

    try:
        supabase.table("vishum_sessions").upsert(
            insert_payload, on_conflict="session_id"
        ).execute()
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"No se pudo registrar la sesión: {exc}"
        ) from exc

    row = _fetch_session_by_id(supabase, session_id)
    if not row:
        raise HTTPException(status_code=500, detail="Respuesta vacía al registrar la sesión.")

    _insert_session_event(
        supabase,
        session_id,
        "init",
        {"name": payload.name, "email": payload.email, "plan": payload.plan},
    )

    return _normalize_record(row)


@router.post("/heartbeat", response_model=DemoSessionRecord)
async def session_heartbeat(
    payload: SessionHeartbeatRequest,
    request: Request,
    supabase: Client = Depends(get_supabase),
) -> DemoSessionRecord:
    if not payload.session_id:
        raise HTTPException(status_code=400, detail="session_id es obligatorio")

    now_iso = _utc_now().isoformat()
    ip_address = request.headers.get("x-forwarded-for")
    if not ip_address and request.client:
        ip_address = request.client.host

    update_payload = {
        "cameras_active": payload.cameras_active,
        "fps_average": payload.fps_average,
        "tokens_used": payload.tokens_used,
        "last_ping_at": now_iso,
        "ip_address": ip_address,
    }

    if payload.status is not None:
        update_payload["status"] = payload.status

    try:
        (
            supabase.table("vishum_sessions")
            .update(update_payload)
            .eq("session_id", payload.session_id)
            .execute()
        )
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("heartbeat update failed for %s: %s", payload.session_id, exc)
        raise HTTPException(
            status_code=503,
            detail="Heartbeat update temporarily unavailable, please retry.",
        ) from exc

    try:
        row = _fetch_session_by_id(supabase, payload.session_id)
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("heartbeat fetch failed for %s: %s", payload.session_id, exc)
        raise HTTPException(
            status_code=503,
            detail="Heartbeat fetch temporarily unavailable, please retry.",
        ) from exc

    if not row:
        init_payload = SessionInitRequest(session_id=payload.session_id, name=None, email=None, plan=None)
        return await init_session(init_payload, request, supabase)

    _insert_session_event(
        supabase,
        payload.session_id,
        "heartbeat",
        {
            "cameras": payload.cameras_active,
            "fps": payload.fps_average,
            "tokens": payload.tokens_used,
            "status": payload.status or "active",
        },
    )

    return _normalize_record(row)


@router.get("/admin", response_model=AdminSessionsResponse)
def list_sessions(
    supabase: Client = Depends(get_supabase),
    _: str = Depends(require_admin_token),
) -> AdminSessionsResponse:
    result = (
        supabase.table("vishum_sessions")
        .select("*")
        .order("last_ping_at", desc=True)
        .limit(250)
        .execute()
    )

    sessions: list[DemoSessionRecord] = []
    active_sessions = 0
    cameras_connected = 0
    sessions_limit = 0
    sessions_banned = 0
    total_duration = 0.0
    tokens_total = 0
    count_for_avg = 0

    for row in result.data or []:
        record = _normalize_record(row)
        status_value = record.status or "active"
        cameras_value = int(record.cameras_active or 0)
        tokens_value = int(record.tokens_used or 0)
        duration = _compute_duration_minutes(row.get("started_at"), row.get("last_ping_at"))

        sessions.append(record)
        tokens_total += tokens_value

        if status_value in ("active", "limit"):
            active_sessions += 1
            cameras_connected += cameras_value
            total_duration += duration
            count_for_avg += 1

        if status_value == "limit":
            sessions_limit += 1
        if status_value == "banned":
            sessions_banned += 1

    summary = AdminSessionsSummary(
        active_sessions=active_sessions,
        cameras_connected=cameras_connected,
        average_duration_minutes=round(total_duration / count_for_avg, 1) if count_for_avg else 0.0,
        sessions_limit=sessions_limit,
        sessions_banned=sessions_banned,
        tokens_used=tokens_total,
    )

    return AdminSessionsResponse(summary=summary, sessions=sessions, generated_at=_utc_now())


def _admin_update_session(
    supabase: Client,
    session_id: str,
    new_status: str,
    action_type: str,
    reason: Optional[str],
) -> DemoSessionRecord:
    now = _utc_now().isoformat()
    (
        supabase.table("vishum_sessions")
        .update({"status": new_status, "last_ping_at": now, "admin_note": reason})
        .eq("session_id", session_id)
        .execute()
    )

    row = _fetch_session_by_id(supabase, session_id)
    if not row:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    _insert_session_event(
        supabase,
        session_id,
        action_type,
        {"reason": reason, "status": new_status},
    )

    return _normalize_record(row)


@router.post("/admin/{session_id}/disconnect", response_model=DemoSessionRecord)
def admin_disconnect_session(
    session_id: str,
    payload: SessionAdminActionRequest,
    supabase: Client = Depends(get_supabase),
    _: str = Depends(require_admin_token),
) -> DemoSessionRecord:
    return _admin_update_session(supabase, session_id, "terminated", "admin_disconnect", payload.reason)


@router.post("/admin/{session_id}/ban", response_model=DemoSessionRecord)
def admin_ban_session(
    session_id: str,
    payload: SessionAdminActionRequest,
    supabase: Client = Depends(get_supabase),
    _: str = Depends(require_admin_token),
) -> DemoSessionRecord:
    return _admin_update_session(supabase, session_id, "banned", "admin_ban", payload.reason)


@router.post("/admin/{session_id}/limit", response_model=DemoSessionRecord)
def admin_limit_session(
    session_id: str,
    payload: SessionAdminActionRequest,
    supabase: Client = Depends(get_supabase),
    _: str = Depends(require_admin_token),
) -> DemoSessionRecord:
    return _admin_update_session(supabase, session_id, "limit", "admin_limit", payload.reason)


def _build_status_alert(
    session: DemoSessionRecord,
    alert_type: str,
    message: str,
    ts: datetime,
    suffix: str,
    action: Optional[str] = None,
) -> AdminAlert:
    return AdminAlert(
        id=f"{alert_type}-{session.session_id}-{suffix}",
        type=alert_type,
        message=message,
        created_at=ts,
        action=action,
    )


@router.get("/admin/alerts", response_model=List[AdminAlert])
def list_alerts(
    supabase: Client = Depends(get_supabase),
    _: str = Depends(require_admin_token),
) -> List[AdminAlert]:
    now = _utc_now()
    alerts: list[AdminAlert] = []
    seen_ids: set[str] = set()

    try:
        sessions_result = (
            supabase.table("vishum_sessions")
            .select(
                "session_id,name,email,plan,status,last_ping_at,started_at,tokens_used,metadata,admin_note"
            )
            .limit(300)
            .execute()
        )

        for row in sessions_result.data or []:
            record = _normalize_record(row)
            status = (record.status or "").lower()
            last_ping_dt = _parse_datetime(record.last_ping_at)
            started_dt = _parse_datetime(record.started_at)

            if status == "limit":
                alert = _build_status_alert(
                    record,
                    "limit",
                    f'La sesión "{record.name or record.email or record.session_id}" alcanzó su cuota asignada.',
                    last_ping_dt or now,
                    "limit",
                    "Contactar",
                )
                if alert.id not in seen_ids:
                    alerts.append(alert)
                    seen_ids.add(alert.id)

            if status == "banned":
                alert = _build_status_alert(
                    record,
                    "warning",
                    f'Usuario "{record.email or record.name or record.session_id}" fue bloqueado por el equipo.',
                    last_ping_dt or now,
                    "banned",
                    "Revisar bloqueo",
                )
                if alert.id not in seen_ids:
                    alerts.append(alert)
                    seen_ids.add(alert.id)

            if status == "terminated":
                alert = _build_status_alert(
                    record,
                    "info",
                    f'Sesión "{record.name or record.email or record.session_id}" fue desconectada por un administrador.',
                    last_ping_dt or now,
                    "terminated",
                )
                if alert.id not in seen_ids:
                    alerts.append(alert)
                    seen_ids.add(alert.id)

            if status in ("active", "limit") and last_ping_dt:
                inactive_minutes = (now - last_ping_dt).total_seconds() / 60.0
                if inactive_minutes >= SESSION_INACTIVITY_ALERT_MINUTES:
                    alert = _build_status_alert(
                        record,
                        "warning",
                        f'Heartbeat perdido ({int(inactive_minutes)} min) para "{record.name or record.email or record.session_id}".',
                        last_ping_dt,
                        "inactive",
                        "Verificar conexión",
                    )
                    if alert.id not in seen_ids:
                        alerts.append(alert)
                        seen_ids.add(alert.id)

            tokens_used_value = 0
            if record.tokens_used is not None:
                try:
                    tokens_used_value = int(record.tokens_used)
                except (TypeError, ValueError):
                    tokens_used_value = 0

            if tokens_used_value >= SESSION_TOKEN_LIMIT and tokens_used_value > 0:
                alert = _build_status_alert(
                    record,
                    "warning",
                    f'Sesión "{record.name or record.email or record.session_id}" consumió {tokens_used_value} tokens.',
                    last_ping_dt or now,
                    "tokens",
                    "Evaluar upsell",
                )
                if alert.id not in seen_ids:
                    alerts.append(alert)
                    seen_ids.add(alert.id)

        events_result = (
            supabase.table("vishum_session_events")
            .select("session_id,event_type,created_at,payload")
            .gte("created_at", (now - timedelta(hours=24)).isoformat())
            .order("created_at", desc=True)
            .limit(100)
            .execute()
        )

        for event in events_result.data or []:
            event_type = event.get("event_type")
            session_id = event.get("session_id")
            created_at = _parse_datetime(event.get("created_at")) or now
            base_id = f"event-{event_type}-{session_id}-{created_at.isoformat()}"
            if base_id in seen_ids:
                continue

            if event_type == "admin_ban":
                alerts.append(
                    AdminAlert(
                        id=base_id,
                        type="warning",
                        message=f'Se aplicó un bloqueo manual a la sesión "{session_id}".',
                        created_at=created_at,
                        action="Revisar bloqueo",
                    )
                )
                seen_ids.add(base_id)
            elif event_type == "admin_disconnect":
                alerts.append(
                    AdminAlert(
                        id=base_id,
                        type="info",
                        message=f'Sesión "{session_id}" se desconectó manualmente.',
                        created_at=created_at,
                        action="Validar estado",
                    )
                )
                seen_ids.add(base_id)
            elif event_type == "heartbeat_timeout":
                alerts.append(
                    AdminAlert(
                        id=base_id,
                        type="warning",
                        message=f'Se detectó timeout de heartbeat en la sesión "{session_id}".',
                        created_at=created_at,
                        action="Revisar conexión",
                    )
                )
                seen_ids.add(base_id)

        alerts.sort(key=lambda item: item.created_at, reverse=True)
        return alerts[:5]
    except Exception as exc:
        import traceback
        traceback.print_exc()
        print("alert_generation_error", {"exc": str(exc)})
        raise HTTPException(status_code=500, detail=f"No se pudieron generar las alertas: {exc}") from exc


@router.get("/admin/banned", response_model=AdminBannedSessionsResponse)
def list_banned_sessions(
    limit: int = Query(DEFAULT_BANNED_LIMIT, ge=1, le=50),
    offset: int = Query(0, ge=0),
    start_date: Optional[str] = Query(None, description="Filtrar sesiones baneadas desde esta fecha (ISO8601)"),
    end_date: Optional[str] = Query(None, description="Filtrar sesiones baneadas hasta esta fecha (ISO8601)"),
    supabase: Client = Depends(get_supabase),
    _: str = Depends(require_admin_token),
) -> AdminBannedSessionsResponse:
    start_dt = _parse_datetime(start_date) if start_date else None
    end_dt = _parse_datetime(end_date) if end_date else None

    if start_dt and end_dt and end_dt < start_dt:
        raise HTTPException(status_code=400, detail="end_date debe ser posterior a start_date")

    try:
        query = (
            supabase.table("vishum_sessions")
            .select("*", count="exact")
            .eq("status", "banned")
            .order("last_ping_at", desc=True)
        )

        if start_dt:
            query = query.gte("last_ping_at", start_dt.isoformat())
        if end_dt:
            query = query.lte("last_ping_at", end_dt.isoformat())

        range_end = offset + limit - 1
        result = query.range(offset, range_end).execute()

        sessions = [_normalize_record(row) for row in result.data or []]
        total = result.count or 0

        return AdminBannedSessionsResponse(
            sessions=sessions,
            total=total,
            limit=limit,
            offset=offset,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"No se pudo obtener la lista de usuarios bloqueados: {exc}") from exc
