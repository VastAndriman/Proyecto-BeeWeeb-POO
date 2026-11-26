"""Visitor: resume varios modelos sin poner el reporte dentro de ellos."""

from datetime import time


class VisitanteResumenInstitucional:
    def __init__(self):
        self.aulas = 0
        self.capacidad = 0
        self.docentes = 0
        self.cursos = 0
        self.estudiantes = 0
        self.horarios = 0
        self.minutos = 0

    def visitar_aula(self, aula):
        self.aulas += 1
        self.capacidad += int(aula.capacidad)

    def visitar_docente(self, _docente):
        self.docentes += 1

    def visitar_curso(self, curso):
        self.cursos += 1
        self.estudiantes += curso.num_estudiantes

    def visitar_horario(self, horario):
        self.horarios += 1
        inicio = time.fromisoformat(str(horario.hora_inicio))
        fin = time.fromisoformat(str(horario.hora_fin))
        self.minutos += (fin.hour * 60 + fin.minute) - (inicio.hour * 60 + inicio.minute)

    def filas(self):
        horas = f"{self.minutos / 60:g}"
        return [
            ["Aulas", f"{self.aulas} registradas; capacidad total: {self.capacidad} puestos"],
            ["Docentes", f"{self.docentes} registrados"],
            ["Cursos", f"{self.cursos} registrados; {self.estudiantes} estudiantes previstos"],
            ["Horarios", f"{self.horarios} bloques; {horas} horas semanales"],
        ]
