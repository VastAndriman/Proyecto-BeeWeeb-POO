"""Datos y resumen semanal del panel de inicio."""

from conexion.supabase_client import SupabaseConnection


def resumir_horarios(horarios, materias, limite=5):
    dias = {dia: indice for indice, dia in enumerate(
        ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado")
    )}
    nombres = {str(materia.get("id")): materia.get("nombre", "") for materia in materias}
    ordenados = sorted(
        horarios,
        key=lambda horario: (
            dias.get(horario.get("dia"), len(dias)),
            str(horario.get("hora_inicio", "")),
        ),
    )
    return [
        (
            horario.get("dia", ""),
            f"{str(horario.get('hora_inicio', ''))[:5]}–{str(horario.get('hora_fin', ''))[:5]}",
            nombres.get(str(horario.get("materia_id")), "Materia sin nombre"),
        )
        for horario in ordenados[:limite]
    ]


class DashboardController:
    def __init__(self, db_client=None):
        self.db = db_client if db_client is not None else SupabaseConnection.get_client()

    def obtener_metricas(self):
        aulas = self.db.table("aulas").select("*", count="exact").execute()
        horarios = self.db.table("horarios").select("*", count="exact").execute()
        filas_horarios = horarios.data or []
        total_aulas = aulas.count if aulas.count is not None else len(aulas.data or [])
        total_horarios = horarios.count if horarios.count is not None else len(filas_horarios)
        return total_aulas, total_horarios, filas_horarios

    def obtener_resumen(self, horarios):
        materias = self.db.table("materias").select("id,nombre").execute().data or []
        return resumir_horarios(horarios, materias)
