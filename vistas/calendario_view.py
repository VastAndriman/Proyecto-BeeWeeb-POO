import customtkinter as ctk
from conexion.supabase_client import supabase
from controladores.horario_controller import HorarioController

class CalendarioView(ctk.CTkFrame):
    def __init__(self, master, horario_controller=None):
        super().__init__(master, fg_color="transparent")
        self.horario_controller = horario_controller or HorarioController()
        
        # Header / Título del módulo
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(20, 10))
        
        self.lbl_titulo = ctk.CTkLabel(self.header_frame, text="📅 Horarios - Vista Semanal", font=("Arial", 22, "bold"))
        self.lbl_titulo.pack(side="left")
        
        btn_refresh = ctk.CTkButton(self.header_frame, text="🔄 Sincronizar Calendario", command=self.cargar_horarios, fg_color="#334155", hover_color="#475569", width=160)
        btn_refresh.pack(side="right")

        # Contenedor Principal de la Grilla Semanal
        self.grid_container = ctk.CTkScrollableFrame(self, corner_radius=10, fg_color=("#ffffff", "#1e293b"))
        self.grid_container.pack(fill="both", expand=True, padx=30, pady=10)

        self.dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
        self.bloques = [
            "07:00 - 08:00",
            "08:00 - 09:00",
            "09:00 - 10:00",
            "10:00 - 11:00",
            "11:00 - 12:00",
            "12:00 - 13:00",
            "13:00 - 14:00",
            "14:00 - 15:00",
            "15:00 - 16:00",
            "16:00 - 17:00",
            "17:00 - 18:00",
            "18:00 - 19:00"
        ]
        
        self.construir_encabezados()
        self.cargar_horarios()

    def normalizar_dia(self, dia_raw):
        if not dia_raw:
            return ""
        d = str(dia_raw).strip().capitalize()
        # Normalizar tildes comunes
        mapeo = {
            "Miercoles": "Miércoles",
            "Sabado": "Sábado"
        }
        return mapeo.get(d, d)

    def construir_encabezados(self):
        # Esquina superior izquierda vacía (Hora/Día)
        lbl_corner = ctk.CTkLabel(self.grid_container, text="Hora / Día", font=("Arial", 11, "bold"), text_color="gray", width=110)
        lbl_corner.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Encabezados de Días de la Semana
        for col_idx, dia in enumerate(self.dias, start=1):
            lbl_dia = ctk.CTkLabel(self.grid_container, text=dia, font=("Arial", 13, "bold"), fg_color="#0f172a", text_color="#38bdf8", corner_radius=6, height=35)
            lbl_dia.grid(row=0, column=col_idx, padx=4, pady=5, sticky="nsew")
            self.grid_container.grid_columnconfigure(col_idx, weight=1)

    def cargar_horarios(self):
        # Limpiar celdas previas de datos
        for widget in self.grid_container.winfo_children():
            info = widget.grid_info()
            if int(info.get("row", 0)) > 0:
                widget.destroy()

        # Dibuja la grilla base de horas
        total_cols = len(self.dias)
        for row_idx, hora in enumerate(self.bloques, start=1):
            lbl_hora = ctk.CTkLabel(self.grid_container, text=hora, font=("Arial", 11, "bold"), text_color="#94a3b8", width=110)
            lbl_hora.grid(row=row_idx, column=0, padx=5, pady=4, sticky="nsew")
            
            for col_idx in range(1, total_cols + 1):
                cell_frame = ctk.CTkFrame(self.grid_container, corner_radius=6, border_width=1, border_color="#334155", fg_color="transparent", height=70)
                cell_frame.grid(row=row_idx, column=col_idx, padx=3, pady=3, sticky="nsew")

        # Consultar la base de datos para mapear las clases guardadas
        try:
            materias_map = {str(m.get("id")): m.get("nombre", f"Materia {m.get('id')}") for m in self.horario_controller.obtener_materias()}
            aulas_map = {str(a.get("id")): str(a.get("numero", a.get("id"))) for a in self.horario_controller.obtener_aulas()}
            docentes_map = {str(d.get("id")): f"{d.get('nombre', '')} {d.get('apellido', '')}".strip() for d in self.horario_controller.obtener_docentes()}
            cursos_map = {str(c.get("id")): c.get("nombre", "") for c in self.horario_controller.obtener_cursos()}

            horarios = self.horario_controller.obtener_horarios_registrados()
            
            for h in (horarios or []):
                dia_str = self.normalizar_dia(h.get("dia") or h.get("dia_semana") or "")
                hora_ini = str(h.get("hora_inicio", "")).strip()[:5]
                hora_fin = str(h.get("hora_fin", "")).strip()[:5]
                
                materia_id = str(h.get("materia_id", ""))
                aula_id = str(h.get("aula_id", ""))
                docente_id = str(h.get("docente_id", ""))
                curso_id = str(h.get("curso_id", ""))

                materia_nom = materias_map.get(materia_id, h.get("materia") or f"Materia {materia_id}")
                aula_nom = aulas_map.get(aula_id, f"Aula {aula_id}")
                docente_nom = docentes_map.get(docente_id, "")
                curso_nom = cursos_map.get(curso_id, "")
                
                if dia_str in self.dias:
                    col_idx = self.dias.index(dia_str) + 1
                    # Buscar la fila adecuada según la hora de inicio
                    row_idx = 1
                    for idx, b in enumerate(self.bloques, start=1):
                        b_ini = b.split("-")[0].strip()
                        if hora_ini == b_ini or hora_ini in b:
                            row_idx = idx
                            break
                    
                    # Colocar tarjeta de la materia en la celda
                    card_materia = ctk.CTkFrame(self.grid_container, fg_color="#1e3a8a", corner_radius=8, border_width=1, border_color="#3b82f6")
                    card_materia.grid(row=row_idx, column=col_idx, padx=3, pady=3, sticky="nsew")
                    
                    texto_tarjeta = f"📘 {materia_nom}"
                    texto_tarjeta += f"\n📍 Aula: {aula_nom}"
                    if docente_nom:
                        texto_tarjeta += f"\n👨‍🏫 {docente_nom}"
                    if curso_nom:
                        texto_tarjeta += f"\n🎓 {curso_nom}"
                    if hora_ini and hora_fin:
                        texto_tarjeta += f"\n⏰ {hora_ini} - {hora_fin}"

                    lbl_m = ctk.CTkLabel(
                        card_materia, 
                        text=texto_tarjeta, 
                        font=("Arial", 10, "bold"), 
                        text_color="#93c5fd", 
                        justify="center",
                        wraplength=140
                    )
                    lbl_m.pack(expand=True, fill="both", padx=6, pady=6)
        except Exception as e:
            print(f"Error al sincronizar calendario: {e}")