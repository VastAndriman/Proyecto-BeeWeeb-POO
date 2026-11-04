import csv
import tempfile
import unittest
from pathlib import Path

from vistas.reportes_view import guardar_csv


class ReporteCsvTests(unittest.TestCase):
    def test_exporta_acentos_y_trata_formulas_como_texto(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "reporte.csv"
            guardar_csv(ruta, ["Número", "Nombre"], [[101, "Álgebra"], [102, "=1+1"]])

            with ruta.open(encoding="utf-8-sig", newline="") as archivo:
                filas = list(csv.reader(archivo, delimiter=";"))

        self.assertEqual(filas, [["Número", "Nombre"], ["101", "Álgebra"], ["102", "'=1+1"]])


if __name__ == "__main__":
    unittest.main()
