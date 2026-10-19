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
            if res.data:
                return res.data
        except Exception:
            pass
        # Asignaturas predeterminadas si la tabla no está creada
        return [
            {"id": 1, "nombre": "Programación Orientada a Objetos"},
            {"id": 2, "nombre": "Estructura de Datos"},
            {"id": 3, "nombre": "Base de Datos"},
            {"id": 4, "nombre": "Ingeniería de Software"},
            {"id": 5, "nombre": "Redes y Conectividad"},
            {"id": 6, "nombre": "Sistemas Operativos"}
        ]

    def obtener_cursos(self_or_cls=None):
        inst = self_or_cls if isinstance(self_or_cls, HorarioController) else HorarioController._get_instancia_defecto()
        try:
            res = inst.db.table("cursos").select("*").execute()
            if res.data:
                return res.data
        except Exception:
            pass
        # Cursos predeterminados si la tabla no está creada
        return [
            {"id": 101, "nombre": "Curso 101 - Paralelo A"},
            {"id": 102, "nombre": "Curso 102 - Paralelo B"},
            {"id": 201, "nombre": "Curso 201 - Paralelo A"},
            {"id": 202, "nombre": "Curso 202 - Paralelo B"},
            {"id": 301, "nombre": "Curso 301 - Paralelo A"}
        ]

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

        client = inst.db
        
        # 1. Validación de Aforo: Capacidad(idAula) >= NumEstudiantes(idCurso)
        aula_res = client.table("aulas").select("capacidad").eq("id", aula_id).execute()
        if aula_res.data:
            capacidad_aula = aula_res.data[0]['capacidad']
            if capacidad_aula < num_estudiantes:
                return False, f"Error: Aforo insuficiente. El aula tiene capacidad para {capacidad_aula} estudiantes, pero se ingresaron {num_estudiantes}."

        # 2. Consultar horarios existentes para validar cruces concurrentes
        horarios_existentes = client.table("horarios").select("*").eq("dia", dia).execute()
        h_inicio_norm = HorarioController.normalizar_hora(hora_inicio)
        
        for h in (horarios_existentes.data or []):
            h_inicio_existente = HorarioController.normalizar_hora(h.get('hora_inicio'))
            
            # Validación de Docente: Docente_Disponible == True
            if str(h.get('docente_id')) == str(docente_id) and h_inicio_existente == h_inicio_norm:
                return False, "Conflicto: El docente ya tiene una clase asignada en este bloque horario."
            
            # Validación de Aula: Aula_Ocupada == False
            if str(h.get('aula_id')) == str(aula_id) and h_inicio_existente == h_inicio_norm:
                return False, "Conflicto: El aula ya se encuentra reservada en este bloque horario."

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