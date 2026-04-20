import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import Hls from 'hls.js'
import { useAppStore } from '../store/appStore'
import type { AppConfig, CameraConfig, CameraDetectionSnapshot, DetectionState } from '../types'

const logWarn = (message: string, error?: unknown) => {
  console.warn(`[CameraFeed] ${message}`, error)
}
const _logError = (message: string, error?: unknown) => {
  console.error(`[CameraFeed] ${message}`, error)
}

type CameraFeedProps = {
  cameraId: string
}

const RESOLUTION_MAP: Record<CameraConfig['resolution'], { width: number; height: number; frameRate: number }> = {
  low: { width: 640, height: 480, frameRate: 24 },
  medium: { width: 1280, height: 720, frameRate: 30 },
  high: { width: 1920, height: 1080, frameRate: 30 },
}

const createEmptySnapshot = (): CameraDetectionSnapshot => ({
  persons: 0,
  faces: 0,
  emotions: [],
  activity: null,
  healthStatus: null,
  objects: [],
})

let _mlSnapshotCanvas: HTMLCanvasElement | null = null
function getMlSnapshotCanvas(): HTMLCanvasElement {
  if (!_mlSnapshotCanvas) {
    _mlSnapshotCanvas = document.createElement('canvas')
    _mlSnapshotCanvas.width = 480
    _mlSnapshotCanvas.height = 360
  }
  return _mlSnapshotCanvas
}

export function CameraFeed({ cameraId }: CameraFeedProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const overlayCanvasRef = useRef<HTMLCanvasElement>(null)
  const overlaysRef = useRef<CameraDetectionSnapshot>(createEmptySnapshot())
  const animationFrameRef = useRef<number | null>(null)
  const ctxRef = useRef<CanvasRenderingContext2D | null>(null)
  const mlTimeoutRef = useRef<number | null>(null)
  const mlIdleRef = useRef<number | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const hlsRef = useRef<Hls | null>(null)
  const nativeHlsCleanupRef = useRef<(() => void) | null>(null)
  const startStreamRef = useRef<(() => Promise<void>) | null>(null)
  const renderLoopActiveRef = useRef(false)

  const [error, setError] = useState<string | null>(null)
  const [isStreaming, setIsStreaming] = useState(false)
  const [isVideoReady, setIsVideoReady] = useState(false)

  const config = useAppStore((state) => state.config)
  const cameraConfig = useAppStore((state) => state.cameraConfigs[cameraId])
  const isExternal = cameraConfig?.sourceType === 'external'
  const updateCameraRuntime = useAppStore((state) => state.updateCameraRuntime)
  const updateCameraDetection = useAppStore((state) => state.updateCameraDetection)

  const mlIntervalStateRef = useRef({
    base: 300,
    current: 300,
    min: 150,
    max: 1500,
  })

  const fpsTrackerRef = useRef({
    frames: 0,
    lastTime: performance.now(),
    currentFPS: 0,
  })

  const effectiveConfig: AppConfig = useMemo(() => {
    if (!cameraConfig) {
      return config
    }

    return {
      ...config,
      personDetection: {
        ...config.personDetection,
        enabled: config.personDetection.enabled && cameraConfig.models.personDetection,
      },
      faceDetection: {
        ...config.faceDetection,
        enabled: config.faceDetection.enabled && cameraConfig.models.faceDetection,
      },
      emotionDetection: {
        ...config.emotionDetection,
        enabled: config.emotionDetection.enabled && cameraConfig.models.emotionDetection,
      },
      movementDetection: {
        ...config.movementDetection,
        enabled: config.movementDetection.enabled && cameraConfig.models.movementDetection,
      },
      objectDetection: {
        ...config.objectDetection,
        enabled: config.objectDetection.enabled && cameraConfig.models.objectDetection,
      },
    }
  }, [config, cameraConfig])

  // Keep effectiveConfig in a ref so the ML loop always reads the latest value
  // without needing it in the useEffect dependency array (which would restart the loop)
  const effectiveConfigRef = useRef(effectiveConfig)
  effectiveConfigRef.current = effectiveConfig

  // ML snapshot resolution used for processing
  const ML_SNAPSHOT_W = 480
  const ML_SNAPSHOT_H = 360

  const drawOverlays = useCallback((ctx: CanvasRenderingContext2D, objects: CameraDetectionSnapshot['objects']) => {
    if (!objects || objects.length === 0) return

    // Scale from ML snapshot (320x240) to actual canvas size
    const canvasW = ctx.canvas.width
    const canvasH = ctx.canvas.height
    const sx = canvasW / ML_SNAPSHOT_W
    const sy = canvasH / ML_SNAPSHOT_H

    const prevFillStyle = ctx.fillStyle
    const prevStrokeStyle = ctx.strokeStyle
    const prevLineWidth = ctx.lineWidth
    const prevFont = ctx.font

    ctx.font = 'bold 13px sans-serif'
    ctx.lineWidth = 2

    for (let i = 0; i < objects.length; i++) {
      const obj = objects[i]
      if (!obj.bbox) continue

      const labelLower = obj.label.toLowerCase()
      const isPerson = labelLower.includes('person')
      const isDevice = labelLower === 'laptop' || labelLower === 'phone' || labelLower === 'cell phone'
      const color = isPerson ? '#0ea5e9' : isDevice ? '#f59e0b' : '#10b981'

      // Scale bbox from ML coordinates to canvas coordinates
      const bx = obj.bbox.x * sx
      const by = obj.bbox.y * sy
      const bw = obj.bbox.width * sx
      const bh = obj.bbox.height * sy

      ctx.fillStyle = `rgba(${isPerson ? '14, 165, 233' : isDevice ? '245, 158, 11' : '16, 185, 129'}, 0.15)`
      ctx.fillRect(bx, by, bw, bh)
      ctx.strokeStyle = color
      ctx.strokeRect(bx, by, bw, bh)

      const label = obj.label[0].toUpperCase() + obj.label.slice(1)
      const confidence = Math.round(obj.confidence * 100)
      const fullLabel = `${label} ${confidence}%`
      const textWidth = ctx.measureText(fullLabel).width
      const textY = by < 20 ? 20 : by - 6

      ctx.fillStyle = 'rgba(0, 0, 0, 0.8)'
      ctx.fillRect(bx, textY - 16, textWidth + 8, 18)
      ctx.fillStyle = color
      ctx.fillText(fullLabel, bx + 4, textY)
    }

    ctx.fillStyle = prevFillStyle
    ctx.strokeStyle = prevStrokeStyle
    ctx.lineWidth = prevLineWidth
    ctx.font = prevFont
  }, [])

  const startRenderLoop = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return

    // Synchronous flag: prevents duplicate loops even when called in the same JS tick
    if (renderLoopActiveRef.current) return
    renderLoopActiveRef.current = true

    // Cancel any stale rAF from a previous loop
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
      animationFrameRef.current = null
    }

    console.log(`[CAM ${cameraId}] startRenderLoop: begin`)

    const video = videoRef.current
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d', {
      alpha: false,
      desynchronized: true,
      willReadFrequently: false,
    })

    if (!ctx) { renderLoopActiveRef.current = false; return }
    ctxRef.current = ctx

    let lastFPSUpdate = performance.now()
    let frameCount = 0
    let canvasWidth = 0
    let canvasHeight = 0

    const renderLoop = (currentTime: number) => {
      // Exit immediately if loop was stopped
      if (!renderLoopActiveRef.current) return

      if (video.paused || video.ended) {
        animationFrameRef.current = requestAnimationFrame(renderLoop)
        return
      }

      if (video.readyState < video.HAVE_CURRENT_DATA) {
        animationFrameRef.current = requestAnimationFrame(renderLoop)
        return
      }

      const vw = video.videoWidth
      const vh = video.videoHeight

      if (canvasWidth !== vw || canvasHeight !== vh) {
        canvasWidth = vw
        canvasHeight = vh
        canvas.width = vw
        canvas.height = vh
      }

      ctx.drawImage(video, 0, 0, vw, vh)

      // Sync overlay canvas size with video canvas (overlays drawn separately by ML callback)
      const oc = overlayCanvasRef.current
      if (oc && (oc.width !== vw || oc.height !== vh)) {
        oc.width = vw
        oc.height = vh
      }

      frameCount++
      const elapsed = currentTime - lastFPSUpdate
      if (elapsed >= 1000) {
        const fps = Math.round((frameCount * 1000) / elapsed)
        fpsTrackerRef.current.currentFPS = fps
        fpsTrackerRef.current.frames = frameCount
        fpsTrackerRef.current.lastTime = currentTime
        frameCount = 0
        lastFPSUpdate = currentTime

        updateCameraDetection(cameraId, { currentFPS: fps })

        const intervalState = mlIntervalStateRef.current
        if (fps < 15) {
          intervalState.current = Math.min(intervalState.current + 100, intervalState.max)
        } else if (fps > 30) {
          intervalState.current = Math.max(intervalState.current - 50, intervalState.base)
        }
      }

      animationFrameRef.current = requestAnimationFrame(renderLoop)
    }

    animationFrameRef.current = requestAnimationFrame(renderLoop)
  }, [cameraId, drawOverlays, updateCameraDetection])

  const stopRenderLoop = useCallback(() => {
    renderLoopActiveRef.current = false
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
      animationFrameRef.current = null
    }
    ctxRef.current = null
  }, [])

  const cleanupMLTimers = useCallback(() => {
    if (mlTimeoutRef.current) {
      clearTimeout(mlTimeoutRef.current)
      mlTimeoutRef.current = null
    }
    if (mlIdleRef.current) {
      if ('cancelIdleCallback' in window) {
        window.cancelIdleCallback(mlIdleRef.current as unknown as number)
      } else {
        clearTimeout(mlIdleRef.current)
      }
      mlIdleRef.current = null
    }
  }, [])

  const stopLocalStream = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop())
      streamRef.current = null
    }
  }, [])

  const cleanupExternalStream = useCallback(() => {
    if (hlsRef.current) {
      hlsRef.current.destroy()
      hlsRef.current = null
    }
    if (nativeHlsCleanupRef.current) {
      nativeHlsCleanupRef.current()
      nativeHlsCleanupRef.current = null
    }
    const video = videoRef.current
    if (video) {
      video.pause()
      video.removeAttribute('src')
      video.load()
    }
  }, [])

  useEffect(() => {
    return () => {
      stopRenderLoop()
      cleanupMLTimers()
      stopLocalStream()
      cleanupExternalStream()
    }
  }, [cleanupExternalStream, cleanupMLTimers, stopLocalStream, stopRenderLoop])

  useEffect(() => {
    if (!cameraConfig?.enabled) {
      console.log(`[CAM ${cameraId}] useEffect: config disabled, stopping everything`)
      stopRenderLoop()
      cleanupMLTimers()
      if (isExternal) {
        cleanupExternalStream()
      } else {
        stopLocalStream()
      }
      setIsStreaming(false)
      setIsVideoReady(false)
      updateCameraRuntime(cameraId, { isStreaming: false, isVideoReady: false })
      updateCameraDetection(cameraId, {
        isProcessing: false,
        currentFPS: 0,
        detections: createEmptySnapshot(),
      })
      import('../lib/ml/processors')
        .then(({ resetCameraState }) => resetCameraState(cameraId))
        .catch(() => {})
      return
    }

    if (isExternal) {
      console.log(`[CAM ${cameraId}] useEffect: external camera, skipping getUserMedia`)
      return
    }

    const activeConfig = cameraConfig
    const constraints = (() => {
      const preset = RESOLUTION_MAP[activeConfig.resolution] ?? RESOLUTION_MAP.medium
      const frameRate = Math.min(Math.max(activeConfig.targetFPS, 10), 60)
      return {
        video: {
          deviceId: activeConfig.deviceId ? { exact: activeConfig.deviceId } : undefined,
          width: { ideal: preset.width, max: preset.width },
          height: { ideal: preset.height, max: preset.height },
          frameRate: { ideal: frameRate, max: frameRate },
          facingMode: 'environment',
        },
        audio: false,
      }
    })()

    console.log(`[CAM ${cameraId}] useEffect: STARTING stream`, {
      enabled: cameraConfig?.enabled,
      deviceId: cameraConfig?.deviceId?.slice(0, 8),
      resolution: cameraConfig?.resolution,
      targetFPS: cameraConfig?.targetFPS,
    })

    let cancelled = false

    const startStream = async () => {
      console.log(`[CAM ${cameraId}] startStream: requesting getUserMedia...`)
      try {
        stopLocalStream()
        const stream = await navigator.mediaDevices.getUserMedia(constraints)
        if (cancelled) {
          console.log(`[CAM ${cameraId}] startStream: cancelled after getUserMedia, releasing`)
          stream.getTracks().forEach((track) => track.stop())
          return
        }
        streamRef.current = stream
        const [track] = stream.getVideoTracks()
        const settings = track?.getSettings()
        console.log(`[CAM ${cameraId}] startStream: SUCCESS`, {
          trackState: track?.readyState,
          actualRes: settings ? `${settings.width}x${settings.height}` : 'unknown',
          actualFPS: settings?.frameRate,
        })

        if (videoRef.current) {
          videoRef.current.srcObject = stream
          videoRef.current.play().catch((err) => {
            if (err.name !== 'AbortError') console.warn(`[CAM ${cameraId}] video.play() failed:`, err.message)
          })
        }
        setError(null)
        setIsStreaming(true)
        updateCameraRuntime(cameraId, { isStreaming: true, lastError: null })

        if (track) {
          track.onended = () => {
            console.warn(`[CAM ${cameraId}] TRACK ENDED — camera disconnected or revoked`)
            setIsStreaming(false)
            setIsVideoReady(false)
            updateCameraRuntime(cameraId, { isStreaming: false, isVideoReady: false })
            if (document.visibilityState === 'visible') {
              console.log(`[CAM ${cameraId}] attempting auto-restart after track ended...`)
              startStreamRef.current?.()
            }
          }
          track.onmute = () => {
            console.warn(`[CAM ${cameraId}] TRACK MUTED — camera paused by system`)
            setIsVideoReady(false)
            updateCameraRuntime(cameraId, { isVideoReady: false })
          }
          track.onunmute = () => {
            console.log(`[CAM ${cameraId}] TRACK UNMUTED — camera resumed`)
            if (videoRef.current) {
              videoRef.current.play().catch((err) => { if (err.name !== 'AbortError') console.warn('Video play failed:', err.message) })
            }
            setIsStreaming(true)
            setIsVideoReady(true)
            updateCameraRuntime(cameraId, { isStreaming: true, isVideoReady: true })
            startRenderLoop()
          }
        }
      } catch (err: any) {
        console.error(`[CAM ${cameraId}] startStream: FAILED`, err?.name, err?.message)
        let errorMessage = 'No se pudo acceder a la cámara.'
        if (err?.name === 'NotAllowedError' || err?.name === 'PermissionDeniedError') {
          errorMessage = 'Permisos de cámara denegados.'
        } else if (err?.name === 'NotFoundError') {
          errorMessage = 'No se encontró la cámara seleccionada.'
        } else if (err?.name === 'NotReadableError') {
          errorMessage = 'La cámara está siendo usada por otra aplicación.'
        }
        setError(errorMessage)
        setIsStreaming(false)
        setIsVideoReady(false)
        updateCameraRuntime(cameraId, { isStreaming: false, lastError: errorMessage })
      }
    }

    startStreamRef.current = startStream
    startStream()

    return () => {
      console.log(`[CAM ${cameraId}] useEffect CLEANUP: stopping stream (deps changed)`)
      cancelled = true
      startStreamRef.current = null
      stopRenderLoop()
      cleanupMLTimers()
      stopLocalStream()
      setIsStreaming(false)
      setIsVideoReady(false)
      updateCameraRuntime(cameraId, { isStreaming: false, isVideoReady: false })
      import('../lib/ml/processors')
        .then(({ resetCameraState }) => resetCameraState(cameraId))
        .catch(() => {})
    }
  }, [
    cameraConfig?.enabled,
    cameraConfig?.deviceId,
    cameraConfig?.resolution,
    cameraConfig?.targetFPS,
    cameraId,
    cleanupExternalStream,
    cleanupMLTimers,
    isExternal,
    startRenderLoop,
    stopLocalStream,
    stopRenderLoop,
    updateCameraDetection,
    updateCameraRuntime,
  ])

  useEffect(() => {
    if (!cameraConfig?.enabled || isExternal) {
      return
    }

    const handleVisibilityChange = () => {
      console.log(`[CAM ${cameraId}] VISIBILITY: ${document.visibilityState}`)
      if (document.visibilityState === 'visible') {
        const stream = streamRef.current
        const video = videoRef.current
        if (stream && video) {
          const [track] = stream.getVideoTracks()
          console.log(`[CAM ${cameraId}] visibility=visible, track=${track?.readyState}, video.readyState=${video.readyState}`)
          if (track && track.readyState === 'live') {
            video.play().catch((err) => { if (err.name !== 'AbortError') console.warn('Video play failed:', err.message) })
            setIsStreaming(true)
            if (video.readyState >= 2) {
              setIsVideoReady(true)
              updateCameraRuntime(cameraId, { isStreaming: true, isVideoReady: true, lastError: null })
              startRenderLoop()
            }
          } else {
            console.warn(`[CAM ${cameraId}] track dead on visibility resume, restarting stream`)
            startStreamRef.current?.()
          }
        } else {
          console.warn(`[CAM ${cameraId}] no stream/video ref on visibility resume, restarting`)
          startStreamRef.current?.()
        }
      } else {
        console.log(`[CAM ${cameraId}] visibility=hidden, pausing`)
        cleanupMLTimers()
        stopRenderLoop()
        videoRef.current?.pause()
        updateCameraRuntime(cameraId, { isVideoReady: false })
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [
    cameraConfig?.enabled,
    cameraId,
    cleanupMLTimers,
    isExternal,
    cleanupExternalStream,
    startRenderLoop,
    stopRenderLoop,
    updateCameraRuntime,
  ])

  useEffect(() => {
    if (!cameraConfig?.enabled || !isExternal) {
      return
    }

    if (!cameraConfig.hlsUrl) {
      setError('Stream HLS no disponible.')
      updateCameraRuntime(cameraId, { isStreaming: false, lastError: 'HLS no disponible' })
      return
    }

    const video = videoRef.current
    if (!video) {
      return
    }

    cleanupExternalStream()
    setError(null)
    setIsStreaming(false)
    setIsVideoReady(false)
    updateCameraRuntime(cameraId, { isStreaming: true, isVideoReady: false, lastError: null })

    const handlePlaybackReady = () => {
      setIsStreaming(true)
      setIsVideoReady(true)
      updateCameraRuntime(cameraId, { isStreaming: true, isVideoReady: true, lastError: null })
      video.play().catch((err) => { if (err.name !== 'AbortError') console.warn('Video play failed:', err.message) })
    }

    const handleVideoError = () => {
      const message = 'Error reproduciendo el stream externo.'
      setError(message)
      updateCameraRuntime(cameraId, { isStreaming: false, lastError: message })
    }

    video.crossOrigin = 'anonymous'
    video.muted = true
    video.playsInline = true
    video.autoplay = true

    if (Hls.isSupported()) {
      const hls = new Hls({ liveSyncDuration: 6 })
      hls.loadSource(cameraConfig.hlsUrl)
      hls.attachMedia(video)
      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        video.play().catch((err) => { if (err.name !== 'AbortError') console.warn('Video play failed:', err.message) })
      })
      hls.on(Hls.Events.ERROR, (_event, data) => {
        if (data.fatal) {
          const detail = data?.details || 'Error fatal en HLS'
          setError(detail)
          updateCameraRuntime(cameraId, { isStreaming: false, lastError: detail })
        }
      })
      hlsRef.current = hls
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = cameraConfig.hlsUrl
      const nativeHandler = () => {
        video.play().catch((err) => { if (err.name !== 'AbortError') console.warn('Video play failed:', err.message) })
      }
      video.addEventListener('loadedmetadata', nativeHandler, { once: true })
      nativeHlsCleanupRef.current = () => video.removeEventListener('loadedmetadata', nativeHandler)
    } else {
      const message = 'El navegador no soporta streams HLS.'
      setError(message)
      updateCameraRuntime(cameraId, { isStreaming: false, lastError: message })
      return
    }

    video.addEventListener('canplay', handlePlaybackReady, { once: true })
    video.addEventListener('error', handleVideoError)

    return () => {
      video.removeEventListener('canplay', handlePlaybackReady)
      video.removeEventListener('error', handleVideoError)
      cleanupExternalStream()
      updateCameraRuntime(cameraId, { isStreaming: false, isVideoReady: false })
      setIsStreaming(false)
      setIsVideoReady(false)
    }
  }, [cameraConfig?.enabled, cameraConfig?.hlsUrl, cameraId, cleanupExternalStream, isExternal, updateCameraRuntime])

  useEffect(() => {
    if (!isStreaming || !cameraConfig?.enabled) return

    const video = videoRef.current
    if (!video) return

    let readyFired = false
    const handleReady = () => {
      if (readyFired) return
      readyFired = true
      setIsVideoReady(true)
      updateCameraRuntime(cameraId, { isVideoReady: true })
      startRenderLoop()
    }

    video.addEventListener('loadedmetadata', handleReady, { once: true })
    video.addEventListener('playing', handleReady, { once: true })

    if (video.readyState >= 2) {
      handleReady()
    }

    return () => {
      video.removeEventListener('loadedmetadata', handleReady)
      video.removeEventListener('playing', handleReady)
    }
  }, [cameraConfig?.enabled, cameraId, isStreaming, startRenderLoop, updateCameraRuntime])

  useEffect(() => {
    if (!isStreaming || !isVideoReady || !cameraConfig?.enabled) {
      console.log(`[CAM ${cameraId}] ML useEffect: skipping (streaming=${isStreaming}, videoReady=${isVideoReady}, enabled=${cameraConfig?.enabled})`)
      return
    }
    console.log(`[CAM ${cameraId}] ML useEffect: STARTING processing loop`)

    let isProcessing = false
    let lastProcessTime = 0
    let mlFrameCount = 0
    let emptyObjectFrames = 0
    const MAX_EMPTY_BEFORE_CLEAR = 10 // Keep bboxes for ~3s (10 × 300ms) after last detection

    const processML = async () => {
      if (isProcessing) return

      const now = Date.now()
      const minGap = mlIntervalStateRef.current.min
      if (now - lastProcessTime < minGap) return

      lastProcessTime = now
      isProcessing = true
      mlFrameCount++
      if (mlFrameCount % 10 === 1) {
        console.log(`[CAM ${cameraId}] ML frame #${mlFrameCount}, interval=${mlIntervalStateRef.current.current}ms`)
      }

      try {
        const canvas = canvasRef.current
        if (!canvas || canvas.width === 0 || canvas.height === 0) {
          isProcessing = false
          return
        }

        const { processFrame, isModelsLoaded, loadModels } = await import('../lib/ml/processors')

        if (!isModelsLoaded()) {
          await loadModels().catch(() => {})
        }

        if (!isModelsLoaded()) {
          isProcessing = false
          return
        }

        const snapshotCanvas = getMlSnapshotCanvas()
        const snapshotCtx = snapshotCanvas.getContext('2d')
        if (!snapshotCtx) {
          isProcessing = false
          return
        }

        snapshotCtx.drawImage(canvas, 0, 0, snapshotCanvas.width, snapshotCanvas.height)

        await processFrame(snapshotCanvas, effectiveConfigRef.current, cameraId, (detections: DetectionState['detections']) => {
          // Persist bboxes: only clear overlay after several empty frames
          if (detections.objects.length > 0) {
            emptyObjectFrames = 0
          } else if (overlaysRef.current.objects.length > 0 && emptyObjectFrames < MAX_EMPTY_BEFORE_CLEAR) {
            emptyObjectFrames++
            detections = { ...detections, objects: overlaysRef.current.objects }
          }

          overlaysRef.current = detections

          // Draw overlays on the SEPARATE overlay canvas — it persists between render frames
          const oc = overlayCanvasRef.current
          if (oc) {
            const octx = oc.getContext('2d')
            if (octx) {
              octx.clearRect(0, 0, oc.width, oc.height)
              if (detections.objects.length > 0) {
                drawOverlays(octx, detections.objects)
              }
            }
          }

          updateCameraDetection(cameraId, {
            detections: {
              persons: detections.persons,
              faces: detections.faces,
              emotions: detections.emotions,
              activity: detections.activity,
              healthStatus: detections.healthStatus,
              objects: detections.objects,
            },
            isProcessing: true,
          })
        })
      } catch (err) {
        logWarn('Error procesando ML', err)
      } finally {
        isProcessing = false
      }
    }

    const scheduleML = () => {
      cleanupMLTimers()
      mlTimeoutRef.current = window.setTimeout(() => {
        processML().finally(scheduleML)
      }, mlIntervalStateRef.current.current)
    }

    scheduleML()

    return () => {
      console.log(`[CAM ${cameraId}] ML useEffect CLEANUP: stopping ML loop (processed ${mlFrameCount} frames)`)
      cleanupMLTimers()
    }
  }, [
    cameraConfig?.enabled,
    cameraId,
    cleanupMLTimers,
    isStreaming,
    isVideoReady,
    updateCameraDetection,
  ])

  const fps = fpsTrackerRef.current.currentFPS

  return (
    <div className="relative w-full animate-fadeIn">
      <div className="flex justify-between items-center mb-2">
        <div>
          <h6 className="text-forest font-semibold mb-0">
            {cameraConfig?.label ?? 'Cámara'}
          </h6>
          {cameraConfig?.location && (
            <small className="text-moss block">
              {cameraConfig.location}
            </small>
          )}
        </div>
        <div className="badge badge-inactive px-3 py-2">
          FPS: {fps}
        </div>
      </div>

      {error && (
        <div className="alert alert-error mb-3" role="alert">
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className="relative bg-gray-900 rounded-xl overflow-hidden w-full shadow-forest-lg border border-gray-200" style={{ aspectRatio: '16 / 9' }}>
        <video ref={videoRef} autoPlay playsInline muted className="hidden" />

        <canvas
          ref={canvasRef}
          className="w-full h-full object-contain"
          style={{ imageRendering: 'auto' }}
        />

        {/* Overlay canvas: drawn ONLY when ML produces results, never cleared by video rendering */}
        <canvas
          ref={overlayCanvasRef}
          className="absolute top-0 left-0 w-full h-full object-contain pointer-events-none"
          style={{ imageRendering: 'auto' }}
        />

        {(!isStreaming || !isVideoReady) && (
          <div
            className="absolute top-0 left-0 w-full h-full flex items-center justify-center"
            style={{ background: 'rgba(4, 32, 44, 0.85)', zIndex: 10 }}
          >
            <div className="text-center">
              <div className="h-8 w-8 animate-spin rounded-full border-3 border-forest border-t-transparent mb-3" role="status">
                <span className="sr-only">Cargando...</span>
              </div>
              <p className="text-moss mb-0 text-sm">
                {error ? 'Error al acceder a la cámara' : isStreaming ? 'Preparando video...' : 'Solicitando acceso a cámara...'}
              </p>
            </div>
          </div>
        )}

        {isStreaming && isVideoReady && (
          <div className="absolute bottom-3 right-3">
            <div className="badge badge-active px-3 py-2">
              ✓ Cámara activa
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

