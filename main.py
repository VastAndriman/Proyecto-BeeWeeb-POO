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
from vistas.login_view import LoginView
from controladores.auth_controller import AuthController
from conexion.supabase_client import supabase

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class BeeWeekApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BeeWeek - Sistema de Gestión y Validación Educativa")
        self.geometry("1180x730")
        self.minsize(980, 620)
        
        self.sidebar_frame = None
        self.content_area = None
        self.vistas = {}
        self.login_view = None

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

        # Crear y mostrar LoginView
        self.login_view = LoginView(self, on_login_success=self.iniciar_aplicacion_principal)
        self.login_view.grid(row=0, column=0, sticky="nsew")

    def iniciar_aplicacion_principal(self, usuario):
        """Carga la interfaz principal y los módulos una vez autenticado el usuario."""
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

        # Actualizar datos del usuario logueado en la barra lateral y dashboard
        nombre_completo = usuario.get_nombre_completo()
        self.lbl_user.configure(
            text=f"👤 {nombre_completo}\n🏷️ Rol: {usuario.rol}\n🌐 uleam.edu.ec"
        )
        self.lbl_bienvenida.configure(text=f"Bienvenido, {nombre_completo}")

        self.cambiar_vista("dashboard")
        self.actualizar_metricas()

    def _construir_interfaz_principal(self):
        # ==========================================
        
        
        # 1. BARRA LATERAL (SIDEBAR CORPORATIVO)
        
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=("#1e293b", "#0f172a"))
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)
        
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
                text_color="#38bdf8"
            )
        else:
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="BeeWeek", font=("Arial", 22, "bold"), text_color="#38bdf8")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(25, 5))
        
        self.sub_logo = ctk.CTkLabel(self.sidebar_frame, text="Panel de Control Educativo", font=("Arial", 11), text_color="#94a3b8")
        self.sub_logo.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        # Botones de Navegación Fijos
        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="📊 Inicio / Métricas", fg_color="transparent", text_color="#f8fafc", anchor="w", hover_color="#334155", command=lambda: self.cambiar_vista("dashboard"))
        self.btn_dashboard.grid(row=2, column=0, padx=15, pady=6, sticky="ew")
        
        self.btn_calendario = ctk.CTkButton(self.sidebar_frame, text="📅 Calendario Semanal", fg_color="transparent", text_color="#f8fafc", anchor="w", hover_color="#334155", command=lambda: self.cambiar_vista("calendario"))
        self.btn_calendario.grid(row=3, column=0, padx=15, pady=6, sticky="ew")

        self.btn_horarios = ctk.CTkButton(self.sidebar_frame, text="⚡ Registro de Horario", fg_color="transparent", text_color="#f8fafc", anchor="w", hover_color="#334155", command=lambda: self.cambiar_vista("horarios"))
        self.btn_horarios.grid(row=4, column=0, padx=15, pady=6, sticky="ew")
        
        self.btn_aulas = ctk.CTkButton(self.sidebar_frame, text="🏢 Gestión de Aulas", fg_color="transparent", text_color="#f8fafc", anchor="w", hover_color="#334155", command=lambda: self.cambiar_vista("aulas"))
        self.btn_aulas.grid(row=5, column=0, padx=15, pady=6, sticky="ew")

        self.btn_docentes = ctk.CTkButton(self.sidebar_frame, text="👨‍🏫 Gestión Docentes", fg_color="transparent", text_color="#f8fafc", anchor="w", hover_color="#334155", command=lambda: self.cambiar_vista("docentes"))
        self.btn_docentes.grid(row=6, column=0, padx=15, pady=6, sticky="ew")

        self.btn_reportes = ctk.CTkButton(self.sidebar_frame, text="📑 Reportes", fg_color="transparent", text_color="#f8fafc", anchor="w", hover_color="#334155", command=lambda: self.cambiar_vista("reportes"))
        self.btn_reportes.grid(row=7, column=0, padx=15, pady=6, sticky="ew")  
        
        # Footer del Usuario y Cerrar Sesión
        self.lbl_user = ctk.CTkLabel(self.sidebar_frame, text="👤 Usuario\n🌐 uleam.edu.ec", font=("Arial", 11), text_color="#94a3b8", anchor="w", justify="left")
        self.lbl_user.grid(row=9, column=0, padx=20, pady=(15, 6), sticky="sw")

        self.btn_logout = ctk.CTkButton(
            self.sidebar_frame,
            text="🚪 Cerrar Sesión",
            fg_color="#dc2626",
            hover_color="#b91c1c",
            text_color="#ffffff",
            height=32,
            font=("Arial", 12, "bold"),
            command=self.cerrar_sesion
        )
        self.btn_logout.grid(row=10, column=0, padx=15, pady=(0, 20), sticky="ew")

        # ==========================================
        # 2. CONTENEDOR PRINCIPAL
        
        self.content_area = ctk.CTkFrame(self, fg_color=("#f1f5f9", "#111827"))
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

        # Registro de vistas
        self.vistas["dashboard"] = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self._construir_dashboard(self.vistas["dashboard"])
        
        self.vistas["calendario"] = CalendarioView(self.content_area)
        self.vistas["horarios"] = HorarioView(self.content_area)
        self.vistas["aulas"] = AulasView(self.content_area)
        self.vistas["docentes"] = DocenteView(self.content_area)
        self.vistas["reportes"] = ReportesView(self.content_area)

    def _construir_dashboard(self, parent):
        self.lbl_bienvenida = ctk.CTkLabel(parent, text="Bienvenido, Usuario", font=("Arial", 22, "bold"))
        self.lbl_bienvenida.pack(anchor="w", padx=30, pady=(25, 5))
        
        lbl_sub = ctk.CTkLabel(parent, text="Resumen general del sistema educativo sincronizado en la nube.", font=("Arial", 13), text_color="gray")
        lbl_sub.pack(anchor="w", padx=30, pady=(0, 15))
        
        # Tarjetas de Métricas
        cards_frame = ctk.CTkFrame(parent, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30, pady=10)
        
        self.card_aulas_val = ctk.CTkLabel(cards_frame, text="...", font=("Arial", 26, "bold"), text_color="#38bdf8")
        card1 = self._crear_tarjeta(cards_frame, "Total de Aulas", self.card_aulas_val)
        card1.pack(side="left", padx=(0, 15), expand=True, fill="both")
        
        self.card_horarios_val = ctk.CTkLabel(cards_frame, text="...", font=("Arial", 26, "bold"), text_color="#34d399")
        card2 = self._crear_tarjeta(cards_frame, "Horarios Activos", self.card_horarios_val)
        card2.pack(side="left", padx=15, expand=True, fill="both")
        
        btn_refresh = ctk.CTkButton(parent, text="🔄 Sincronizar Métrica Supabase", command=self.actualizar_metricas, fg_color="#334155")
        btn_refresh.pack(anchor="w", padx=30, pady=10)

        # Panel Informativo
        info_frame = ctk.CTkFrame(parent, corner_radius=10)
        info_frame.pack(fill="both", expand=True, padx=30, pady=15)
        
        ctk.CTkLabel(info_frame, text="🚀 Estado del Motor de Validación y Arquitectura", font=("Arial", 16, "bold")).pack(padx=20, pady=(15, 10), anchor="w")
        ctk.CTkLabel(info_frame, text="• Algoritmo anti-cruces de horarios: ACTIVO", font=("Arial", 13), text_color="#34d399").pack(padx=20, pady=4, anchor="w")
        ctk.CTkLabel(info_frame, text="• Sincronización con Supabase (Cloud DB): CONECTADO", font=("Arial", 13), text_color="#34d399").pack(padx=20, pady=4, anchor="w")
        ctk.CTkLabel(info_frame, text="• Módulo de Autenticación y Sesión: ACTIVO", font=("Arial", 13), text_color="#34d399").pack(padx=20, pady=4, anchor="w")
        ctk.CTkLabel(info_frame, text="• Vista de Horario Semanal (Grid / Matriz): OPERATIVO", font=("Arial", 13), text_color="#34d399").pack(padx=20, pady=4, anchor="w")
        ctk.CTkLabel(info_frame, text="• Arquitectura Orientada a Objetos (POO): IMPLEMENTADA", font=("Arial", 13), text_color="#34d399").pack(padx=20, pady=(4, 15), anchor="w")

    def _crear_tarjeta(self, parent, titulo, lbl_valor):
        card = ctk.CTkFrame(parent, width=200, height=100, corner_radius=10)
        ctk.CTkLabel(card, text=titulo, font=("Arial", 12, "bold"), text_color="gray").pack(padx=15, pady=(15, 5), anchor="w")
        lbl_valor.pack(padx=15, pady=(0, 15), anchor="w")
        return card

    def actualizar_metricas(self):
        try:
            res_aulas = supabase.table("aulas").select("*", count="exact").execute()
            total_aulas = res_aulas.count if res_aulas.count is not None else len(res_aulas.data)
            self.card_aulas_val.configure(text=str(total_aulas))
            
            res_horarios = supabase.table("horarios").select("*", count="exact").execute()
            total_horarios = res_horarios.count if res_horarios.count is not None else len(res_horarios.data)
            self.card_horarios_val.configure(text=str(total_horarios))
        except Exception:
            self.card_aulas_val.configure(text="Err")
            self.card_horarios_val.configure(text="Err")

    def cambiar_vista(self, nombre_vista):
        for vista in self.vistas.values():
            vista.pack_forget()
        vista_activa = self.vistas[nombre_vista]
        vista_activa.pack(fill="both", expand=True)
        if hasattr(vista_activa, "cargar_datos_dinamicos"):
            vista_activa.cargar_datos_dinamicos()
        elif hasattr(vista_activa, "cargar_horarios"):
            vista_activa.cargar_horarios()
        elif hasattr(vista_activa, "cargar_aulas"):
            vista_activa.cargar_aulas()

    def cerrar_sesion(self):
        """Cierra la sesión actual y regresa a la pantalla de login."""
        AuthController.cerrar_sesion()
        self.mostrar_login()

if __name__ == "__main__":
    app = BeeWeekApp()
    app.mainloop()