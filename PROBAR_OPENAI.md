# 🧪 Cómo Probar tu API Key de OpenAI

He creado scripts de prueba para verificar que tu API key funciona correctamente.

## 🚀 Prueba Rápida (Recomendado)

### Opción 1: Script Rápido

```bash
cd apps/api
python test_openai_quick.py
```

Este script hace una prueba mínima y te dice si funciona o no.

### Opción 2: Script Completo

```bash
cd apps/api
python test_openai.py
```

Este script hace una prueba más completa:
- ✅ Verifica que la key existe
- ✅ Prueba la conexión
- ✅ Envía un mensaje de prueba
- ✅ Muestra estadísticas y costos
- ✅ Opcionalmente prueba Text-to-Speech

## 📋 Requisitos Previos

1. **Asegúrate de tener el archivo `.env` creado:**
   ```bash
   cd apps/api
   # Verifica que existe .env
   ls -la .env
   ```

2. **Verifica que contiene la API key:**
   ```bash
   # Ver las primeras líneas (sin mostrar la key completa)
   head -n 5 .env
   ```

3. **Instala las dependencias si no lo has hecho:**
   ```bash
   pip install -r requirements.txt
   ```

## ✅ Resultado Esperado

### Si funciona correctamente:

```
✅ API Key encontrada: sk-proj-RG_bchjjPKYnCx...
✅ Cliente inicializado correctamente
✅ ¡PRUEBA EXITOSA!

📝 Respuesta de OpenAI:
   Hola, la conexión funciona correctamente
```

### Si hay error:

El script te mostrará:
- ❌ El tipo de error
- 💡 Soluciones específicas
- 🔧 Pasos para resolverlo

## 🐛 Errores Comunes

### Error: "Invalid API key"

**Causa:** La key no es válida o está mal copiada

**Solución:**
1. Verifica que copiaste la key completa
2. Asegúrate de que no hay espacios al inicio o final
3. Verifica que la key no haya expirado
4. Obtén una nueva key: https://platform.openai.com/api-keys

### Error: "No se encontró OPENAI_API_KEY"

**Causa:** El archivo `.env` no existe o no tiene la variable

**Solución:**
1. Crea el archivo `apps/api/.env`
2. Agrega la línea: `OPENAI_API_KEY=tu_key_aqui`
3. Sin espacios alrededor del `=`

### Error: "Insufficient quota"

**Causa:** No tienes créditos en tu cuenta de OpenAI

**Solución:**
1. Ve a: https://platform.openai.com/account/billing
2. Agrega créditos a tu cuenta
3. Verifica tu plan

### Error: "Rate limit"

**Causa:** Demasiadas solicitudes en poco tiempo

**Solución:**
- Espera unos minutos y vuelve a intentar

## 🔍 Verificar Manualmente

También puedes probar directamente desde Python:

```python
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hola"}],
)

print(response.choices[0].message.content)
```

## 📊 Costos

Las pruebas usan:
- **GPT-4o-mini**: ~$0.0001 por prueba
- **TTS**: ~$0.0001 por prueba

Son muy económicas, no te preocupes por los costos de las pruebas.

## 🎯 Próximos Pasos

Una vez que la prueba funcione:

1. ✅ Tu backend podrá usar OpenAI
2. ✅ Los endpoints `/api/ai/*` estarán disponibles
3. ✅ Puedes generar resúmenes inteligentes
4. ✅ Puedes usar Text-to-Speech

---

**¿Problemas?** Ejecuta el script de prueba y comparte el error que recibes.

