import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from controladores.horario_controller import HorarioController


class ValidacionHorariosTests(unittest.TestCase):
    def setUp(self):
        self.db = Mock()
        self.curso = Mock()
        self.aula = Mock()
        self.horarios = Mock()
        self.curso.select.return_value.eq.return_value.execute.return_value = SimpleNamespace(
            data=[{"num_estudiantes": 20}]
        )
        self.aula.select.return_value.eq.return_value.execute.return_value = SimpleNamespace(
            data=[{"capacidad": 40}]
        )
        self.horarios.select.return_value.eq.return_value.execute.return_value = SimpleNamespace(
            data=[]
        )
        self.db.table.side_effect = {
            "cursos": self.curso, "aulas": self.aula, "horarios": self.horarios,
        }.__getitem__
        self.controller = HorarioController(self.db)
        self.datos = dict(
            dia="Martes", hora_inicio="10:00", hora_fin="11:00",
            materia_id=1, docente_id=1, aula_id=2, curso_id=1,
        )

    def test_rechaza_aforo_insuficiente_sin_insertar(self):
        self.aula.select.return_value.eq.return_value.execute.return_value = SimpleNamespace(
            data=[{"capacidad": 19}]
        )

        ok, mensaje = self.controller.validar_y_crear_horario(**self.datos)

        self.assertFalse(ok)
        self.assertIn("Aforo insuficiente", mensaje)
        self.horarios.insert.assert_not_called()

    def test_rechaza_cruce_de_docente_sin_insertar(self):
        self.horarios.select.return_value.eq.return_value.execute.return_value = SimpleNamespace(
            data=[{
                "hora_inicio": "09:30:00", "hora_fin": "10:30:00",
                "docente_id": 1, "aula_id": 9, "curso_id": 9,
            }]
        )

        ok, mensaje = self.controller.validar_y_crear_horario(**self.datos)

        self.assertFalse(ok)
        self.assertIn("docente", mensaje)
        self.horarios.insert.assert_not_called()

    def test_rechaza_horas_invertidas_antes_de_consultar(self):
        self.datos.update(hora_inicio="11:00", hora_fin="10:00")

        ok, mensaje = self.controller.validar_y_crear_horario(**self.datos)

        self.assertFalse(ok)
        self.assertIn("posterior", mensaje)
        self.db.table.assert_not_called()


if __name__ == "__main__":
    unittest.main()
