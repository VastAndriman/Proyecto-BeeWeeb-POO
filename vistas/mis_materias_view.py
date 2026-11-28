from tkinter import messagebox

import customtkinter as ctk

from componentes.tareas_ui import iniciar_tarea


class MisMateriasView(ctk.CTkScrollableFrame):
    """Inscripciones propias a materias con horarios publicados."""

    def __init__(self, master, inscripciones_controller):
        super().__init__(master, fg_color="transparent")
        self.controller = inscripciones_controller
        self.ofertas = {}
        self.inscripciones = {}
        self._ocupado = False

        ctk.CTkLabel(self, text="Mis materias", font=("Arial", 22, "bold"),
                     text_color="#4b3f76").pack(anchor="w", padx=30, pady=(25, 5))
        ctk.CTkLabel(self, text="Inscríbete en una materia con horario publicado o retírate de una inscripción.",
                     text_color="#786f95").pack(anchor="w", padx=30, pady=(0, 18))

        self.bloque_ofertas = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=14)
        self.bloque_ofertas.pack(fill="x", padx=30, pady=(0, 16))
        ctk.CTkLabel(self.bloque_ofertas, text="Materias disponibles",
                     font=("Arial", 16, "bold"), text_color="#4b3f76").pack(
                         anchor="w", padx=20, pady=(18, 8))
        self.selector_oferta = ctk.CTkOptionMenu(
            self.bloque_ofertas, values=["Cargando..."], width=450,
            fg_color="#7256ac", button_color="#5e4497", command=self._seleccionar_oferta)
        self.selector_oferta.pack(anchor="w", padx=20, pady=(0, 9))
        self.lbl_horario = ctk.CTkLabel(self.bloque_ofertas, text="", text_color="#786f95",
                                        wraplength=650, justify="left")
        self.lbl_horario.pack(anchor="w", padx=20, pady=(0, 10))
        self.btn_inscribir = ctk.CTkButton(
            self.bloque_ofertas, text="Inscribirme", command=self.inscribir,
            fg_color="#7256ac", hover_color="#5e4497")
        self.btn_inscribir.pack(anchor="w", padx=20, pady=(0, 18))

        self.bloque_inscritas = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=14)
        self.bloque_inscritas.pack(fill="x", padx=30, pady=(0, 16))
        ctk.CTkLabel(self.bloque_inscritas, text="Mis inscripciones",
                     font=("Arial", 16, "bold"), text_color="#4b3f76").pack(
                         anchor="w", padx=20, pady=(18, 8))
        self.selector_inscripcion = ctk.CTkOptionMenu(
            self.bloque_inscritas, values=["Cargando..."], width=450,
            fg_color="#7256ac", button_color="#5e4497")
        self.selector_inscripcion.pack(anchor="w", padx=20, pady=(0, 10))
        self.btn_retirar = ctk.CTkButton(
            self.bloque_inscritas, text="Retirarme de la materia", command=self.retirar,
            fg_color="#b42333", hover_color="#921c28", width=190)
        self.btn_retirar.pack(anchor="w", padx=20, pady=(0, 18))

        self.btn_actualizar = ctk.CTkButton(
            self, text="Actualizar materias", command=self.cargar_datos_dinamicos,
            fg_color="#eee8fc", text_color="#4b3f76", hover_color="#d6c9f3")
        self.btn_actualizar.pack(anchor="w", padx=30)
        self.lbl_estado = ctk.CTkLabel(self, text="", text_color="#786f95")
        self.lbl_estado.pack(anchor="w", padx=30, pady=(8, 20))
        self.cargar_datos_dinamicos()

    @staticmethod
    def _etiqueta(item):
        return f"{item['materia']} · {item['curso']}"

    def _seleccionar_oferta(self, etiqueta):
        oferta = self.ofertas.get(etiqueta)
        if oferta:
            self.lbl_horario.configure(
                text=f"Horario: {oferta['horario']}  |  Cupos disponibles: {oferta['cupos']}")
            inscrita = any(
                i['materia_id'] == oferta['materia_id'] and i['curso_id'] == oferta['curso_id']
                for i in self.inscripciones.values())
            self.btn_inscribir.configure(
                state="disabled" if self._ocupado or inscrita or oferta['cupos'] == 0 else "normal")
        else:
            self.lbl_horario.configure(text="No hay materias con horario publicado.")
            self.btn_inscribir.configure(state="disabled")

    def cargar_datos_dinamicos(self, mensaje_exito=None):
        if self._ocupado:
            return
        self._ocupado = True
        self.btn_inscribir.configure(state="disabled")
        self.btn_retirar.configure(state="disabled")
        self.btn_actualizar.configure(state="disabled")
        self.lbl_estado.configure(text="Cargando materias...", text_color="#786f95")

        def terminar(datos):
            self._ocupado = False
            self.btn_actualizar.configure(state="normal")
            self.ofertas = {self._etiqueta(i): i for i in datos.get("ofertas", [])}
            self.inscripciones = {self._etiqueta(i): i for i in datos.get("inscripciones", [])}
            opciones = list(self.ofertas) or ["Sin materias disponibles"]
            self.selector_oferta.configure(values=opciones)
            self.selector_oferta.set(opciones[0])
            self._seleccionar_oferta(opciones[0])
            inscritas = list(self.inscripciones) or ["Aún no tienes materias inscritas"]
            self.selector_inscripcion.configure(values=inscritas)
            self.selector_inscripcion.set(inscritas[0])
            self.btn_retirar.configure(state="normal" if self.inscripciones else "disabled")
            self.lbl_estado.configure(
                text=mensaje_exito or f"Tienes {len(self.inscripciones)} materia(s) inscrita(s).",
                text_color="#15803d")

        def fallar(_error):
            self._ocupado = False
            self.btn_actualizar.configure(state="normal")
            self.lbl_estado.configure(text="No se pudieron cargar tus materias. Revisa la conexión.",
                                      text_color="#b42333")

        iniciar_tarea(self, self.controller.catalogo, terminar, fallar)

    def _cambiar(self, trabajo, mensaje):
        self._ocupado = True
        self.btn_inscribir.configure(state="disabled")
        self.btn_retirar.configure(state="disabled")
        self.lbl_estado.configure(text="Guardando cambio...", text_color="#786f95")

        def terminar(_resultado):
            self._ocupado = False
            self.cargar_datos_dinamicos(
                "Materia inscrita correctamente." if mensaje == "inscribir la materia"
                else "Te retiraste de la materia correctamente.")

        def fallar(error):
            self._ocupado = False
            self.btn_retirar.configure(state="normal" if self.inscripciones else "disabled")
            self._seleccionar_oferta(self.selector_oferta.get())
            detalle = str(getattr(error, "message", error)).lower()
            if "cupos" in detalle:
                self.lbl_estado.configure(text="Ya no quedan cupos disponibles.", text_color="#b42333")
            elif "cruza" in detalle:
                self.lbl_estado.configure(text="La materia se cruza con otra de tus clases.",
                                          text_color="#b42333")
            elif "inscrito" in detalle:
                self.lbl_estado.configure(text="Ya estás inscrito en esa materia.",
                                          text_color="#b42333")
            else:
                self.lbl_estado.configure(text=f"No se pudo {mensaje}. Actualiza e inténtalo de nuevo.",
                                          text_color="#b42333")

        iniciar_tarea(self, trabajo, terminar, fallar)

    def inscribir(self):
        if self._ocupado:
            return
        oferta = self.ofertas.get(self.selector_oferta.get())
        if not oferta or oferta["cupos"] == 0:
            return
        self._cambiar(lambda: self.controller.inscribir(oferta["materia_id"], oferta["curso_id"]),
                      "inscribir la materia")

    def retirar(self):
        if self._ocupado:
            return
        inscripcion = self.inscripciones.get(self.selector_inscripcion.get())
        if not inscripcion:
            return
        if not messagebox.askyesno(
            "Confirmar retiro", f"¿Retirarte de {inscripcion['materia']}?",
            parent=self,
        ):
            return
        self._cambiar(lambda: self.controller.retirar(
            inscripcion["materia_id"], inscripcion["curso_id"]), "retirar la materia")
