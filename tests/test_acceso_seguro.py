import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from controladores.auth_controller import AuthController
from modelos.estudiante import Estudiante


class AccesoSeguroTests(unittest.TestCase):
    def setUp(self):
        self.db = Mock()
        self.controller = AuthController(self.db)

    def test_login_usa_rpc_y_no_consulta_hashes(self):
        perfil = {
            "id": 1, "identificacion": "1234567890", "nombre": "Ana",
            "apellido": "Paz", "email": "ana@uleam.edu.ec",
            "username": "ana", "rol": "Estudiante", "activo": True,
        }
        self.db.rpc.return_value.execute.return_value = SimpleNamespace(data=perfil)

        ok, _, usuario = self.controller.iniciar_sesion("ana", "clave-segura")

        self.assertTrue(ok)
        self.assertEqual(usuario.username, "ana")
        self.db.rpc.assert_called_once_with(
            "beeweek_login", {"p_login": "ana", "p_password": "clave-segura"}
        )
        self.db.table.assert_not_called()

    def test_registro_no_permita_autocrear_administrador(self):
        ok, mensaje = self.controller.registrar_usuario(
            identificacion="1234567890", nombre="Ana", apellido="Paz",
            email="ana@uleam.edu.ec", username="ana123",
            contrasena="clave-segura", rol="Administrador",
        )
        self.assertFalse(ok)
        self.assertIn("rol", mensaje.lower())
        self.db.rpc.assert_not_called()

    def test_registro_usa_rpc_para_guardar_clave_en_servidor(self):
        ok, _ = self.controller.registrar_usuario(
            identificacion="1234567890", nombre="Ana", apellido="Paz",
            email="ana@uleam.edu.ec", username="ana123",
            contrasena="clave-segura", rol="Estudiante",
        )
        self.assertTrue(ok)
        nombre, parametros = self.db.rpc.call_args.args
        self.assertEqual(nombre, "beeweek_register")
        self.assertEqual(parametros["p_password"], "clave-segura")
        self.assertEqual(parametros["p_rol"], "Estudiante")
        self.db.table.assert_not_called()

    def test_estudiante_guarda_relacion_con_curso(self):
        estudiante = Estudiante(
            "1234567890", "Ana", "Paz", "ana@uleam.edu.ec",
            "M001", "Software", db_client=self.db, curso_id=7,
        )
        estudiante.guardar()
        tabla = self.db.table.return_value
        tabla.insert.assert_called_once()
        self.assertEqual(tabla.insert.call_args.args[0]["curso_id"], 7)


if __name__ == "__main__":
    unittest.main()
