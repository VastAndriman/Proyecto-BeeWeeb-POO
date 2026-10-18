import customtkinter as ctk
from conexion.supabase_client import SupabaseConnection

class DocenteView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # Header / Título de la vista
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(20, 10))
        
        self.titulo = ctk.CTkLabel(self.header_frame, text="👨‍🏫 Gestión de Docentes", font=("Arial", 22, "bold"))
        self.titulo.pack(side="left")
        
        btn_refrescar = ctk.CTkButton(self.header_frame, text="🔄 Sincronizar Lista", command=self.cargar_docentes, fg_color="#334155", width=150)
        btn_refrescar.pack(side="right")

        # Contenedor principal de dos columnas
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=30, pady=10)

        # -------------------------------------------------------------
        # COLUMNA IZQUIERDA: Formulario de Registro
        # -------------------------------------------------------------
        self.form_frame = ctk.CTkFrame(self.main_container, corner_radius=10, width=320)
        self.form_frame.pack(side="left", fill="y", padx=(0, 15), pady=0)

        ctk.CTkLabel(self.form_frame, text="Registrar Nuevo Docente", font=("Arial", 14, "bold")).pack(pady=(15, 10))

        self.entry_identificacion = ctk.CTkEntry(self.form_frame, placeholder_text="Identificación / Cédula", width=260)
        self.entry_identificacion.pack(pady=8, padx=20)
        
        self.entry_nombre = ctk.CTkEntry(self.form_frame, placeholder_text="Nombre", width=260)
        self.entry_nombre.pack(pady=8, padx=20)
        
        self.entry_apellido = ctk.CTkEntry(self.form_frame, placeholder_text="Apellido", width=260)
        self.entry_apellido.pack(pady=8, padx=20)
        
        self.entry_email = ctk.CTkEntry(self.form_frame, placeholder_text="Correo Electrónico", width=260)
        self.entry_email.pack(pady=8, padx=20)
        
        self.entry_especialidad = ctk.CTkEntry(self.form_frame, placeholder_text="Especialidad (ej. Software)", width=260)
        self.entry_especialidad.pack(pady=8, padx=20)
        
        # Botón para guardar
        self.btn_guardar = ctk.CTkButton(self.form_frame, text="💾 Guardar en Supabase", command=self.guardar_docente, fg_color="#2563eb", width=260)
        self.btn_guardar.pack(pady=15, padx=20)
        
        # Etiqueta de mensajes
        self.lbl_mensaje = ctk.CTkLabel(self.form_frame, text="", font=("Arial", 11), wraplength=250)
        self.lbl_mensaje.pack(pady=5, padx=10)

        # -------------------------------------------------------------
        # COLUMNA DERECHA: Tabla / Consola con Lista de Docentes
        # -------------------------------------------------------------
        self.list_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.list_frame.pack(side="right", fill="both", expand=True, padx=0, pady=0)

        self.textbox = ctk.CTkTextbox(self.list_frame, font=("Courier", 11))
        self.textbox.pack(fill="both", expand=True, padx=15, pady=15)

        # Carga inicial de datos desde Supabase
        self.cargar_docentes()

    def guardar_docente(self):
        identificacion = self.entry_identificacion.get()
        nombre = self.entry_nombre.get()
        apellido = self.entry_apellido.get()
        email = self.entry_email.get()
        especialidad = self.entry_especialidad.get()
        
        if not identificacion or not nombre or not apellido or not email or not especialidad:
            self.lbl_mensaje.configure(text="Por favor completa todos los campos.", text_color="orange")
            return
            
        try:
            client = SupabaseConnection.get_client()
            data = {
                "identificacion": identificacion,
                "nombre": nombre,
                "apellido": apellido,
                "email": email,
                "especialidad": especialidad
            }
            client.table("docentes").insert(data).execute()
            self.lbl_mensaje.configure(text="¡Docente guardado con éxito!", text_color="#34d399")
            
            # Limpiar campos
            self.entry_identificacion.delete(0, 'end')
            self.entry_nombre.delete(0, 'end')
            self.entry_apellido.delete(0, 'end')
            self.entry_email.delete(0, 'end')
            self.entry_especialidad.delete(0, 'end')

            # Recargar la lista en vivo
            self.cargar_docentes()
            
        except Exception as e:
            self.lbl_mensaje.configure(text=f"Error al guardar: {e}", text_color="#ef4444")

    def cargar_docentes(self):
        self.textbox.delete("0.0", "end")
        try:
            client = SupabaseConnection.get_client()
            res = client.table("docentes").select("*").execute()
            data = res.data if res.data else []
            
            encabezado = f"{'CÉDULA':<12} | {'NOMBRE Y APELLIDO':<25} | {'ESPECIALIDAD':<18}\n"
            encabezado += "=" * 62 + "\n"
            self.textbox.insert("end", encabezado)
            
            if not data:
                self.textbox.insert("end", "No hay docentes registrados aún en Supabase.\n")
                
            for item in data:
                ced = str(item.get('identificacion', item.get('id', 'N/A')))
                nom = f"{item.get('nombre', '')} {item.get('apellido', '')}".strip()
                esp = str(item.get('especialidad', 'General'))
                
                linea = f"{ced:<12} | {nom:<25} | {esp:<18}\n"
                self.textbox.insert("end", linea)
                
        except Exception as e:
            self.textbox.insert("end", f"Error al consultar Supabase: {e}")