import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from main import BeeWeekApp


class PermisosUiTests(unittest.TestCase):
    def test_modulo_se_crea_al_abrirlo_y_no_se_recarga_dos_veces(self):
        dashboard = SimpleNamespace(pack=Mock(), pack_forget=Mock())
        calendario = SimpleNamespace(pack=Mock(), pack_forget=Mock(), cargar_horarios=Mock())
        app = SimpleNamespace(
            rol_actual="Administrador", vistas={"dashboard": dashboard},
            _crear_vista=Mock(return_value=calendario),
        )

        BeeWeekApp.cambiar_vista(app, "calendario")

        app._crear_vista.assert_called_once_with("calendario")
        calendario.cargar_horarios.assert_not_called()
        BeeWeekApp.cambiar_vista(app, "calendario")
        calendario.cargar_horarios.assert_called_once_with()

    def test_estudiante_no_crea_modulos_de_gestion(self):
        dashboard = SimpleNamespace(pack=Mock(), pack_forget=Mock())
        calendario = SimpleNamespace(pack=Mock(), pack_forget=Mock(), cargar_horarios=Mock())
        app = SimpleNamespace(
            rol_actual="Estudiante", vistas={"dashboard": dashboard},
            _crear_vista=Mock(return_value=calendario),
        )

        BeeWeekApp.cambiar_vista(app, "horarios")

        app._crear_vista.assert_called_once_with("calendario")
        self.assertNotIn("horarios", app.vistas)

    def test_gestion_se_oculta_para_estudiante_y_se_recupera_para_admin(self):
        botones = {name: Mock() for name in (
            "btn_horarios", "btn_aulas", "btn_docentes",
            "btn_estudiantes", "btn_academico", "btn_reportes",
        )}
        app = SimpleNamespace(rol_actual="Estudiante", **botones)
        BeeWeekApp._aplicar_permisos_visuales(app)
        for boton in botones.values():
            boton.grid_remove.assert_called_once_with()

        app.rol_actual = "Administrador"
        BeeWeekApp._aplicar_permisos_visuales(app)
        for boton in botones.values():
            boton.grid.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
