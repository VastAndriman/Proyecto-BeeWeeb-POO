import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from vistas.estudiante_view import EstudianteView


class EstudianteViewTests(unittest.TestCase):
    def test_avisa_si_no_se_pueden_cargar_los_cursos(self):
        db = Mock()
        db.table.return_value.select.return_value.execute.side_effect = RuntimeError("sin conexión")
        vista = SimpleNamespace(
            db=db, cursos_map={"Curso anterior": 1},
            combo_curso=Mock(), lbl_mensaje=Mock(),
        )

        EstudianteView.cargar_cursos(vista)

        self.assertEqual(vista.cursos_map, {})
        vista.combo_curso.set.assert_called_with("Sin curso")
        self.assertIn("No se pudieron cargar", vista.lbl_mensaje.configure.call_args.kwargs["text"])

    def test_no_registra_campos_con_solo_espacios(self):
        campos = {
            "entry_identificacion": "1234567890",
            "entry_nombre": "   ",
            "entry_apellido": "Pérez",
            "entry_email": "ejemplo@uleam.edu.ec",
            "entry_matricula": "2026001",
            "entry_carrera": "Software",
        }
        vista = SimpleNamespace(
            **{nombre: Mock(**{"get.return_value": valor}) for nombre, valor in campos.items()},
            combo_curso=Mock(), cursos_map={}, lbl_mensaje=Mock(),
            creador_estudiante=Mock(), db=Mock(),
        )

        EstudianteView.guardar_estudiante(vista)

        vista.creador_estudiante.registrar.assert_not_called()
        vista.lbl_mensaje.configure.assert_called_once_with(
            text="Por favor completa todos los campos.", text_color="orange"
        )


if __name__ == "__main__":
    unittest.main()
