"""
Script de prueba para verificar que la API key de OpenAI funciona correctamente
Ejecutar: python test_openai.py
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Cargar variables de entorno
load_dotenv()

def test_openai_connection():
    """Probar la conexión con OpenAI"""
    
    print("=" * 60)
    print("🧪 PRUEBA DE CONEXIÓN CON OPENAI")
    print("=" * 60)
    print()
    
    # Obtener API key
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ ERROR: No se encontró OPENAI_API_KEY en el archivo .env")
        print()
        print("💡 SOLUCIÓN:")
        print("   1. Asegúrate de que existe el archivo apps/api/.env")
        print("   2. Verifica que contiene: OPENAI_API_KEY=tu_key_aqui")
        return False
    
    # Verificar formato básico de la key
    if not api_key.startswith("sk-"):
        print("⚠️  ADVERTENCIA: La API key no parece tener el formato correcto")
        print(f"   Formato esperado: sk-...")
        print(f"   Tu key comienza con: {api_key[:10]}...")
        print()
    
    print(f"✅ API Key encontrada: {api_key[:20]}...{api_key[-10:]}")
    print()
    
    try:
        # Inicializar cliente
        print("🔄 Inicializando cliente de OpenAI...")
        client = OpenAI(api_key=api_key)
        print("✅ Cliente inicializado correctamente")
        print()
        
        # Probar con una llamada simple
        print("🔄 Probando conexión con OpenAI API...")
        print("   (Enviando prueba simple...)")
        print()
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente útil. Responde brevemente."
                },
                {
                    "role": "user",
                    "content": "Di 'Hola, la conexión funciona correctamente' en español."
                }
            ],
            max_tokens=50,
            temperature=0.7,
        )
        
        # Obtener respuesta
        message = response.choices[0].message.content
        
        print("=" * 60)
        print("✅ ¡PRUEBA EXITOSA!")
        print("=" * 60)
        print()
        print("📝 Respuesta de OpenAI:")
        print(f"   {message}")
        print()
        print("📊 Información de la respuesta:")
        print(f"   Modelo usado: {response.model}")
        print(f"   Tokens usados: {response.usage.total_tokens}")
        print(f"   - Prompt: {response.usage.prompt_tokens}")
        print(f"   - Completación: {response.usage.completion_tokens}")
        print()
        print("💰 Costo estimado:")
        # GPT-4o-mini: $0.15/1M input tokens, $0.60/1M output tokens
        input_cost = (response.usage.prompt_tokens / 1_000_000) * 0.15
        output_cost = (response.usage.completion_tokens / 1_000_000) * 0.60
        total_cost = input_cost + output_cost
        print(f"   ~${total_cost:.6f} USD")
        print()
        print("=" * 60)
        print("🎉 Tu API key de OpenAI funciona correctamente!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print("=" * 60)
        print("❌ ERROR EN LA PRUEBA")
        print("=" * 60)
        print()
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Mensaje: {str(e)}")
        print()
        
        # Errores comunes y soluciones
        if "Invalid API key" in str(e) or "401" in str(e):
            print("💡 PROBLEMA: La API key es inválida o incorrecta")
            print()
            print("SOLUCIÓN:")
            print("   1. Verifica que copiaste la key completa")
            print("   2. Asegúrate de que no hay espacios extra")
            print("   3. Verifica que la key no haya expirado")
            print("   4. Obtén una nueva key en: https://platform.openai.com/api-keys")
        elif "Rate limit" in str(e) or "429" in str(e):
            print("💡 PROBLEMA: Límite de tasa excedido")
            print()
            print("SOLUCIÓN:")
            print("   Espera unos minutos y vuelve a intentar")
        elif "Insufficient quota" in str(e) or "insufficient_quota" in str(e):
            print("💡 PROBLEMA: Cuota insuficiente")
            print()
            print("SOLUCIÓN:")
            print("   1. Verifica tu plan de OpenAI")
            print("   2. Agrega créditos en: https://platform.openai.com/account/billing")
        else:
            print("💡 PROBLEMA: Error desconocido")
            print()
            print("SOLUCIÓN:")
            print("   1. Verifica tu conexión a internet")
            print("   2. Revisa los logs completos arriba")
            print("   3. Consulta: https://platform.openai.com/docs/guides/error-codes")
        
        print()
        return False


def test_tts():
    """Probar Text-to-Speech (opcional)"""
    
    print()
    print("=" * 60)
    print("🧪 PRUEBA DE TEXT-TO-SPEECH (TTS)")
    print("=" * 60)
    print()
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ No se puede probar TTS sin API key")
        return False
    
    try:
        client = OpenAI(api_key=api_key)
        
        print("🔄 Generando audio de prueba...")
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input="Hola, esta es una prueba de síntesis de voz con OpenAI."
        )
        
        # Guardar audio
        audio_filename = "test_audio.mp3"
        with open(audio_filename, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Audio generado exitosamente: {audio_filename}")
        print(f"   Tamaño: {len(response.content)} bytes")
        print()
        print("💰 Costo estimado:")
        text_length = len("Hola, esta es una prueba de síntesis de voz con OpenAI.")
        cost = (text_length / 1_000_000) * 15  # $15 por 1M caracteres
        print(f"   ~${cost:.6f} USD")
        print()
        print("🎵 Puedes reproducir el archivo test_audio.mp3 para verificar")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en TTS: {str(e)}")
        return False


if __name__ == "__main__":
    print()
    print("🚀 Iniciando pruebas de OpenAI...")
    print()
    
    # Probar conexión básica
    success = test_openai_connection()
    
    if success:
        # Preguntar si probar TTS
        print()
        respuesta = input("¿Quieres probar también Text-to-Speech (TTS)? (s/n): ")
        if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            test_tts()
    
    print()
    print("=" * 60)
    print("✨ Pruebas completadas")
    print("=" * 60)
    print()

