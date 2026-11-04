"""Comprueba la conexión sin crear registros de prueba."""

from conexion.supabase_client import SupabaseConnection


if __name__ == "__main__":
    try:
        SupabaseConnection.get_client().table("aulas").select("id").limit(1).execute()
        print("Conexión con Supabase correcta.")
    except Exception as error:
        print(f"No se pudo conectar con Supabase: {error}")
