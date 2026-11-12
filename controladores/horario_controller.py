from datetime import time

from conexion.supabase_client import SupabaseConnection
from patrones_creacionales_beeweek import HorarioBuilder

class HorarioController:
    _instancia_defecto = None

    def __init__(self, db_client=None):
        """
        Inyección de Dependencias: Permite inyectar cualquier cliente de base de datos
        (por ejemplo, mock para pruebas o cliente real de Supabase).
        """
        self.db = db_client if db_client is not None else SupabaseConnection.get_client()

    @classmethod
    def _get_instancia_defecto(cls):
        if cls._instancia_defecto is None:
            cls._instancia_defecto = cls()
        return cls._instancia_defecto

    @staticmethod
    def normalizar_hora(h_str):
        if not h_str:
            return ""
        parts = str(h_str).strip().split(":")
        if len(parts) >= 2:
            return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}"
        return str(h_str).strip()

    @staticmethod
    def convertir_hora(valor):
        """Acepta horas HH:MM y HH:MM:SS, como las devuelve Supabase."""
        return time.fromisoformat(str(valor).strip())

    def obtener_aulas(self_or_cls=None, *, estricto=False):
        inst = self_or_cls if isinstance(self_or_cls, HorarioController) else HorarioController._get_instancia_defecto()
        try:
            res = inst.db.table("aulas").select("*").execute()
            return res.data if res.data else []
        except Exception:
            if estricto:
                raise
            return []

    def obtener_docentes(self_or_cls=None, *, estricto=False):
        inst = self_or_cls if isinstance(self_or_cls, HorarioController) else HorarioController._get_instancia_defecto()
        try:
            res = inst.db.table("docentes").select("*").execute()
            return res.data if res.data else []
        except Exception:
            if estricto:
                raise
            return []

    def obtener_materias(self_or_cls=None, *, estricto=False):
        inst = self_or_cls if isinstance(self_or_cls, HorarioController) else HorarioController._get_instancia_defecto()
        try:
            res = inst.db.table("materias").select("*").execute()
            return res.data or []
        except Exception:
            if estricto:
                raise
            return []

    def obtener_cursos(self_or_cls=None, *, estricto=False):
        inst = self_or_cls if isinstance(self_or_cls, HorarioController) else HorarioController._get_instancia_defecto()
        try:
            res = inst.db.table("cursos").select("*").execute()
            return [
                {**curso, "nombre": curso.get("nombre") or curso.get("paralelo", "")}
                for curso in (res.data or [])
            ]
        except Exception:
            if estricto:
                raise
            return []

    def obtener_horarios_registrados(self_or_cls=None, *, estricto=False):
        inst = self_or_cls if isinstance(self_or_cls, HorarioController) else HorarioController._get_instancia_defecto()
        try:
            res = inst.db.table("horarios").select("*").execute()
            return res.data if res.data else []
        except Exception:
            if estricto:
                raise
            return []

    def validar_y_crear_horario(self_or_dia=None, dia=None, hora_inicio=None, hora_fin=None, materia_id=None, docente_id=None, aula_id=None, curso_id=None, num_estudiantes=None, *args, **kwargs):
        if isinstance(self_or_dia, HorarioController):
            inst = self_or_dia
        else:
            inst = HorarioController._get_instancia_defecto()
            if self_or_dia is not None and not isinstance(self_or_dia, type):
                dia = self_or_dia

        dia = dia or kwargs.get("dia")
        hora_inicio = hora_inicio or kwargs.get("hora_inicio")
        hora_fin = hora_fin or kwargs.get("hora_fin")
        materia_id = materia_id if materia_id is not None else kwargs.get("materia_id")
        docente_id = docente_id if docente_id is not None else kwargs.get("docente_id")
        aula_id = aula_id if aula_id is not None else kwargs.get("aula_id")
        curso_id = curso_id if curso_id is not None else kwargs.get("curso_id")
        num_estudiantes = num_estudiantes if num_estudiantes is not None else kwargs.get("num_estudiantes")

        try:
            horario = (HorarioBuilder().dia(dia).horas(hora_inicio, hora_fin)
                       .materia(materia_id).docente(docente_id)
                       .aula(aula_id).curso(curso_id).construir())
        except ValueError as error:
            return False, str(error)
        dia = horario.dia
        inicio = HorarioController.convertir_hora(horario.hora_inicio)
        fin = HorarioController.convertir_hora(horario.hora_fin)
        curso_id = horario.curso_id
        aula_id = horario.aula_id
        docente_id = horario.docente_id

        client = inst.db

        # La matrícula del curso se obtiene de la base, no del formulario.
        curso_res = client.table("cursos").select("num_estudiantes").eq("id", curso_id).execute()
        if not curso_res.data:
            return False, "El curso seleccionado no existe. Actualiza la lista de cursos."
        try:
            cantidad_estudiantes = int(curso_res.data[0].get("num_estudiantes"))
        except (TypeError, ValueError):
            return False, "El curso no tiene una cantidad válida de estudiantes."
        if cantidad_estudiantes <= 0:
            return False, "El curso debe tener al menos un estudiante."
        
        # 1. Validación de Aforo: Capacidad(idAula) >= NumEstudiantes(idCurso)
        aula_res = client.table("aulas").select("capacidad").eq("id", aula_id).execute()
        if not aula_res.data:
            return False, "El aula seleccionada no existe. Actualiza la lista de aulas."
        capacidad_aula = aula_res.data[0].get("capacidad")
        if capacidad_aula is None:
            return False, "El aula no tiene una capacidad registrada."
        if cantidad_estudiantes > int(capacidad_aula):
            return False, f"Error: Aforo insuficiente. El aula tiene capacidad para {capacidad_aula} estudiantes, pero se ingresaron {cantidad_estudiantes}."

        # 2. Consultar horarios existentes para validar cruces concurrentes
        horarios_existentes = client.table("horarios").select("*").eq("dia", dia).execute()
        for h in (horarios_existentes.data or []):
            try:
                inicio_existente = HorarioController.convertir_hora(h.get("hora_inicio"))
                fin_existente = HorarioController.convertir_hora(h.get("hora_fin"))
            except (TypeError, ValueError):
                return False, "Hay un horario registrado con horas inválidas. Revísalo antes de continuar."

            # Los extremos contiguos son válidos: 08:00-09:00 y 09:00-10:00.
            if not (inicio < fin_existente and inicio_existente < fin):
                continue

            if str(h.get('docente_id')) == str(docente_id):
                return False, "Conflicto: El docente ya tiene una clase asignada en este bloque horario."

            if str(h.get('aula_id')) == str(aula_id):
                return False, "Conflicto: El aula ya se encuentra reservada en este bloque horario."

            if str(h.get('curso_id')) == str(curso_id):
                return False, "Conflicto: El curso ya tiene una clase asignada en este bloque horario."

        # 3. Si pasa todas las validaciones, se registra el horario en Supabase
        nuevo_horario = horario.para_guardar()
        
        client.table("horarios").insert(nuevo_horario).execute()
        return True, "¡Horario registrado exitosamente sin cruces!"

    def actualizar_horario(self, horario_id, *, dia, hora_inicio, hora_fin,
                           materia_id, docente_id, aula_id, curso_id):
        """Edita un bloque; el trigger de Supabase valida cruces y aforo."""
        if not isinstance(horario_id, int) or horario_id <= 0:
            return False, "Selecciona un horario válido."
        try:
            horario = (HorarioBuilder().dia(dia).horas(hora_inicio, hora_fin)
                       .materia(materia_id).docente(docente_id)
                       .aula(aula_id).curso(curso_id).construir())
            self.db.table("horarios").update(horario.para_guardar()).eq("id", horario_id).execute()
            return True, "Horario actualizado."
        except ValueError as error:
            return False, str(error)

    def eliminar_horario(self, horario_id):
        if not isinstance(horario_id, int) or horario_id <= 0:
            return False, "Selecciona un horario válido."
        self.db.table("horarios").delete().eq("id", horario_id).execute()
        return True, "Horario eliminado."
