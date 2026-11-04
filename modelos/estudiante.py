from modelos.persona import Persona
from conexion.supabase_client import SupabaseConnection

class Estudiante(Persona):
    def __init__(self, identificacion: str, nombre: str, apellido: str, email: str, matricula: str, carrera: str, db_client=None, curso_id: int | None = None):
        super().__init__(identificacion, nombre, apellido, email)
        self.__matricula = matricula    # Atributo privado
        self.__carrera = carrera
        self.__curso_id = curso_id
        self.db = db_client

    def obtener_tipo(self) -> str:
        return "Estudiante"

    def guardar(self):
        client = self.db if self.db is not None else SupabaseConnection.get_client()
        data = {
            "identificacion": self._identificacion,
            "nombre": self._nombre,
            "apellido": self._apellido,
            "email": self._email,
            "matricula": self.__matricula,
            "carrera": self.__carrera,
            "curso_id": self.__curso_id
        }
        client.table("estudiantes").insert(data).execute()
