import customtkinter as ctk
from controladores.horario_controller import HorarioController

class HorarioView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # Mapeos internos de etiquetas legibles a IDs
        self.docentes_map = {}
        self.aulas_map = {}
        self.materias_map = {}
        self.cursos_map = {}

        # Contenedor desplazable principal
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True, padx=25, pady=15)
        
        # ==========================================
        # 1. ENCABEZADO DE LA VISTA
        # ==========================================
        self.header_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 15))
        
        self.titulo = ctk.CTkLabel(
            self.header_frame, 
            text="⚡ Gestión y Validación de Horarios", 
            font=("Arial", 22, "bold")
        )
        self.titulo.pack(side="left")

        self.btn_recargar = ctk.CTkButton(
            self.header_frame,
            text="🔄 Actualizar Opciones",
            width=160,
            fg_color="#334155",
            hover_color="#475569",
            command=self.cargar_datos_dinamicos
        )
        self.btn_recargar.pack(side="right")
        
        self.subtitulo = ctk.CTkLabel(
            self.scroll_container,
            text="Selecciona los datos mediante listas desplegables. El motor valida automáticamente aforo y choques de horario.",
            font=("Arial", 12),
            text_color="gray"
        )
        self.subtitulo.pack(anchor="w", pady=(0, 15))

        # ==========================================
        # 2. TARJETA PRINCIPAL DEL FORMULARIO
        # ==========================================
        self.form_card = ctk.CTkFrame(self.scroll_container, corner_radius=12, fg_color=("#ffffff", "#1e293b"))
        self.form_card.pack(fill="x", pady=(0, 15), padx=5)

        # Configuración de 2 columnas proporcionales
        self.form_card.grid_columnconfigure(0, weight=1)
        self.form_card.grid_columnconfigure(1, weight=1)

        # --- COLUMNA IZQUIERDA: Tiempo y Capacidad ---
        self.col_left = ctk.CTkFrame(self.form_card, fg_color="transparent")
        self.col_left.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Día
        ctk.CTkLabel(self.col_left, text="📅 Día de la Semana:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.combo_dia = ctk.CTkComboBox(
            self.col_left,
            values=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"],
            state="readonly",
            height=34
        )
        self.combo_dia.set("Lunes")
        self.combo_dia.pack(fill="x", pady=(0, 12))

        # Hora Inicio
        ctk.CTkLabel(self.col_left, text="⏰ Hora de Inicio:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.combo_h_inicio = ctk.CTkComboBox(
            self.col_left, 
            values=["07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"],
            height=34
        )
        self.combo_h_inicio.set("08:00")
        self.combo_h_inicio.pack(fill="x", pady=(0, 12))

        # Hora Fin
        ctk.CTkLabel(self.col_left, text="⏳ Hora de Fin:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.combo_h_fin = ctk.CTkComboBox(
            self.col_left,
            values=["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"],
            height=34
        )
        self.combo_h_fin.set("10:00")
        self.combo_h_fin.pack(fill="x", pady=(0, 12))

        # Número de Estudiantes
        ctk.CTkLabel(self.col_left, text="👥 Estudiantes en el Curso (Aforo):", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.entry_estudiantes = ctk.CTkEntry(
            self.col_left,
            placeholder_text="Ej. 30",
            height=34
        )
        self.entry_estudiantes.insert(0, "30")
        self.entry_estudiantes.pack(fill="x", pady=(0, 5))

        # Indicador de aforo
        self.lbl_info_aforo = ctk.CTkLabel(
            self.col_left,
            text="ℹ️ Capacidad estimada: Pendiente de seleccionar aula",
            font=("Arial", 11),
            text_color="#94a3b8"
        )
        self.lbl_info_aforo.pack(anchor="w")

        # --- COLUMNA DERECHA: Asignación Académica ---
        self.col_right = ctk.CTkFrame(self.form_card, fg_color="transparent")
        self.col_right.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Docente
        ctk.CTkLabel(self.col_right, text="👨‍🏫 Docente:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.combo_docente = ctk.CTkComboBox(
            self.col_right,
            values=["Cargando docentes..."],
            height=34
        )
        self.combo_docente.pack(fill="x", pady=(0, 12))

        # Aula
        ctk.CTkLabel(self.col_right, text="🏢 Aula Asignada:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.combo_aula = ctk.CTkComboBox(
            self.col_right,
            values=["Cargando aulas..."],
            height=34,
            command=self.al_seleccionar_aula
        )
        self.combo_aula.pack(fill="x", pady=(0, 12))

        # Materia
        ctk.CTkLabel(self.col_right, text="📚 Materia / Asignatura:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.combo_materia = ctk.CTkComboBox(
            self.col_right,
            values=["Cargando materias..."],
            height=34
        )
        self.combo_materia.pack(fill="x", pady=(0, 12))

        # Curso
        ctk.CTkLabel(self.col_right, text="🎓 Curso / Paralelo:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.combo_curso = ctk.CTkComboBox(
            self.col_right,
            values=["Cargando cursos..."],
            height=34
        )
        self.combo_curso.pack(fill="x", pady=(0, 12))

        # --- PIE DEL FORMULARIO: Botón y Notificación ---
        self.action_frame = ctk.CTkFrame(self.form_card, fg_color="transparent")
        self.action_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")

        self.btn_crear = ctk.CTkButton(
            self.action_frame, 
            text="✨ Validar y Registrar Horario", 
            font=("Arial", 14, "bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            height=42,
            command=self.crear_horario
        )
        self.btn_crear.pack(fill="x", pady=(5, 5))
        
        self.lbl_mensaje = ctk.CTkLabel(self.action_frame, text="", font=("Arial", 12, "bold"))
        self.lbl_mensaje.pack(pady=4)

        # ==========================================
        # 3. LISTADO DE HORARIOS EXISTENTES
        # ==========================================
        self.tabla_frame = ctk.CTkFrame(self.scroll_container, corner_radius=12, fg_color=("#ffffff", "#1e293b"))
        self.tabla_frame.pack(fill="both", expand=True, pady=(5, 20), padx=5)

        ctk.CTkLabel(
            self.tabla_frame,
            text="📋 Horarios Registrados en el Sistema",
            font=("Arial", 15, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 5))

        self.textbox_horarios = ctk.CTkTextbox(
            self.tabla_frame,
            height=200,
            font=("Courier", 11)
        )
        self.textbox_horarios.pack(fill="both", expand=True, padx=20, pady=(5, 15))

        # Cargar datos desde Supabase
        self.cargar_datos_dinamicos()

    def al_seleccionar_aula(self, seleccion):
        """Actualiza el indicador de capacidad cuando se elige un aula"""
        aula_info = self.aulas_map.get(seleccion)
        if aula_info and "capacidad" in aula_info:
            cap = aula_info["capacidad"]
            self.lbl_info_aforo.configure(
                text=f"✅ Capacidad máxima del aula: {cap} estudiantes",
                text_color="#34d399"
            )
        else:
            self.lbl_info_aforo.configure(
                text="ℹ️ Capacidad estimada: Seleccionada manualmente",
                text_color="#94a3b8"
            )

    def cargar_datos_dinamicos(self):
        """Carga aulas, docentes, materias y cursos en los selectores desplegables"""
        self.lbl_mensaje.configure(text="Sincronizando listas con Supabase...", text_color="#38bdf8")

        # 1. Cargar Docentes
        docentes = HorarioController.obtener_docentes()
        self.docentes_map.clear()
        docentes_vals = []
        for d in docentes:
            label = f"{d.get('nombre', '')} {d.get('apellido', '')} - {d.get('especialidad', 'Docente')} [ID: {d.get('id')}]"
            self.docentes_map[label] = d.get('id')
            docentes_vals.append(label)
        if docentes_vals:
            self.combo_docente.configure(values=docentes_vals)
            self.combo_docente.set(docentes_vals[0])
        else:
            self.combo_docente.configure(values=["1 - Docente Predeterminado"])
            self.combo_docente.set("1 - Docente Predeterminado")
            self.docentes_map["1 - Docente Predeterminado"] = 1

        # 2. Cargar Aulas
        aulas = HorarioController.obtener_aulas()
        self.aulas_map.clear()
        aulas_vals = []
        for a in aulas:
            label = f"Aula {a.get('numero', '')} ({a.get('tipo', 'Aula')}) - Cap: {a.get('capacidad', 'N/A')} [ID: {a.get('id')}]"
            self.aulas_map[label] = {"id": a.get('id'), "capacidad": a.get('capacidad')}
            aulas_vals.append(label)
        if aulas_vals:
            self.combo_aula.configure(values=aulas_vals)
            self.combo_aula.set(aulas_vals[0])
            self.al_seleccionar_aula(aulas_vals[0])
        else:
            self.combo_aula.configure(values=["1 - Aula General"])
            self.combo_aula.set("1 - Aula General")
            self.aulas_map["1 - Aula General"] = {"id": 1, "capacidad": 40}

        # 3. Cargar Materias
        materias = HorarioController.obtener_materias()
        self.materias_map.clear()
        materias_vals = []
        for m in materias:
            label = f"{m.get('nombre', 'Materia')} [ID: {m.get('id')}]"
            self.materias_map[label] = m.get('id')
            materias_vals.append(label)
        self.combo_materia.configure(values=materias_vals)
        if materias_vals:
            self.combo_materia.set(materias_vals[0])

        # 4. Cargar Cursos
        cursos = HorarioController.obtener_cursos()
        self.cursos_map.clear()
        cursos_vals = []
        for c in cursos:
            label = f"{c.get('nombre', 'Curso')} [ID: {c.get('id')}]"
            self.cursos_map[label] = c.get('id')
            cursos_vals.append(label)
        self.combo_curso.configure(values=cursos_vals)
        if cursos_vals:
            self.combo_curso.set(cursos_vals[0])

        # 5. Cargar Horarios Registrados en el historial
        self.refrescar_historial_horarios()
        self.lbl_mensaje.configure(text="✅ Datos sincronizados correctamente.", text_color="#34d399")

    def refrescar_historial_horarios(self):
        """Muestra los horarios ya registrados en la base de datos con nombres legibles"""
        self.textbox_horarios.delete("0.0", "end")
        horarios = HorarioController.obtener_horarios_registrados()
        if not horarios:
            self.textbox_horarios.insert("end", "No hay horarios registrados en el sistema.\n")
            return

        # Mapeos rápidos para mostrar nombres en lugar de sólo IDs
        materias_lookup = {str(m.get("id")): m.get("nombre", "") for m in HorarioController.obtener_materias()}
        cursos_lookup = {str(c.get("id")): c.get("nombre", "") for c in HorarioController.obtener_cursos()}
        aulas_lookup = {str(a.get("id")): f"Aula {a.get('numero', a.get('id'))}" for a in HorarioController.obtener_aulas()}
        docentes_lookup = {str(d.get("id")): f"{d.get('nombre', '')} {d.get('apellido', '')}".strip() for d in HorarioController.obtener_docentes()}

        encabezado = f"{'DÍA':<10} | {'HORA':<13} | {'AULA':<12} | {'DOCENTE':<20} | {'MATERIA':<28} | {'CURSO':<18}\n"
        encabezado += "=" * 108 + "\n"
        self.textbox_horarios.insert("end", encabezado)

        for h in horarios:
            dia = str(h.get('dia', ''))[:10]
            h_ini = str(h.get('hora_inicio', ''))[:5]
            h_fin = str(h.get('hora_fin', ''))[:5]
            hora_str = f"{h_ini}-{h_fin}"
            
            aula_id = str(h.get('aula_id', ''))
            docente_id = str(h.get('docente_id', ''))
            materia_id = str(h.get('materia_id', ''))
            curso_id = str(h.get('curso_id', ''))

            aula_nom = aulas_lookup.get(aula_id, f"ID: {aula_id}")[:12]
            docente_nom = docentes_lookup.get(docente_id, f"ID: {docente_id}")[:20]
            materia_nom = materias_lookup.get(materia_id, f"ID: {materia_id}")[:28]
            curso_nom = cursos_lookup.get(curso_id, f"ID: {curso_id}")[:18]

            linea = f"{dia:<10} | {hora_str:<13} | {aula_nom:<12} | {docente_nom:<20} | {materia_nom:<28} | {curso_nom:<18}\n"
            self.textbox_horarios.insert("end", linea)

    def _resolver_id(self, valor, mapa):
        """Extrae el ID entero ya sea del mapa de opciones o de un número ingresado directamente"""
        if valor in mapa:
            res = mapa[valor]
            return res["id"] if isinstance(res, dict) else res
        # Si el usuario escribió directamente un número o un texto tipo 'ID: 5'
        val_str = str(valor).strip()
        if val_str.isdigit():
            return int(val_str)
        if "[ID:" in val_str:
            try:
                sub = val_str.split("[ID:")[1].split("]")[0].strip()
                return int(sub)
            except Exception:
                pass
        return None

    def crear_horario(self):
        dia = self.combo_dia.get()
        h_inicio = self.combo_h_inicio.get().strip()
        h_fin = self.combo_h_fin.get().strip()
        sel_docente = self.combo_docente.get()
        sel_aula = self.combo_aula.get()
        sel_materia = self.combo_materia.get()
        sel_curso = self.combo_curso.get()
        str_estudiantes = self.entry_estudiantes.get().strip()

        if not all([dia, h_inicio, h_fin, sel_docente, sel_aula, sel_materia, sel_curso, str_estudiantes]):
            self.lbl_mensaje.configure(text="⚠️ Por favor completa todos los campos del horario.", text_color="orange")
            return

        try:
            num_estudiantes = int(str_estudiantes)
            if num_estudiantes <= 0:
                self.lbl_mensaje.configure(text="⚠️ El número de estudiantes debe ser mayor a 0.", text_color="orange")
                return
        except ValueError:
            self.lbl_mensaje.configure(text="⚠️ La cantidad de estudiantes debe ser un número entero.", text_color="orange")
            return

        docente_id = self._resolver_id(sel_docente, self.docentes_map)
        aula_id = self._resolver_id(sel_aula, self.aulas_map)
        materia_id = self._resolver_id(sel_materia, self.materias_map)
        curso_id = self._resolver_id(sel_curso, self.cursos_map)

        if docente_id is None:
            self.lbl_mensaje.configure(text="⚠️ No se pudo determinar el ID del docente seleccionado.", text_color="red")
            return
        if aula_id is None:
            self.lbl_mensaje.configure(text="⚠️ No se pudo determinar el ID del aula seleccionada.", text_color="red")
            return
        if materia_id is None:
            self.lbl_mensaje.configure(text="⚠️ No se pudo determinar el ID de la materia seleccionada.", text_color="red")
            return
        if curso_id is None:
            self.lbl_mensaje.configure(text="⚠️ No se pudo determinar el ID del curso seleccionado.", text_color="red")
            return

        try:
            # Validación y creación en la base de datos a través del controlador
            exito, mensaje = HorarioController.validar_y_crear_horario(
                dia=dia,
                hora_inicio=h_inicio,
                hora_fin=h_fin,
                materia_id=int(materia_id),
                docente_id=int(docente_id),
                aula_id=int(aula_id),
                curso_id=int(curso_id),
                num_estudiantes=num_estudiantes
            )

            if exito:
                self.lbl_mensaje.configure(text=f"✅ {mensaje}", text_color="#34d399")
                self.refrescar_historial_horarios()
            else:
                self.lbl_mensaje.configure(text=f"❌ {mensaje}", text_color="#f87171")
        except Exception as e:
            self.lbl_mensaje.configure(text=f"❌ Error al procesar el horario: {e}", text_color="#f87171")