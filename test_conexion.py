"""Comprueba la conexión sin crear registros de prueba."""

from conexion.supabase_client import SupabaseConnection


if __name__ == "__main__":
    try:
        SupabaseConnection.get_client().rpc("beeweek_login", {
            "p_login": "__beeweek_verificacion__", "p_password": "sin_clave",
        }).execute()
        print("Conexión con Supabase correcta.")
    except Exception as error:
        print(f"No se pudo conectar con Supabase: {error}")
        raise SystemExit(1) from None
