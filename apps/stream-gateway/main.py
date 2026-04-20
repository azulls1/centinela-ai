import asyncio
import os
import shutil
import signal
import subprocess
import uuid
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator


class StreamRequest(BaseModel):
    source_url: str
    stream_id: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    hls_time: int = 2
    hls_list_size: int = 6

    @field_validator("hls_time", "hls_list_size")
    @classmethod
    def positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Value must be positive")
        return v


class StreamResponse(BaseModel):
    stream_id: str
    hls_url: str
    status: str


class StopRequest(BaseModel):
    delete_files: bool = True


STREAM_ROOT = Path(os.getenv("STREAM_GATEWAY_STREAMS_DIR", "./streams")).resolve()
STREAM_ROOT.mkdir(parents=True, exist_ok=True)

FFMPEG_BINARY = os.getenv("STREAM_GATEWAY_FFMPEG_PATH", "ffmpeg")
BASE_URL = (
    os.getenv("STREAM_GATEWAY_PUBLIC_BASE_URL")
    or os.getenv("STREAM_GATEWAY_BASE_URL")
    or "http://localhost:9302"
)


class StreamProcess:
    def __init__(self, stream_id: str, process: subprocess.Popen):
        self.stream_id = stream_id
        self.process = process
        self.created_at = asyncio.get_event_loop().time()

    def stop(self):
        if self.process.poll() is None:
            self.process.send_signal(signal.SIGTERM)
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()


STREAM_PROCESSES: Dict[str, StreamProcess] = {}

app = FastAPI(
    title="Stream Gateway",
    description="Convierte fuentes RTSP/HTTP en HLS reproducible por el navegador",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/streams", StaticFiles(directory=STREAM_ROOT, html=False), name="streams")


def build_authenticated_url(source_url: str, username: Optional[str], password: Optional[str]) -> str:
    if username and password and "://" in source_url and "@" not in source_url:
        scheme, rest = source_url.split("://", 1)
        return f"{scheme}://{username}:{password}@{rest}"
    return str(source_url)


def build_ffmpeg_command(target_dir: Path, source_url: str, request: StreamRequest) -> list[str]:
    playlist = target_dir / "index.m3u8"
    segment_pattern = target_dir / "segment_%05d.ts"
    return [
        FFMPEG_BINARY,
        "-i",
        source_url,
        "-rtsp_transport",
        "tcp",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-hls_time",
        str(request.hls_time),
        "-hls_list_size",
        str(request.hls_list_size),
        "-hls_flags",
        "delete_segments+omit_endlist",
        "-hls_segment_filename",
        str(segment_pattern),
        str(playlist),
    ]


def ensure_stream_id(stream_id: Optional[str]) -> str:
    if stream_id:
        return stream_id
    return str(uuid.uuid4())


def get_stream_directory(stream_id: str) -> Path:
    return STREAM_ROOT / stream_id


def hls_public_url(stream_id: str) -> str:
    return f"{BASE_URL.rstrip('/')}/streams/{stream_id}/index.m3u8"


def cleanup_stream(stream_id: str, delete_files: bool = True):
    process = STREAM_PROCESSES.pop(stream_id, None)
    if process:
        process.stop()
    if delete_files:
        stream_dir = get_stream_directory(stream_id)
        if stream_dir.exists():
            shutil.rmtree(stream_dir, ignore_errors=True)


@app.post("/streams", response_model=StreamResponse)
async def start_stream(request: StreamRequest):
    stream_id = ensure_stream_id(request.stream_id)

    if stream_id in STREAM_PROCESSES:
        raise HTTPException(status_code=409, detail="Stream already running")

    stream_dir = get_stream_directory(stream_id)
    stream_dir.mkdir(parents=True, exist_ok=True)

    source_url = build_authenticated_url(request.source_url, request.username, request.password)
    command = build_ffmpeg_command(stream_dir, source_url, request)

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        cleanup_stream(stream_id)
        raise HTTPException(status_code=500, detail=f"ffmpeg not found: {exc}") from exc
    except Exception as exc:
        cleanup_stream(stream_id)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    STREAM_PROCESSES[stream_id] = StreamProcess(stream_id, process)
    return StreamResponse(stream_id=stream_id, hls_url=hls_public_url(stream_id), status="starting")


@app.delete("/streams/{stream_id}")
async def stop_stream(stream_id: str, request: StopRequest):
    if stream_id not in STREAM_PROCESSES and not get_stream_directory(stream_id).exists():
        raise HTTPException(status_code=404, detail="Stream not found")

    cleanup_stream(stream_id, delete_files=request.delete_files)
    return JSONResponse({"stream_id": stream_id, "status": "stopped"})


@app.get("/streams/{stream_id}/status", response_model=StreamResponse)
async def stream_status(stream_id: str):
    process = STREAM_PROCESSES.get(stream_id)
    status = "stopped"
    if process:
        status = "running" if process.process.poll() is None else "stopped"
        if status == "stopped":
            cleanup_stream(stream_id, delete_files=False)

    stream_dir = get_stream_directory(stream_id)
    if not stream_dir.exists():
        raise HTTPException(status_code=404, detail="Stream not found")

    return StreamResponse(stream_id=stream_id, hls_url=hls_public_url(stream_id), status=status)


@app.get("/health")
async def health():
    return {"status": "ok", "active_streams": len(STREAM_PROCESSES)}


