import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from controladores.horario_controller import HorarioController
from modelos.estado_horario import estado_horario


class EstadoHorarioTests(unittest.TestCase):
    def test_transiciones_y_visibilidad(self):
        borrador = estado_horario("Borrador")
        self.assertFalse(borrador.visible_en_calendario())
        self.assertTrue(borrador.cambiar_a("Publicado").visible_en_calendario())
        self.assertFalse(estado_horario("Cancelado").puede_editar())
        with self.assertRaises(ValueError):
            estado_horario("Publicado").cambiar_a("Borrador")

    def test_cambiar_estado_actualiza_y_notifica(self):
        db = Mock()
        db.table.return_value.select.return_value.eq.return_value.execute.return_value = SimpleNamespace(
            data=[{"id": 7, "estado": "Borrador"}]
        )
        controller = HorarioController(db)
        observador = Mock()
        controller.suscribir(observador)

        ok, _ = controller.cambiar_estado(7, "Publicado")

        self.assertTrue(ok)
        db.table.return_value.update.assert_called_once_with({"estado": "Publicado"})
        observador.assert_called_once_with("estado")


if __name__ == "__main__":
    unittest.main()
