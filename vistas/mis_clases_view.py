import customtkinter as ctk

from componentes.tareas_ui import iniciar_tarea


class MisClasesView(ctk.CTkScrollableFrame):
    """Horario y estudiantes de las clases asignadas al docente actual."""

    def __init__(self, master, clases_controller):
        super().__init__(master, fg_color="transparent")
        self.controller = clases_controller
        self._cargando = False
        ctk.CTkLabel(self, text="Mis clases", font=("Arial", 22, "bold"),
                     text_color="#4b3f76").pack(anchor="w", padx=30, pady=(25, 5))
        ctk.CTkLabel(self, text="Horarios publicados y estudiantes inscritos en tus materias.",
                     text_color="#786f95").pack(anchor="w", padx=30, pady=(0, 15))
        self.btn_actualizar = ctk.CTkButton(
            self, text="Actualizar clases", command=self.cargar_datos_dinamicos,
            fg_color="#7256ac", hover_color="#5e4497")
        self.btn_actualizar.pack(anchor="w", padx=30, pady=(0, 12))
        self.lbl_estado = ctk.CTkLabel(self, text="", text_color="#786f95")
        self.lbl_estado.pack(anchor="w", padx=30, pady=(0, 10))
        self.contenido = ctk.CTkFrame(self, fg_color="transparent")
        self.contenido.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        self.cargar_datos_dinamicos()

    def cargar_datos_dinamicos(self):
        if self._cargando:
            return
        self._cargando = True
        self.btn_actualizar.configure(state="disabled")
        self.lbl_estado.configure(text="Cargando tus clases...", text_color="#786f95")

        def terminar(datos):
            self._cargando = False
            self.btn_actualizar.configure(state="normal")
            for widget in self.contenido.winfo_children():
                widget.destroy()
            if not datos.get("vinculado"):
                self.lbl_estado.configure(
                    text="Tu cuenta aún no está vinculada a una ficha docente. Solicita al administrador que la vincule.",
                    text_color="#9a6700")
                return
            clases = datos.get("clases") or []
            self.lbl_estado.configure(
                text=f"{len(clases)} clase(s) asignada(s)." if clases
                else "Aún no tienes horarios publicados.", text_color="#4b3f76")
            for clase in clases:
                self._crear_tarjeta(clase)

        def fallar(_error):
            self._cargando = False
            self.btn_actualizar.configure(state="normal")
            self.lbl_estado.configure(
                text="No se pudieron cargar tus clases. Revisa la conexión e inténtalo de nuevo.",
                text_color="#b42333")

        iniciar_tarea(self, self.controller.listar, terminar, fallar)

    def _crear_tarjeta(self, clase):
        tarjeta = ctk.CTkFrame(self.contenido, fg_color="#ffffff", corner_radius=14)
        tarjeta.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(tarjeta, text=clase["materia"], font=("Arial", 17, "bold"),
                     text_color="#4b3f76").pack(anchor="w", padx=20, pady=(16, 4))
        ctk.CTkLabel(
            tarjeta,
            text=f"{clase['dia']} · {clase['hora_inicio']}–{clase['hora_fin']}"
                 f"   |   {clase['curso']}   |   Aula {clase['aula']}",
            text_color="#7256ac",
        ).pack(anchor="w", padx=20, pady=(0, 10))
        alumnos = clase.get("estudiantes") or []
        ctk.CTkLabel(tarjeta, text=f"Estudiantes inscritos: {len(alumnos)}",
                     font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(0, 5))
        nombres = ", ".join(f"{a['nombre']} {a['apellido']}" for a in alumnos)
        ctk.CTkLabel(
            tarjeta, text=nombres or "Todavía no hay estudiantes inscritos.",
            wraplength=650, justify="left", text_color="#786f95",
        ).pack(anchor="w", padx=20, pady=(0, 18))
