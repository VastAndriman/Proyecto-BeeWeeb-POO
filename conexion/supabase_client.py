import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class SupabaseConnection:
    _instance: Client = None

    @classmethod
    def get_client(cls) -> Client:
        if cls._instance is None:
            if not SUPABASE_URL or not SUPABASE_KEY:
                raise ValueError("Faltan las credenciales de Supabase en el archivo .env")
            cls._instance = create_client(SUPABASE_URL, SUPABASE_KEY)
        return cls._instance
supabase = SupabaseConnection.get_client()