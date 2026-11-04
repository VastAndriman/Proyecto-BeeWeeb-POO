import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from main import BeeWeekApp


class PermisosUiTests(unittest.TestCase):
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
