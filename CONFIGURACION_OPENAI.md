# 🤖 Configuración de OpenAI

Tu API key de OpenAI ha sido configurada en el backend. Esto permite usar funcionalidades de IA generativa.

## ✅ Configuración Completada

La API key de OpenAI está configurada en:
- **Archivo**: `apps/api/.env`
- **Variable**: `OPENAI_API_KEY`

## 🚀 Funcionalidades Disponibles

Con OpenAI configurado, ahora puedes usar:

### 1. Resúmenes Inteligentes de Eventos

**Endpoint**: `POST /api/ai/generate-summary`

Genera un resumen en lenguaje natural de los eventos detectados.

**Ejemplo de uso:**

```bash
curl -X POST "http://localhost:8000/api/ai/generate-summary?hours=24&language=es"
```

**Respuesta:**
```json
{
  "summary": "En las últimas 24 horas se detectaron 15 eventos...",
  "language": "es",
  "period": "24 horas",
  "events_analyzed": 15,
  "generated_at": "2024-01-01T12:00:00"
}
```

### 2. Descripciones de Audio (Text-to-Speech)

**Endpoint**: `POST /api/ai/generate-voice-description`

Convierte texto a voz usando OpenAI TTS.

**Ejemplo de uso:**

```bash
curl -X POST "http://localhost:8000/api/ai/generate-voice-description?text=Resumen%20de%20eventos&voice=nova"
```

**Voces disponibles:**
- `alloy` - Voz neutra
- `echo` - Voz masculina
- `fable` - Voz británica
- `onyx` - Voz masculina profunda
- `nova` - Voz femenina
- `shimmer` - Voz femenina suave

## 🔧 Integración en el Frontend

Puedes crear un componente en React para usar estos endpoints:

```typescript
// Ejemplo de función para obtener resumen
async function getAISummary(hours: number = 24) {
  const response = await fetch(
    `http://localhost:8000/api/ai/generate-summary?hours=${hours}&language=es`
  );
  return await response.json();
}
```

## 💰 Costos de OpenAI

Los modelos usados son económicos:

- **GPT-4o-mini**: ~$0.15 por 1M tokens de entrada, ~$0.60 por 1M tokens de salida
- **TTS-1**: ~$15 por 1M caracteres

**Nota**: Los resúmenes usan pocos tokens, así que el costo será mínimo.

## 🔒 Seguridad

- ✅ La API key está en `.env` (no se sube a Git)
- ✅ Solo el backend tiene acceso a la key
- ✅ El frontend nunca expone la key directamente

## 🧪 Probar la Configuración

1. **Inicia el backend:**
   ```bash
   cd apps/api
   python main.py
   ```

2. **Prueba el endpoint de salud:**
   ```bash
   curl http://localhost:8000/api/health
   ```

3. **Prueba generar un resumen** (necesitas tener eventos en Supabase):
   ```bash
   curl -X POST "http://localhost:8000/api/ai/generate-summary?hours=24"
   ```

## 📝 Notas

- La API key se carga automáticamente al iniciar el servidor
- Si la key no está configurada, los endpoints de IA retornarán error 503
- Los modelos usados son optimizados para costo y velocidad

## 🚧 Próximas Mejoras

- [ ] Integrar resúmenes en el Dashboard
- [ ] Generar reportes PDF con resúmenes de IA
- [ ] Audio automático de resúmenes
- [ ] Análisis predictivo de patrones

---

**Configuración completada** ✅

