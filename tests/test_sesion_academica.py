import unittest
from unittest.mock import Mock

from conexion.supabase_client import BeeWeekClient


class SesionAcademicaTests(unittest.TestCase):
    def setUp(self):
        self.raw = Mock()
        self.db = BeeWeekClient(self.raw)

    def test_bloquea_lectura_sin_login(self):
        with self.assertRaises(PermissionError):
            self.db.table("aulas").select("*").execute()
        self.raw.rpc.assert_not_called()

    def test_lectura_e_insercion_usan_token_y_rpc(self):
        token = "a" * 64
        self.db.iniciar_sesion(token)
        self.raw.rpc.return_value.execute.return_value.data = [{"id": 2, "dia": "Lunes"}]
        rows = self.db.table("horarios").select("id", count="exact").eq("dia", "Lunes").execute()
        self.assertEqual(rows.data, [{"id": 2}])
        self.assertEqual(rows.count, 1)
        self.raw.rpc.assert_called_with("beeweek_list", {
            "p_token": token, "p_table": "horarios",
            "p_filter_column": "dia", "p_filter_value": "Lunes",
        })

        self.raw.rpc.return_value.execute.return_value.data = {"id": 3, "numero": "A1"}
        inserted = self.db.table("aulas").insert({"numero": "A1"}).execute()
        self.assertEqual(inserted.data[0]["id"], 3)
        self.raw.rpc.assert_called_with("beeweek_insert", {
            "p_token": token, "p_table": "aulas", "p_data": {"numero": "A1"},
        })

    def test_cerrar_sesion_revoca_token_local(self):
        self.db.iniciar_sesion("a" * 64)
        self.db.cerrar_sesion()
        with self.assertRaises(PermissionError):
            self.db.table("aulas").select().execute()

    def test_edicion_y_eliminacion_envian_id_y_sesion_al_servidor(self):
        token = "a" * 64
        self.db.iniciar_sesion(token)
        self.raw.rpc.return_value.execute.return_value.data = {"id": 9}

        self.db.table("aulas").update({"capacidad": 40}).eq("id", 9).execute()
        self.raw.rpc.assert_called_with("beeweek_update", {
            "p_token": token, "p_table": "aulas", "p_id": 9,
            "p_data": {"capacidad": 40},
        })
        self.db.table("horarios").delete().eq("id", 9).execute()
        self.raw.rpc.assert_called_with("beeweek_delete", {
            "p_token": token, "p_table": "horarios", "p_id": 9,
        })

    def test_no_permite_borrado_sin_id(self):
        self.db.iniciar_sesion("a" * 64)
        with self.assertRaises(ValueError):
            self.db.table("aulas").delete().execute()
        self.raw.rpc.assert_not_called()


if __name__ == "__main__":
    unittest.main()
