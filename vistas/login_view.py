import tkinter as tk
import customtkinter as ctk
from controladores.auth_controller import AuthController

class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master, fg_color=("#f3ebf2", "#130914"))
        self.on_login_success = on_login_success

        # Centrar la tarjeta principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ========================================================
        # TARJETA CONTENEDORA PRINCIPAL (SPLIT CARD)
        # ========================================================
        self.card = ctk.CTkFrame(
            self,
            width=760,
            height=480,
            corner_radius=18,
            fg_color="#ffffff",
            border_width=1,
            border_color="#e2e8f0"
        )
        self.card.grid(row=0, column=0, padx=20, pady=20)
        self.card.grid_propagate(False)

        self.card.grid_columnconfigure(0, weight=0) # Panel izquierdo
        self.card.grid_columnconfigure(1, weight=1) # Formulario derecho
        self.card.grid_rowconfigure(0, weight=1)

        # --------------------------------------------------------
        # 1. PANEL IZQUIERDO: ARTE GEOMÉTRICO ORIGAMI NATIVO (CANVAS)
        # --------------------------------------------------------
        self._construir_banner_origami(self.card)

        # --------------------------------------------------------
        # 2. PANEL DERECHO: FORMULARIO BLANCO LIMPIO NATIVO
        # --------------------------------------------------------
        self._construir_formulario(self.card)

    def _construir_banner_origami(self, parent):
        """Dibuja nativamente la composición geométrica de origami con la paleta de colores del diseño."""
        w, h = 320, 480
        self.canvas_origami = tk.Canvas(
            parent,
            width=w,
            height=h,
            bg="#f0bfd8",          # Color base rosa suave
            highlightthickness=0
        )
        self.canvas_origami.grid(row=0, column=0, sticky="nsew")

        # Capa 1: Esquina superior izquierda (vino oscuro profundo)
        self.canvas_origami.create_polygon(
            0, 0,
            140, 0,
            0, 180,
            fill="#560f33", outline=""
        )

        # Sombra sutil de pliegue origami
        self.canvas_origami.create_polygon(
            0, 160,
            150, 0,
            165, 0,
            0, 195,
            fill="#440b28", outline=""
        )

        # Capa 2: Franja diagonal superior (magenta profundo)
        self.canvas_origami.create_polygon(
            0, 90,
            230, 0,
            275, 0,
            0, 290,
            fill="#751846", outline=""
        )

        # Capa 3: Faceta central diagonal (magenta / mora)
        self.canvas_origami.create_polygon(
            0, 200,
            275, 80,
            225, 270,
            0, 370,
            fill="#98255e", outline=""
        )

        # Sombra intermedia
        self.canvas_origami.create_polygon(
            0, 350,
            225, 270,
            215, 285,
            0, 375,
            fill="#6d1541", outline=""
        )

        # Capa 4: Faceta inferior izquierda (rosa berry intenso)
        self.canvas_origami.create_polygon(
            0, 300,
            215, 285,
            175, 430,
            0, 455,
            fill="#b83c7a", outline=""
        )

        # Capa 5: Esquina inferior (vino medio)
        self.canvas_origami.create_polygon(
            0, 420,
            185, 410,
            220, h,
            0, h,
            fill="#6b123d", outline=""
        )

        # Capa 6: Faceta derecha inferior (rosa medio)
        self.canvas_origami.create_polygon(
            225, 270,
            w, 230,
            w, h,
            185, h,
            fill="#d475a4", outline=""
        )

        # Pestaña curva blanca saliente hacia la izquierda (tal como en la referencia)
        # Unión redondeada con la sección derecha blanca
        tab_y = 175
        self.canvas_origami.create_oval(
            155, tab_y - 28,
            215, tab_y + 28,
            fill="#ffffff", outline=""
        )
        self.canvas_origami.create_rectangle(
            185, tab_y - 28,
            w + 2, tab_y + 28,
            fill="#ffffff", outline=""
        )

        # Texto dentro de la pestaña curva blanca
        self.canvas_origami.create_text(
            245, tab_y,
            text="ACCESO",
            font=("Arial", 11, "bold"),
            fill="#62193c"
        )

        # Texto decorativo institucional debajo de la pestaña
        self.canvas_origami.create_text(
            245, tab_y + 55,
            text="ULEAM",
            font=("Arial", 13, "bold"),
            fill="#ffffff"
        )

    def _construir_formulario(self, parent):
        """Construye el formulario derecho recreando fielmente los elementos y estilo de la referencia."""
        self.form_frame = ctk.CTkFrame(parent, fg_color="#ffffff", corner_radius=18)
        self.form_frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=25)

        # 1. Avatar circular superior dibujado nativamente en Canvas (con silueta blanca)
        self.canvas_avatar = tk.Canvas(
            self.form_frame,
            width=76,
            height=76,
            bg="#ffffff",
            highlightthickness=0
        )
        self.canvas_avatar.pack(pady=(10, 6))

        # Círculo base magenta/vino
        self.canvas_avatar.create_oval(4, 4, 72, 72, fill="#7b1a4a", outline="")
        # Cabeza de la silueta (círculo blanco)
        self.canvas_avatar.create_oval(27, 18, 49, 40, outline="#ffffff", width=3)
        # Hombros de la silueta (arco curvo blanco)
        self.canvas_avatar.create_arc(16, 41, 60, 79, start=15, extent=150, style="arc", outline="#ffffff", width=3)

        # 2. Título "INICIAR SESIÓN"
        self.lbl_titulo = ctk.CTkLabel(
            self.form_frame,
            text="INICIAR SESIÓN",
            font=("Arial", 19, "bold"),
            text_color="#62193c"
        )
        self.lbl_titulo.pack(pady=(0, 22))

        # 3. Campo: Email o Usuario (Estilo minimalista con línea inferior)
        self.user_box = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.user_box.pack(fill="x", padx=25, pady=(0, 2))

        self.lbl_icon_user = ctk.CTkLabel(self.user_box, text="👤", font=("Arial", 15), text_color="#64748b")
        self.lbl_icon_user.pack(side="left", padx=(0, 8))

        self.entry_usuario = ctk.CTkEntry(
            self.user_box,
            placeholder_text="Email o Usuario",
            height=34,
            font=("Arial", 13),
            fg_color="transparent",
            border_width=0,
            text_color="#0f172a",
            placeholder_text_color="#94a3b8"
        )
        self.entry_usuario.pack(side="left", fill="x", expand=True)

        # Línea divisoria inferior (underline)
        self.line_user = ctk.CTkFrame(self.form_frame, height=1, fg_color="#cbd5e1")
        self.line_user.pack(fill="x", padx=25, pady=(0, 16))

        # 4. Campo: Contraseña (Estilo minimalista con línea inferior)
        self.pass_box = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.pass_box.pack(fill="x", padx=25, pady=(0, 2))

        self.lbl_icon_pass = ctk.CTkLabel(self.pass_box, text="🔒", font=("Arial", 15), text_color="#64748b")
        self.lbl_icon_pass.pack(side="left", padx=(0, 8))

        self.entry_password = ctk.CTkEntry(
            self.pass_box,
            placeholder_text="Contraseña",
            show="*",
            height=34,
            font=("Arial", 13),
            fg_color="transparent",
            border_width=0,
            text_color="#0f172a",
            placeholder_text_color="#94a3b8"
        )
        self.entry_password.pack(side="left", fill="x", expand=True)

        # Línea divisoria inferior (underline)
        self.line_pass = ctk.CTkFrame(self.form_frame, height=1, fg_color="#cbd5e1")
        self.line_pass.pack(fill="x", padx=25, pady=(0, 14))

        # 5. Checkbox para ver contraseña
        self.check_var = ctk.StringVar(value="off")
        self.chk_mostrar = ctk.CTkCheckBox(
            self.form_frame,
            text="Mostrar contraseña",
            command=self._toggle_password,
            variable=self.check_var,
            onvalue="on",
            offvalue="off",
            font=("Arial", 11),
            text_color="#64748b",
            checkbox_width=16,
            checkbox_height=16,
            fg_color="#be4a82",
            hover_color="#9e2f65"
        )
        self.chk_mostrar.pack(anchor="w", padx=25, pady=(0, 16))

        # 6. Fila inferior: ¿Olvidaste tu contraseña? + Botón píldora INGRESAR
        self.action_box = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.action_box.pack(fill="x", padx=25, pady=(0, 10))

        self.lbl_olvido = ctk.CTkLabel(
            self.action_box,
            text="¿Olvidaste tu contraseña?",
            font=("Arial", 11),
            text_color="#9d2963",
            cursor="hand2"
        )
        self.lbl_olvido.pack(side="left")

        self.btn_login = ctk.CTkButton(
            self.action_box,
            text="INGRESAR",
            height=36,
            width=115,
            font=("Arial", 12, "bold"),
            fg_color="#be4a82",
            hover_color="#9e2f65",
            text_color="#ffffff",
            corner_radius=18,
            command=self._ejecutar_login
        )
        self.btn_login.pack(side="right")

        # 7. Mensaje de estado
        self.lbl_mensaje = ctk.CTkLabel(
            self.form_frame,
            text="",
            font=("Arial", 11),
            wraplength=340
        )
        self.lbl_mensaje.pack(fill="x", padx=25, pady=(4, 4))

        # Atajo Enter para iniciar sesión
        self.entry_usuario.bind("<Return>", lambda e: self._ejecutar_login())
        self.entry_password.bind("<Return>", lambda e: self._ejecutar_login())

        # Foco en el primer campo
        self.entry_usuario.focus()

    def _toggle_password(self):
        """Alterna visibilidad de la contraseña."""
        if self.check_var.get() == "on":
            self.entry_password.configure(show="")
        else:
            self.entry_password.configure(show="*")

    def _ejecutar_login(self):
        usuario = self.entry_usuario.get().strip()
        contrasena = self.entry_password.get().strip()

        if not usuario or not contrasena:
            self.lbl_mensaje.configure(text="⚠️ Por favor completa todos los campos.", text_color="#d97706")
            return

        self.btn_login.configure(state="disabled", text="Validando...")
        self.lbl_mensaje.configure(text="")
        self.update_idletasks()

        exito, mensaje, usuario_obj = AuthController.iniciar_sesion(usuario, contrasena)

        if exito:
            self.lbl_mensaje.configure(text=f"✅ {mensaje}", text_color="#16a34a")
            self.update_idletasks()
            self.after(350, lambda: self.on_login_success(usuario_obj))
        else:
            self.lbl_mensaje.configure(text=f"❌ {mensaje}", text_color="#dc2626")
            self.btn_login.configure(state="normal", text="INGRESAR")
