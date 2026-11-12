import unittest

from componentes.tabla_busqueda import filtrar_registros


class TablaBusquedaTests(unittest.TestCase):
    def test_busca_sin_distinguir_tildes_de_mayusculas(self):
        registros = [
            {"nombre": "Ana Pérez", "curso": "Paralelo A"},
            {"nombre": "Carlos Mendoza", "curso": "Paralelo B"},
        ]

        self.assertEqual(
            filtrar_registros(registros, ("nombre", "curso"), "  PEREZ "),
            [registros[0]],
        )
        self.assertEqual(
            filtrar_registros(registros, ("nombre", "curso"), "paralelo b"),
            [registros[1]],
        )


if __name__ == "__main__":
    unittest.main()
