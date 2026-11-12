import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from main import BeeWeekApp


class DashboardTests(unittest.TestCase):
    def test_metricas_confirman_sincronizacion_solo_si_ambas_consultas_funcionan(self):
        db = Mock()
        db.table.side_effect = [
            Mock(select=Mock(return_value=Mock(execute=Mock(return_value=SimpleNamespace(count=2, data=[]))))),
            Mock(select=Mock(return_value=Mock(execute=Mock(return_value=SimpleNamespace(count=3, data=[]))))),
        ]
        app = SimpleNamespace(db_client=db, card_aulas_val=Mock(),
                              card_horarios_val=Mock(), lbl_estado_conexion=Mock())

        BeeWeekApp.actualizar_metricas(app)

        app.card_aulas_val.configure.assert_called_with(text="2")
        app.card_horarios_val.configure.assert_called_with(text="3")
        self.assertIn("actualizados", app.lbl_estado_conexion.configure.call_args.kwargs["text"])

    def test_fallo_de_consulta_no_muestra_conexion_exitosa(self):
        db = Mock()
        db.table.return_value.select.return_value.execute.side_effect = RuntimeError("sin red")
        app = SimpleNamespace(db_client=db, card_aulas_val=Mock(),
                              card_horarios_val=Mock(), lbl_estado_conexion=Mock())

        BeeWeekApp.actualizar_metricas(app)

        app.card_aulas_val.configure.assert_called_with(text="Err")
        app.card_horarios_val.configure.assert_called_with(text="Err")
        self.assertIn("No se pudieron cargar", app.lbl_estado_conexion.configure.call_args.kwargs["text"])


if __name__ == "__main__":
    unittest.main()
