import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from vistas.estudiante_view import EstudianteView


class EstudianteViewTests(unittest.TestCase):
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
