import customtkinter as ctk
from conexion.supabase_client import SupabaseConnection

class DocenteView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # Título de la vista
        self.titulo = ctk.CTkLabel(self, text="Gestión de Docentes", font=("Arial", 20, "bold"))
        self.titulo.pack(pady=20)
        
        # Campos de entrada
        self.entry_identificacion = ctk.CTkEntry(self, placeholder_text="Identificación / Cédula")
        self.entry_identificacion.pack(pady=8)
        
        self.entry_nombre = ctk.CTkEntry(self, placeholder_text="Nombre")
        self.entry_nombre.pack(pady=8)
        
        self.entry_apellido = ctk.CTkEntry(self, placeholder_text="Apellido")
        self.entry_apellido.pack(pady=8)
        
        self.entry_email = ctk.CTkEntry(self, placeholder_text="Correo Electrónico")
        self.entry_email.pack(pady=8)
        
        self.entry_especialidad = ctk.CTkEntry(self, placeholder_text="Especialidad (ej. Software)")
        self.entry_especialidad.pack(pady=8)
        
        # Botón para guardar
        self.btn_guardar = ctk.CTkButton(self, text="Guardar Docente en Supabase", command=self.guardar_docente)
        self.btn_guardar.pack(pady=15)
        
        # Etiqueta de mensajes
        self.lbl_mensaje = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.lbl_mensaje.pack(pady=5)

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
            self.lbl_mensaje.configure(text="¡Docente guardado con éxito en la nube!", text_color="green")
            
            # Limpiar campos
            self.entry_identificacion.delete(0, 'end')
            self.entry_nombre.delete(0, 'end')
            self.entry_apellido.delete(0, 'end')
            self.entry_email.delete(0, 'end')
            self.entry_especialidad.delete(0, 'end')
        except Exception as e:
            self.lbl_mensaje.configure(text=f"Error al guardar: {e}", text_color="red")