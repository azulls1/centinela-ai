# SKILL: Integracion OpenAI (Backup)

> **Version:** 3.8.0
> **Trigger:** Integracion con OpenAI como backup multimedia
> **Agente:** nxt-search
> **Track:** shared

> **NOTA v3.3.0:** Este skill es ahora un **backup opcional**.
> La multimedia principal usa **Gemini** (ver SKILL-gemini.md).
> Solo usar OpenAI si Gemini no está disponible o falla.

## Proposito
Integrar las capacidades de OpenAI como opcion de respaldo para
generacion de imagenes, video, audio y analisis visual.

## Estado Actual en NXT

> **IMPORTANTE:** Desde v1.2.3, Gemini es el LLM primario para multimedia.
> OpenAI se mantiene como **opcion de backup** para casos especificos.

### Decision Tree: Cuando Usar OpenAI vs Gemini?
```
Que necesitas?
├── Busquedas web / info actual --> Gemini (Search Grounding)
├── Generacion de imagenes --> Gemini (Nano Banana Pro)
├── Video --> Gemini (Veo 3)
├── TTS --> Gemini (30 voces)
├── Transcripcion de audio --> OpenAI Whisper (mejor accuracy en espanol)
├── Fine-tuning custom --> OpenAI (mas tooling disponible)
├── Embeddings para RAG --> Cualquiera (OpenAI ada-002 o Gemini embedding)
├── Todo lo demas --> Gemini (primary)
```

### Configuracion como Backup
```bash
# .env - Solo configurar si necesitas Whisper o fine-tuning
OPENAI_API_KEY=sk-...  # Opcional, no requerido para uso normal
```

## Cuando se Activa (Solo como Backup)
- Si Gemini no esta disponible
- Si se requiere especificamente OpenAI
- Para funcionalidades no disponibles en Gemini

## Capacidades de OpenAI

### 1. GPT-Image-1 (Imagenes con Texto)
Generacion de imagenes con texto superior, ideal para logos y UI.

```python
# Generar imagen con texto
python herramientas/openai_tools.py image "logo minimalista para app llamada NeuralMind" logo.png

# Especificaciones:
# - Resolucion: hasta 1024x1024
# - Formato: PNG, JPEG
# - Mejor para: texto, logos, UI mockups
```

### 2. DALL-E 3 (Imagenes Creativas)
Generacion de imagenes artisticas y creativas.

```python
# Generar ilustracion
python herramientas/openai_tools.py dalle "ciudad futurista con vehiculos voladores" ciudad.png

# Especificaciones:
# - Resolucion: hasta 1792x1024 (landscape) o 1024x1792 (portrait)
# - Formato: PNG
# - Mejor para: arte, conceptos, ilustraciones
```

### 3. Sora 2 (Video)
Generacion de video con audio sincronizado.

```python
# Generar video
python herramientas/openai_tools.py video "demo de aplicacion movil con transiciones suaves" demo.mp4 10

# Especificaciones:
# - Duracion: hasta 60 segundos
# - Resolucion: hasta 1080p
# - Audio sincronizado incluido
```

### 4. Whisper (Transcripcion)
Transcripcion de audio en 99+ idiomas.

```python
# Transcribir audio
python herramientas/openai_tools.py transcribe reunion.mp3 es

# Traducir a ingles
python herramientas/openai_tools.py translate audio_espanol.mp3

# Especificaciones:
# - Idiomas: 99+
# - Formatos: mp3, mp4, m4a, wav, webm
# - Tamano maximo: 25MB
```

### 5. TTS (Text-to-Speech)
Generar audio narrado con 6 voces expresivas.

```python
# Generar audio
python herramientas/openai_tools.py tts "Bienvenidos a nuestra aplicacion" bienvenida.mp3 nova

# Voces disponibles:
# - alloy: Neutral, balanceada
# - echo: Calida, conversacional
# - fable: Expresiva, narrativa
# - onyx: Profunda, autoritaria
# - nova: Amigable, alegre
# - shimmer: Clara, profesional
```

### 6. Vision (Analisis de Imagenes)
Analizar contenido de imagenes.

```python
# Analizar imagen
python herramientas/openai_tools.py analyze screenshot.png "que elementos UI ves?"

# Comparar imagenes
python herramientas/openai_tools.py compare diseño1.png diseño2.png "cual tiene mejor UX?"
```

## Modelos Disponibles

| Modelo | Uso | Capacidad |
|--------|-----|-----------|
| gpt-4o | Vision, analisis | Multimodal |
| gpt-image-1 | Imagenes con texto | Alta calidad texto |
| dall-e-3 | Imagenes creativas | Artistico |
| sora-2 | Video | Con audio |
| whisper-1 | Transcripcion | 99+ idiomas |
| tts-1 / tts-1-hd | Voz | 6 voces |

## Configuracion

### Variables de Entorno
```env
OPENAI_API_KEY=sk-...
```

### Configuracion en nxt.config.yaml
```yaml
openai:
  modelo_default: "gpt-4o"
  capacidades:
    - gpt_image_1
    - dalle_3
    - sora_2
    - whisper
    - tts
    - vision
```

## Comandos Completos

| Comando | Descripcion |
|---------|-------------|
| `image "prompt" output.png` | Imagen con GPT-Image-1 |
| `dalle "prompt" output.png` | Imagen con DALL-E 3 |
| `video "prompt" output.mp4 [duracion]` | Video con Sora 2 |
| `transcribe audio.mp3 [idioma]` | Transcripcion |
| `translate audio.mp3` | Traducir a ingles |
| `tts "texto" output.mp3 [voz]` | Text-to-speech |
| `analyze imagen.png "pregunta"` | Analizar imagen |
| `compare img1.png img2.png "pregunta"` | Comparar imagenes |

## Ejemplos de Uso

### Crear Logo
```bash
python herramientas/openai_tools.py image "logo profesional para empresa de tecnologia llamada TechFlow, estilo minimalista, colores azul y blanco" logo.png
```

### Transcribir Reunion
```bash
python herramientas/openai_tools.py transcribe reunion_planning.mp3 es
```

Salida:
```json
{
  "text": "Bueno, vamos a revisar el backlog del sprint...",
  "duration": "45:32",
  "language": "es",
  "segments": [
    {"start": 0, "end": 5, "text": "Bueno, vamos a..."},
    ...
  ]
}
```

### Generar Narración
```bash
python herramientas/openai_tools.py tts "Bienvenido a NXT Framework, el sistema de desarrollo con inteligencia artificial" intro.mp3 nova
```

### Analizar Mockup
```bash
python herramientas/openai_tools.py analyze mockup.png "describe los componentes UI y sugiere mejoras de usabilidad"
```

## Integracion con Agentes NXT

### nxt-analyst
```python
# Analizar imagenes de competencia
await openai.analyze("competidor_app.png", "que features tiene")
```

### nxt-design
```python
# Generar mockups visuales
await openai.image("UI dashboard con graficos y metricas", "mockup.png")
```

### nxt-pm
```python
# Transcribir reuniones con stakeholders
await openai.transcribe("reunion_cliente.mp3", "es")
```

### nxt-dev
```python
# Analizar screenshots de bugs
await openai.analyze("bug_screenshot.png", "que error se muestra")
```

## Voces TTS Detalladas

| Voz | Genero | Tono | Uso Recomendado |
|-----|--------|------|-----------------|
| alloy | Neutro | Balanceado | Documentacion, tutoriales generales |
| echo | Masculino | Calido | Tutoriales, explicaciones |
| fable | Femenino | Expresivo | Storytelling, marketing |
| onyx | Masculino | Autoritario | Corporativo, presentaciones |
| nova | Femenino | Alegre | Apps consumer, demos |
| shimmer | Femenino | Profesional | Presentaciones, reportes |

## Prompts Efectivos para Imagenes

### Para Logos
```
"Logo [estilo] para [empresa/producto], colores [colores],
fondo [color], estilo [minimalista/moderno/corporativo]"
```

### Para UI Mockups
```
"UI mockup de [pantalla/feature], estilo [iOS/Android/Web],
mostrando [elementos especificos], colores [paleta]"
```

### Para Ilustraciones
```
"Ilustracion de [escena/concepto], estilo [realista/cartoon/flat],
colores [vibrantes/pasteles/monocromatico]"
```

## Limitaciones

- Imagenes: No genera texto perfecto siempre
- Video: Duracion maxima 60 segundos
- Audio: Archivo maximo 25MB
- Vision: Puede fallar con texto pequeño

## Costos (Referencia)

| Servicio | Costo |
|----------|-------|
| GPT-Image-1 | $0.04/imagen |
| DALL-E 3 HD | $0.12/imagen |
| Whisper | $0.006/minuto |
| TTS | $0.015/1K caracteres |
| TTS HD | $0.030/1K caracteres |

## Seguridad

- No generar contenido inapropiado
- Verificar derechos de imagenes
- No transcribir audio sin consentimiento
- Respetar politicas de uso de OpenAI
