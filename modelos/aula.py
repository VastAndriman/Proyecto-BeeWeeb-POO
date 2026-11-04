from conexion.supabase_client import SupabaseConnection

class Aula:
    def __init__(self, numero: str, capacidad: int, tipo: str, db_client=None):
        self.__numero = numero          # Atributo privado
        self.__capacidad = capacidad
        self.__tipo = tipo
        self.db = db_client

    def validar_aforo(self, cantidad_estudiantes: int) -> bool:
        return self.__capacidad >= cantidad_estudiantes

    def guardar(self):
        client = self.db if self.db is not None else SupabaseConnection.get_client()
        data = {
            "numero": self.__numero,
            "capacidad": self.__capacidad,
            "tipo": self.__tipo
        }
        client.table("aulas").insert(data).execute()
