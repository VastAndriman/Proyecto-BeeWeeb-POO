"""Patrones creacionales usados por BeeWeek.

Factory Method crea los modelos concretos para las vistas de personas.
Builder prepara un horario completo antes de las comprobaciones de la base.
La conexión Singleton real está en conexion.supabase_client.SupabaseConnection.

Este archivo también se puede ejecutar solo: ``python patrones_creacionales_beeweek.py``.
La demostración usa objetos en memoria y no modifica Supabase.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import time
from threading import Lock


class CreadorPersona(ABC):
    """Creador base; cada subclase elige el producto concreto."""

    @abstractmethod
    def crear_persona(self, **datos):
        pass

    def registrar(self, **datos):
        """Flujo común para los modelos Docente y Estudiante."""
        persona = self.crear_persona(**datos)
        persona.guardar()
        return persona


class CreadorDocente(CreadorPersona):
    def __init__(self, modelo=None):
        self._modelo = modelo

    def crear_persona(self, **datos):
        modelo = self._modelo
        if modelo is None:
            from modelos.docente import Docente
            modelo = Docente
        return modelo(**datos)


class CreadorEstudiante(CreadorPersona):
    def __init__(self, modelo=None):
        self._modelo = modelo

    def crear_persona(self, **datos):
        modelo = self._modelo
        if modelo is None:
            from modelos.estudiante import Estudiante
            modelo = Estudiante
        return modelo(**datos)


@dataclass(frozen=True)
class HorarioPreparado:
    dia: str
    hora_inicio: str
    hora_fin: str
    materia_id: int
    docente_id: int
    aula_id: int
    curso_id: int

    def para_guardar(self) -> dict:
        return {
            "dia": self.dia,
            "hora_inicio": self.hora_inicio,
            "hora_fin": self.hora_fin,
            "materia_id": self.materia_id,
            "docente_id": self.docente_id,
            "aula_id": self.aula_id,
            "curso_id": self.curso_id,
        }


class HorarioBuilder:
    """Construye un horario por pasos y valida su estructura."""

    DIAS = {"Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"}

    def __init__(self):
        self._datos = {}

    def dia(self, valor: str) -> HorarioBuilder:
        self._datos["dia"] = str(valor).strip() if valor is not None else ""
        return self

    def horas(self, inicio: str, fin: str) -> HorarioBuilder:
        self._datos["hora_inicio"] = str(inicio).strip() if inicio is not None else ""
        self._datos["hora_fin"] = str(fin).strip() if fin is not None else ""
        return self

    def materia(self, identificador: int) -> HorarioBuilder:
        self._datos["materia_id"] = identificador
        return self

    def docente(self, identificador: int) -> HorarioBuilder:
        self._datos["docente_id"] = identificador
        return self

    def aula(self, identificador: int) -> HorarioBuilder:
        self._datos["aula_id"] = identificador
        return self

    def curso(self, identificador: int) -> HorarioBuilder:
        self._datos["curso_id"] = identificador
        return self

    def construir(self) -> HorarioPreparado:
        requeridos = set(HorarioPreparado.__dataclass_fields__)
        if requeridos - self._datos.keys():
            raise ValueError("Completa todos los campos del horario.")
        if self._datos["dia"] not in self.DIAS:
            raise ValueError("Selecciona un día válido.")
        try:
            inicio = time.fromisoformat(self._datos["hora_inicio"])
            fin = time.fromisoformat(self._datos["hora_fin"])
        except (TypeError, ValueError):
            raise ValueError("Ingresa horas válidas en formato HH:MM.") from None
        if inicio >= fin:
            raise ValueError("La hora de fin debe ser posterior a la hora de inicio.")
        for campo in ("materia_id", "docente_id", "aula_id", "curso_id"):
            try:
                numero = int(self._datos[campo])
            except (TypeError, ValueError):
                raise ValueError("Selecciona una materia, docente, aula y curso válidos.") from None
            if numero <= 0:
                raise ValueError("Selecciona una materia, docente, aula y curso válidos.")
            self._datos[campo] = numero
        return HorarioPreparado(**self._datos)


# Singleton de memoria para demostrar el mecanismo sin credenciales.
# La aplicación usa el Singleton de SupabaseConnection, no esta clase.
class AlmacenDemostracion:
    _instancia = None
    _candado = Lock()

    def __new__(cls):
        if cls._instancia is None:
            with cls._candado:
                if cls._instancia is None:
                    cls._instancia = super().__new__(cls)
                    cls._instancia.personas = []
        return cls._instancia


def demostracion():
    """Comprueba los tres patrones sin red ni dependencias externas."""
    almacen = AlmacenDemostracion()
    assert almacen is AlmacenDemostracion()

    class PersonaPrueba:
        def __init__(self, tipo, **datos):
            self.tipo = tipo
            self.datos = datos

        def guardar(self):
            almacen.personas.append(self)

    docente = CreadorDocente(
        modelo=lambda **datos: PersonaPrueba("Docente", **datos)
    ).registrar(nombre="Ana", especialidad="Software")
    estudiante = CreadorEstudiante(
        modelo=lambda **datos: PersonaPrueba("Estudiante", **datos)
    ).registrar(nombre="Luis", matricula="MAT-001")
    assert docente.tipo == "Docente" and estudiante.tipo == "Estudiante"
    assert len(almacen.personas) == 2

    horario = (HorarioBuilder().dia("Lunes").horas("08:00", "09:00")
               .materia(1).docente(2).aula(3).curso(4).construir())
    assert horario.para_guardar()["curso_id"] == 4
    try:
        (HorarioBuilder().dia("Lunes").horas("10:00", "09:00")
         .materia(1).docente(2).aula(3).curso(4).construir())
    except ValueError:
        pass
    else:
        raise AssertionError("Builder aceptó horas invertidas")

    print("Singleton: una sola instancia de memoria")
    print("Factory Method: Docente y Estudiante creados y registrados")
    print("Builder: horario completo; horas invertidas rechazadas")
    print("Demostración correcta. No se modificó Supabase.")


if __name__ == "__main__":
    demostracion()
