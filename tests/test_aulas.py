import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from vistas.aulas_view import AulasView


class AulasTests(unittest.TestCase):
    def test_error_al_cargar_invalida_la_seleccion_anterior(self):
        db = Mock()
        db.table.return_value.select.return_value.execute.side_effect = RuntimeError("sin conexión")
        vista = SimpleNamespace(
            db=db,
            textbox=Mock(),
            selector=Mock(),
            mensaje=Mock(),
            aulas_por_opcion={"Aula anterior": {"id": 1}},
        )
        vista.selector.get.return_value = "Aula anterior"
        vista._mostrar_error = lambda error: AulasView._mostrar_error(vista, error)

        AulasView.cargar_aulas(vista)

        self.assertEqual(vista.aulas_por_opcion, {})
        vista.selector.configure.assert_called_with(values=["Selecciona un aula"])
        vista.selector.set.assert_called_with("Selecciona un aula")
        with self.assertRaisesRegex(ValueError, "Selecciona un aula"):
            AulasView._id_seleccionado(vista)


if __name__ == "__main__":
    unittest.main()
