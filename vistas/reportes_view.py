import customtkinter as ctk
from conexion.supabase_client import supabase
from controladores.horario_controller import HorarioController

class ReportesView(ctk.CTkFrame):
    def __init__(self, master, horario_controller=None):
        super().__init__(master, fg_color="transparent")
        self.horario_controller = horario_controller or HorarioController()
        
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

        self.txt_reporte = ctk.CTkTextbox(self.preview_frame, font=("Courier", 11))
        self.txt_reporte.pack(fill="both", expand=True, padx=15, pady=15)

    def generar_reporte(self):
        tipo = self.combo_tipo.get()
        self.txt_reporte.delete("0.0", "end")
        
        encabezado = "=========================================================================================================\n"
        encabezado += "                           UNIVERSIDAD LAICA ELOY ALFARO DE MANABÍ (ULEAM)\n"
        encabezado += "                                 SISTEMA BEEWEEK - REPORTE OFICIAL\n"
        encabezado += f" Tipo de Reporte: {tipo}\n"
        encabezado += "=========================================================================================================\n\n"
        self.txt_reporte.insert("end", encabezado)

        try:
            if tipo == "Aulas y Aforo":
                res = supabase.table("aulas").select("*").execute()
                data = res.data if res.data else []
                self.txt_reporte.insert("end", f"{'ID':<6} | {'NÚMERO':<12} | {'CAPACIDAD':<14} | {'TIPO':<20}\n")
                self.txt_reporte.insert("end", "-" * 60 + "\n")
                for row in data:
                    self.txt_reporte.insert("end", f"{row.get('id',''):<6} | {row.get('numero',''):<12} | {row.get('capacidad',''):<14} | {row.get('tipo',''):<20}\n")
            else:
                materias_map = {str(m.get("id")): m.get("nombre", f"ID: {m.get('id')}") for m in self.horario_controller.obtener_materias()}
                aulas_map = {str(a.get("id")): f"Aula {a.get('numero', a.get('id'))}" for a in self.horario_controller.obtener_aulas()}
                docentes_map = {str(d.get("id")): f"{d.get('nombre', '')} {d.get('apellido', '')}".strip() for d in self.horario_controller.obtener_docentes()}
                cursos_map = {str(c.get("id")): c.get("nombre", f"ID: {c.get('id')}") for c in self.horario_controller.obtener_cursos()}

                data = self.horario_controller.obtener_horarios_registrados()
                
                self.txt_reporte.insert("end", f"{'DÍA':<10} | {'HORA':<13} | {'AULA':<12} | {'DOCENTE':<22} | {'MATERIA':<28} | {'CURSO':<15}\n")
                self.txt_reporte.insert("end", "-" * 105 + "\n")
                for row in data:
                    dia_val = str(row.get('dia', 'N/A'))[:10]
                    h_ini = str(row.get('hora_inicio', ''))[:5]
                    h_fin = str(row.get('hora_fin', ''))[:5]
                    hora_val = f"{h_ini}-{h_fin}" if h_fin else h_ini

                    aula_val = aulas_map.get(str(row.get('aula_id')), f"ID: {row.get('aula_id')}")[:12]
                    docente_val = docentes_map.get(str(row.get('docente_id')), f"ID: {row.get('docente_id')}")[:22]
                    materia_val = materias_map.get(str(row.get('materia_id')), f"ID: {row.get('materia_id')}")[:28]
                    curso_val = cursos_map.get(str(row.get('curso_id')), f"ID: {row.get('curso_id')}")[:15]
                    
                    self.txt_reporte.insert("end", f"{dia_val:<10} | {hora_val:<13} | {aula_val:<12} | {docente_val:<22} | {materia_val:<28} | {curso_val:<15}\n")
        except Exception as e:
            self.txt_reporte.insert("end", f"Error al recuperar datos de la nube: {e}")