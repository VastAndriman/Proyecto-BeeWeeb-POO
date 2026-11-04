import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vistas.calendario_view import CalendarioView


class CalendarioTests(unittest.TestCase):
    def test_muestra_aviso_si_falla_la_sincronizacion(self):
        controller = Mock()
        controller.obtener_materias.side_effect = RuntimeError("sin conexión")
        estado = Mock()
        calendario = SimpleNamespace(
            lbl_estado=estado,
            grid_container=Mock(),
            dias=["Lunes"],
            bloques=["07:00 - 08:00"],
            horario_controller=controller,
        )
        calendario.grid_container.winfo_children.return_value = []

        with patch("vistas.calendario_view.ctk.CTkLabel"), patch("vistas.calendario_view.ctk.CTkFrame"):
            CalendarioView.cargar_horarios(calendario)

        estado.configure.assert_any_call(text="")
        self.assertIn("No se pudo cargar", estado.configure.call_args.kwargs["text"])

    def test_una_clase_de_ocho_no_aparece_en_el_bloque_de_siete(self):
        bloques = ["07:00 - 08:00", "08:00 - 09:00", "09:00 - 10:00"]
        self.assertEqual(CalendarioView.fila_para_hora("08:00", bloques), 2)
        self.assertEqual(CalendarioView.fila_para_hora("08:30", bloques), 2)
        self.assertIsNone(CalendarioView.fila_para_hora("10:00", bloques))
        self.assertIsNone(CalendarioView.fila_para_hora("hora inválida", bloques))


if __name__ == "__main__":
    unittest.main()
