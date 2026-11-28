from datetime import date, timedelta

import customtkinter as ctk

from componentes.tareas_ui import iniciar_tarea


DIAS = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo")
ESTADOS = ("Sin marcar", "Presente", "Ausente", "Atrasado", "Justificado")


def mensaje_error_asistencia(error):
    if isinstance(error, ValueError):
        return str(error)
    detalle = str(getattr(error, "message", error)).lower()
    if "fecha no coincide" in detalle:
        return "La fecha no corresponde al día de esa clase."
    if "alumno o estado" in detalle:
        return "La lista cambió. Carga los estudiantes nuevamente."
    if "sesion" in detalle or "sesión" in detalle:
        return "La sesión terminó. Cierra sesión e ingresa nuevamente."
    return "No se pudo guardar o consultar la asistencia. Revisa la conexión."


class AsistenciaDocenteView(ctk.CTkScrollableFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.clases = {}
        self.alumnos = []
        self.selectores = {}
        self.fecha_cargada = None
        self._ocupado = False

        ctk.CTkLabel(self, text="Control de asistencia", font=("Arial", 22, "bold"),
                     text_color="#4b3f76").pack(anchor="w", padx=30, pady=(25, 6))
        ctk.CTkLabel(self, text="Selecciona tu clase y la fecha para marcar asistencia.",
                     text_color="#786f95").pack(anchor="w", padx=30, pady=(0, 16))
        panel = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=14)
        panel.pack(fill="x", padx=30, pady=(0, 16))
        ctk.CTkLabel(panel, text="Clase", font=("Arial", 13, "bold")).pack(
            anchor="w", padx=20, pady=(16, 5))
        self.selector_clase = ctk.CTkOptionMenu(
            panel, values=["Cargando clases..."], width=480, command=self._seleccionar_clase,
            fg_color="#7256ac", button_color="#5e4497")
        self.selector_clase.pack(anchor="w", padx=20, pady=(0, 12))
        ctk.CTkLabel(panel, text="Fecha (AAAA-MM-DD)", font=("Arial", 13, "bold")).pack(
            anchor="w", padx=20)
        self.entry_fecha = ctk.CTkEntry(panel, width=180)
        self.entry_fecha.pack(anchor="w", padx=20, pady=(5, 12))
        self.btn_cargar = ctk.CTkButton(panel, text="Cargar estudiantes",
                                       command=self.cargar_lista, fg_color="#7256ac")
        self.btn_cargar.pack(anchor="w", padx=20, pady=(0, 16))
        self.lbl_estado = ctk.CTkLabel(self, text="", text_color="#786f95",
                                       wraplength=680, justify="left")
        self.lbl_estado.pack(anchor="w", padx=30, pady=(0, 10))
        self.lista_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=14)
        self.lista_frame.pack(fill="x", padx=30, pady=(0, 12))
        self.btn_guardar = ctk.CTkButton(self, text="Guardar asistencia",
                                        command=self.guardar, fg_color="#7256ac")
        self.btn_guardar.pack(anchor="w", padx=30, pady=(0, 20))
        self.btn_guardar.configure(state="disabled")
        self.cargar_datos_dinamicos()

    def _seleccionar_clase(self, etiqueta):
        clase = self.clases.get(etiqueta)
        if not clase:
            return
        hoy = date.today()
        dia_clase = DIAS.index(clase["dia"])
        fecha = hoy - timedelta(days=(hoy.weekday() - dia_clase) % 7)
        self.entry_fecha.delete(0, "end")
        self.entry_fecha.insert(0, fecha.isoformat())
        self.alumnos = []
        self.fecha_cargada = None
        self.btn_guardar.configure(state="disabled")
        for widget in self.lista_frame.winfo_children():
            widget.destroy()

    def cargar_datos_dinamicos(self):
        if self._ocupado:
            return
        self._ocupado = True
        self.btn_cargar.configure(state="disabled")
        self.lbl_estado.configure(text="Cargando clases...", text_color="#786f95")

        def terminar(datos):
            self._ocupado = False
            self.btn_cargar.configure(state="normal")
            clases = datos.get("clases") or []
            self.clases = {
                f"{c['materia']} · {c['curso']} · {c['dia']} {c['hora_inicio']} (ID {c['horario_id']})": c
                for c in clases
            }
            opciones = list(self.clases) or ["No hay clases asignadas"]
            self.selector_clase.configure(values=opciones)
            self.selector_clase.set(opciones[0])
            self._seleccionar_clase(opciones[0])
            if not datos.get("vinculado"):
                mensaje = "Tu cuenta aún no está vinculada. Pide al administrador que la vincule."
            elif not clases:
                mensaje = "No tienes horarios publicados."
            else:
                mensaje = "Elige la clase y pulsa Cargar estudiantes."
            self.lbl_estado.configure(text=mensaje, text_color="#4b3f76")

        def fallar(_error):
            self._ocupado = False
            self.btn_cargar.configure(state="normal")
            self.lbl_estado.configure(text="No se pudieron cargar tus clases.",
                                      text_color="#b42333")

        iniciar_tarea(self, self.controller.clases_docente, terminar, fallar)

    def cargar_lista(self):
        if self._ocupado:
            return
        clase = self.clases.get(self.selector_clase.get())
        if not clase:
            return
        fecha = self.entry_fecha.get().strip()
        self._ocupado = True
        self.btn_cargar.configure(state="disabled")
        self.btn_guardar.configure(state="disabled")
        self.lbl_estado.configure(text="Cargando estudiantes...", text_color="#786f95")

        def terminar(alumnos):
            self._ocupado = False
            self.btn_cargar.configure(state="normal")
            self.alumnos = alumnos
            self.fecha_cargada = fecha
            self.selectores = {}
            for widget in self.lista_frame.winfo_children():
                widget.destroy()
            for alumno in alumnos:
                fila = ctk.CTkFrame(self.lista_frame, fg_color="transparent")
                fila.pack(fill="x", padx=18, pady=5)
                ctk.CTkLabel(fila, text=f"{alumno['nombre']} {alumno['apellido']}",
                             width=250, anchor="w").pack(side="left")
                selector = ctk.CTkOptionMenu(
                    fila, values=list(ESTADOS), width=160,
                    fg_color="#7256ac", button_color="#5e4497")
                selector.set(alumno.get("estado") or "Sin marcar")
                selector.pack(side="left", padx=8)
                self.selectores[alumno["usuario_id"]] = selector
            self.btn_guardar.configure(state="normal" if alumnos else "disabled")
            self.lbl_estado.configure(
                text=f"{len(alumnos)} estudiante(s). Marca todos los estados y guarda." if alumnos
                else "No hay estudiantes inscritos en esta clase.", text_color="#4b3f76")

        def fallar(error):
            self._ocupado = False
            self.btn_cargar.configure(state="normal")
            self.lbl_estado.configure(text=mensaje_error_asistencia(error),
                                      text_color="#b42333")

        iniciar_tarea(self, lambda: self.controller.lista(clase["horario_id"], fecha),
                     terminar, fallar)

    def guardar(self):
        if self._ocupado or not self.alumnos:
            return
        if self.entry_fecha.get().strip() != self.fecha_cargada:
            self.lbl_estado.configure(text="Cambiaste la fecha. Carga nuevamente los estudiantes.",
                                      text_color="#b42333")
            return
        clase = self.clases.get(self.selector_clase.get())
        if not clase:
            return
        registros = [{"usuario_id": u["usuario_id"],
                      "estado": self.selectores[u["usuario_id"]].get()}
                     for u in self.alumnos]
        if any(r["estado"] == "Sin marcar" for r in registros):
            self.lbl_estado.configure(text="Marca la asistencia de todos los estudiantes.",
                                      text_color="#b42333")
            return
        fecha = self.entry_fecha.get().strip()
        self._ocupado = True
        self.btn_guardar.configure(state="disabled")
        self.lbl_estado.configure(text="Guardando asistencia...", text_color="#786f95")

        def terminar(resultado):
            self._ocupado = False
            self.btn_guardar.configure(state="normal")
            self.lbl_estado.configure(
                text=f"Asistencia guardada para {resultado['guardados']} estudiante(s).",
                text_color="#15803d")

        def fallar(error):
            self._ocupado = False
            self.btn_guardar.configure(state="normal")
            self.lbl_estado.configure(text=mensaje_error_asistencia(error),
                                      text_color="#b42333")

        iniciar_tarea(self, lambda: self.controller.guardar(clase["horario_id"], fecha, registros),
                     terminar, fallar)


class HistorialAsistenciaView(ctk.CTkScrollableFrame):
    def __init__(self, master, controller, rol):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.rol = rol
        titulo = "Mi asistencia" if rol == "Estudiante" else "Resumen de asistencia"
        ctk.CTkLabel(self, text=titulo, font=("Arial", 22, "bold"),
                     text_color="#4b3f76").pack(anchor="w", padx=30, pady=(25, 10))
        self.btn_actualizar = ctk.CTkButton(self, text="Actualizar",
                                            command=self.cargar_datos_dinamicos,
                                            fg_color="#7256ac")
        self.btn_actualizar.pack(anchor="w", padx=30, pady=(0, 12))
        self.lbl_estado = ctk.CTkLabel(self, text="", text_color="#786f95")
        self.lbl_estado.pack(anchor="w", padx=30, pady=(0, 10))
        self.contenido = ctk.CTkFrame(self, fg_color="transparent")
        self.contenido.pack(fill="x", padx=30, pady=(0, 20))
        self._cargando = False
        self.cargar_datos_dinamicos()

    def cargar_datos_dinamicos(self):
        if self._cargando:
            return
        self._cargando = True
        self.btn_actualizar.configure(state="disabled")

        def terminar(filas):
            self._cargando = False
            self.btn_actualizar.configure(state="normal")
            for widget in self.contenido.winfo_children():
                widget.destroy()
            self.lbl_estado.configure(
                text=f"{len(filas)} registro(s)." if filas else "Todavía no hay asistencia registrada.")
            for fila in filas:
                if self.rol == "Estudiante":
                    texto = f"{fila['fecha']}  ·  {fila['materia']}  ·  {fila['curso']}  ·  {fila['estado']}"
                else:
                    texto = (f"{fila['fecha']}  ·  {fila['hora']}  ·  "
                             f"{fila['materia']}  ·  {fila['curso']}\n"
                             f"Presentes: {fila['presentes']}   Ausentes: {fila['ausentes']}   "
                             f"Atrasados: {fila['atrasados']}   Justificados: {fila['justificados']}")
                tarjeta = ctk.CTkLabel(self.contenido, text=texto, fg_color="#ffffff",
                                       corner_radius=10, anchor="w", justify="left",
                                       text_color="#4b3f76")
                tarjeta.pack(fill="x", pady=(0, 8), ipady=12, padx=0)

        def fallar(_error):
            self._cargando = False
            self.btn_actualizar.configure(state="normal")
            self.lbl_estado.configure(text="No se pudo cargar la asistencia.",
                                      text_color="#b42333")

        trabajo = self.controller.estudiante if self.rol == "Estudiante" else self.controller.administrador
        iniciar_tarea(self, trabajo, terminar, fallar)
