import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from controladores.aulas_controller import AulasController
from vistas.aulas_view import AulasView


class AulasTests(unittest.TestCase):
    def test_guardado_avisa_si_falla_recarga_posterior(self):
        vista = SimpleNamespace(
            controller=Mock(), mensaje=Mock(),
            _datos_formulario=Mock(return_value=("901", "30", "Aula")),
            cargar_aulas=Mock(return_value=False),
        )

        AulasView.crear_aula(vista)

        vista.controller.crear.assert_called_once_with("901", "30", "Aula")
        self.assertIn("Aula añadida", vista.mensaje.configure.call_args.kwargs["text"])
        self.assertIn("no se pudo actualizar", vista.mensaje.configure.call_args.kwargs["text"])

    def test_error_al_cargar_invalida_la_seleccion_anterior(self):
        controller = Mock()
        controller.listar.side_effect = RuntimeError("sin conexión")
        vista = SimpleNamespace(
            controller=controller,
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

    def test_controlador_valida_antes_de_escribir_y_usa_el_modelo(self):
        db = Mock()
        controller = AulasController(db)

        with self.assertRaisesRegex(ValueError, "capacidad"):
            controller.crear("901", "0", "Laboratorio")
        db.table.assert_not_called()

        controller.crear(" 901 ", "30", " Laboratorio ")
        db.table.assert_called_once_with("aulas")
        db.table.return_value.insert.assert_called_once_with({
            "numero": "901", "capacidad": 30, "tipo": "Laboratorio",
        })


if __name__ == "__main__":
    unittest.main()
