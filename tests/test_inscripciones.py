import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from conexion.supabase_client import BeeWeekClient
from controladores.inscripciones_controller import InscripcionesController


class InscripcionesTests(unittest.TestCase):
    def setUp(self):
        self.supabase = Mock()
        self.cliente = BeeWeekClient(self.supabase)
        self.controller = InscripcionesController(self.cliente)

    def test_sin_sesion_no_consulta(self):
        with self.assertRaises(PermissionError):
            self.controller.catalogo()
        self.supabase.rpc.assert_not_called()

    def test_catalogo_usa_sesion_servidor(self):
        self.cliente._session_token = "a" * 64
        self.supabase.rpc.return_value.execute.return_value = SimpleNamespace(
            data={"ofertas": [], "inscripciones": []})
        self.assertEqual(self.controller.catalogo()["ofertas"], [])
        self.supabase.rpc.assert_called_once_with(
            "beeweek_student_catalog", {"p_token": "a" * 64})

    def test_inscripcion_y_retiro_no_escriben_tablas_directamente(self):
        self.cliente._session_token = "a" * 64
        self.supabase.rpc.return_value.execute.return_value = SimpleNamespace(data={})
        self.controller.inscribir(1, 2)
        self.controller.retirar(1, 2)
        self.assertEqual(self.supabase.rpc.call_args_list[0].args, (
            "beeweek_student_enroll", {"p_token": "a" * 64,
                                      "p_materia_id": 1, "p_curso_id": 2}))
        self.assertEqual(self.supabase.rpc.call_args_list[1].args, (
            "beeweek_student_withdraw", {"p_token": "a" * 64,
                                        "p_materia_id": 1, "p_curso_id": 2}))
        self.supabase.table.assert_not_called()


if __name__ == "__main__":
    unittest.main()
