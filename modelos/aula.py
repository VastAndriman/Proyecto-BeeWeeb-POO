from conexion.supabase_client import SupabaseConnection

class Aula:
    def __init__(self, numero: str, capacidad: int, tipo: str):
        self.__numero = numero          # Atributo privado
        self.__capacidad = capacidad
        self.__tipo = tipo

    def validar_aforo(self, cantidad_estudiantes: int) -> bool:
        return self.__capacidad >= cantidad_estudiantes

    def guardar(self):
        client = SupabaseConnection.get_client()
        data = {
            "numero": self.__numero,
            "capacidad": self.__capacidad,
            "tipo": self.__tipo
        }
        client.table("aulas").insert(data).execute()