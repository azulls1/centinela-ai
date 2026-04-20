"""
Script rápido de prueba - Solo verifica que la key funciona
Ejecutar: python test_openai_quick.py
"""

import os
import sys
import io
from dotenv import load_dotenv
from openai import OpenAI

# Configurar stdout para UTF-8 (Windows)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("ERROR: No se encontro OPENAI_API_KEY")
    exit(1)

print(f"[OK] Key encontrada: {api_key[:20]}...{api_key[-10:]}")
print("[*] Probando conexion...")

try:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Responde solo: OK"}],
        max_tokens=10
    )
    result = response.choices[0].message.content
    print(f"[SUCCESS] ¡Funciona! Respuesta: {result}")
    print(f"[INFO] Tokens usados: {response.usage.total_tokens}")
    print("[SUCCESS] Token de OpenAI verificado correctamente!")
except Exception as e:
    print(f"[ERROR] Error: {str(e)}")
    exit(1)

