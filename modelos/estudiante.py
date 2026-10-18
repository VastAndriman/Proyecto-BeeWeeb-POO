from modelos.persona import Persona
from conexion.supabase_client import SupabaseConnection

class Estudiante(Persona):
    def __init__(self, identificacion: str, nombre: str, apellido: str, email: str, matricula: str, carrera: str):
        super().__init__(identificacion, nombre, apellido, email)
        self.__matricula = matricula    # Atributo privado
        self.__carrera = carrera

    def guardar(self):
        client = SupabaseConnection.get_client()
        data = {
            "identificacion": self._identificacion,
            "nombre": self._nombre,
            "apellido": self._apellido,
            "email": self._email,
            "matricula": self.__matricula,
            "carrera": self.__carrera
        }
        client.table("estudiantes").insert(data).execute()