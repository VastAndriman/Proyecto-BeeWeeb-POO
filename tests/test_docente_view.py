import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from vistas.docente_view import DocenteView


class DocenteViewTests(unittest.TestCase):
    def test_guardado_avisa_si_no_se_puede_recargar_lista(self):
        campos = {
            nombre: Mock(**{"get.return_value": valor})
            for nombre, valor in (
                ("entry_identificacion", "1234567890"), ("entry_nombre", "Ana"),
                ("entry_apellido", "Paz"), ("entry_email", "ana@ejemplo.edu"),
                ("entry_especialidad", "Software"),
            )
        }
        vista = SimpleNamespace(
            **campos, lbl_mensaje=Mock(), creador_docente=Mock(),
            db=Mock(), cargar_docentes=Mock(return_value=False),
        )

        DocenteView.guardar_docente(vista)

        vista.creador_docente.registrar.assert_called_once()
        self.assertIn("guardado", vista.lbl_mensaje.configure.call_args.kwargs["text"])
        self.assertIn("no se pudo actualizar", vista.lbl_mensaje.configure.call_args.kwargs["text"])


if __name__ == "__main__":
    unittest.main()
