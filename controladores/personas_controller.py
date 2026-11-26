"""Operaciones de docentes y estudiantes fuera de la interfaz gráfica."""

from conexion.supabase_client import SupabaseConnection
from patrones_creacionales_beeweek import CreadorDocente, CreadorEstudiante


class DocentesController:
    def __init__(self, db_client=None, creador=None):
        self.db = db_client if db_client is not None else SupabaseConnection.get_client()
        self.creador = creador if creador is not None else CreadorDocente()

    def listar(self):
        return self.db.table("docentes").select("*").execute().data or []

    def registrar(self, **datos):
        if not all(str(valor).strip() for valor in datos.values()):
            raise ValueError("Por favor completa todos los campos.")
        return self.creador.registrar(**datos, db_client=self.db)


class EstudiantesController:
    def __init__(self, db_client=None, creador=None):
        self.db = db_client if db_client is not None else SupabaseConnection.get_client()
        self.creador = creador if creador is not None else CreadorEstudiante()

    def listar_cursos(self):
        return self.db.table("cursos").select("id,paralelo").execute().data or []

    def listar(self):
        return self.db.table("estudiantes").select("*").execute().data or []

    def registrar(self, **datos):
        obligatorios = (valor for clave, valor in datos.items() if clave != "curso_id")
        if not all(str(valor).strip() for valor in obligatorios):
            raise ValueError("Por favor completa todos los campos.")
        return self.creador.registrar(**datos, db_client=self.db)
