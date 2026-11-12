import os
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    Image = None
    HAS_PIL = False
import customtkinter as ctk
from vistas.horario_view import HorarioView
from vistas.aulas_view import AulasView
from vistas.calendario_view import CalendarioView
from vistas.reportes_view import ReportesView
from vistas.docente_view import DocenteView
from vistas.estudiante_view import EstudianteView
from vistas.login_view import LoginView
from vistas.academico_view import AcademicoView
from controladores.auth_controller import AuthController
from controladores.horario_controller import HorarioController
from controladores.academico_controller import AcademicoController
from conexion.supabase_client import SupabaseConnection

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme(os.path.join(os.path.dirname(__file__), "assets", "lavanda_theme.json"))

class BeeWeekApp(ctk.CTk):
    def __init__(self, db_client=None):
        super().__init__()
        self.title("BeeWeek - Sistema de Gestión y Validación Educativa")
        self.geometry("1180x730")
        self.minsize(980, 620)
        
        # ========================================================
        # COMPOSITION ROOT: Inyección de Dependencias
        # ========================================================
        self.db_client = db_client if db_client is not None else SupabaseConnection.get_client()
        self.auth_controller = AuthController(self.db_client)
        self.horario_controller = HorarioController(self.db_client)
        self.academico_controller = AcademicoController(self.db_client)

        self.sidebar_frame = None
        self.content_area = None
        self.vistas = {}
        self.login_view = None
        self.rol_actual = None

        # Iniciar directamente con la pantalla de autenticación
        self.mostrar_login()

    def mostrar_login(self):
        """Muestra la vista de inicio de sesión ocupando la ventana principal."""
        # Si la interfaz principal estaba visible, ocultarla
        if self.sidebar_frame:
            self.sidebar_frame.grid_forget()
        if self.content_area:
            self.content_area.grid_forget()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # Crear y mostrar LoginView con AuthController inyectado
        self.login_view = LoginView(
            self, 
            on_login_success=self.iniciar_aplicacion_principal,
            auth_controller=self.auth_controller
        )
        self.login_view.grid(row=0, column=0, sticky="nsew")

    def iniciar_aplicacion_principal(self, usuario):
        """Carga la interfaz principal y los módulos una vez autenticado el usuario."""
        self.rol_actual = usuario.obtener_tipo()
        if self.login_view:
            self.login_view.destroy()
            self.login_view = None

        # Reconfigurar el sistema de grilla para Sidebar + Contenido
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        if not self.sidebar_frame:
            self._construir_interfaz_principal()
        else:
            self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
            self.content_area.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

        self._aplicar_permisos_visuales()

        # Actualizar datos del usuario logueado en la barra lateral y dashboard
        nombre_completo = usuario.get_nombre_completo()
        self.lbl_user.configure(
            text=f"👤 {nombre_completo}\n🏷️ Rol: {usuario.obtener_tipo()}\n✉ {usuario.email}"
        )
        self.lbl_bienvenida.configure(text=f"Bienvenido, {nombre_completo}")

        self.cambiar_vista("dashboard")
        self.actualizar_metricas()

    def _aplicar_permisos_visuales(self):
        """Muestra las pantallas que corresponden al rol; el servidor tambien lo valida."""
        gestion = (
            self.btn_horarios, self.btn_aulas, self.btn_docentes,
            self.btn_estudiantes, self.btn_academico, self.btn_reportes,
        )
        for boton in gestion:
            if self.rol_actual == "Administrador":
                boton.grid()
            else:
                boton.grid_remove()

    def _construir_interfaz_principal(self):
        # ==========================================
        
        
        # 1. BARRA LATERAL (SIDEBAR CORPORATIVO)
        
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#e8e1fb")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)
        
        # Logo y Subtítulo (Reemplazo de la abeja por el cuadro azul)
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        logo_path = os.path.join(assets_dir, "logo_cuadro_32.png")
        if HAS_PIL and os.path.exists(logo_path):
            img_cuadro = Image.open(logo_path)
            self.logo_img = ctk.CTkImage(light_image=img_cuadro, dark_image=img_cuadro, size=(24, 26))
            self.logo_label = ctk.CTkLabel(
                self.sidebar_frame,
                text=" BeeWeek",
                image=self.logo_img,
                compound="left",
                font=("Arial", 22, "bold"),
                text_color="#7256ac"
            )
        else:
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="BeeWeek", font=("Arial", 22, "bold"), text_color="#7256ac")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(25, 5))
        
        self.sub_logo = ctk.CTkLabel(self.sidebar_frame, text="Panel de Control Educativo", font=("Arial", 11), text_color="#786f95")
        self.sub_logo.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        # Botones de Navegación Fijos
        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="📊 Inicio / Métricas", fg_color="transparent", text_color="#4b3f76", anchor="w", hover_color="#d6c9f3", command=lambda: self.cambiar_vista("dashboard"))
        self.btn_dashboard.grid(row=2, column=0, padx=15, pady=6, sticky="ew")
        
        self.btn_calendario = ctk.CTkButton(self.sidebar_frame, text="📅 Calendario Semanal", fg_color="transparent", text_color="#4b3f76", anchor="w", hover_color="#d6c9f3", command=lambda: self.cambiar_vista("calendario"))
        self.btn_calendario.grid(row=3, column=0, padx=15, pady=6, sticky="ew")

        self.btn_horarios = ctk.CTkButton(self.sidebar_frame, text="⚡ Registro de Horario", fg_color="transparent", text_color="#4b3f76", anchor="w", hover_color="#d6c9f3", command=lambda: self.cambiar_vista("horarios"))
        self.btn_horarios.grid(row=4, column=0, padx=15, pady=6, sticky="ew")
        
        self.btn_aulas = ctk.CTkButton(self.sidebar_frame, text="🏢 Gestión de Aulas", fg_color="transparent", text_color="#4b3f76", anchor="w", hover_color="#d6c9f3", command=lambda: self.cambiar_vista("aulas"))
        self.btn_aulas.grid(row=5, column=0, padx=15, pady=6, sticky="ew")

        self.btn_docentes = ctk.CTkButton(self.sidebar_frame, text="👨‍🏫 Gestión Docentes", fg_color="transparent", text_color="#4b3f76", anchor="w", hover_color="#d6c9f3", command=lambda: self.cambiar_vista("docentes"))
        self.btn_docentes.grid(row=6, column=0, padx=15, pady=6, sticky="ew")

        self.btn_estudiantes = ctk.CTkButton(self.sidebar_frame, text="🎓 Gestión Estudiantes", fg_color="transparent", text_color="#4b3f76", anchor="w", hover_color="#d6c9f3", command=lambda: self.cambiar_vista("estudiantes"))
        self.btn_estudiantes.grid(row=7, column=0, padx=15, pady=6, sticky="ew")

        self.btn_academico = ctk.CTkButton(self.sidebar_frame, text="📚 Materias y Cursos", fg_color="transparent", text_color="#4b3f76", anchor="w", hover_color="#d6c9f3", command=lambda: self.cambiar_vista("academico"))
        self.btn_academico.grid(row=8, column=0, padx=15, pady=6, sticky="ew")

        self.btn_reportes = ctk.CTkButton(self.sidebar_frame, text="📑 Reportes", fg_color="transparent", text_color="#4b3f76", anchor="w", hover_color="#d6c9f3", command=lambda: self.cambiar_vista("reportes"))
        self.btn_reportes.grid(row=9, column=0, padx=15, pady=6, sticky="ew")
        
        # Footer del Usuario y Cerrar Sesión
        self.lbl_user = ctk.CTkLabel(self.sidebar_frame, text="👤 Usuario\n🌐 uleam.edu.ec", font=("Arial", 11), text_color="#786f95", anchor="w", justify="left")
        self.lbl_user.grid(row=11, column=0, padx=20, pady=(15, 6), sticky="sw")

        self.btn_logout = ctk.CTkButton(
            self.sidebar_frame,
            text="🚪 Cerrar Sesión",
            fg_color="#7256ac",
            hover_color="#5e4497",
            text_color="#ffffff",
            height=32,
            font=("Arial", 12, "bold"),
            command=self.cerrar_sesion
        )
        self.btn_logout.grid(row=12, column=0, padx=15, pady=(0, 20), sticky="ew")

        # ==========================================
        # 2. CONTENEDOR PRINCIPAL
        
        self.content_area = ctk.CTkFrame(self, fg_color="#f3f0fb")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

        # Registro de vistas
        self.vistas["dashboard"] = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self._construir_dashboard(self.vistas["dashboard"])

    def _crear_vista(self, nombre_vista):
        """Construye un módulo solo cuando la persona lo abre por primera vez."""
        constructores = {
            "calendario": lambda: CalendarioView(self.content_area, horario_controller=self.horario_controller),
            "horarios": lambda: HorarioView(self.content_area, horario_controller=self.horario_controller),
            "aulas": lambda: AulasView(self.content_area, db_client=self.db_client),
            "docentes": lambda: DocenteView(self.content_area, db_client=self.db_client),
            "estudiantes": lambda: EstudianteView(self.content_area, db_client=self.db_client),
            "academico": lambda: AcademicoView(self.content_area, academico_controller=self.academico_controller),
            "reportes": lambda: ReportesView(self.content_area, horario_controller=self.horario_controller),
        }
        return constructores[nombre_vista]()

    def _construir_dashboard(self, parent):
        self.lbl_bienvenida = ctk.CTkLabel(parent, text="Bienvenido, Usuario", font=("Arial", 22, "bold"))
        self.lbl_bienvenida.pack(anchor="w", padx=30, pady=(25, 5))
        
        lbl_sub = ctk.CTkLabel(parent, text="Resumen general del sistema educativo sincronizado en la nube.", font=("Arial", 13), text_color="gray")
        lbl_sub.pack(anchor="w", padx=30, pady=(0, 15))
        
        # Tarjetas de Métricas
        cards_frame = ctk.CTkFrame(parent, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30, pady=10)
        
        card1, self.card_aulas_val = self._crear_tarjeta(cards_frame, "Total de Aulas", "#7256ac")
        card1.pack(side="left", padx=(0, 15), expand=True, fill="both")
        
        card2, self.card_horarios_val = self._crear_tarjeta(cards_frame, "Horarios Activos", "#15803d")
        card2.pack(side="left", padx=15, expand=True, fill="both")
        
        btn_refresh = ctk.CTkButton(parent, text="🔄 Actualizar datos", command=self.actualizar_metricas, fg_color="#7256ac")
        btn_refresh.pack(anchor="w", padx=30, pady=10)

        self.lbl_estado_conexion = ctk.CTkLabel(parent, text="Esperando sincronización...", text_color="#786f95")
        self.lbl_estado_conexion.pack(anchor="w", padx=30)

        # Resumen de funciones disponibles; no simula comprobaciones de servicio.
        info_frame = ctk.CTkFrame(parent, corner_radius=10)
        info_frame.pack(fill="both", expand=True, padx=30, pady=15)
        
        ctk.CTkLabel(info_frame, text="BeeWeek en resumen", font=("Arial", 16, "bold")).pack(padx=20, pady=(15, 10), anchor="w")
        ctk.CTkLabel(info_frame, text="Consulta las clases de la semana en Calendario Semanal.", font=("Arial", 13), text_color="#4b3f76").pack(padx=20, pady=4, anchor="w")
        ctk.CTkLabel(info_frame, text="Los horarios se validan al registrarlos o modificarlos.", font=("Arial", 13), text_color="#4b3f76").pack(padx=20, pady=4, anchor="w")
        ctk.CTkLabel(info_frame, text="Los datos mostrados arriba provienen de Supabase.", font=("Arial", 13), text_color="#4b3f76").pack(padx=20, pady=(4, 15), anchor="w")

    def _crear_tarjeta(self, parent, titulo, color_valor):
        card = ctk.CTkFrame(parent, width=200, height=100, corner_radius=10)
        ctk.CTkLabel(card, text=titulo, font=("Arial", 12, "bold"), text_color="gray").pack(padx=15, pady=(15, 5), anchor="w")
        lbl_valor = ctk.CTkLabel(card, text="...", font=("Arial", 26, "bold"), text_color=color_valor)
        lbl_valor.pack(padx=15, pady=(0, 15), anchor="w")
        return card, lbl_valor

    def actualizar_metricas(self):
        try:
            res_aulas = self.db_client.table("aulas").select("*", count="exact").execute()
            total_aulas = res_aulas.count if res_aulas.count is not None else len(res_aulas.data)
            self.card_aulas_val.configure(text=str(total_aulas))
            
            res_horarios = self.db_client.table("horarios").select("*", count="exact").execute()
            total_horarios = res_horarios.count if res_horarios.count is not None else len(res_horarios.data)
            self.card_horarios_val.configure(text=str(total_horarios))
            self.lbl_estado_conexion.configure(text="Datos actualizados desde Supabase.", text_color="#15803d")
        except Exception:
            self.card_aulas_val.configure(text="Err")
            self.card_horarios_val.configure(text="Err")
            self.lbl_estado_conexion.configure(
                text="No se pudieron cargar las métricas. Revisa la conexión y pulsa Actualizar datos.",
                text_color="#b42333",
            )

    def cambiar_vista(self, nombre_vista):
        if self.rol_actual != "Administrador" and nombre_vista not in ("dashboard", "calendario"):
            nombre_vista = "calendario"
        nueva = nombre_vista not in self.vistas
        if nueva:
            self.vistas[nombre_vista] = self._crear_vista(nombre_vista)
        for vista in self.vistas.values():
            vista.pack_forget()
        vista_activa = self.vistas[nombre_vista]
        vista_activa.pack(fill="both", expand=True)
        # Los módulos nuevos ya cargan sus datos en __init__.
        if nueva:
            return
        if hasattr(vista_activa, "cargar_datos_dinamicos"):
            vista_activa.cargar_datos_dinamicos()
        elif hasattr(vista_activa, "cargar_horarios"):
            vista_activa.cargar_horarios()
        elif hasattr(vista_activa, "cargar_aulas"):
            vista_activa.cargar_aulas()
        elif hasattr(vista_activa, "cargar_docentes"):
            vista_activa.cargar_docentes()
        elif hasattr(vista_activa, "cargar_estudiantes"):
            vista_activa.cargar_estudiantes()

    def cerrar_sesion(self):
        """Cierra la sesión actual y regresa a la pantalla de login."""
        self.auth_controller.cerrar_sesion()
        self.rol_actual = None
        self.mostrar_login()

if __name__ == "__main__":
    try:
        app = BeeWeekApp()
        app.mainloop()
    except KeyboardInterrupt:
        pass
