import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from conexion.supabase_client import BeeWeekClient
from controladores.usuarios_controller import UsuariosController


class GestionUsuariosTests(unittest.TestCase):
    def setUp(self):
        self.supabase = Mock()
        self.cliente = BeeWeekClient(self.supabase)
        self.controller = UsuariosController(self.cliente)

    def test_sin_sesion_no_consulta_usuarios(self):
        with self.assertRaises(PermissionError):
            self.controller.listar()
        self.supabase.rpc.assert_not_called()

    def test_lista_se_obtiene_por_rpc_con_sesion(self):
        self.cliente._session_token = "a" * 64
        self.supabase.rpc.return_value.execute.return_value = SimpleNamespace(data=[{"id": 2}])
        self.assertEqual(self.controller.listar(), [{"id": 2}])
        self.supabase.rpc.assert_called_once_with(
            "beeweek_admin_list_users", {"p_token": "a" * 64})

    def test_no_acepta_un_rol_inventado(self):
        self.cliente._session_token = "a" * 64
        with self.assertRaises(ValueError):
            self.controller.cambiar_rol(2, "Superusuario")
        self.supabase.rpc.assert_not_called()

    def test_cambio_usa_rpc_sin_escribir_la_tabla_directamente(self):
        self.cliente._session_token = "a" * 64
        self.supabase.rpc.return_value.execute.return_value = SimpleNamespace(
            data={"id": 2, "rol": "Administrador"})
        self.assertEqual(self.controller.cambiar_rol(2, "Administrador")["rol"],
                         "Administrador")
        self.supabase.rpc.assert_called_once_with("beeweek_admin_set_role", {
            "p_token": "a" * 64, "p_user_id": 2, "p_role": "Administrador"})
        self.supabase.table.assert_not_called()


if __name__ == "__main__":
    unittest.main()
