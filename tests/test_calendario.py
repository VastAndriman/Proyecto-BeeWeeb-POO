import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vistas.calendario_view import CalendarioView


class CalendarioTests(unittest.TestCase):
    def test_avisa_si_un_horario_queda_fuera_de_la_grilla(self):
        controller = Mock()
        controller.obtener_materias.return_value = []
        controller.obtener_aulas.return_value = []
        controller.obtener_docentes.return_value = []
        controller.obtener_cursos.return_value = []
        controller.obtener_horarios_registrados.return_value = [{
            "dia": "Lunes", "hora_inicio": "19:00:00", "hora_fin": "20:00:00",
        }]
        calendario = SimpleNamespace(
            lbl_estado=Mock(), grid_container=Mock(), dias=["Lunes"],
            bloques=["07:00 - 08:00"], horario_controller=controller,
            normalizar_dia=lambda dia: dia,
        )
        calendario.grid_container.winfo_children.return_value = []

        with patch("vistas.calendario_view.ctk.CTkLabel"), patch("vistas.calendario_view.ctk.CTkFrame"):
            CalendarioView.cargar_horarios(calendario)

        self.assertIn("1 horario", calendario.lbl_estado.configure.call_args.kwargs["text"])

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

    def test_clase_larga_ocupa_todas_sus_horas(self):
        bloques = [f"{hora:02d}:00 - {hora + 1:02d}:00" for hora in range(7, 19)]
        self.assertEqual(
            CalendarioView.filas_para_intervalo("07:00", "19:00", bloques),
            (1, 12),
        )
        self.assertEqual(
            CalendarioView.filas_para_intervalo("08:00", "10:00", bloques),
            (2, 2),
        )

    def test_clase_larga_se_muestra_en_cada_bloque_sin_tapar_celdas(self):
        controller = Mock()
        controller.obtener_materias.return_value = [{"id": 1, "nombre": "POO"}]
        controller.obtener_aulas.return_value = [{"id": 2, "numero": "101"}]
        controller.obtener_docentes.return_value = [{"id": 3, "nombre": "Ana"}]
        controller.obtener_cursos.return_value = [{"id": 4, "nombre": "A"}]
        controller.obtener_horarios_registrados.return_value = [{
            "dia": "Viernes", "hora_inicio": "07:00:00", "hora_fin": "19:00:00",
            "materia_id": 1, "aula_id": 2, "docente_id": 3, "curso_id": 4,
        }]
        calendario = SimpleNamespace(
            lbl_estado=Mock(), grid_container=Mock(),
            dias=["Viernes"],
            bloques=[f"{hora:02d}:00 - {hora + 1:02d}:00" for hora in range(7, 19)],
            horario_controller=controller,
            normalizar_dia=lambda dia: dia,
            filas_para_intervalo=CalendarioView.filas_para_intervalo,
        )
        calendario.grid_container.winfo_children.return_value = []

        marcos = [Mock() for _ in range(24)]
        with patch("vistas.calendario_view.ctk.CTkLabel"), patch(
            "vistas.calendario_view.ctk.CTkFrame", side_effect=marcos
        ) as frame:
            CalendarioView.cargar_horarios(calendario)

        self.assertEqual(frame.call_count, 24)
        for tarjeta in marcos[12:]:
            tarjeta.pack.assert_called_once()
            tarjeta.grid.assert_not_called()

    def test_clases_simultaneas_comparten_celda_sin_superponerse(self):
        controller = Mock()
        controller.obtener_materias.return_value = [{"id": 1, "nombre": "POO"}]
        controller.obtener_aulas.return_value = [{"id": 2, "numero": "101"}]
        controller.obtener_docentes.return_value = [{"id": 3, "nombre": "Ana"}]
        controller.obtener_cursos.return_value = [{"id": 4, "nombre": "A"}]
        horario = {
            "dia": "Lunes", "hora_inicio": "07:00:00", "hora_fin": "08:00:00",
            "materia_id": 1, "aula_id": 2, "docente_id": 3, "curso_id": 4,
        }
        controller.obtener_horarios_registrados.return_value = [
            horario, {**horario, "aula_id": 8, "docente_id": 9, "curso_id": 10},
        ]
        calendario = SimpleNamespace(
            lbl_estado=Mock(), grid_container=Mock(), dias=["Lunes"],
            bloques=["07:00 - 08:00"], horario_controller=controller,
            normalizar_dia=lambda dia: dia,
            filas_para_intervalo=CalendarioView.filas_para_intervalo,
        )
        calendario.grid_container.winfo_children.return_value = []
        marcos = [Mock() for _ in range(3)]

        with patch("vistas.calendario_view.ctk.CTkLabel"), patch(
            "vistas.calendario_view.ctk.CTkFrame", side_effect=marcos
        ) as frame:
            CalendarioView.cargar_horarios(calendario)

        self.assertEqual(frame.call_count, 3)
        self.assertIs(frame.call_args_list[1].args[0], marcos[0])
        self.assertIs(frame.call_args_list[2].args[0], marcos[0])
        marcos[1].pack.assert_called_once()
        marcos[2].pack.assert_called_once()


if __name__ == "__main__":
    unittest.main()
