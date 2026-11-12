import customtkinter as ctk

from componentes.tabla_busqueda import TablaBusqueda
from controladores.academico_controller import AcademicoController


class AcademicoView(ctk.CTkFrame):
    def __init__(self, master, academico_controller=None):
        super().__init__(master, fg_color="transparent")
        self.controller = (academico_controller if academico_controller is not None
                           else AcademicoController())

        ctk.CTkLabel(
            self, text="Materias y Cursos", font=("Arial", 22, "bold")
        ).pack(anchor="w", padx=30, pady=(22, 4))
        ctk.CTkLabel(
            self, text="Registra los datos académicos que usarás al crear horarios.",
            font=("Arial", 12), text_color="gray"
        ).pack(anchor="w", padx=30, pady=(0, 15))

        columns = ctk.CTkFrame(self, fg_color="transparent")
        columns.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        materia_frame = ctk.CTkFrame(columns, corner_radius=10)
        materia_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))
        curso_frame = ctk.CTkFrame(columns, corner_radius=10)
        curso_frame.pack(side="left", fill="both", expand=True, padx=(8, 0))

        self._construir_materias(materia_frame)
        self._construir_cursos(curso_frame)
        self.cargar_datos_dinamicos()

    def _campo(self, parent, titulo, ejemplo):
        ctk.CTkLabel(parent, text=titulo, font=("Arial", 12)).pack(
            anchor="w", padx=18, pady=(7, 3)
        )
        entrada = ctk.CTkEntry(parent, placeholder_text=ejemplo, height=34)
        entrada.pack(fill="x", padx=18)
        return entrada

    def _construir_materias(self, parent):
        ctk.CTkLabel(parent, text="Materias", font=("Arial", 17, "bold")).pack(
            anchor="w", padx=18, pady=(15, 5)
        )
        self.materia_nombre = self._campo(parent, "Nombre", "Programación Orientada a Objetos")
        self.materia_creditos = self._campo(parent, "Créditos", "4")
        self.materia_semestre = self._campo(parent, "Semestre", "3")
        ctk.CTkButton(parent, text="Guardar materia", command=self.guardar_materia).pack(
            fill="x", padx=18, pady=(12, 4)
        )
        self.materia_mensaje = ctk.CTkLabel(parent, text="", wraplength=350)
        self.materia_mensaje.pack(fill="x", padx=18)
        self.materias_lista = TablaBusqueda(
            parent,
            (("nombre", "Materia", 190), ("creditos", "Créditos", 90),
             ("semestre", "Semestre", 90)),
        )
        self.materias_lista.pack(fill="both", expand=True, padx=18, pady=(8, 18))

    def _construir_cursos(self, parent):
        ctk.CTkLabel(parent, text="Cursos", font=("Arial", 17, "bold")).pack(
            anchor="w", padx=18, pady=(15, 5)
        )
        self.curso_paralelo = self._campo(parent, "Paralelo", "Tercero A")
        self.curso_estudiantes = self._campo(parent, "Número de estudiantes", "30")
        ctk.CTkButton(parent, text="Guardar curso", command=self.guardar_curso).pack(
            fill="x", padx=18, pady=(12, 4)
        )
        self.curso_mensaje = ctk.CTkLabel(parent, text="", wraplength=350)
        self.curso_mensaje.pack(fill="x", padx=18)
        self.cursos_lista = TablaBusqueda(
            parent,
            (("paralelo", "Curso / paralelo", 190),
             ("num_estudiantes", "Estudiantes", 110)),
        )
        self.cursos_lista.pack(fill="both", expand=True, padx=18, pady=(8, 18))

    def cargar_datos_dinamicos(self):
        self.materias_lista.set_rows([])
        self.cursos_lista.set_rows([])
        materias_ok = cursos_ok = True
        try:
            materias = self.controller.listar_materias()
            self.materias_lista.set_rows(materias)
        except Exception as error:
            materias_ok = False
            self.materias_lista.set_error(f"No se pudieron cargar las materias: {error}")
        try:
            cursos = self.controller.listar_cursos()
            self.cursos_lista.set_rows(cursos)
        except Exception as error:
            cursos_ok = False
            self.cursos_lista.set_error(f"No se pudieron cargar los cursos: {error}")
        return materias_ok, cursos_ok

    def guardar_materia(self):
        ok, mensaje = self.controller.crear_materia(
            self.materia_nombre.get(), self.materia_creditos.get(), self.materia_semestre.get()
        )
        color = "#15803d" if ok else "#b42333"
        if ok:
            for campo in (self.materia_nombre, self.materia_creditos, self.materia_semestre):
                campo.delete(0, "end")
            materias_ok, _ = self.cargar_datos_dinamicos()
            if not materias_ok:
                mensaje += " No se pudo actualizar la lista; vuelve a abrir Materias y Cursos."
                color = "#9a6700"
        self.materia_mensaje.configure(text=mensaje, text_color=color)

    def guardar_curso(self):
        ok, mensaje = self.controller.crear_curso(
            self.curso_paralelo.get(), self.curso_estudiantes.get()
        )
        color = "#15803d" if ok else "#b42333"
        if ok:
            for campo in (self.curso_paralelo, self.curso_estudiantes):
                campo.delete(0, "end")
            _, cursos_ok = self.cargar_datos_dinamicos()
            if not cursos_ok:
                mensaje += " No se pudo actualizar la lista; vuelve a abrir Materias y Cursos."
                color = "#9a6700"
        self.curso_mensaje.configure(text=mensaje, text_color=color)
