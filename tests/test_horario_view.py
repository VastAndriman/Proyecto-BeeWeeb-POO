import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from vistas.horario_view import HorarioView


class HorarioViewTests(unittest.TestCase):
    def test_dejar_de_editar_habilita_crear_con_opciones_completas(self):
        vista = SimpleNamespace(
            combo_horario=Mock(), combo_dia=Mock(), combo_h_inicio=Mock(),
            combo_h_fin=Mock(), combo_docente=Mock(), combo_aula=Mock(),
            combo_materia=Mock(), combo_curso=Mock(), btn_crear=Mock(),
            lbl_mensaje=Mock(), al_seleccionar_aula=Mock(), al_seleccionar_curso=Mock(),
            docentes_map={"Ana": 1}, aulas_map={"Aula 101": {"id": 2}},
            materias_map={"POO": 3}, cursos_map={"Paralelo A": {"id": 4}},
        )

        HorarioView.dejar_de_editar(vista)

        vista.combo_horario.set.assert_called_with("Selecciona un horario para editar o eliminar")
        vista.btn_crear.configure.assert_called_with(state="normal")

    def test_fallo_al_sincronizar_deshabilita_registro(self):
        controller = Mock()
        controller.obtener_docentes.side_effect = RuntimeError("sin conexión")
        vista = SimpleNamespace(
            horario_controller=controller,
            docentes_map={"anterior": 1}, aulas_map={"anterior": 2},
            materias_map={"anterior": 3}, cursos_map={"anterior": 4},
            horarios_map={"anterior": {"id": 5}},
            combo_docente=Mock(), combo_aula=Mock(), combo_materia=Mock(),
            combo_curso=Mock(), combo_horario=Mock(),
            al_seleccionar_aula=Mock(), al_seleccionar_curso=Mock(),
            textbox_horarios=Mock(), btn_crear=Mock(), lbl_mensaje=Mock(),
        )

        HorarioView.cargar_datos_dinamicos(vista)

        self.assertEqual(vista.horarios_map, {})
        vista.btn_crear.configure.assert_called_with(state="disabled")
        self.assertIn("No se pudieron sincronizar", vista.lbl_mensaje.configure.call_args.kwargs["text"])

    def test_fallo_del_historial_no_aparece_como_lista_vacia(self):
        controller = Mock()
        controller.obtener_horarios_registrados.side_effect = RuntimeError("sin conexión")
        vista = SimpleNamespace(
            horario_controller=controller, textbox_horarios=Mock(),
            combo_horario=Mock(), horarios_map={"anterior": {"id": 5}},
        )

        ok = HorarioView.refrescar_historial_horarios(vista)

        self.assertFalse(ok)
        self.assertEqual(vista.horarios_map, {})
        self.assertIn("No se pudo cargar", vista.textbox_horarios.insert.call_args.args[1])

    def test_guardado_exitoso_con_historial_no_disponible(self):
        vista = SimpleNamespace(
            lbl_mensaje=Mock(),
            refrescar_historial_horarios=Mock(return_value=False),
        )

        HorarioView._mostrar_resultado_horario(vista, True, "Horario actualizado.")

        texto = vista.lbl_mensaje.configure.call_args.kwargs["text"]
        self.assertIn("Horario actualizado", texto)
        self.assertIn("No se pudo actualizar el historial", texto)

    def test_rechazo_no_recarga_historial(self):
        vista = SimpleNamespace(
            lbl_mensaje=Mock(),
            refrescar_historial_horarios=Mock(),
        )

        HorarioView._mostrar_resultado_horario(vista, False, "Hay un cruce.")

        vista.refrescar_historial_horarios.assert_not_called()
        self.assertIn("Hay un cruce", vista.lbl_mensaje.configure.call_args.kwargs["text"])


if __name__ == "__main__":
    unittest.main()
