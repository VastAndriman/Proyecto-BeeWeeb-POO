import unittest

from vistas.calendario_view import CalendarioView


class CalendarioTests(unittest.TestCase):
    def test_una_clase_de_ocho_no_aparece_en_el_bloque_de_siete(self):
        bloques = ["07:00 - 08:00", "08:00 - 09:00", "09:00 - 10:00"]
        self.assertEqual(CalendarioView.fila_para_hora("08:00", bloques), 2)
        self.assertEqual(CalendarioView.fila_para_hora("08:30", bloques), 2)
        self.assertIsNone(CalendarioView.fila_para_hora("10:00", bloques))
        self.assertIsNone(CalendarioView.fila_para_hora("hora inválida", bloques))


if __name__ == "__main__":
    unittest.main()
