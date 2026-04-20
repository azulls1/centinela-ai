"""
Router para gestionar cámaras externas (RTSP/HTTP) integradas al gateway de streaming
"""

import os
import uuid
from typing import Optional

import requests
from fastapi import APIRouter, HTTPException, Depends

from models import ExternalCameraCreate, ExternalCamera, ExternalCameraAction
from supabase_client import get_supabase_client, Client

GATEWAY_URL = (
    os.getenv("STREAM_GATEWAY_URL")
    or os.getenv("STREAM_GATEWAY_API_URL")
    or os.getenv("STREAM_GATEWAY_BASE_URL")
    or "http://localhost:9302"
)

router = APIRouter()


def gateway_request(method: str, path: str, json: Optional[dict] = None):
    url = f"{GATEWAY_URL.rstrip('/')}{path}"
    try:
        response = requests.request(method, url, json=json, timeout=15)
        response.raise_for_status()
        if response.content:
            return response.json()
        return None
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Stream Gateway error: {exc}") from exc


def get_supabase() -> Client:
    return get_supabase_client()


@router.get("/", response_model=list[ExternalCamera])
@router.get("", response_model=list[ExternalCamera], include_in_schema=False)
def list_external_cameras(supabase: Client = Depends(get_supabase)):
    result = supabase.table("vishum_external_cameras").select("*").execute()
    data = result.data or []
    return data


@router.post("/", response_model=ExternalCamera, status_code=201)
@router.post("", response_model=ExternalCamera, status_code=201, include_in_schema=False)
def create_external_camera(
    payload: ExternalCameraCreate,
    supabase: Client = Depends(get_supabase),
):
    user_id = "anonymous"
    stream_id = str(uuid.uuid4())

    gateway_payload = {
        "source_url": payload.source_url,
        "stream_id": stream_id,
        "username": payload.username,
        "password": payload.password,
    }
    gateway_response = gateway_request("POST", "/streams", json=gateway_payload)

    insert_payload = {
        "user_id": user_id,
        "name": payload.name,
        "source_url": payload.source_url,
        "auth_username": payload.username,
        "auth_password": payload.password,
        "stream_id": gateway_response["stream_id"],
        "hls_url": gateway_response["hls_url"],
        "status": gateway_response.get("status", "starting"),
    }

    result = supabase.table("vishum_external_cameras").insert(insert_payload).select("*").execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="No se pudo guardar la cámara en la base de datos")
    return result.data[0]


@router.post("/{camera_id}/start", response_model=ExternalCamera)
def start_external_camera(camera_id: str, supabase: Client = Depends(get_supabase)):
    result = (
        supabase.table("vishum_external_cameras")
        .select("*")
        .eq("id", camera_id)
        .single()
        .execute()
    )
    camera = result.data
    if not camera:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")

    stream_id = camera.get("stream_id") or str(uuid.uuid4())
    gateway_payload = {
        "source_url": camera["source_url"],
        "stream_id": stream_id,
        "username": camera.get("auth_username"),
        "password": camera.get("auth_password"),
    }
    gateway_response = gateway_request("POST", "/streams", json=gateway_payload)

    update_payload = {
        "stream_id": gateway_response["stream_id"],
        "hls_url": gateway_response["hls_url"],
        "status": gateway_response.get("status", "starting"),
    }
    updated = (
        supabase.table("vishum_external_cameras")
        .update(update_payload)
        .eq("id", camera_id)
        .select("*")
        .single()
        .execute()
    )
    return updated.data


@router.post("/{camera_id}/stop", response_model=ExternalCamera)
def stop_external_camera(
    camera_id: str,
    request: ExternalCameraAction,
    supabase: Client = Depends(get_supabase),
):
    result = (
        supabase.table("vishum_external_cameras")
        .select("*")
        .eq("id", camera_id)
        .single()
        .execute()
    )
    camera = result.data
    if not camera:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")

    stream_id = camera.get("stream_id")
    if stream_id:
        gateway_request(
            "DELETE",
            f"/streams/{stream_id}",
            json={"delete_files": request.delete_stream},
        )

    updated = (
        supabase.table("vishum_external_cameras")
        .update({"status": "stopped", "stream_id": None, "hls_url": None})
        .eq("id", camera_id)
        .select("*")
        .single()
        .execute()
    )
    return updated.data


@router.delete("/{camera_id}", status_code=204)
def delete_external_camera(camera_id: str, supabase: Client = Depends(get_supabase)):
    result = (
        supabase.table("vishum_external_cameras")
        .select("stream_id")
        .eq("id", camera_id)
        .single()
        .execute()
    )
    camera = result.data
    if camera and camera.get("stream_id"):
        try:
            gateway_request("DELETE", f"/streams/{camera['stream_id']}", json={"delete_files": True})
        except HTTPException:
            pass

    supabase.table("vishum_external_cameras").delete().eq("id", camera_id).execute()
    return {"message": "deleted"}

