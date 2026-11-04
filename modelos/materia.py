from conexion.supabase_client import SupabaseConnection


class Materia:
    def __init__(self, nombre: str, creditos: int, semestre: int, db_client=None):
        self.nombre = nombre.strip()
        if not self.nombre:
            raise ValueError("Ingresa el nombre de la materia.")
        try:
            self.creditos = int(creditos)
            self.semestre = int(semestre)
        except (TypeError, ValueError):
            raise ValueError("Los créditos y el semestre deben ser números enteros.") from None
        if self.creditos <= 0 or self.semestre <= 0:
            raise ValueError("Los créditos y el semestre deben ser mayores a cero.")
        self.db = db_client if db_client is not None else SupabaseConnection.get_client()

    def guardar(self):
        return self.db.table("materias").insert({
            "nombre": self.nombre,
            "creditos": self.creditos,
            "semestre": self.semestre,
        }).execute()
