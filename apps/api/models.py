"""
Modelos Pydantic para validación de datos
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class EventCreate(BaseModel):
    """Modelo para crear un nuevo evento"""
    event_type: str = Field(..., description="Tipo de evento detectado")
    payload: Dict[str, Any] = Field(..., description="Payload con datos del evento")
    user_id: Optional[str] = Field(None, description="ID del usuario (opcional)")
    camera_id: Optional[str] = Field(None, description="ID de la cámara que generó el evento")


class Event(BaseModel):
    """Modelo de evento completo"""
    id: str = Field(..., description="UUID del evento")
    user_id: str = Field(..., description="ID del usuario")
    event_type: str = Field(..., description="Tipo de evento")
    payload: Dict[str, Any] = Field(..., description="Payload del evento")
    camera_id: Optional[str] = Field(None, description="ID de la cámara que generó el evento")
    created_at: datetime = Field(..., description="Fecha de creación")
    
    class Config:
        from_attributes = True


class EventStats(BaseModel):
    """Estadísticas de eventos"""
    total: int = Field(..., description="Total de eventos")
    by_type: Dict[str, int] = Field(..., description="Eventos agrupados por tipo")
    by_camera: Dict[str, int] = Field(default_factory=dict, description="Eventos agrupados por cámara")
    period_hours: int = Field(..., description="Período en horas")
    start_date: datetime = Field(..., description="Fecha de inicio")
    end_date: datetime = Field(..., description="Fecha de fin")
    hourly: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Conteo de eventos agrupados por hora",
    )


class AdminLoginRequest(BaseModel):
    """Credenciales para iniciar sesión en el panel admin"""
    username: str = Field(..., description="Usuario administrativo")
    password: str = Field(..., description="Contraseña administrativa")


class AdminLoginResponse(BaseModel):
    """Respuesta para inicio de sesión administrativo"""
    token: str = Field(..., description="Token que habilita solicitudes administrativas")
    username: str = Field(..., description="Nombre de usuario autenticado")


class HealthSummary(BaseModel):
    """Resumen de estado de salud"""
    total_detections: int = Field(..., description="Total de detecciones")
    emotions: Dict[str, int] = Field(..., description="Conteo de emociones")
    activities: Dict[str, int] = Field(..., description="Conteo de actividades")
    health_status: Dict[str, int] = Field(..., description="Conteo de estados de salud")
    alerts: List[str] = Field(default_factory=list, description="Alertas generadas")
    period_hours: int = Field(..., description="Período analizado")
    by_camera: Dict[str, int] = Field(default_factory=dict, description="Detecciones agrupadas por cámara")


class ReportRequest(BaseModel):
    """Solicitud de generación de reporte"""
    start_date: datetime = Field(..., description="Fecha de inicio")
    end_date: datetime = Field(..., description="Fecha de fin")
    format: str = Field("pdf", description="Formato del reporte (pdf, json)")
    include_charts: bool = Field(True, description="Incluir gráficas")
    user_id: Optional[str] = Field(None, description="ID del usuario")
    camera_id: Optional[str] = Field(None, description="ID de la cámara a filtrar")


class ReportResponse(BaseModel):
    """Respuesta con el reporte generado"""
    report_id: str = Field(..., description="ID del reporte")
    url: Optional[str] = Field(None, description="URL del reporte (si está disponible)")
    format: str = Field(..., description="Formato del reporte")
    created_at: datetime = Field(..., description="Fecha de creación")


class ExternalCameraBase(BaseModel):
    """Datos base de una cámara externa"""
    name: str = Field(..., description="Alias de la cámara")
    source_url: str = Field(..., description="URL RTSP/RTMP/HTTP de la cámara")
    username: Optional[str] = Field(None, description="Usuario para autenticación (opcional)")
    password: Optional[str] = Field(None, description="Password para autenticación (opcional)")


class ExternalCameraCreate(ExternalCameraBase):
    """Solicitud para registrar una cámara externa"""
    pass


class ExternalCamera(ExternalCameraBase):
    """Cámara externa registrada"""
    id: str
    user_id: str
    stream_id: Optional[str]
    hls_url: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ExternalCameraAction(BaseModel):
    """Acción para iniciar/detener cámara externa"""
    delete_stream: bool = Field(True, description="Eliminar archivos HLS al detener")


class SessionInitRequest(BaseModel):
    """Datos enviados al iniciar una sesión de demo"""
    session_id: str = Field(..., description="Identificador único de la sesión (UUID)")
    name: Optional[str] = Field(None, description="Nombre o alias del visitante")
    email: Optional[str] = Field(None, description="Correo de contacto")
    plan: Optional[str] = Field(None, description="Plan o preset seleccionado para la demo")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Información adicional capturada en el formulario"
    )


class SessionHeartbeatRequest(BaseModel):
    """Ping periódico desde el frontend para mantener la sesión activa"""
    session_id: str = Field(..., description="Identificador de la sesión")
    cameras_active: int = Field(0, description="Número de cámaras activas")
    fps_average: Optional[float] = Field(None, description="FPS promedio actual")
    tokens_used: Optional[int] = Field(None, description="Tokens consumidos/estimados")
    status: Optional[str] = Field(None, description="Estado reportado por el frontend (active, limit, etc.)")


class DemoSessionRecord(BaseModel):
    """Registro completo de una sesión en la plataforma"""
    session_id: str
    name: Optional[str]
    email: Optional[str]
    plan: Optional[str]
    organization: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    referer: Optional[str]
    cameras_active: Optional[int]
    fps_average: Optional[float]
    tokens_used: Optional[int]
    status: Optional[str]
    started_at: Optional[datetime]
    last_ping_at: Optional[datetime]
    admin_note: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class SessionInfo(BaseModel):
    """Detalle de una sesión para el panel admin"""
    session_id: str
    name: Optional[str]
    email: Optional[str]
    organization: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    cameras_active: int
    fps_average: float
    tokens_used: int
    status: str
    started_at: datetime
    last_ping_at: datetime
    duration_minutes: float


class SessionStartResponse(BaseModel):
    """Respuesta al iniciar una sesión"""
    session_id: str
    status: str
    started_at: datetime


class SessionHeartbeatResponse(BaseModel):
    """Respuesta al heartbeat de sesión"""
    status: str
    limit_reason: Optional[str] = None
    message: Optional[str] = None


class AdminSessionsSummary(BaseModel):
    """Resumen agregado para el panel administrativo"""
    active_sessions: int
    cameras_connected: int
    average_duration_minutes: float
    sessions_limit: int
    sessions_banned: int
    tokens_used: int


class AdminSessionsResponse(BaseModel):
    """Respuesta completa para el panel admin"""
    summary: AdminSessionsSummary
    sessions: List[DemoSessionRecord]
    generated_at: datetime


class AdminBannedSessionsResponse(BaseModel):
    """Sesiones con estado bloqueado (para panel admin)"""
    sessions: List[DemoSessionRecord]
    total: int
    limit: int
    offset: int


class AdminAlert(BaseModel):
    """Alerta administrativa para el panel"""
    id: str
    type: str
    message: str
    created_at: datetime
    action: Optional[str] = None


class SessionAdminActionRequest(BaseModel):
    """Payload genérico para acciones administrativas sobre una sesión"""
    reason: Optional[str] = Field(None, description="Motivo de la acción aplicada")

