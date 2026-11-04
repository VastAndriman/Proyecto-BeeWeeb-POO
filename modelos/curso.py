from conexion.supabase_client import SupabaseConnection


class Curso:
    def __init__(self, paralelo: str, num_estudiantes: int, db_client=None):
        self.paralelo = paralelo.strip()
        if not self.paralelo:
            raise ValueError("Ingresa el paralelo del curso.")
        try:
            self.num_estudiantes = int(num_estudiantes)
        except (TypeError, ValueError):
            raise ValueError("La cantidad de estudiantes debe ser un número entero.") from None
        if self.num_estudiantes <= 0:
            raise ValueError("La cantidad de estudiantes debe ser mayor a cero.")
        self.db = db_client if db_client is not None else SupabaseConnection.get_client()

    def guardar(self):
        return self.db.table("cursos").insert({
            "paralelo": self.paralelo,
            "num_estudiantes": self.num_estudiantes,
        }).execute()
