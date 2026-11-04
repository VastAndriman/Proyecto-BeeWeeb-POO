import customtkinter as ctk

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
        self.materias_lista = ctk.CTkTextbox(parent, height=170, font=("Courier", 11))
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
        self.cursos_lista = ctk.CTkTextbox(parent, height=170, font=("Courier", 11))
        self.cursos_lista.pack(fill="both", expand=True, padx=18, pady=(8, 18))

    def cargar_datos_dinamicos(self):
        self.materias_lista.delete("0.0", "end")
        self.cursos_lista.delete("0.0", "end")
        try:
            materias = self.controller.listar_materias()
            for materia in materias:
                self.materias_lista.insert(
                    "end", f"{materia.get('nombre', '')} · {materia.get('creditos', '')} créditos · Sem. {materia.get('semestre', '')}\n"
                )
            if not materias:
                self.materias_lista.insert("end", "No hay materias registradas.")
        except Exception as error:
            self.materias_lista.insert("end", f"No se pudieron cargar las materias: {error}")
        try:
            cursos = self.controller.listar_cursos()
            for curso in cursos:
                self.cursos_lista.insert(
                    "end", f"{curso.get('paralelo', '')} · {curso.get('num_estudiantes', '')} estudiantes\n"
                )
            if not cursos:
                self.cursos_lista.insert("end", "No hay cursos registrados.")
        except Exception as error:
            self.cursos_lista.insert("end", f"No se pudieron cargar los cursos: {error}")

    def guardar_materia(self):
        ok, mensaje = self.controller.crear_materia(
            self.materia_nombre.get(), self.materia_creditos.get(), self.materia_semestre.get()
        )
        self.materia_mensaje.configure(text=mensaje, text_color="#34d399" if ok else "#f87171")
        if ok:
            for campo in (self.materia_nombre, self.materia_creditos, self.materia_semestre):
                campo.delete(0, "end")
            self.cargar_datos_dinamicos()

    def guardar_curso(self):
        ok, mensaje = self.controller.crear_curso(
            self.curso_paralelo.get(), self.curso_estudiantes.get()
        )
        self.curso_mensaje.configure(text=mensaje, text_color="#34d399" if ok else "#f87171")
        if ok:
            for campo in (self.curso_paralelo, self.curso_estudiantes):
                campo.delete(0, "end")
            self.cargar_datos_dinamicos()
