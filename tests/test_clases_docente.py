import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from conexion.supabase_client import BeeWeekClient
from controladores.clases_docente_controller import ClasesDocenteController


class ClasesDocenteTests(unittest.TestCase):
    def setUp(self):
        self.supabase = Mock()
        self.cliente = BeeWeekClient(self.supabase)

    def test_sin_sesion_no_consulta_clases(self):
        with self.assertRaises(PermissionError):
            ClasesDocenteController(self.cliente).listar()
        self.supabase.rpc.assert_not_called()

    def test_consulta_clases_con_sesion(self):
        self.cliente._session_token = "a" * 64
        self.supabase.rpc.return_value.execute.return_value = SimpleNamespace(
            data={"vinculado": True, "clases": []})
        self.assertEqual(ClasesDocenteController(self.cliente).listar()["clases"], [])
        self.supabase.rpc.assert_called_once_with(
            "beeweek_teacher_classes", {"p_token": "a" * 64})
        self.supabase.table.assert_not_called()

    def test_vinculo_docente_usa_rpc_protegida(self):
        self.cliente._session_token = "a" * 64
        self.supabase.rpc.return_value.execute.return_value = SimpleNamespace(data={})
        self.cliente.vincular_cuenta_docente(8, 3)
        self.supabase.rpc.assert_called_once_with("beeweek_admin_link_teacher", {
            "p_token": "a" * 64, "p_user_id": 8, "p_docente_id": 3})
        self.supabase.table.assert_not_called()


if __name__ == "__main__":
    unittest.main()
