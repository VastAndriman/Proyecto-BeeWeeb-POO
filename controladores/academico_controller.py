from conexion.supabase_client import SupabaseConnection
from modelos.curso import Curso
from modelos.materia import Materia


class AcademicoController:
    def __init__(self, db_client=None):
        self.db = db_client if db_client is not None else SupabaseConnection.get_client()

    def listar_materias(self):
        return self.db.table("materias").select("*").execute().data or []

    def listar_cursos(self):
        return self.db.table("cursos").select("*").execute().data or []

    def crear_materia(self, nombre: str, creditos: int, semestre: int):
        try:
            materia = Materia(nombre, creditos, semestre, db_client=self.db)
            if any(item.get("nombre", "").casefold() == materia.nombre.casefold()
                   for item in self.listar_materias()):
                return False, "Ya existe una materia con ese nombre."
            materia.guardar()
            return True, "Materia registrada correctamente."
        except ValueError as error:
            return False, str(error)
        except Exception as error:
            return False, f"No se pudo guardar la materia: {error}"

    def crear_curso(self, paralelo: str, num_estudiantes: int):
        try:
            curso = Curso(paralelo, num_estudiantes, db_client=self.db)
            if any(item.get("paralelo", "").casefold() == curso.paralelo.casefold()
                   for item in self.listar_cursos()):
                return False, "Ya existe un curso con ese paralelo."
            curso.guardar()
            return True, "Curso registrado correctamente."
        except ValueError as error:
            return False, str(error)
        except Exception as error:
            return False, f"No se pudo guardar el curso: {error}"
