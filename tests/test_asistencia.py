import unittest
from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import Mock

from conexion.supabase_client import BeeWeekClient
from controladores.asistencia_controller import AsistenciaController


class AsistenciaTests(unittest.TestCase):
    def setUp(self):
        self.supabase = Mock()
        self.cliente = BeeWeekClient(self.supabase)
        self.controller = AsistenciaController(self.cliente)

    def test_fecha_futura_se_rechaza_antes_de_la_red(self):
        futura = (date.today() + timedelta(days=1)).isoformat()
        with self.assertRaises(ValueError):
            self.controller.lista(1, futura)
        self.supabase.rpc.assert_not_called()

    def test_no_se_puede_guardar_sin_marcar_todos(self):
        with self.assertRaises(ValueError):
            self.controller.guardar(1, date.today().isoformat(),
                                    [{"usuario_id": 3, "estado": "Sin marcar"}])
        self.supabase.rpc.assert_not_called()

    def test_docente_envia_lista_y_guardado_por_sesion(self):
        self.cliente._session_token = "a" * 64
        self.supabase.rpc.return_value.execute.return_value = SimpleNamespace(data=[])
        fecha = date.today().isoformat()
        self.controller.lista(7, fecha)
        self.controller.guardar(7, fecha, [{"usuario_id": 3, "estado": "Presente"}])
        self.assertEqual(self.supabase.rpc.call_args_list[0].args, (
            "beeweek_attendance_roster", {"p_token": "a" * 64,
                                          "p_horario_id": 7, "p_fecha": fecha}))
        self.assertEqual(self.supabase.rpc.call_args_list[1].args, (
            "beeweek_attendance_save", {"p_token": "a" * 64,
                                        "p_horario_id": 7, "p_fecha": fecha,
                                        "p_registros": [{"usuario_id": 3, "estado": "Presente"}]}))
        self.supabase.table.assert_not_called()

    def test_consultas_de_estudiante_y_admin_son_distintas(self):
        self.cliente._session_token = "a" * 64
        self.supabase.rpc.return_value.execute.return_value = SimpleNamespace(data=[])
        self.controller.estudiante()
        self.controller.administrador()
        self.assertEqual(self.supabase.rpc.call_args_list[0].args[0],
                         "beeweek_student_attendance")
        self.assertEqual(self.supabase.rpc.call_args_list[1].args[0],
                         "beeweek_admin_attendance")


if __name__ == "__main__":
    unittest.main()
