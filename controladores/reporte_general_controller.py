"""Construye el reporte general a partir de modelos visitables."""

from controladores.horario_controller import HorarioController
from modelos.aula import Aula
from modelos.curso import Curso
from modelos.docente import Docente
from patrones_creacionales_beeweek import HorarioPreparado
from reportes.visitante_resumen import VisitanteResumenInstitucional


class ReporteGeneralController:
    def __init__(self, horario_controller=None):
        self.horarios = horario_controller if horario_controller is not None else HorarioController()

    def generar(self):
        visitante = VisitanteResumenInstitucional()
        for fila in self.horarios.obtener_aulas(estricto=True):
            Aula(fila["numero"], fila["capacidad"], fila["tipo"]).aceptar(visitante)
        for fila in self.horarios.obtener_docentes(estricto=True):
            Docente(
                fila["identificacion"], fila["nombre"], fila["apellido"],
                fila["email"], fila["especialidad"],
            ).aceptar(visitante)
        for fila in self.horarios.obtener_cursos(estricto=True):
            Curso(fila["paralelo"], fila["num_estudiantes"], db_client=self.horarios.db).aceptar(visitante)
        for fila in self.horarios.obtener_horarios_registrados(estricto=True):
            HorarioPreparado(
                dia=fila["dia"], hora_inicio=str(fila["hora_inicio"]),
                hora_fin=str(fila["hora_fin"]), materia_id=fila["materia_id"],
                docente_id=fila["docente_id"], aula_id=fila["aula_id"],
                curso_id=fila["curso_id"],
            ).aceptar(visitante)
        return ["Recurso", "Resumen"], visitante.filas()
