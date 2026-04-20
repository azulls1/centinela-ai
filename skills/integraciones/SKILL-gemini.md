# SKILL: Integracion Google Gemini

> **Version:** 3.8.0
> **Trigger:** Integracion con Google Gemini para busquedas y multimedia
> **Agente:** nxt-search, nxt-media
> **Track:** shared

## Proposito
Integrar las capacidades de Google Gemini para busquedas web, mapas,
verificacion de hechos y procesamiento de documentos grandes.

## Cuando se Activa
- Buscar informacion actual en web
- Buscar ubicaciones y lugares
- Verificar hechos
- Procesar documentos muy grandes
- Ejecutar codigo Python
- Razonamiento profundo

## Capacidades de Gemini

### 1. Google Search Grounding
Busqueda web con fuentes verificadas y citas.

```python
# Uso basico
python herramientas/gemini_tools.py search "tendencias IA 2025"

# Respuesta incluye:
# - Texto de respuesta
# - Lista de fuentes con URLs
# - Fecha de la informacion
```

### 2. Google Maps Grounding
Acceso a 250M+ lugares con reviews y direcciones.

```python
# Buscar lugares cerca de coordenadas
python herramientas/gemini_tools.py maps "restaurantes italianos" 40.4168 -3.7038

# Respuesta incluye:
# - Lista de lugares
# - Ratings y reviews
# - Direcciones
# - Horarios
```

### 3. Code Execution
Ejecutar codigo Python en servidores de Google.

```python
# Ejecutar calculo complejo
python herramientas/gemini_tools.py code "calcular los primeros 100 numeros de fibonacci"

# Util para:
# - Calculos matematicos complejos
# - Analisis de datos
# - Generacion de graficos
```

### 4. Deep Think
Razonamiento profundo para problemas complejos.

```python
# Problema complejo
python herramientas/gemini_tools.py think "disenar arquitectura para sistema de trading de alta frecuencia"

# Genera analisis profundo con:
# - Consideraciones
# - Trade-offs
# - Recomendaciones
```

### 5. 1M Token Context
Procesar documentos enormes (hasta 1M tokens).

```python
# Analizar documento grande
python herramientas/gemini_tools.py analyze "documento_grande.pdf" "resume los puntos principales"

# Soporta:
# - PDFs grandes
# - Multiples documentos
# - Contextos extensos
```

### 6. URL Context
Analizar paginas web completas.

```python
# Analizar URL
python herramientas/gemini_tools.py url "https://example.com/article" "que dice sobre X"
```

## Modelos Disponibles (v3.3.0)

| Modelo | Uso | Contexto |
|--------|-----|----------|
| gemini-3-pro-preview | Busquedas, razonamiento | 1M tokens |
| nano-banana-pro-preview | Imagenes con texto/logos | - |
| veo-3.0-generate-001 | Videos con audio | 8 seg |
| gemini-2.5-pro-preview-tts | Text-to-Speech | 30 voces |

## Configuracion

### Variables de Entorno
```env
GEMINI_API_KEY=AIza...
```

### Configuracion en nxt.config.yaml
```yaml
gemini:
  modelo_default: "gemini-3-pro-preview"
  capacidades:
    - search_grounding
    - maps_grounding
    - code_execution
    - deep_think
    - context_1m
    - nano_banana_pro    # Imagenes
    - veo_3              # Videos
    - native_audio       # TTS 30 voces
```

## Comandos Completos

| Comando | Descripcion |
|---------|-------------|
| `search "query"` | Busqueda web con fuentes |
| `current "topic"` | Informacion actual |
| `maps "query" lat lon` | Busqueda de lugares |
| `fact_check "claim"` | Verificar afirmacion |
| `code "task"` | Ejecutar codigo Python |
| `url "url" "question"` | Analizar pagina web |
| `think "problem"` | Razonamiento profundo |
| `analyze "file" "question"` | Analizar documento grande |

## Ejemplos de Uso

### Investigacion de Mercado
```bash
python herramientas/gemini_tools.py search "market size fintech latam 2025"
```

Respuesta:
```json
{
  "text": "El mercado fintech en LATAM alcanza los $150B en 2025...",
  "sources": [
    {"title": "Fintech Report 2025", "url": "https://..."},
    {"title": "LATAM Banking Study", "url": "https://..."}
  ],
  "confidence": "high",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Busqueda de Oficinas
```bash
python herramientas/gemini_tools.py maps "coworking spaces" 40.4168 -3.7038
```

Respuesta:
```json
{
  "places": [
    {
      "name": "WeWork Castellana",
      "rating": 4.5,
      "reviews": 230,
      "address": "Paseo de la Castellana 79",
      "hours": "24/7"
    }
  ]
}
```

### Verificacion de Hechos
```bash
python herramientas/gemini_tools.py fact_check "Python es el lenguaje mas usado en 2025"
```

Respuesta:
```json
{
  "claim": "Python es el lenguaje mas usado en 2025",
  "verdict": "PARTIALLY_TRUE",
  "explanation": "Python lidera en ML/DS pero JavaScript lidera en web",
  "sources": ["Stack Overflow Survey", "TIOBE Index"]
}
```

## Integracion con Agentes NXT

### nxt-analyst
```python
# Investigacion de mercado
await gemini.search("competidores de [producto] en [mercado]")
```

### nxt-pm
```python
# Validar features con tendencias
await gemini.current("tendencias UX 2025")
```

### nxt-architect
```python
# Buscar documentacion tecnica
await gemini.search("best practices [tecnologia] 2025")
```

### nxt-dev
```python
# Resolver problemas de codigo
await gemini.search("error [mensaje] [framework]")
```

## Limitaciones

- Rate limits segun plan de API
- Informacion puede tener horas de retraso
- Solo informacion publica
- Requiere conexion a internet

## Costos (Referencia)

| Modelo | Input (1M tokens) | Output (1M tokens) |
|--------|-------------------|-------------------|
| Flash | $0.075 | $0.30 |
| Pro | $1.25 | $5.00 |

## Seguridad

- No enviar informacion sensible
- Verificar fuentes de busquedas
- No usar para decisiones criticas sin validacion
- Logs se almacenan temporalmente

---

## Llamada Real con Error Handling

```python
import os
from google import genai

def gemini_search(query: str) -> dict:
    """Busqueda con Gemini Search Grounding."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY not set", "fallback": "Use WebSearch tool instead"}

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=query,
            config={"tools": [{"google_search": {}}]},
        )
        return {
            "answer": response.text,
            "sources": [s.uri for s in getattr(response, 'grounding_sources', [])],
            "model": "gemini-2.0-flash"
        }
    except Exception as e:
        return {"error": str(e), "fallback": "Use WebSearch tool instead"}
```

### Rate Limiting

```python
# Gemini free tier: 15 RPM, 1M TPM
# Para evitar 429: esperar 4 segundos entre llamadas
import time
LAST_CALL = 0
def rate_limited_call(fn, *args):
    global LAST_CALL
    elapsed = time.time() - LAST_CALL
    if elapsed < 4:
        time.sleep(4 - elapsed)
    LAST_CALL = time.time()
    return fn(*args)
```
