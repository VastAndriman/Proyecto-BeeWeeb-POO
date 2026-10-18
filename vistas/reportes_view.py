import customtkinter as ctk
from conexion.supabase_client import supabase

class ReportesView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # Header / Título del módulo
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(20, 10))
        
        self.lbl_titulo = ctk.CTkLabel(self.header_frame, text="📊 Reportes y Exportación de Datos", font=("Arial", 22, "bold"))
        self.lbl_titulo.pack(side="left")

        # Tarjeta de Filtros de Reporte
        self.filter_frame = ctk.CTkFrame(self, corner_radius=10)
        self.filter_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(self.filter_frame, text="Generar Reporte Institucional", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
        
        # Selectores
        self.combo_tipo = ctk.CTkOptionMenu(self.filter_frame, values=["Horarios Registrados", "Aulas y Aforo"])
        self.combo_tipo.pack(side="left", padx=20, pady=(0, 20))

        btn_generar = ctk.CTkButton(self.filter_frame, text="📄 Generar Vistas de Reporte", command=self.generar_reporte, fg_color="#2563eb")
        btn_generar.pack(side="left", padx=10, pady=(0, 20))

        # Consola de Previsualización del Reporte
        self.preview_frame = ctk.CTkFrame(self, corner_radius=10)
        self.preview_frame.pack(fill="both", expand=True, padx=30, pady=10)

        self.txt_reporte = ctk.CTkTextbox(self.preview_frame, font=("Courier", 12))
        self.txt_reporte.pack(fill="both", expand=True, padx=15, pady=15)

    def generar_reporte(self):
        tipo = self.combo_tipo.get()
        self.txt_reporte.delete("0.0", "end")
        
        encabezado = "===========================================================\n"
        encabezado += "        UNIVERSIDAD LAICA ELOY ALFARO DE MANABÍ (ULEAM)\n"
        encabezado += "              SISTEMA BEEWEEK - REPORTE OFICIAL\n"
        encabezado += f" Tipo de Reporte: {tipo}\n"
        encabezado += "===========================================================\n\n"
        self.txt_reporte.insert("end", encabezado)

        try:
            if tipo == "Aulas y Aforo":
                res = supabase.table("aulas").select("*").execute()
                data = res.data if res.data else []
                self.txt_reporte.insert("end", f"{'ID':<5} | {'NÚMERO':<10} | {'CAPACIDAD':<12} | {'TIPO':<15}\n")
                self.txt_reporte.insert("end", "-" * 55 + "\n")
                for row in data:
                    self.txt_reporte.insert("end", f"{row.get('id',''):<5} | {row.get('numero',''):<10} | {row.get('capacidad',''):<12} | {row.get('tipo',''):<15}\n")
            else:
                res = supabase.table("horarios").select("*").execute()
                data = res.data if res.data else []
                self.txt_reporte.insert("end", f"{'DÍA':<12} | {'HORA INICIO':<15} | {'AULA':<8} | {'DOCENTE':<10}\n")
                self.txt_reporte.insert("end", "-" * 60 + "\n")
                for row in data:
                    # Usamos exactamente la columna 'dia' que vimos en tu Supabase
                    dia_val = str(row.get('dia', 'N/A'))
                    hora_val = str(row.get('hora_inicio', 'N/A'))
                    aula_val = str(row.get('aula_id', 'N/A'))
                    docente_val = str(row.get('docente_id', 'N/A'))
                    
                    self.txt_reporte.insert("end", f"{dia_val:<12} | {hora_val:<15} | {aula_val:<8} | {docente_val:<10}\n")
        except Exception as e:
            self.txt_reporte.insert("end", f"Error al recuperar datos de la nube: {e}")