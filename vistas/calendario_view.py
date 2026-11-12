import customtkinter as ctk
from datetime import time
from controladores.horario_controller import HorarioController

class CalendarioView(ctk.CTkFrame):
    def __init__(self, master, horario_controller=None):
        super().__init__(master, fg_color="transparent")
        self.horario_controller = horario_controller if horario_controller is not None else HorarioController()
        
        # Header / Título del módulo
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(20, 10))
        
        self.lbl_titulo = ctk.CTkLabel(self.header_frame, text="📅 Horarios - Vista Semanal", font=("Arial", 22, "bold"))
        self.lbl_titulo.pack(side="left")
        
        btn_refresh = ctk.CTkButton(self.header_frame, text="🔄 Sincronizar Calendario", command=self.cargar_horarios, fg_color="#7256ac", hover_color="#5e4497", width=160)
        btn_refresh.pack(side="right")

        self.lbl_estado = ctk.CTkLabel(self, text="", text_color="#b42318", anchor="w")
        self.lbl_estado.pack(fill="x", padx=30)

        # Contenedor Principal de la Grilla Semanal
        self.grid_container = ctk.CTkScrollableFrame(self, corner_radius=10, fg_color="#ffffff")
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

    @staticmethod
    def fila_para_hora(hora_inicio, bloques):
        """Ubica una clase en el bloque que comienza o contiene su hora de inicio."""
        try:
            hora = time.fromisoformat(str(hora_inicio).strip())
        except (TypeError, ValueError):
            return None
        for fila, bloque in enumerate(bloques, start=1):
            inicio, fin = (time.fromisoformat(parte.strip()) for parte in bloque.split("-"))
            if inicio <= hora < fin:
                return fila
        return None

    @staticmethod
    def filas_para_intervalo(hora_inicio, hora_fin, bloques):
        """Devuelve la primera fila y cuántos bloques ocupa una clase."""
        fila = CalendarioView.fila_para_hora(hora_inicio, bloques)
        if fila is None:
            return None, 0
        try:
            fin = time.fromisoformat(str(hora_fin).strip())
        except (TypeError, ValueError):
            return fila, 1
        ocupados = 0
        for bloque in bloques[fila - 1:]:
            inicio_bloque = time.fromisoformat(bloque.split("-")[0].strip())
            if inicio_bloque >= fin:
                break
            ocupados += 1
        return fila, max(1, ocupados)

    def construir_encabezados(self):
        # Esquina superior izquierda vacía (Hora/Día)
        lbl_corner = ctk.CTkLabel(self.grid_container, text="Hora / Día", font=("Arial", 11, "bold"), text_color="gray", width=110)
        lbl_corner.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Encabezados de Días de la Semana
        for col_idx, dia in enumerate(self.dias, start=1):
            lbl_dia = ctk.CTkLabel(self.grid_container, text=dia, font=("Arial", 13, "bold"), fg_color="#e8e1fb", text_color="#4b3f76", corner_radius=6, height=35)
            lbl_dia.grid(row=0, column=col_idx, padx=4, pady=5, sticky="nsew")
            self.grid_container.grid_columnconfigure(col_idx, weight=1)

    def cargar_horarios(self):
        self.lbl_estado.configure(text="")
        # Limpiar celdas previas de datos
        for widget in self.grid_container.winfo_children():
            info = widget.grid_info()
            if int(info.get("row", 0)) > 0:
                widget.destroy()

        # Dibuja la grilla base de horas
        total_cols = len(self.dias)
        celdas = {}
        for row_idx, hora in enumerate(self.bloques, start=1):
            lbl_hora = ctk.CTkLabel(self.grid_container, text=hora, font=("Arial", 11, "bold"), text_color="#786f95", width=110)
            lbl_hora.grid(row=row_idx, column=0, padx=5, pady=4, sticky="nsew")
            
            for col_idx in range(1, total_cols + 1):
                cell_frame = ctk.CTkFrame(self.grid_container, corner_radius=6, border_width=1, border_color="#d2cbe8", fg_color="transparent", height=70)
                cell_frame.grid(row=row_idx, column=col_idx, padx=3, pady=3, sticky="nsew")
                celdas[(row_idx, col_idx)] = cell_frame

        # Consultar la base de datos para mapear las clases guardadas
        try:
            materias_map = {str(m.get("id")): m.get("nombre", f"Materia {m.get('id')}") for m in self.horario_controller.obtener_materias(estricto=True)}
            aulas_map = {str(a.get("id")): str(a.get("numero", a.get("id"))) for a in self.horario_controller.obtener_aulas(estricto=True)}
            docentes_map = {str(d.get("id")): f"{d.get('nombre', '')} {d.get('apellido', '')}".strip() for d in self.horario_controller.obtener_docentes(estricto=True)}
            cursos_map = {str(c.get("id")): c.get("nombre", "") for c in self.horario_controller.obtener_cursos(estricto=True)}

            horarios = self.horario_controller.obtener_horarios_registrados(estricto=True)
            
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
                    row_idx, filas = self.filas_para_intervalo(hora_ini, hora_fin, self.bloques)
                    if row_idx is None:
                        continue
                    
                    # Cada hora conserva su propia celda. Así dos clases simultáneas
                    # pueden apilarse sin que una tarjeta tape a la otra.
                    for fila in range(row_idx, min(row_idx + filas, len(self.bloques) + 1)):
                        card_materia = ctk.CTkFrame(
                            celdas[(fila, col_idx)], fg_color="#e8e1fb", corner_radius=8,
                            border_width=1, border_color="#c7b8e9",
                        )
                        card_materia.pack(fill="x", padx=3, pady=3)
                        if fila == row_idx:
                            texto_tarjeta = f"📘 {materia_nom}\n📍 Aula: {aula_nom}"
                            if docente_nom:
                                texto_tarjeta += f"\n👨‍🏫 {docente_nom}"
                            if curso_nom:
                                texto_tarjeta += f"\n🎓 {curso_nom}"
                            texto_tarjeta += f"\n⏰ {hora_ini} - {hora_fin}"
                        else:
                            texto_tarjeta = f"↳ {materia_nom} · Aula {aula_nom}"
                        ctk.CTkLabel(
                            card_materia, text=texto_tarjeta, font=("Arial", 10, "bold"),
                            text_color="#7256ac", justify="center", wraplength=140,
                        ).pack(expand=True, fill="both", padx=6, pady=6)
        except Exception:
            self.lbl_estado.configure(
                text="No se pudo cargar el calendario. Revisa tu conexión y vuelve a sincronizar."
            )
