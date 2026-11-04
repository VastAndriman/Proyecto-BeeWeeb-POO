from modelos.persona import Persona
from conexion.supabase_client import SupabaseConnection

class Docente(Persona):
    def __init__(self, identificacion: str, nombre: str, apellido: str, email: str, especialidad: str, db_client=None):
        super().__init__(identificacion, nombre, apellido, email)
        self.__especialidad = especialidad  # Atributo privado
        self.db = db_client

    def obtener_tipo(self) -> str:
        return "Docente"

    def guardar(self):
        client = self.db if self.db is not None else SupabaseConnection.get_client()
        data = {
            "identificacion": self._identificacion,
            "nombre": self._nombre,
            "apellido": self._apellido,
            "email": self._email,
            "especialidad": self.__especialidad
        }
        client.table("docentes").insert(data).execute()
