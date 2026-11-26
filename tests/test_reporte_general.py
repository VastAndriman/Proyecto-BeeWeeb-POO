import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from controladores.reporte_general_controller import ReporteGeneralController
from vistas.reportes_view import ReportesView


class ReporteGeneralTests(unittest.TestCase):
    def test_resume_modelos_y_aparece_en_reportes(self):
        horarios = Mock()
        horarios.obtener_aulas.return_value = [{"numero": "101", "capacidad": 40, "tipo": "Laboratorio"}]
        horarios.obtener_docentes.return_value = [{
            "identificacion": "1234567890", "nombre": "Ana", "apellido": "Paz",
            "email": "ana@uleam.edu.ec", "especialidad": "Software",
        }]
        horarios.obtener_cursos.return_value = [{"paralelo": "A", "num_estudiantes": 25}]
        horarios.obtener_horarios_registrados.return_value = [{
            "dia": "Lunes", "hora_inicio": "08:00:00", "hora_fin": "10:00:00",
            "materia_id": 1, "docente_id": 1, "aula_id": 1, "curso_id": 1,
        }]
        vista = SimpleNamespace(
            reporte_general_controller=ReporteGeneralController(horarios),
            combo_tipo=Mock(), txt_reporte=Mock(), lbl_resumen=Mock(),
            btn_exportar=Mock(), csv_columnas=[], csv_filas=[],
        )
        vista.combo_tipo.get.return_value = "Resumen Institucional"

        ReportesView.generar_reporte(vista)

        self.assertEqual(vista.csv_columnas, ["Recurso", "Resumen"])
        self.assertIn(["Horarios", "1 bloques; 2 horas semanales"], vista.csv_filas)
        self.assertIn(["Aulas", "1 registradas; capacidad total: 40 puestos"], vista.csv_filas)
        vista.btn_exportar.configure.assert_any_call(state="normal")


if __name__ == "__main__":
    unittest.main()
