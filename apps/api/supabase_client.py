"""
Cliente de Supabase para el backend
"""

from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener credenciales de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Validar que las variables estén definidas
if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError(
        "Faltan las variables de entorno de Supabase (SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)"
    )

# Crear cliente de Supabase con service role key (permisos completos)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def get_supabase_client() -> Client:
    """Obtener el cliente de Supabase"""
    return supabase

