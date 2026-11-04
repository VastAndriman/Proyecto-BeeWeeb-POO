from datetime import time

from conexion.supabase_client import SupabaseConnection

class HorarioController:
    _instancia_defecto = None

    def __init__(self, db_client=None):
        """
        Inyección de Dependencias: Permite inyectar cualquier cliente de base de datos
        (por ejemplo, mock para pruebas o cliente real de Supabase).
        """
        self.db = db_client or SupabaseConnection.get_client()

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

    def obtener_aulas(self_or_cls=None):
        inst = self_or_cls if isinstance(self_or_cls, HorarioController) else HorarioController._get_instancia_defecto()
        try:
            res = inst.db.table("aulas").select("*").execute()
            return res.data if res.data else []
        except Exception:
            return []

    def obtener_docentes(self_or_cls=None):
        inst = self_or_cls if isinstance(self_or_cls, HorarioController) else HorarioController._get_instancia_defecto()
        try:
            res = inst.db.table("docentes").select("*").execute()
            return res.data if res.data else []
        except Exception:
            return []

    def obtener_materias(self_or_cls=None):
        inst = self_or_cls if isinstance(self_or_cls, HorarioController) else HorarioController._get_instancia_defecto()
        try:
            res = inst.db.table("materias").select("*").execute()
            return res.data or []
        except Exception:
            return []

    def obtener_cursos(self_or_cls=None):
        inst = self_or_cls if isinstance(self_or_cls, HorarioController) else HorarioController._get_instancia_defecto()
        try:
            res = inst.db.table("cursos").select("*").execute()
            return res.data or []
        except Exception:
            return []

    def obtener_horarios_registrados(self_or_cls=None):
        inst = self_or_cls if isinstance(self_or_cls, HorarioController) else HorarioController._get_instancia_defecto()
        try:
            res = inst.db.table("horarios").select("*").execute()
            return res.data if res.data else []
        except Exception:
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
            inicio = HorarioController.convertir_hora(hora_inicio)
            fin = HorarioController.convertir_hora(hora_fin)
        except (TypeError, ValueError):
            return False, "Ingresa horas válidas en formato HH:MM."
        if inicio >= fin:
            return False, "La hora de fin debe ser posterior a la hora de inicio."

        client = inst.db
        
        # 1. Validación de Aforo: Capacidad(idAula) >= NumEstudiantes(idCurso)
        aula_res = client.table("aulas").select("capacidad").eq("id", aula_id).execute()
        if aula_res.data:
            capacidad_aula = aula_res.data[0]['capacidad']
            if capacidad_aula < num_estudiantes:
                return False, f"Error: Aforo insuficiente. El aula tiene capacidad para {capacidad_aula} estudiantes, pero se ingresaron {num_estudiantes}."

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
        nuevo_horario = {
            "dia": dia,
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin,
            "materia_id": materia_id,
            "docente_id": docente_id,
            "aula_id": aula_id,
            "curso_id": curso_id
        }
        
        client.table("horarios").insert(nuevo_horario).execute()
        return True, "¡Horario registrado exitosamente sin cruces!"
