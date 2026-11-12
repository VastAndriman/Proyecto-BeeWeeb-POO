
import tkinter as tk
import re
import customtkinter as ctk
from controladores.auth_controller import AuthController


class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success, auth_controller=None):
        super().__init__(master, fg_color="#f3f0fb")
        self.on_login_success = on_login_success
        self.auth_controller = auth_controller if auth_controller is not None else AuthController()
        self.modo_actual = "login"

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.card = ctk.CTkFrame(
            self,
            width=800,
            height=540,
            corner_radius=18,
            fg_color="#ffffff",
            border_width=1,
            border_color="#e3dcf1"
        )
        self.card.grid(row=0, column=0, padx=20, pady=20)
        self.card.grid_propagate(False)

        self.card.grid_columnconfigure(0, weight=0)
        self.card.grid_columnconfigure(1, weight=1)
        self.card.grid_rowconfigure(0, weight=1)

        self._construir_banner_origami(self.card)

        self.form_container = ctk.CTkFrame(
            self.card,
            fg_color="#ffffff",
            corner_radius=18
        )
        self.form_container.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=25,
            pady=15
        )
        self.form_container.grid_rowconfigure(0, weight=1)
        self.form_container.grid_columnconfigure(0, weight=1)

        self.cambiar_modo("login")

    def _construir_banner_origami(self, parent):
        w, h = 320, 540

        self.canvas_origami = tk.Canvas(
            parent,
            width=w,
            height=h,
            bg="#e8e1fb",
            highlightthickness=0
        )
        self.canvas_origami.grid(row=0, column=0, sticky="nsew")

        self.canvas_origami.create_polygon(
            0, 0, 140, 0, 0, 180,
            fill="#d6c9f3", outline=""
        )
        self.canvas_origami.create_polygon(
            0, 160, 150, 0, 165, 0, 0, 195,
            fill="#d0c1ef", outline=""
        )
        self.canvas_origami.create_polygon(
            0, 90, 230, 0, 275, 0, 0, 290,
            fill="#ddd3f5", outline=""
        )
        self.canvas_origami.create_polygon(
            0, 200, 275, 80, 225, 270, 0, 370,
            fill="#cbbbea", outline=""
        )
        self.canvas_origami.create_polygon(
            0, 350, 225, 270, 215, 285, 0, 375,
            fill="#d7c9f2", outline=""
        )
        self.canvas_origami.create_polygon(
            0, 300, 215, 285, 175, 410, 0, 435,
            fill="#d2c4ee", outline=""
        )
        self.canvas_origami.create_polygon(
            0, 400, 185, 390, 220, 470, 0, 470,
            fill="#c7b8e9", outline=""
        )
        self.canvas_origami.create_polygon(
            225, 270, w, 230, w, 470, 185, 470,
            fill="#e2d8f8", outline=""
        )

        self.canvas_origami.create_text(
            26, 54, text="BeeWeek", anchor="w",
            font=("Arial", 23, "bold"), fill="#4b3f76"
        )
        abeja = "#7156a5"
        self.canvas_origami.create_line(
            40, 345, 53, 354, 72, 350, 82, 336, 100, 329,
            fill=abeja, width=2, dash=(4, 4), smooth=True
        )
        self.canvas_origami.create_oval(
            119, 306, 147, 336, outline=abeja, width=2
        )
        self.canvas_origami.create_oval(
            139, 301, 168, 333, outline=abeja, width=2
        )
        self.canvas_origami.create_oval(
            111, 326, 177, 364, outline=abeja, width=2
        )
        self.canvas_origami.create_oval(
            173, 329, 197, 353, outline=abeja, width=2
        )
        self.canvas_origami.create_line(
            133, 328, 133, 361, fill=abeja, width=2
        )
        self.canvas_origami.create_line(
            151, 327, 151, 363, fill=abeja, width=2
        )
        self.canvas_origami.create_line(
            183, 329, 188, 320, 194, 319, fill=abeja, width=2,
            smooth=True
        )
        self.canvas_origami.create_oval(
            188, 337, 191, 340, fill=abeja, outline=abeja
        )
        self.canvas_origami.create_text(
            26, 425,
            text="Como abejitas al volar,\ncada clase en su lugar.",
            anchor="w", justify="left", font=("Arial", 15, "bold"),
            fill="#4b3f76"
        )
        self.canvas_origami.create_text(
            26, 505, text="ULEAM · Gestión educativa", anchor="w",
            font=("Arial", 11, "bold"), fill="#4b3f76"
        )

        self._redibujar_pestanas()

    def _redibujar_pestanas(self):
        w = 320
        self.canvas_origami.delete("pestaña")

        y_acceso = 150
        es_acceso = self.modo_actual == "login"
        bg_acceso = "#ffffff" if es_acceso else "#d6c9f3"
        fg_acceso = "#7256ac" if es_acceso else "#4b3f76"

        self.canvas_origami.create_oval(
            160, y_acceso - 24, 210, y_acceso + 24,
            fill=bg_acceso, outline="",
            tags=("pestaña", "btn_tab_acceso")
        )
        self.canvas_origami.create_rectangle(
            185, y_acceso - 24, w + 2, y_acceso + 24,
            fill=bg_acceso, outline="",
            tags=("pestaña", "btn_tab_acceso")
        )
        self.canvas_origami.create_text(
            245, y_acceso,
            text="ACCESO",
            font=("Arial", 11, "bold"),
            fill=fg_acceso,
            tags=("pestaña", "btn_tab_acceso")
        )

        y_registro = 215
        es_registro = self.modo_actual == "registro"
        bg_reg = "#ffffff" if es_registro else "#d6c9f3"
        fg_reg = "#7256ac" if es_registro else "#4b3f76"

        self.canvas_origami.create_oval(
            160, y_registro - 24, 210, y_registro + 24,
            fill=bg_reg, outline="",
            tags=("pestaña", "btn_tab_registro")
        )
        self.canvas_origami.create_rectangle(
            185, y_registro - 24, w + 2, y_registro + 24,
            fill=bg_reg, outline="",
            tags=("pestaña", "btn_tab_registro")
        )
        self.canvas_origami.create_text(
            245, y_registro,
            text="REGISTRO",
            font=("Arial", 11, "bold"),
            fill=fg_reg,
            tags=("pestaña", "btn_tab_registro")
        )

        self.canvas_origami.tag_bind(
            "btn_tab_acceso", "<Button-1>",
            lambda e: self.cambiar_modo("login")
        )
        self.canvas_origami.tag_bind(
            "btn_tab_registro", "<Button-1>",
            lambda e: self.cambiar_modo("registro")
        )
        self.canvas_origami.tag_bind(
            "pestaña", "<Enter>",
            lambda e: self.canvas_origami.config(cursor="hand2")
        )
        self.canvas_origami.tag_bind(
            "pestaña", "<Leave>",
            lambda e: self.canvas_origami.config(cursor="")
        )

    def cambiar_modo(self, modo: str):
        if modo not in ("login", "registro"):
            return

        self.modo_actual = modo
        self._redibujar_pestanas()

        for widget in self.form_container.winfo_children():
            widget.destroy()

        if modo == "login":
            self._construir_formulario_login(self.form_container)
        else:
            self._construir_formulario_registro(self.form_container)

    def _construir_formulario_login(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=15, pady=(65, 10))

        ctk.CTkLabel(
            frame,
            text="Iniciar sesión",
            font=("Arial", 23, "bold"),
            text_color="#4b3f76"
        ).pack(anchor="w", padx=25, pady=(0, 4))
        ctk.CTkLabel(
            frame, text="Accede a tu espacio de trabajo.",
            font=("Arial", 12), text_color="#786f95"
        ).pack(anchor="w", padx=25, pady=(0, 22))

        ctk.CTkLabel(
            frame, text="Correo o usuario", font=("Arial", 12),
            text_color="#4b3f76"
        ).pack(anchor="w", padx=25, pady=(0, 5))

        self.entry_usuario = ctk.CTkEntry(
            frame,
            placeholder_text="nombre@uleam.edu.ec",
            height=39,
            font=("Arial", 13),
            fg_color="#ffffff",
            border_width=1,
            border_color="#d2cbe8",
            corner_radius=9,
            text_color="#4b3f76",
            placeholder_text_color="#9c91b7"
        )
        self.entry_usuario.pack(fill="x", padx=25, pady=(0, 14))

        ctk.CTkLabel(
            frame, text="Contraseña", font=("Arial", 12),
            text_color="#4b3f76"
        ).pack(anchor="w", padx=25, pady=(0, 5))

        self.entry_password = ctk.CTkEntry(
            frame,
            placeholder_text="Tu contraseña",
            show="*",
            height=39,
            font=("Arial", 13),
            fg_color="#ffffff",
            border_width=1,
            border_color="#d2cbe8",
            corner_radius=9,
            text_color="#4b3f76",
            placeholder_text_color="#9c91b7"
        )
        self.entry_password.pack(fill="x", padx=25, pady=(0, 12))

        self.check_var = ctk.StringVar(value="off")
        ctk.CTkCheckBox(
            frame,
            text="Mostrar contraseña",
            command=self._toggle_password,
            variable=self.check_var,
            onvalue="on",
            offvalue="off",
            font=("Arial", 11),
            text_color="#786f95",
            checkbox_width=16,
            checkbox_height=16,
            fg_color="#7256ac",
            hover_color="#5e4497"
        ).pack(anchor="w", padx=25, pady=(0, 18))

        self.btn_login = ctk.CTkButton(
            frame,
            text="Ingresar",
            height=40,
            font=("Arial", 13, "bold"),
            fg_color="#7256ac",
            hover_color="#5e4497",
            text_color="#ffffff",
            corner_radius=9,
            command=self._ejecutar_login
        )
        self.btn_login.pack(fill="x", padx=25, pady=(0, 10))

        registro_box = ctk.CTkFrame(frame, fg_color="transparent")
        registro_box.pack(fill="x", padx=25, pady=(4, 6))

        ctk.CTkLabel(
            registro_box,
            text="¿No tienes una cuenta?",
            font=("Arial", 11),
            text_color="#786f95"
        ).pack(side="left")

        ctk.CTkButton(
            registro_box,
            text="Registrarse",
            height=26,
            font=("Arial", 11, "bold"),
            fg_color="#f5f2fc",
            text_color="#7256ac",
            hover_color="#e1d8fa",
            border_width=1,
            border_color="#e8e1fb",
            corner_radius=13,
            command=lambda: self.cambiar_modo("registro")
        ).pack(side="right")

        self.lbl_mensaje = ctk.CTkLabel(
            frame, text="", font=("Arial", 11), wraplength=340
        )
        self.lbl_mensaje.pack(fill="x", padx=25, pady=(4, 4))

        self.entry_usuario.bind(
            "<Return>", lambda e: self._ejecutar_login()
        )
        self.entry_password.bind(
            "<Return>", lambda e: self._ejecutar_login()
        )
        self.entry_usuario.focus()

    def _construir_formulario_registro(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=15, pady=(10, 2))

        ctk.CTkLabel(
            frame,
            text="Crear cuenta",
            font=("Arial", 23, "bold"),
            text_color="#4b3f76"
        ).pack(anchor="w", padx=25, pady=(0, 4))

        ctk.CTkLabel(
            frame,
            text="Completa tus datos para usar BeeWeek.",
            font=("Arial", 12),
            text_color="#786f95"
        ).pack(anchor="w", padx=25, pady=(0, 8))

        self.reg_cedula = self._crear_campo(
            frame, "Cédula / Identificación", "10 dígitos"
        )

        fila_nombres = ctk.CTkFrame(frame, fg_color="transparent")
        fila_nombres.pack(fill="x", padx=25, pady=(0, 6))
        fila_nombres.grid_columnconfigure(0, weight=1)
        fila_nombres.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            fila_nombres, text="Nombre", font=("Arial", 12),
            text_color="#4b3f76"
        ).grid(row=0, column=0, padx=(0, 5), sticky="w")
        ctk.CTkLabel(
            fila_nombres, text="Apellido", font=("Arial", 12),
            text_color="#4b3f76"
        ).grid(row=0, column=1, padx=(5, 0), sticky="w")

        self.reg_nombre = ctk.CTkEntry(
            fila_nombres, placeholder_text="Nombre",
            height=34, font=("Arial", 12), fg_color="#ffffff",
            text_color="#4b3f76", border_color="#d2cbe8",
            border_width=1, corner_radius=9
        )
        self.reg_nombre.grid(
            row=1, column=0, padx=(0, 5), sticky="ew"
        )

        self.reg_apellido = ctk.CTkEntry(
            fila_nombres, placeholder_text="Apellido",
            height=34, font=("Arial", 12), fg_color="#ffffff",
            text_color="#4b3f76", border_color="#d2cbe8",
            border_width=1, corner_radius=9
        )
        self.reg_apellido.grid(
            row=1, column=1, padx=(5, 0), sticky="ew"
        )

        self.reg_email = self._crear_campo(
            frame, "Correo institucional", "nombre@uleam.edu.ec"
        )

        fila_cred = ctk.CTkFrame(frame, fg_color="transparent")
        fila_cred.pack(fill="x", padx=25, pady=(0, 6))
        fila_cred.grid_columnconfigure(0, weight=1)
        fila_cred.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            fila_cred, text="Usuario", font=("Arial", 12),
            text_color="#4b3f76"
        ).grid(row=0, column=0, padx=(0, 5), sticky="w")
        ctk.CTkLabel(
            fila_cred, text="Contraseña", font=("Arial", 12),
            text_color="#4b3f76"
        ).grid(row=0, column=1, padx=(5, 0), sticky="w")

        self.reg_user = ctk.CTkEntry(
            fila_cred, placeholder_text="Usuario",
            height=34, font=("Arial", 12), fg_color="#ffffff",
            text_color="#4b3f76", border_color="#d2cbe8",
            border_width=1, corner_radius=9
        )
        self.reg_user.grid(
            row=1, column=0, padx=(0, 5), sticky="ew"
        )

        self.reg_pass = ctk.CTkEntry(
            fila_cred, placeholder_text="Contraseña",
            show="*", height=34, font=("Arial", 12),
            fg_color="#ffffff", text_color="#4b3f76",
            border_color="#d2cbe8", border_width=1, corner_radius=9
        )
        self.reg_pass.grid(
            row=1, column=1, padx=(5, 0), sticky="ew"
        )

        rol_box = ctk.CTkFrame(frame, fg_color="transparent")
        rol_box.pack(fill="x", padx=25, pady=(0, 8))

        ctk.CTkLabel(
            rol_box, text="Rol:",
            font=("Arial", 11, "bold"),
            text_color="#4b3f76"
        ).pack(side="left", padx=(0, 8))

        self.reg_rol = ctk.CTkSegmentedButton(
            rol_box,
            values=["Docente", "Estudiante"],
            fg_color="#e8e1fb",
            selected_color="#e8e1fb",
            selected_hover_color="#d0c1ef",
            unselected_color="#f5f2fc",
            unselected_hover_color="#e1d8fa",
            text_color="#4b3f76",
            font=("Arial", 11)
        )
        self.reg_rol.set("Docente")
        self.reg_rol.pack(side="left", fill="x", expand=True)

        self.btn_registrar = ctk.CTkButton(
            frame,
            text="Crear cuenta",
            height=40,
            font=("Arial", 13, "bold"),
            fg_color="#7256ac",
            hover_color="#5e4497",
            text_color="#ffffff",
            corner_radius=9,
            command=self._ejecutar_registro
        )
        self.btn_registrar.pack(fill="x", padx=25, pady=(0, 6))

        login_box = ctk.CTkFrame(frame, fg_color="transparent")
        login_box.pack(fill="x", padx=25, pady=(2, 4))

        ctk.CTkLabel(
            login_box,
            text="¿Ya tienes cuenta?",
            font=("Arial", 11),
            text_color="#786f95"
        ).pack(side="left")

        ctk.CTkButton(
            login_box,
            text="Iniciar Sesión",
            height=24,
            font=("Arial", 11, "bold"),
            fg_color="#f5f2fc",
            text_color="#7256ac",
            hover_color="#e1d8fa",
            border_width=1,
            border_color="#e8e1fb",
            corner_radius=12,
            command=lambda: self.cambiar_modo("login")
        ).pack(side="right")

        self.lbl_mensaje_reg = ctk.CTkLabel(
            frame, text="", font=("Arial", 11), wraplength=340
        )
        self.lbl_mensaje_reg.pack(fill="x", padx=25, pady=(2, 2))

        self.reg_cedula.focus()

    def _crear_campo(self, parent, placeholder: str, icono: str):
        ctk.CTkLabel(
            parent, text=placeholder,
            font=("Arial", 12), text_color="#4b3f76"
        ).pack(anchor="w", padx=25, pady=(0, 5))

        entry = ctk.CTkEntry(
            parent,
            placeholder_text=icono,
            height=34,
            font=("Arial", 12),
            fg_color="#ffffff",
            border_width=1,
            border_color="#d2cbe8",
            corner_radius=9,
            text_color="#4b3f76",
            placeholder_text_color="#9c91b7"
        )
        entry.pack(fill="x", padx=25, pady=(0, 6))

        return entry

    def _toggle_password(self):
        if self.check_var.get() == "on":
            self.entry_password.configure(show="")
        else:
            self.entry_password.configure(show="*")

    def _ejecutar_login(self):
        usuario = self.entry_usuario.get().strip()
        contrasena = self.entry_password.get()

        if not usuario or not contrasena:
            self.lbl_mensaje.configure(
                text="Por favor completa todos los campos.",
                text_color="#d97706"
            )
            return

        self.btn_login.configure(
            state="disabled", text="Validando..."
        )
        self.lbl_mensaje.configure(text="")
        self.update_idletasks()

        try:
            exito, mensaje, usuario_obj = (
                self.auth_controller.iniciar_sesion(
                    usuario, contrasena
                )
            )

            if exito:
                self.lbl_mensaje.configure(
                    text=f"{mensaje}",
                    text_color="#16a34a"
                )
                self.after(
                    350,
                    lambda: self.on_login_success(usuario_obj)
                )
            else:
                self.lbl_mensaje.configure(
                    text=f"{mensaje}",
                    text_color="#dc2626"
                )

        except Exception:
            self.lbl_mensaje.configure(
                text="Ocurrió un error al iniciar sesión.",
                text_color="#dc2626"
            )
        finally:
            self.btn_login.configure(
                state="normal", text="INGRESAR"
            )

    def _ejecutar_registro(self):
        cedula = self.reg_cedula.get().strip()
        nombre = self.reg_nombre.get().strip()
        apellido = self.reg_apellido.get().strip()
        email = self.reg_email.get().strip()
        username = self.reg_user.get().strip()
        contrasena = self.reg_pass.get()
        rol = self.reg_rol.get()

        if not all([
            cedula, nombre, apellido,
            email, username, contrasena
        ]):
            self.lbl_mensaje_reg.configure(
                text="Completa todos los campos obligatorios.",
                text_color="#d97706"
            )
            return

        if not cedula.isdigit() or len(cedula) != 10:
            self.lbl_mensaje_reg.configure(
                text="La cédula debe contener 10 dígitos.",
                text_color="#d97706"
            )
            self.reg_cedula.focus()
            return

        if not re.fullmatch(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            email
        ):
            self.lbl_mensaje_reg.configure(
                text="Ingresa un correo electrónico válido.",
                text_color="#d97706"
            )
            self.reg_email.focus()
            return

        if not email.lower().endswith("@uleam.edu.ec"):
            self.lbl_mensaje_reg.configure(
                text="Utiliza tu correo institucional @uleam.edu.ec.",
                text_color="#d97706"
            )
            self.reg_email.focus()
            return

        if len(contrasena) < 8:
            self.lbl_mensaje_reg.configure(
                text="La contraseña debe tener al menos 8 caracteres.",
                text_color="#d97706"
            )
            self.reg_pass.focus()
            return

        if len(username) < 4:
            self.lbl_mensaje_reg.configure(
                text="El usuario debe tener al menos 4 caracteres.",
                text_color="#d97706"
            )
            self.reg_user.focus()
            return

        self.btn_registrar.configure(
            state="disabled", text="Registrando..."
        )
        self.lbl_mensaje_reg.configure(text="")
        self.update_idletasks()

        try:
            exito, mensaje = self.auth_controller.registrar_usuario(
                identificacion=cedula,
                nombre=nombre,
                apellido=apellido,
                email=email,
                username=username,
                contrasena=contrasena,
                rol=rol
            )

            if exito:
                self.lbl_mensaje_reg.configure(
                    text=f"{mensaje}",
                    text_color="#16a34a"
                )
                self.after(
                    1200,
                    lambda: self._ir_a_login_con_datos(username)
                )
            else:
                self.lbl_mensaje_reg.configure(
                    text=f"{mensaje}",
                    text_color="#dc2626"
                )

        except Exception:
            self.lbl_mensaje_reg.configure(
                text="Ocurrió un error al registrar el usuario.",
                text_color="#dc2626"
            )
        finally:
            self.btn_registrar.configure(
                state="normal", text="Crear cuenta"
            )

    def _ir_a_login_con_datos(self, username: str):
        self.cambiar_modo("login")
        self.entry_usuario.delete(0, tk.END)
        self.entry_usuario.insert(0, username)
        self.entry_password.focus()
        self.lbl_mensaje.configure(
            text="Registro completado. Ingresa tu contraseña para acceder.",
            text_color="#16a34a"
        )
