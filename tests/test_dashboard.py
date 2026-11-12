import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from main import BeeWeekApp, resumir_horarios


class DashboardTests(unittest.TestCase):
    def test_metricas_confirman_sincronizacion_solo_si_ambas_consultas_funcionan(self):
        db = Mock()
        db.table.side_effect = [
            Mock(select=Mock(return_value=Mock(execute=Mock(return_value=SimpleNamespace(count=2, data=[]))))),
            Mock(select=Mock(return_value=Mock(execute=Mock(return_value=SimpleNamespace(count=3, data=[]))))),
        ]
        app = SimpleNamespace(db_client=db, card_aulas_val=Mock(),
                              card_horarios_val=Mock(), lbl_estado_conexion=Mock(),
                              _mostrar_resumen_horario=Mock())

        BeeWeekApp.actualizar_metricas(app)

        app.card_aulas_val.configure.assert_called_with(text="2")
        app.card_horarios_val.configure.assert_called_with(text="3")
        self.assertIn("actualizados", app.lbl_estado_conexion.configure.call_args.kwargs["text"])

    def test_fallo_de_consulta_no_muestra_conexion_exitosa(self):
        db = Mock()
        db.table.return_value.select.return_value.execute.side_effect = RuntimeError("sin red")
        app = SimpleNamespace(db_client=db, card_aulas_val=Mock(),
                              card_horarios_val=Mock(), lbl_estado_conexion=Mock(),
                              _mostrar_resumen_horario=Mock())

        BeeWeekApp.actualizar_metricas(app)

        app.card_aulas_val.configure.assert_called_with(text="Err")
        app.card_horarios_val.configure.assert_called_with(text="Err")
        self.assertIn("No se pudieron cargar", app.lbl_estado_conexion.configure.call_args.kwargs["text"])

    def test_resumen_muestra_materias_en_orden_semanal(self):
        horarios = [
            {"dia": "Viernes", "hora_inicio": "09:00:00", "hora_fin": "11:00:00", "materia_id": 2},
            {"dia": "Lunes", "hora_inicio": "08:00:00", "hora_fin": "10:00:00", "materia_id": 1},
        ]
        db = Mock()
        db.table.side_effect = [
            Mock(select=Mock(return_value=Mock(execute=Mock(return_value=SimpleNamespace(count=1, data=[{}]))))),
            Mock(select=Mock(return_value=Mock(execute=Mock(return_value=SimpleNamespace(count=2, data=horarios))))),
            Mock(select=Mock(return_value=Mock(execute=Mock(return_value=SimpleNamespace(
                data=[{"id": 1, "nombre": "POO"}, {"id": 2, "nombre": "Bases de Datos"}]
            ))))),
        ]
        app = SimpleNamespace(db_client=db, card_aulas_val=Mock(),
                              card_horarios_val=Mock(), lbl_estado_conexion=Mock(),
                              _mostrar_resumen_horario=Mock())

        BeeWeekApp.actualizar_metricas(app)

        app._mostrar_resumen_horario.assert_called_once_with([
            ("Lunes", "08:00–10:00", "POO"),
            ("Viernes", "09:00–11:00", "Bases de Datos"),
        ])
        self.assertEqual(resumir_horarios(horarios, [], limite=1)[0][0], "Lunes")


if __name__ == "__main__":
    unittest.main()
