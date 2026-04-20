#!/usr/bin/env python3
"""
NXT Telemetry - Sistema de Analytics del Framework
===================================================
Captura métricas de uso: quién, cuándo, qué agentes, cuánto tiempo.

Componentes:
- Identificación de usuario (git config / env / OS)
- Logging local en JSONL (append-only)
- Webhook central opcional (opt-in, fire-and-forget)
- CLI para stats, flush, prune

Versión: 3.8.0
"""

import json
import os
import platform
import subprocess
import sys
import hashlib
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from collections import Counter, defaultdict

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

@dataclass
class TelemetryConfig:
    """Configuración de telemetría cargada desde nxt.config.yaml."""
    habilitado: bool = True
    # Supabase (central, en tiempo real)
    supabase_habilitado: bool = True
    supabase_url: str = "https://nxtsupabase.gruponxt.dev"
    supabase_anon_key: str = os.environ.get("NXT_SUPABASE_ANON_KEY", "")
    supabase_service_key: str = os.environ.get("NXT_SUPABASE_SERVICE_KEY", "")
    supabase_timeout: int = 3
    # Webhook genérico (legacy)
    webhook_habilitado: bool = False
    webhook_url: str = ""
    webhook_batch_size: int = 50
    webhook_timeout: int = 3
    # Local
    archivo: str = ".nxt/telemetry.jsonl"
    max_size_mb: int = 50
    retention_days: int = 90
    identity_source: str = "auto"
    anonimizar_email: bool = False
    excluir_task_content: bool = False

    @classmethod
    def load(cls, root: Path = None) -> "TelemetryConfig":
        """Carga config desde nxt.config.yaml."""
        if root is None:
            root = Path.cwd()

        config_file = root / ".nxt" / "nxt.config.yaml"
        if not config_file.exists():
            return cls()

        try:
            import yaml
            data = yaml.safe_load(config_file.read_text(encoding="utf-8"))
            tel = data.get("telemetria", {})
            webhook = tel.get("webhook", {})
            local = tel.get("local", {})
            privacy = tel.get("privacidad", {})
            identity = tel.get("identity", {})

            supabase = tel.get("supabase", {})

            return cls(
                habilitado=tel.get("habilitado", True),
                supabase_habilitado=supabase.get("habilitado", True),
                supabase_url=supabase.get("url", cls.supabase_url),
                supabase_anon_key=supabase.get("anon_key", cls.supabase_anon_key),
                supabase_service_key=supabase.get("service_key", cls.supabase_service_key),
                supabase_timeout=supabase.get("timeout_seconds", 3),
                webhook_habilitado=webhook.get("habilitado", False),
                webhook_url=webhook.get("url", ""),
                webhook_batch_size=webhook.get("batch_size", 50),
                webhook_timeout=webhook.get("timeout_seconds", 3),
                archivo=local.get("archivo", ".nxt/telemetry.jsonl"),
                max_size_mb=local.get("max_size_mb", 50),
                retention_days=local.get("retention_days", 90),
                identity_source=identity.get("source", "auto"),
                anonimizar_email=privacy.get("anonimizar_email", False),
                excluir_task_content=privacy.get("excluir_task_content", False),
            )
        except Exception:
            return cls()


# =============================================================================
# IDENTIFICACIÓN DE USUARIO
# =============================================================================

_cached_identity: Optional[dict] = None


def _run_git_config(key: str) -> str:
    """Ejecuta git config y retorna el valor."""
    try:
        result = subprocess.run(
            ["git", "config", "--get", key],
            capture_output=True, text=True, timeout=3
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def identify_user(root: Path = None, source: str = "auto") -> dict:
    """
    Identifica al usuario actual.

    Orden de resolución:
    1. Cache en memoria
    2. Cache en archivo (.nxt/telemetry-identity.json)
    3. git config user.name / user.email
    4. Variable de entorno NXT_USER
    5. OS username + machine name
    """
    global _cached_identity
    if _cached_identity is not None:
        return _cached_identity

    if root is None:
        root = Path.cwd()

    # Intentar cache en archivo
    identity_file = root / ".nxt" / "telemetry-identity.json"
    if identity_file.exists():
        try:
            cached = json.loads(identity_file.read_text(encoding="utf-8"))
            if cached.get("name") and cached.get("ts"):
                # Cache válido por 24 horas
                cached_ts = datetime.fromisoformat(cached["ts"])
                if datetime.now() - cached_ts < timedelta(hours=24):
                    _cached_identity = cached
                    return cached
        except Exception:
            pass

    # Resolver identidad
    identity = {
        "name": "",
        "email": "",
        "os_user": "",
        "machine": platform.node(),
        "ts": datetime.now().isoformat(),
    }

    # OS username
    try:
        identity["os_user"] = os.getlogin()
    except Exception:
        identity["os_user"] = os.environ.get("USERNAME", os.environ.get("USER", "unknown"))

    if source in ("auto", "git"):
        git_name = _run_git_config("user.name")
        git_email = _run_git_config("user.email")
        if git_name:
            identity["name"] = git_name
        if git_email:
            identity["email"] = git_email

    if source in ("auto", "env"):
        env_user = os.environ.get("NXT_USER", "")
        if env_user and not identity["name"]:
            identity["name"] = env_user

    # Fallback a OS user
    if not identity["name"]:
        identity["name"] = identity["os_user"]

    # Guardar cache
    try:
        identity_file.parent.mkdir(parents=True, exist_ok=True)
        identity_file.write_text(json.dumps(identity, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

    _cached_identity = identity
    return identity


def _hash_email(email: str) -> str:
    """SHA-256 del email para anonimización."""
    return hashlib.sha256(email.encode()).hexdigest()[:16] if email else ""


# =============================================================================
# SESSION TRACKING
# =============================================================================

_session_id: Optional[str] = None


def get_session_id() -> str:
    """Retorna o genera un session ID para la sesión actual."""
    global _session_id
    if _session_id is None:
        _session_id = uuid.uuid4().hex[:12]
    return _session_id


# =============================================================================
# EVENT TRACKING (CORE)
# =============================================================================

def track(event: str, data: dict = None, duration_ms: int = None,
          root: Path = None, config: TelemetryConfig = None):
    """
    Registra un evento de telemetría.

    Args:
        event: Tipo de evento (session_start, user_message, agent_activated, etc.)
        data: Datos adicionales del evento
        duration_ms: Duración en milisegundos (opcional)
        root: Raíz del proyecto
        config: Configuración de telemetría
    """
    if root is None:
        root = Path.cwd()
    if config is None:
        config = TelemetryConfig.load(root)

    if not config.habilitado:
        return

    user = identify_user(root, config.identity_source)
    project_name = _detect_project_name(root)

    record = {
        "v": 1,
        "ts": datetime.now().isoformat(),
        "event": event,
        "user": {
            "name": user.get("name", ""),
            "email": user.get("email", ""),
            "os_user": user.get("os_user", ""),
            "machine": user.get("machine", ""),
        },
        "session_id": get_session_id(),
        "project": project_name,
        "fw_version": "3.8.0",
        "data": data or {},
    }

    if duration_ms is not None:
        record["duration_ms"] = duration_ms

    # Anonimización si está configurada
    if config.anonimizar_email and record["user"]["email"]:
        record["user"]["email"] = _hash_email(record["user"]["email"])

    if config.excluir_task_content and "task" in record.get("data", {}):
        record["data"]["task"] = "[redacted]"

    # Escribir localmente
    _append_event(root, config, record)

    # Enviar a Supabase (síncrono con timeout corto, fire-and-forget)
    if config.supabase_habilitado:
        _send_to_supabase(config, record)


def _detect_project_name(root: Path) -> str:
    """Detecta el nombre del proyecto."""
    # package.json
    pkg = root / "package.json"
    if pkg.exists():
        try:
            return json.loads(pkg.read_text(encoding="utf-8")).get("name", root.name)
        except Exception:
            pass

    # pyproject.toml
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8")
            for line in content.split("\n"):
                if line.strip().startswith("name"):
                    return line.split("=")[1].strip().strip('"').strip("'")
        except Exception:
            pass

    return root.name


def _append_event(root: Path, config: TelemetryConfig, record: dict):
    """Escribe un evento al archivo JSONL con file locking."""
    telemetry_file = root / config.archivo
    telemetry_file.parent.mkdir(parents=True, exist_ok=True)

    line = json.dumps(record, ensure_ascii=False) + "\n"

    # Verificar rotación
    if telemetry_file.exists():
        size_mb = telemetry_file.stat().st_size / (1024 * 1024)
        if size_mb >= config.max_size_mb:
            _rotate_file(telemetry_file)

    # Append con locking
    try:
        if platform.system() == "Windows":
            _append_windows(telemetry_file, line)
        else:
            _append_unix(telemetry_file, line)
    except Exception:
        # Fallback sin locking
        with open(telemetry_file, "a", encoding="utf-8") as f:
            f.write(line)


def _append_windows(filepath: Path, line: str):
    """Append con locking en Windows usando msvcrt."""
    import msvcrt
    with open(filepath, "a", encoding="utf-8") as f:
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
        try:
            f.write(line)
        finally:
            try:
                f.seek(0, 2)  # seek to end
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            except Exception:
                pass


def _append_unix(filepath: Path, line: str):
    """Append con locking en Unix usando fcntl."""
    import fcntl
    with open(filepath, "a", encoding="utf-8") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.write(line)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def _rotate_file(filepath: Path):
    """Rota el archivo JSONL cuando excede el tamaño máximo."""
    rotated = filepath.with_suffix(f".{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl")
    try:
        filepath.rename(rotated)
    except Exception:
        pass


# =============================================================================
# SUPABASE (CENTRAL, REAL-TIME)
# =============================================================================

def _send_to_supabase(config: TelemetryConfig, record: dict):
    """
    Envía un evento a Supabase via pg-meta SQL endpoint.
    Usa pg-meta en lugar de PostgREST porque el pgbouncer en modo transacción
    no permite NOTIFY para recargar el schema cache de PostgREST.
    Se ejecuta en un thread daemon para no bloquear el hook.
    Reintenta hasta 3 veces (conexión intermitente por pool de pgbouncer).
    """
    try:
        import urllib.request

        data = record.get("data", {})
        user = record.get("user", {})

        # Escapar comillas simples para SQL
        def esc(val):
            if val is None:
                return "NULL"
            return "'" + str(val).replace("'", "''") + "'"

        extra = {
            k: v for k, v in data.items()
            if k not in ("agent", "phase", "task_scale", "command", "task",
                         "step", "total_steps", "artifacts") and v is not None
        }

        # Construir columnas y valores dinámicamente
        cols = ["event_type", "event_ts", "session_id", "fw_version",
                "user_name", "user_email", "user_os", "user_machine",
                "project_name", "extra_data"]
        vals = [
            esc(record.get("event", "unknown")),
            esc(record.get("ts")),
            esc(record.get("session_id")),
            esc(record.get("fw_version", "3.8.0")),
            esc(user.get("name", "")),
            esc(user.get("email", "")),
            esc(user.get("os_user", "")),
            esc(user.get("machine", "")),
            esc(record.get("project", "")),
            esc(json.dumps(extra, ensure_ascii=False)) + "::jsonb",
        ]

        # Agregar campos opcionales
        optional = {
            "agent": data.get("agent"),
            "phase": data.get("phase"),
            "task_scale": data.get("task_scale"),
            "command": data.get("command"),
            "task": data.get("task"),
            "step": data.get("step"),
            "total_steps": data.get("total_steps"),
            "artifacts_count": data.get("artifacts"),
            "duration_ms": record.get("duration_ms"),
            "input_length": data.get("input_length"),
            "is_slash_command": data.get("is_slash_command"),
        }
        for col, val in optional.items():
            if val is not None:
                cols.append(col)
                if isinstance(val, bool):
                    vals.append("true" if val else "false")
                elif isinstance(val, int):
                    vals.append(str(val))
                else:
                    vals.append(esc(val))

        sql = f"INSERT INTO public.nxt_devai_telemetry ({', '.join(cols)}) VALUES ({', '.join(vals)})"

        url = f"{config.supabase_url.rstrip('/')}/pg/query"
        payload = json.dumps({"query": sql}, ensure_ascii=False).encode("utf-8")

        # Reintentar hasta 3 veces (conexión intermitente por pgbouncer)
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, data=payload, method="POST")
                req.add_header("Content-Type", "application/json")
                req.add_header("apikey", config.supabase_service_key)
                req.add_header("Authorization", f"Bearer {config.supabase_service_key}")

                with urllib.request.urlopen(req, timeout=config.supabase_timeout) as resp:
                    body = resp.read().decode("utf-8")
                    if "error" not in body.lower():
                        return  # Success
            except Exception:
                pass
    except Exception:
        pass  # Fire-and-forget: nunca bloquea ni falla


def supabase_test_connection(config: TelemetryConfig = None) -> dict:
    """Prueba la conexión a Supabase insertando y leyendo un evento de test."""
    if config is None:
        config = TelemetryConfig.load()

    try:
        import urllib.request

        url = f"{config.supabase_url.rstrip('/')}/pg/query"

        # Intentar SELECT
        for attempt in range(5):
            try:
                payload = json.dumps({
                    "query": "SELECT COUNT(*) as total FROM public.nxt_devai_telemetry"
                }).encode("utf-8")

                req = urllib.request.Request(url, data=payload, method="POST")
                req.add_header("Content-Type", "application/json")
                req.add_header("apikey", config.supabase_service_key)
                req.add_header("Authorization", f"Bearer {config.supabase_service_key}")

                with urllib.request.urlopen(req, timeout=5) as resp:
                    body = resp.read().decode("utf-8")
                    if "error" not in body.lower():
                        data = json.loads(body)
                        return {"status": "ok", "total_events": data[0]["total"] if data else 0}
            except Exception:
                pass

        return {"status": "error", "message": "No se pudo conectar después de 5 intentos"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def supabase_get_stats(config: TelemetryConfig = None, days: int = 30) -> dict:
    """Obtiene estadísticas desde Supabase via pg-meta SQL."""
    if config is None:
        config = TelemetryConfig.load()

    try:
        import urllib.request

        url = f"{config.supabase_url.rstrip('/')}/pg/query"
        sql = f"SELECT nxt_devai_telemetry_summary({days})"

        for attempt in range(5):
            try:
                payload = json.dumps({"query": sql}).encode("utf-8")
                req = urllib.request.Request(url, data=payload, method="POST")
                req.add_header("Content-Type", "application/json")
                req.add_header("apikey", config.supabase_service_key)
                req.add_header("Authorization", f"Bearer {config.supabase_service_key}")

                with urllib.request.urlopen(req, timeout=10) as resp:
                    body = resp.read().decode("utf-8")
                    if "error" not in body.lower():
                        data = json.loads(body)
                        if data and "nxt_telemetry_summary" in data[0]:
                            return data[0]["nxt_telemetry_summary"]
                        return data
            except Exception:
                pass

        return {"error": "No se pudo conectar después de 5 intentos"}
    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# WEBHOOK (LEGACY CENTRAL REPORTING)
# =============================================================================

def flush_to_webhook(root: Path = None, config: TelemetryConfig = None) -> dict:
    """
    Envía eventos pendientes al webhook central.

    Retorna: {"sent": N, "errors": N, "total_pending": N}
    """
    if root is None:
        root = Path.cwd()
    if config is None:
        config = TelemetryConfig.load(root)

    if not config.webhook_habilitado or not config.webhook_url:
        return {"sent": 0, "errors": 0, "message": "Webhook no configurado"}

    telemetry_file = root / config.archivo
    cursor_file = root / ".nxt" / "telemetry-cursor.json"

    if not telemetry_file.exists():
        return {"sent": 0, "errors": 0, "total_pending": 0}

    # Leer cursor
    last_synced = 0
    if cursor_file.exists():
        try:
            cursor = json.loads(cursor_file.read_text(encoding="utf-8"))
            last_synced = cursor.get("last_synced_line", 0)
        except Exception:
            pass

    # Leer eventos nuevos
    events = []
    line_num = 0
    with open(telemetry_file, "r", encoding="utf-8") as f:
        for line in f:
            line_num += 1
            if line_num <= last_synced:
                continue
            try:
                events.append(json.loads(line.strip()))
            except Exception:
                continue

    if not events:
        return {"sent": 0, "errors": 0, "total_pending": 0}

    # Enviar en batches
    sent = 0
    errors = 0
    for i in range(0, len(events), config.webhook_batch_size):
        batch = events[i:i + config.webhook_batch_size]
        payload = {
            "framework_version": "3.8.0",
            "batch_id": uuid.uuid4().hex,
            "sent_at": datetime.now().isoformat(),
            "events_count": len(batch),
            "events": batch,
        }

        try:
            import urllib.request
            req = urllib.request.Request(
                config.webhook_url,
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=config.webhook_timeout) as resp:
                if 200 <= resp.status < 300:
                    sent += len(batch)
                    last_synced += len(batch)
                else:
                    errors += len(batch)
        except Exception:
            errors += len(batch)

    # Actualizar cursor
    if sent > 0:
        try:
            cursor_file.write_text(
                json.dumps({"last_synced_line": last_synced}, ensure_ascii=False),
                encoding="utf-8"
            )
        except Exception:
            pass

    return {
        "sent": sent,
        "errors": errors,
        "total_pending": len(events) - sent,
    }


# =============================================================================
# STATS & ANALYTICS
# =============================================================================

def get_local_stats(root: Path = None, days: int = 30,
                    user_filter: str = None) -> dict:
    """
    Genera estadísticas de uso local.

    Args:
        root: Raíz del proyecto
        days: Días a incluir (default 30)
        user_filter: Filtrar por nombre de usuario

    Returns:
        dict con estadísticas agregadas
    """
    if root is None:
        root = Path.cwd()

    config = TelemetryConfig.load(root)
    telemetry_file = root / config.archivo

    if not telemetry_file.exists():
        return {"message": "No hay datos de telemetría", "total_events": 0}

    cutoff = datetime.now() - timedelta(days=days)
    events = []

    with open(telemetry_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                evt = json.loads(line.strip())
                evt_ts = datetime.fromisoformat(evt["ts"])
                if evt_ts < cutoff:
                    continue
                if user_filter:
                    user = evt.get("user", {})
                    if (user_filter.lower() not in user.get("name", "").lower() and
                            user_filter.lower() not in user.get("email", "").lower() and
                            user_filter.lower() not in user.get("os_user", "").lower()):
                        continue
                events.append(evt)
            except Exception:
                continue

    if not events:
        return {"message": "No hay eventos en el periodo", "total_events": 0, "days": days}

    # Agregar estadísticas
    users = Counter()
    agents = Counter()
    event_types = Counter()
    projects = Counter()
    daily = Counter()
    sessions = set()
    user_details = {}

    for evt in events:
        user = evt.get("user", {})
        user_key = user.get("name", user.get("os_user", "unknown"))
        users[user_key] += 1
        user_details[user_key] = user.get("email", "")

        data = evt.get("data", {})
        agent = data.get("agent")
        if agent:
            agents[agent] += 1

        event_types[evt.get("event", "unknown")] += 1
        projects[evt.get("project", "unknown")] += 1

        day = evt["ts"][:10]
        daily[day] += 1

        sid = evt.get("session_id", "")
        if sid:
            sessions.add(f"{user_key}:{sid}")

    # Calcular duración de sesiones
    session_events = defaultdict(list)
    for evt in events:
        user = evt.get("user", {})
        user_key = user.get("name", user.get("os_user", "unknown"))
        sid = evt.get("session_id", "")
        if sid:
            session_events[f"{user_key}:{sid}"].append(evt["ts"])

    session_durations = []
    for key, timestamps in session_events.items():
        if len(timestamps) >= 2:
            sorted_ts = sorted(timestamps)
            start = datetime.fromisoformat(sorted_ts[0])
            end = datetime.fromisoformat(sorted_ts[-1])
            duration_min = (end - start).total_seconds() / 60
            if duration_min > 0:
                session_durations.append(duration_min)

    avg_duration = sum(session_durations) / len(session_durations) if session_durations else 0

    return {
        "period_days": days,
        "total_events": len(events),
        "total_sessions": len(sessions),
        "avg_session_minutes": round(avg_duration, 1),
        "users": {
            name: {"messages": count, "email": user_details.get(name, "")}
            for name, count in users.most_common()
        },
        "top_agents": dict(agents.most_common(15)),
        "event_types": dict(event_types.most_common()),
        "projects": dict(projects.most_common(10)),
        "daily_activity": dict(sorted(daily.items(), reverse=True)[:30]),
    }


def format_stats_table(stats: dict) -> str:
    """Formatea estadísticas para output en terminal."""
    if stats.get("total_events", 0) == 0:
        return f"\n  {stats.get('message', 'Sin datos')}\n"

    lines = []
    lines.append("")
    lines.append("=" * 60)
    lines.append("  NXT TELEMETRY - Estadísticas de Uso")
    lines.append("=" * 60)
    lines.append(f"  Periodo: últimos {stats['period_days']} días")
    lines.append(f"  Total eventos: {stats['total_events']}")
    lines.append(f"  Sesiones: {stats['total_sessions']}")
    lines.append(f"  Duración promedio: {stats['avg_session_minutes']} min")

    # Usuarios
    lines.append("")
    lines.append("  USUARIOS")
    lines.append("  " + "-" * 50)
    for name, info in stats.get("users", {}).items():
        email = f" ({info['email']})" if info.get("email") else ""
        lines.append(f"    {name}{email}  {info['messages']} mensajes")

    # Agentes
    lines.append("")
    lines.append("  TOP AGENTES")
    lines.append("  " + "-" * 50)
    max_count = max(stats.get("top_agents", {}).values(), default=1)
    for agent, count in stats.get("top_agents", {}).items():
        bar_len = int((count / max_count) * 20)
        bar = "█" * bar_len
        lines.append(f"    {agent:<22} {bar} {count}")

    # Actividad diaria
    lines.append("")
    lines.append("  ACTIVIDAD DIARIA")
    lines.append("  " + "-" * 50)
    daily = stats.get("daily_activity", {})
    max_daily = max(daily.values(), default=1)
    for day, count in list(daily.items())[:14]:
        try:
            weekday = datetime.fromisoformat(day).strftime("%a")
        except Exception:
            weekday = "???"
        bar_len = int((count / max_daily) * 25)
        bar = "█" * bar_len
        lines.append(f"    {day} {weekday}  {bar} {count}")

    # Proyectos
    if len(stats.get("projects", {})) > 1:
        lines.append("")
        lines.append("  PROYECTOS")
        lines.append("  " + "-" * 50)
        for proj, count in stats.get("projects", {}).items():
            lines.append(f"    {proj:<30} {count} eventos")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


# =============================================================================
# PRUNE (LIMPIEZA)
# =============================================================================

def prune_events(root: Path = None, config: TelemetryConfig = None) -> dict:
    """Elimina eventos más antiguos que retention_days."""
    if root is None:
        root = Path.cwd()
    if config is None:
        config = TelemetryConfig.load(root)

    telemetry_file = root / config.archivo
    if not telemetry_file.exists():
        return {"pruned": 0, "kept": 0}

    cutoff = datetime.now() - timedelta(days=config.retention_days)
    kept = []
    pruned = 0

    with open(telemetry_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                evt = json.loads(line.strip())
                evt_ts = datetime.fromisoformat(evt["ts"])
                if evt_ts >= cutoff:
                    kept.append(line)
                else:
                    pruned += 1
            except Exception:
                kept.append(line)  # Mantener líneas no parseables

    if pruned > 0:
        with open(telemetry_file, "w", encoding="utf-8") as f:
            f.writelines(kept)

    return {"pruned": pruned, "kept": len(kept)}


# =============================================================================
# STATUS
# =============================================================================

def get_telemetry_status(root: Path = None) -> dict:
    """Retorna el estado actual de la configuración de telemetría."""
    if root is None:
        root = Path.cwd()

    config = TelemetryConfig.load(root)
    telemetry_file = root / config.archivo
    cursor_file = root / ".nxt" / "telemetry-cursor.json"

    # Contar eventos
    total_events = 0
    if telemetry_file.exists():
        with open(telemetry_file, "r", encoding="utf-8") as f:
            total_events = sum(1 for _ in f)

    # Cursor
    synced = 0
    if cursor_file.exists():
        try:
            synced = json.loads(cursor_file.read_text(encoding="utf-8")).get("last_synced_line", 0)
        except Exception:
            pass

    # File size
    file_size_mb = 0
    if telemetry_file.exists():
        file_size_mb = round(telemetry_file.stat().st_size / (1024 * 1024), 2)

    user = identify_user(root, config.identity_source)

    return {
        "habilitado": config.habilitado,
        "webhook": {
            "habilitado": config.webhook_habilitado,
            "url": config.webhook_url[:30] + "..." if len(config.webhook_url) > 30 else config.webhook_url,
        },
        "local": {
            "archivo": config.archivo,
            "total_events": total_events,
            "synced_events": synced,
            "pending_sync": total_events - synced,
            "file_size_mb": file_size_mb,
            "max_size_mb": config.max_size_mb,
            "retention_days": config.retention_days,
        },
        "usuario_actual": {
            "name": user.get("name", ""),
            "email": user.get("email", ""),
            "machine": user.get("machine", ""),
        },
        "privacidad": {
            "anonimizar_email": config.anonimizar_email,
            "excluir_task_content": config.excluir_task_content,
        },
    }


# =============================================================================
# CLI INTERFACE
# =============================================================================

def cli_main():
    """Punto de entrada CLI standalone."""
    import argparse

    parser = argparse.ArgumentParser(
        description="NXT Telemetry - Analytics de uso del framework"
    )
    parser.add_argument("action", nargs="?", default="stats",
                        choices=["stats", "flush", "status", "prune", "identify"],
                        help="Acción a ejecutar")
    parser.add_argument("--days", type=int, default=30,
                        help="Días a incluir en stats (default: 30)")
    parser.add_argument("--user", default=None,
                        help="Filtrar por nombre de usuario")
    parser.add_argument("--json", action="store_true",
                        help="Output en formato JSON")

    args = parser.parse_args()
    root = Path.cwd()

    if args.action == "stats":
        stats = get_local_stats(root, days=args.days, user_filter=args.user)
        if args.json:
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        else:
            print(format_stats_table(stats))

    elif args.action == "flush":
        result = flush_to_webhook(root)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.action == "status":
        status = get_telemetry_status(root)
        if args.json:
            print(json.dumps(status, indent=2, ensure_ascii=False))
        else:
            print("\n" + "=" * 60)
            print("  NXT TELEMETRY - Estado")
            print("=" * 60)
            print(f"  Habilitado: {status['habilitado']}")
            print(f"  Usuario: {status['usuario_actual']['name']} ({status['usuario_actual']['email']})")
            print(f"  Machine: {status['usuario_actual']['machine']}")
            print(f"\n  LOCAL:")
            print(f"    Archivo: {status['local']['archivo']}")
            print(f"    Eventos: {status['local']['total_events']}")
            print(f"    Tamaño: {status['local']['file_size_mb']} MB / {status['local']['max_size_mb']} MB")
            print(f"    Retención: {status['local']['retention_days']} días")
            print(f"\n  WEBHOOK:")
            print(f"    Habilitado: {status['webhook']['habilitado']}")
            print(f"    URL: {status['webhook']['url'] or '(no configurado)'}")
            print(f"    Pendientes sync: {status['local']['pending_sync']}")
            print(f"\n  PRIVACIDAD:")
            print(f"    Anonimizar email: {status['privacidad']['anonimizar_email']}")
            print(f"    Excluir contenido: {status['privacidad']['excluir_task_content']}")
            print("=" * 60)

    elif args.action == "prune":
        result = prune_events(root)
        print(f"Pruned: {result['pruned']} eventos eliminados, {result['kept']} conservados")

    elif args.action == "identify":
        user = identify_user(root)
        print(json.dumps(user, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    cli_main()
