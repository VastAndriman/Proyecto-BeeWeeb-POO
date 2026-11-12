import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from vistas.academico_view import AcademicoView


class AcademicoViewTests(unittest.TestCase):
    def test_guardado_de_materia_avisa_si_falla_la_recarga(self):
        controller = Mock()
        controller.crear_materia.return_value = (True, "Materia registrada correctamente.")
        vista = SimpleNamespace(
            controller=controller, materia_nombre=Mock(), materia_creditos=Mock(),
            materia_semestre=Mock(), materia_mensaje=Mock(),
            cargar_datos_dinamicos=Mock(return_value=(False, True)),
        )

        AcademicoView.guardar_materia(vista)

        self.assertIn("Materia registrada", vista.materia_mensaje.configure.call_args.kwargs["text"])
        self.assertIn("No se pudo actualizar", vista.materia_mensaje.configure.call_args.kwargs["text"])

    def test_guardado_de_curso_avisa_si_falla_la_recarga(self):
        controller = Mock()
        controller.crear_curso.return_value = (True, "Curso registrado correctamente.")
        vista = SimpleNamespace(
            controller=controller, curso_paralelo=Mock(), curso_estudiantes=Mock(),
            curso_mensaje=Mock(), cargar_datos_dinamicos=Mock(return_value=(True, False)),
        )

        AcademicoView.guardar_curso(vista)

        self.assertIn("Curso registrado", vista.curso_mensaje.configure.call_args.kwargs["text"])
        self.assertIn("No se pudo actualizar", vista.curso_mensaje.configure.call_args.kwargs["text"])


if __name__ == "__main__":
    unittest.main()
