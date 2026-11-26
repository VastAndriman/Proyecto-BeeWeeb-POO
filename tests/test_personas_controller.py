import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from controladores.personas_controller import DocentesController, EstudiantesController


class PersonasControllerTests(unittest.TestCase):
    def test_docente_usa_factory_con_cliente_inyectado(self):
        db = Mock()
        creador = Mock()
        controller = DocentesController(db, creador)

        controller.registrar(identificacion="123", nombre="Ana")

        creador.registrar.assert_called_once_with(
            identificacion="123", nombre="Ana", db_client=db,
        )

    def test_estudiantes_no_consultan_cursos_al_listarse(self):
        db = Mock()
        db.table.return_value.select.return_value.execute.return_value = SimpleNamespace(
            data=[{"id": 1, "nombre": "Ana"}]
        )
        controller = EstudiantesController(db)

        self.assertEqual(controller.listar()[0]["nombre"], "Ana")
        db.table.assert_called_once_with("estudiantes")


if __name__ == "__main__":
    unittest.main()
