from tkinter import messagebox

import customtkinter as ctk

from componentes.tareas_ui import iniciar_tarea


class UsuariosView(ctk.CTkFrame):
    """Permite a un administrador asignar roles a cuentas ya registradas."""

    def __init__(self, master, usuarios_controller):
        super().__init__(master, fg_color="transparent")
        self.controller = usuarios_controller
        self.usuarios = {}
        self._ocupado = False

        contenedor = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=14)
        contenedor.pack(fill="x", padx=30, pady=30)
        ctk.CTkLabel(contenedor, text="Gestión de usuarios", font=("Arial", 22, "bold"),
                     text_color="#4b3f76").pack(anchor="w", padx=24, pady=(22, 5))
        ctk.CTkLabel(
            contenedor,
            text="Elige una cuenta registrada para asignarle o retirarle permisos de administrador.",
            text_color="#786f95",
        ).pack(anchor="w", padx=24, pady=(0, 20))

        ctk.CTkLabel(contenedor, text="Cuenta", font=("Arial", 13, "bold")).pack(
            anchor="w", padx=24)
        self.selector_usuario = ctk.CTkOptionMenu(
            contenedor, values=["Cargando cuentas..."], command=self._seleccionar_usuario,
            width=450, fg_color="#7256ac", button_color="#5e4497",
        )
        self.selector_usuario.pack(anchor="w", padx=24, pady=(6, 16))

        ctk.CTkLabel(contenedor, text="Nuevo rol", font=("Arial", 13, "bold")).pack(
            anchor="w", padx=24)
        self.selector_rol = ctk.CTkOptionMenu(
            contenedor, values=list(self.controller.ROLES), width=220,
            fg_color="#7256ac", button_color="#5e4497",
        )
        self.selector_rol.pack(anchor="w", padx=24, pady=(6, 18))

        acciones = ctk.CTkFrame(contenedor, fg_color="transparent")
        acciones.pack(anchor="w", padx=24, pady=(0, 14))
        self.btn_guardar = ctk.CTkButton(
            acciones, text="Guardar cambio de rol", command=self.guardar_rol,
            fg_color="#7256ac", hover_color="#5e4497", width=190,
        )
        self.btn_guardar.pack(side="left", padx=(0, 12))
        self.btn_refrescar = ctk.CTkButton(
            acciones, text="Actualizar lista", command=self.cargar_usuarios,
            fg_color="#eee8fc", text_color="#4b3f76", hover_color="#d6c9f3",
            width=140,
        )
        self.btn_refrescar.pack(side="left")
        self.lbl_estado = ctk.CTkLabel(contenedor, text="", text_color="#786f95")
        self.lbl_estado.pack(anchor="w", padx=24, pady=(0, 22))
        self.cargar_usuarios()

    def _seleccionar_usuario(self, etiqueta):
        usuario = self.usuarios.get(etiqueta)
        if usuario:
            self.selector_rol.set(usuario["rol"])

    def cargar_usuarios(self):
        if self._ocupado:
            return
        self._ocupado = True
        self.btn_guardar.configure(state="disabled")
        self.btn_refrescar.configure(state="disabled")
        self.lbl_estado.configure(text="Cargando cuentas...", text_color="#786f95")

        def terminar(cuentas):
            self._ocupado = False
            self.btn_refrescar.configure(state="normal")
            self.usuarios = {
                f"{u['username']} · {u['nombre']} {u['apellido']} · {u['rol']}": u
                for u in cuentas if u.get("activo")
            }
            if self.usuarios:
                opciones = list(self.usuarios)
                self.selector_usuario.configure(values=opciones)
                self.selector_usuario.set(opciones[0])
                self._seleccionar_usuario(opciones[0])
                self.btn_guardar.configure(state="normal")
                self.lbl_estado.configure(text=f"{len(opciones)} cuentas activas.",
                                          text_color="#15803d")
            else:
                self.selector_usuario.configure(values=["No hay cuentas activas"])
                self.selector_usuario.set("No hay cuentas activas")
                self.lbl_estado.configure(text="No hay cuentas disponibles.")

        def fallar(_error):
            self._ocupado = False
            self.btn_refrescar.configure(state="normal")
            self.lbl_estado.configure(
                text="No se pudieron cargar las cuentas. Revisa la conexión o la migración.",
                text_color="#b42333",
            )

        iniciar_tarea(self, self.controller.listar, terminar, fallar)

    def guardar_rol(self):
        if self._ocupado:
            return
        usuario = self.usuarios.get(self.selector_usuario.get())
        rol = self.selector_rol.get()
        if not usuario or rol == usuario["rol"]:
            self.lbl_estado.configure(text="Selecciona una cuenta y un rol diferente.",
                                      text_color="#9a6700")
            return
        if not messagebox.askyesno(
            "Confirmar cambio de rol",
            f"¿Cambiar el rol de {usuario['username']} de {usuario['rol']} a {rol}?\n"
            "La cuenta deberá iniciar sesión nuevamente.",
            parent=self,
        ):
            return
        self._ocupado = True
        self.btn_guardar.configure(state="disabled")
        self.btn_refrescar.configure(state="disabled")
        self.lbl_estado.configure(text="Guardando cambio...", text_color="#786f95")

        def terminar(_resultado):
            self._ocupado = False
            self.lbl_estado.configure(text="Rol actualizado. La cuenta debe volver a iniciar sesión.",
                                      text_color="#15803d")
            self.cargar_usuarios()

        def fallar(_error):
            self._ocupado = False
            self.btn_guardar.configure(state="normal")
            self.btn_refrescar.configure(state="normal")
            self.lbl_estado.configure(
                text="No se pudo cambiar el rol. Comprueba que no sea tu propia cuenta.",
                text_color="#b42333",
            )

        iniciar_tarea(self, lambda: self.controller.cambiar_rol(usuario["id"], rol),
                     terminar, fallar)
