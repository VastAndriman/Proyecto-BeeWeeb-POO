import threading
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from componentes.tareas_ui import iniciar_tarea
from controladores.disponibilidad_horario import evaluar_disponibilidad
from controladores.filtros_horario import filtrar_horarios
from vistas.horario_view import HorarioView


class MejorasHorariosTests(unittest.TestCase):
    def setUp(self):
        self.horarios = [{
            "id": 1, "dia": "Miércoles", "hora_inicio": "08:00:00",
            "hora_fin": "10:00:00", "aula_id": 2, "docente_id": 3,
            "materia_id": 4, "curso_id": 5, "estado": "Publicado",
        }, {
            "id": 2, "dia": "Viernes", "hora_inicio": "11:00:00",
            "hora_fin": "12:00:00", "aula_id": 2, "docente_id": 3,
            "materia_id": 6, "curso_id": 5, "estado": "Borrador",
        }]

    def test_busqueda_local_por_materia_dia_y_estado(self):
        filtrados = filtrar_horarios(
            self.horarios, texto="programacion", dia="Miércoles",
            estado="Publicado", nombres={"materia": {"4": "Programación Orientada a Objetos"}},
        )
        self.assertEqual([fila["id"] for fila in filtrados], [1])

        vista = SimpleNamespace(
            _horarios_historial=self.horarios,
            _aulas_lookup={}, _docentes_lookup={},
            _materias_lookup={"4": "Programación Orientada a Objetos"},
            _cursos_lookup={}, entry_buscar_horario=Mock(),
            combo_filtro_dia=Mock(), combo_filtro_estado=Mock(),
            lbl_total_horarios=Mock(), textbox_horarios=Mock(), combo_horario=Mock(),
        )
        vista.entry_buscar_horario.get.return_value = "programacion"
        vista.combo_filtro_dia.get.return_value = "Miércoles"
        vista.combo_filtro_estado.get.return_value = "Publicado"
        HorarioView._filtrar_historial(vista)
        self.assertEqual(len(vista.horarios_map), 1)
        self.assertIn("1 de 2", vista.lbl_total_horarios.configure.call_args.kwargs["text"])

    def test_vista_previa_detecta_cruce_y_aforo(self):
        datos = dict(
            dia="Miércoles", inicio="09:00", fin="10:00", aula_id=2,
            docente_id=3, curso_id=5, estudiantes=20, capacidad=40,
            horarios=self.horarios,
        )
        disponible, mensaje = evaluar_disponibilidad(**datos)
        self.assertFalse(disponible)
        self.assertIn("Cruce", mensaje)
        disponible, _ = evaluar_disponibilidad(**{**datos, "estado": "Borrador"})
        self.assertTrue(disponible)
        disponible, mensaje = evaluar_disponibilidad(**{**datos, "capacidad": 10})
        self.assertFalse(disponible)
        self.assertIn("Aforo", mensaje)

    def test_respuesta_remota_no_bloquea_la_interfaz(self):
        callbacks = []
        principal = threading.get_ident()
        liberado = threading.Event()
        widget = Mock()
        widget.winfo_exists.return_value = True
        widget.after.side_effect = lambda _ms, callback: callbacks.append(callback)
        terminado = Mock()

        futuro = iniciar_tarea(
            widget, lambda: (liberado.wait(2), threading.get_ident())[1],
            terminado, Mock(),
        )
        self.assertFalse(futuro.done())
        liberado.set()
        trabajador = futuro.result(timeout=3)
        while callbacks:
            callbacks.pop(0)()
        self.assertNotEqual(trabajador, principal)
        terminado.assert_called_once_with(trabajador)


if __name__ == "__main__":
    unittest.main()
