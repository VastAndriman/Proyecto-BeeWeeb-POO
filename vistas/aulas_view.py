import customtkinter as ctk
from conexion.supabase_client import supabase

class AulasView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.titulo = ctk.CTkLabel(self, text="Listado de Aulas Registradas en la Nube", font=("Arial", 18, "bold"))
        self.titulo.pack(pady=15)
        
        self.btn_cargar = ctk.CTkButton(self, text="Cargar Aulas desde Supabase", command=self.cargar_aulas)
        self.btn_cargar.pack(pady=10)
        
        # Cuadro de texto para mostrar los datos en formato limpio
        self.textbox = ctk.CTkTextbox(self, width=600, height=350, font=("Courier", 12))
        self.textbox.pack(pady=10)
        
        # Cargar al iniciar la vista
        self.cargar_aulas()

    def cargar_aulas(self):
        self.textbox.delete("0.0", "end")
        try:
            # Petición directa a Supabase usando el cliente centralizado
            response = supabase.table("aulas").select("*").execute()
            data = response.data
            
            if not data:
                self.textbox.insert("0.0", "No hay aulas registradas todavía.")
                return
                
            texto_formateado = f"{'ID':<5} | {'NÚMERO':<10} | {'CAPACIDAD':<10} | {'TIPO':<15}\n"
            texto_formateado += "-" * 50 + "\n"
            
            for aula in data:
                texto_formateado += f"{aula['id']:<5} | {aula['numero']:<10} | {aula['capacidad']:<10} | {aula['tipo']:<15}\n"
                
            self.textbox.insert("0.0", texto_formateado)
        except Exception as e:
            self.textbox.insert("0.0", f"Error al conectar con la base de datos: {e}")