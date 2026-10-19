import customtkinter as ctk
from conexion.supabase_client import supabase
from controladores.horario_controller import HorarioController

class CalendarioView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # Header / Título del módulo
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(20, 10))
        
        self.lbl_titulo = ctk.CTkLabel(self.header_frame, text="📅 Horarios - Vista Semanal", font=("Arial", 22, "bold"))
        self.lbl_titulo.pack(side="left")
        
        btn_refresh = ctk.CTkButton(self.header_frame, text="🔄 Sincronizar Calendario", command=self.cargar_horarios, fg_color="#334155", width=160)
        btn_refresh.pack(side="right")

        # Contenedor Principal de la Grilla Semanal
        self.grid_container = ctk.CTkScrollableFrame(self, corner_radius=10, fg_color=("#ffffff", "#1e293b"))
        self.grid_container.pack(fill="both", expand=True, padx=30, pady=10)

        self.dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        self.bloques = ["07:00 - 08:00", "08:00 - 09:00", "09:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00", "12:00 - 13:00", "13:00 - 14:00"]
        
        self.construir_encabezados()
        self.cargar_horarios()

    def construir_encabezados(self):
        # Esquina superior izquierda vacía (Hora/Día)
        lbl_corner = ctk.CTkLabel(self.grid_container, text="Hora / Día", font=("Arial", 11, "bold"), text_color="gray", width=120)
        lbl_corner.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Encabezados de Días de la Semana
        for col_idx, dia in enumerate(self.dias, start=1):
            lbl_dia = ctk.CTkLabel(self.grid_container, text=dia, font=("Arial", 13, "bold"), fg_color="#0f172a", text_color="#38bdf8", corner_radius=6, height=35)
            lbl_dia.grid(row=0, column=col_idx, padx=4, pady=5, sticky="nsew")
            self.grid_container.grid_columnconfigure(col_idx, weight=1)

    def cargar_horarios(self):
        # Limpiar celda de datos
        for widget in self.grid_container.winfo_children():
            info = widget.grid_info()
            if int(info["row"]) > 0:
                widget.destroy()

        # Dibuja la grilla de horas
        for row_idx, hora in enumerate(self.bloques, start=1):
            lbl_hora = ctk.CTkLabel(self.grid_container, text=hora, font=("Arial", 11, "bold"), text_color="#94a3b8", width=120)
            lbl_hora.grid(row=row_idx, column=0, padx=5, pady=5, sticky="nsew")
            
            for col_idx in range(1, 6):
                cell_frame = ctk.CTkFrame(self.grid_container, corner_radius=6, border_width=1, border_color="#334155", fg_color="transparent", height=65)
                cell_frame.grid(row=row_idx, column=col_idx, padx=4, pady=4, sticky="nsew")

        # Consultar la base de datos para mapear las clases guardadas
        try:
            materias_map = {str(m.get("id")): m.get("nombre", f"Materia {m.get('id')}") for m in HorarioController.obtener_materias()}
            aulas_map = {str(a.get("id")): str(a.get("numero", a.get("id"))) for a in HorarioController.obtener_aulas()}
            docentes_map = {str(d.get("id")): f"{d.get('nombre', '')} {d.get('apellido', '')}".strip() for d in HorarioController.obtener_docentes()}

            res = supabase.table("horarios").select("*").execute()
            horarios = res.data if res.data else []
            
            for h in horarios:
                dia_str = str(h.get("dia") or h.get("dia_semana") or "").strip().capitalize()
                hora_str = str(h.get("hora_inicio", "")).strip()[:5]
                
                materia_id = str(h.get("materia_id", ""))
                aula_id = str(h.get("aula_id", ""))
                docente_id = str(h.get("docente_id", ""))

                materia_nom = materias_map.get(materia_id, h.get("materia") or f"Materia {materia_id}")
                aula_nom = aulas_map.get(aula_id, aula_id)
                docente_nom = docentes_map.get(docente_id, "")
                
                if dia_str in self.dias:
                    col_idx = self.dias.index(dia_str) + 1
                    # Buscar la fila adecuada según la hora
                    row_idx = 1
                    for idx, b in enumerate(self.bloques, start=1):
                        if hora_str in b:
                            row_idx = idx
                            break
                    
                    # Colocar tarjeta de la materia en la celda
                    card_materia = ctk.CTkFrame(self.grid_container, fg_color="#1e3a8a", corner_radius=6)
                    card_materia.grid(row=row_idx, column=col_idx, padx=4, pady=4, sticky="nsew")
                    
                    texto_tarjeta = f"📘 {materia_nom}\n📍 Aula: {aula_nom}"
                    if docente_nom:
                        texto_tarjeta += f"\n👨‍🏫 {docente_nom}"
                    lbl_m = ctk.CTkLabel(card_materia, text=texto_tarjeta, font=("Arial", 10, "bold"), text_color="#93c5fd", justify="center")
                    lbl_m.pack(expand=True, fill="both", padx=5, pady=5)
        except Exception:
            pass