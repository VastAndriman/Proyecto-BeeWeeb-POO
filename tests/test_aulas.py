import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from vistas.aulas_view import AulasView


class AulasTests(unittest.TestCase):
    def test_guardado_avisa_si_falla_recarga_posterior(self):
        vista = SimpleNamespace(
            db=Mock(), mensaje=Mock(),
            _datos_formulario=Mock(return_value={"numero": "901", "capacidad": 30, "tipo": "Aula"}),
            cargar_aulas=Mock(return_value=False),
        )

        AulasView.crear_aula(vista)

        vista.db.table.return_value.insert.return_value.execute.assert_called_once_with()
        self.assertIn("Aula añadida", vista.mensaje.configure.call_args.kwargs["text"])
        self.assertIn("no se pudo actualizar", vista.mensaje.configure.call_args.kwargs["text"])

    def test_error_al_cargar_invalida_la_seleccion_anterior(self):
        db = Mock()
        db.table.return_value.select.return_value.execute.side_effect = RuntimeError("sin conexión")
        vista = SimpleNamespace(
            db=db,
            tabla=Mock(),
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
        vista.tabla.set_error.assert_called_once()
        with self.assertRaisesRegex(ValueError, "Selecciona un aula"):
            AulasView._id_seleccionado(vista)


if __name__ == "__main__":
    unittest.main()
