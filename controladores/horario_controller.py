from conexion.supabase_client import SupabaseConnection

class HorarioController:
    @staticmethod
    def validar_y_crear_horario(dia, hora_inicio, hora_fin, materia_id, docente_id, aula_id, curso_id, num_estudiantes):
        client = SupabaseConnection.get_client()
        
        # 1. Validación de Aforo: Capacidad(idAula) >= NumEstudiantes(idCurso)
        aula_res = client.table("aulas").select("capacidad").eq("id", aula_id).execute()
        if aula_res.data:
            capacidad_aula = aula_res.data[0]['capacidad']
            if capacidad_aula < num_estudiantes:
                return False, "Error: El aforo del aula es insuficiente para la cantidad de estudiantes."

        # 2. Consultar horarios existentes para validar cruces concurrentes
        horarios_existentes = client.table("horarios").select("*").eq("dia", dia).execute()
        
        for h in horarios_existentes.data:
            # Validación de Docente: Docente_Disponible == True
            if h['docente_id'] == docente_id and h['hora_inicio'] == hora_inicio:
                return False, "Conflicto: El docente ya tiene una clase asignada en este bloque horario."
            
            # Validación de Aula: Aula_Ocupada == False
            if h['aula_id'] == aula_id and h['hora_inicio'] == hora_inicio:
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
        return True, "Horario creado exitosamente sin cruces."