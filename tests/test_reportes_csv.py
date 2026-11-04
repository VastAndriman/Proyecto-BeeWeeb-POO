import csv
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from vistas.reportes_view import ReportesView, guardar_csv


class ReporteCsvTests(unittest.TestCase):
    def test_horario_aparece_en_reporte_y_csv(self):
        controller = Mock()
        controller.obtener_materias.return_value = [{"id": 1, "nombre": "POO"}]
        controller.obtener_aulas.return_value = [{"id": 2, "numero": "101"}]
        controller.obtener_docentes.return_value = [{"id": 3, "nombre": "Ana", "apellido": "Paz"}]
        controller.obtener_cursos.return_value = [{"id": 4, "nombre": "Paralelo A"}]
        controller.obtener_horarios_registrados.return_value = [{
            "dia": "Martes", "hora_inicio": "10:00:00", "hora_fin": "11:00:00",
            "aula_id": 2, "docente_id": 3, "materia_id": 1, "curso_id": 4,
        }]
        vista = SimpleNamespace(
            horario_controller=controller, combo_tipo=Mock(),
            txt_reporte=Mock(), btn_exportar=Mock(),
            csv_columnas=[], csv_filas=[],
        )
        vista.combo_tipo.get.return_value = "Horarios Registrados"

        ReportesView.generar_reporte(vista)

        self.assertEqual(len(vista.csv_filas), 1)
        self.assertEqual(vista.csv_filas[0], [
            "Martes", "10:00-11:00", "Aula 101", "Ana Paz", "POO", "Paralelo A"
        ])
        vista.btn_exportar.configure.assert_any_call(state="normal")
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "horarios.csv"
            guardar_csv(ruta, vista.csv_columnas, vista.csv_filas)
            with ruta.open(encoding="utf-8-sig", newline="") as archivo:
                filas = list(csv.reader(archivo, delimiter=";"))
        self.assertEqual(filas[1], vista.csv_filas[0])

    def test_exporta_acentos_y_trata_formulas_como_texto(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "reporte.csv"
            guardar_csv(ruta, ["Número", "Nombre"], [[101, "Álgebra"], [102, "=1+1"]])

            with ruta.open(encoding="utf-8-sig", newline="") as archivo:
                filas = list(csv.reader(archivo, delimiter=";"))

        self.assertEqual(filas, [["Número", "Nombre"], ["101", "Álgebra"], ["102", "'=1+1"]])


if __name__ == "__main__":
    unittest.main()
