import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from controladores.horario_controller import HorarioController
from modelos.docente import Docente
from modelos.estudiante import Estudiante
from patrones_creacionales_beeweek import (
    AlmacenDemostracion, CreadorDocente, CreadorEstudiante, HorarioBuilder,
)


class PatronesCreacionalesTests(unittest.TestCase):
    def test_singleton_de_demostracion_comparte_instancia(self):
        self.assertIs(AlmacenDemostracion(), AlmacenDemostracion())

    def test_factory_method_crea_y_guarda_modelos_reales(self):
        db = Mock()
        docente = CreadorDocente().registrar(
            identificacion="1000000001", nombre="Ana", apellido="Luna",
            email="ana@ejemplo.edu", especialidad="Software", db_client=db,
        )
        estudiante = CreadorEstudiante().registrar(
            identificacion="1000000002", nombre="Luis", apellido="Mora",
            email="luis@ejemplo.edu", matricula="MAT-1", carrera="Software",
            curso_id=7, db_client=db,
        )
        self.assertIsInstance(docente, Docente)
        self.assertIsInstance(estudiante, Estudiante)
        self.assertEqual(docente.obtener_tipo(), "Docente")
        self.assertEqual(estudiante.obtener_tipo(), "Estudiante")
        self.assertEqual(db.table.call_args_list[0].args, ("docentes",))
        self.assertEqual(db.table.call_args_list[1].args, ("estudiantes",))
        self.assertEqual(db.table.return_value.insert.call_args.args[0]["curso_id"], 7)

    def test_builder_rechaza_datos_incompletos_y_horas_invertidas(self):
        with self.assertRaisesRegex(ValueError, "Completa"):
            HorarioBuilder().dia("Lunes").construir()
        with self.assertRaisesRegex(ValueError, "posterior"):
            (HorarioBuilder().dia("Lunes").horas("10:00", "09:00")
             .materia(1).docente(2).aula(3).curso(4).construir())

    def test_controlador_usa_builder_y_registra_horario_valido(self):
        db = Mock()
        curso = Mock()
        curso.select.return_value.eq.return_value.execute.return_value = SimpleNamespace(
            data=[{"num_estudiantes": 25}]
        )
        aula = Mock()
        aula.select.return_value.eq.return_value.execute.return_value = SimpleNamespace(
            data=[{"capacidad": 30}]
        )
        horarios = Mock()
        horarios.select.return_value.eq.return_value.execute.return_value = SimpleNamespace(data=[])
        db.table.side_effect = {"cursos": curso, "aulas": aula, "horarios": horarios}.__getitem__

        ok, _ = HorarioController(db).validar_y_crear_horario(
            dia="Lunes", hora_inicio="08:00", hora_fin="09:00",
            materia_id=1, docente_id=2, aula_id=3, curso_id=4,
        )

        self.assertTrue(ok)
        self.assertEqual(horarios.insert.call_args.args[0]["curso_id"], 4)
        self.assertEqual(horarios.insert.call_args.args[0]["hora_inicio"], "08:00")

    def test_builder_impide_escritura_si_faltan_referencias(self):
        db = Mock()
        ok, _ = HorarioController(db).validar_y_crear_horario(
            dia="Lunes", hora_inicio="08:00", hora_fin="09:00",
            materia_id=None, docente_id=2, aula_id=3, curso_id=4,
        )
        self.assertFalse(ok)
        db.table.assert_not_called()


if __name__ == "__main__":
    unittest.main()
