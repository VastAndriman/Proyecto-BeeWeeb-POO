import customtkinter as ctk
from tkinter import messagebox
from controladores.horario_controller import HorarioController

class HorarioView(ctk.CTkFrame):
    def __init__(self, master, horario_controller=None):
        super().__init__(master, fg_color="transparent")
        self.horario_controller = horario_controller if horario_controller is not None else HorarioController()
        
        # Mapeos internos de etiquetas legibles a IDs
        self.docentes_map = {}
        self.aulas_map = {}
        self.materias_map = {}
        self.cursos_map = {}
        self.horarios_map = {}
        self.historial_disponible = False
        self._materias_lookup = {}
        self._cursos_lookup = {}
        self._aulas_lookup = {}
        self._docentes_lookup = {}

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
            text="Gestión y Validación de Horarios",
            font=("Arial", 22, "bold")
        )
        self.titulo.pack(side="left")

        self.btn_recargar = ctk.CTkButton(
            self.header_frame,
            text="Actualizar Opciones",
            width=160,
            fg_color="#7256ac",
            hover_color="#5e4497",
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
        self.form_card = ctk.CTkFrame(self.scroll_container, corner_radius=12, fg_color="#ffffff")
        self.form_card.pack(fill="x", pady=(0, 15), padx=5)
        ctk.CTkLabel(
            self.form_card, text="Nuevo horario", font=("Arial", 16, "bold"),
            text_color="#4b3f76",
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 0), sticky="w")

        # Configuración de 2 columnas proporcionales
        self.form_card.grid_columnconfigure(0, weight=1)
        self.form_card.grid_columnconfigure(1, weight=1)

        # --- COLUMNA IZQUIERDA: Tiempo y Capacidad ---
        self.col_left = ctk.CTkFrame(self.form_card, fg_color="transparent")
        self.col_left.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        # Día
        ctk.CTkLabel(self.col_left, text="Día de la Semana:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.combo_dia = ctk.CTkComboBox(
            self.col_left,
            values=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"],
            state="readonly",
            height=34
        )
        self.combo_dia.set("Lunes")
        self.combo_dia.pack(fill="x", pady=(0, 12))

        # Hora Inicio
        ctk.CTkLabel(self.col_left, text="Hora de Inicio:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.combo_h_inicio = ctk.CTkComboBox(
            self.col_left, 
            values=["07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"],
            height=34
        )
        self.combo_h_inicio.set("08:00")
        self.combo_h_inicio.pack(fill="x", pady=(0, 12))

        # Hora Fin
        ctk.CTkLabel(self.col_left, text="Hora de Fin:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.combo_h_fin = ctk.CTkComboBox(
            self.col_left,
            values=["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"],
            height=34
        )
        self.combo_h_fin.set("10:00")
        self.combo_h_fin.pack(fill="x", pady=(0, 12))

        # Número de Estudiantes
        ctk.CTkLabel(self.col_left, text="Estudiantes en el Curso (Aforo):", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.entry_estudiantes = ctk.CTkEntry(
            self.col_left,
            placeholder_text="Selecciona un curso",
            height=34,
            state="readonly"
        )
        self.entry_estudiantes.pack(fill="x", pady=(0, 5))

        # Indicador de aforo
        self.lbl_info_aforo = ctk.CTkLabel(
            self.col_left,
            text="Capacidad estimada: Pendiente de seleccionar aula",
            font=("Arial", 11),
            text_color="#786f95"
        )
        self.lbl_info_aforo.pack(anchor="w")

        # --- COLUMNA DERECHA: Asignación Académica ---
        self.col_right = ctk.CTkFrame(self.form_card, fg_color="transparent")
        self.col_right.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")

        # Docente
        ctk.CTkLabel(self.col_right, text="Docente:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.combo_docente = ctk.CTkComboBox(
            self.col_right,
            values=["Cargando docentes..."],
            height=34
        )
        self.combo_docente.pack(fill="x", pady=(0, 12))

        # Aula
        ctk.CTkLabel(self.col_right, text="Aula Asignada:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.combo_aula = ctk.CTkComboBox(
            self.col_right,
            values=["Cargando aulas..."],
            height=34,
            command=self.al_seleccionar_aula
        )
        self.combo_aula.pack(fill="x", pady=(0, 12))

        # Materia
        ctk.CTkLabel(self.col_right, text="Materia / Asignatura:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.combo_materia = ctk.CTkComboBox(
            self.col_right,
            values=["Cargando materias..."],
            height=34
        )
        self.combo_materia.pack(fill="x", pady=(0, 12))

        # Curso
        ctk.CTkLabel(self.col_right, text="Curso / Paralelo:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.combo_curso = ctk.CTkComboBox(
            self.col_right,
            values=["Cargando cursos..."],
            height=34,
            command=self.al_seleccionar_curso
        )
        self.combo_curso.pack(fill="x", pady=(0, 12))

        # --- PIE DEL FORMULARIO: Botón y Notificación ---
        self.action_frame = ctk.CTkFrame(self.form_card, fg_color="transparent")
        self.action_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")

        self.btn_crear = ctk.CTkButton(
            self.action_frame, 
            text="Validar y Registrar Horario",
            font=("Arial", 14, "bold"),
            fg_color="#7256ac",
            hover_color="#5e4497",
            height=42,
            command=self.crear_horario
        )
        self.btn_crear.pack(fill="x", pady=(5, 5))

        self.edit_card = ctk.CTkFrame(self.scroll_container, corner_radius=12, fg_color="#ffffff")
        self.edit_card.pack(fill="x", pady=(0, 12), padx=5)
        ctk.CTkLabel(
            self.edit_card, text="Editar o eliminar un horario", font=("Arial", 16, "bold"),
            text_color="#4b3f76",
        ).pack(anchor="w", padx=20, pady=(15, 3))
        ctk.CTkLabel(
            self.edit_card, text="Selecciona uno para cargar sus datos en el formulario de arriba.",
            text_color="#786f95", font=("Arial", 12),
        ).pack(anchor="w", padx=20, pady=(0, 8))
        self.combo_horario = ctk.CTkOptionMenu(
            self.edit_card,
            values=["Selecciona un horario para editar o eliminar"],
            command=self.seleccionar_horario,
            fg_color="#7256ac",
        )
        self.combo_horario.pack(fill="x", padx=20, pady=(0, 8))
        self.combo_horario.set("Selecciona un horario para editar o eliminar")
        botones_edicion = ctk.CTkFrame(self.edit_card, fg_color="transparent")
        botones_edicion.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkButton(botones_edicion, text="Guardar cambios", command=self.actualizar_horario,
                      fg_color="#7256ac").pack(side="left", padx=(0, 8))
        ctk.CTkButton(botones_edicion, text="Eliminar horario", command=self.eliminar_horario,
                      fg_color="#b42333", hover_color="#8b1c2a").pack(side="left")
        ctk.CTkButton(
            botones_edicion, text="Dejar de editar", command=self.dejar_de_editar,
            fg_color="#eee9fb", hover_color="#d6c9f3", text_color="#4b3f76",
        ).pack(side="left", padx=(8, 0))
        
        self.lbl_mensaje = ctk.CTkLabel(self.scroll_container, text="", font=("Arial", 12, "bold"))
        self.lbl_mensaje.pack(pady=(0, 8))

        # ==========================================
        # 3. LISTADO DE HORARIOS EXISTENTES
        # ==========================================
        self.tabla_frame = ctk.CTkFrame(self.scroll_container, corner_radius=12, fg_color="#ffffff")
        self.tabla_frame.pack(fill="both", expand=True, pady=(5, 20), padx=5)

        ctk.CTkLabel(
            self.tabla_frame,
            text="Horarios Registrados en el Sistema",
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
                text=f"Capacidad máxima del aula: {cap} estudiantes",
                text_color="#15803d"
            )
        else:
            self.lbl_info_aforo.configure(
                text="Selecciona un aula registrada para conocer su capacidad",
                text_color="#786f95"
            )

    def al_seleccionar_curso(self, seleccion):
        """Muestra la matrícula guardada del curso sin permitir cambiarla aquí."""
        info = self.cursos_map.get(seleccion, {})
        self.entry_estudiantes.configure(state="normal")
        self.entry_estudiantes.delete(0, "end")
        if info.get("num_estudiantes") is not None:
            self.entry_estudiantes.insert(0, str(info["num_estudiantes"]))
        self.entry_estudiantes.configure(state="readonly")

    def cargar_datos_dinamicos(self):
        """Carga aulas, docentes, materias y cursos en los selectores desplegables"""
        self.historial_disponible = False
        self.lbl_mensaje.configure(text="Sincronizando listas con Supabase...", text_color="#7256ac")

        try:
            docentes = self.horario_controller.obtener_docentes(estricto=True)
            aulas = self.horario_controller.obtener_aulas(estricto=True)
            materias = self.horario_controller.obtener_materias(estricto=True)
            cursos = self.horario_controller.obtener_cursos(estricto=True)
        except Exception:
            self._materias_lookup = {}
            self._cursos_lookup = {}
            self._aulas_lookup = {}
            self._docentes_lookup = {}
            for mapa in (self.docentes_map, self.aulas_map, self.materias_map,
                         self.cursos_map, self.horarios_map):
                mapa.clear()
            for combo, aviso in (
                (self.combo_docente, "Sin docentes cargados"),
                (self.combo_aula, "Sin aulas cargadas"),
                (self.combo_materia, "Sin materias cargadas"),
                (self.combo_curso, "Sin cursos cargados"),
                (self.combo_horario, "Selecciona un horario para editar o eliminar"),
            ):
                combo.configure(values=[aviso])
                combo.set(aviso)
            self.al_seleccionar_aula("")
            self.al_seleccionar_curso("")
            self.textbox_horarios.delete("0.0", "end")
            self.textbox_horarios.insert("end", "No se pudieron cargar los horarios.")
            self.btn_crear.configure(state="disabled")
            self.lbl_mensaje.configure(
                text="No se pudieron sincronizar los datos. Revisa tu conexión y pulsa Actualizar Opciones.",
                text_color="#b42333",
            )
            return

        # Reutiliza estas listas al dibujar el historial; evita cuatro consultas extra.
        self._materias_lookup = {str(m.get("id")): m.get("nombre", "") for m in materias}
        self._cursos_lookup = {str(c.get("id")): c.get("nombre", "") for c in cursos}
        self._aulas_lookup = {
            str(a.get("id")): f"Aula {a.get('numero', a.get('id'))}" for a in aulas
        }
        self._docentes_lookup = {
            str(d.get("id")): f"{d.get('nombre', '')} {d.get('apellido', '')}".strip()
            for d in docentes
        }

        # 1. Cargar Docentes
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
            self.combo_docente.configure(values=["Sin docentes registrados"])
            self.combo_docente.set("Sin docentes registrados")

        # 2. Cargar Aulas
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
            self.combo_aula.configure(values=["Sin aulas registradas"])
            self.combo_aula.set("Sin aulas registradas")
            self.al_seleccionar_aula("")

        # 3. Cargar Materias
        self.materias_map.clear()
        materias_vals = []
        for m in materias:
            label = f"{m.get('nombre', 'Materia')} [ID: {m.get('id')}]"
            self.materias_map[label] = m.get('id')
            materias_vals.append(label)
        self.combo_materia.configure(values=materias_vals or ["Sin materias registradas"])
        if materias_vals:
            self.combo_materia.set(materias_vals[0])
        else:
            self.combo_materia.set("Sin materias registradas")

        # 4. Cargar Cursos
        self.cursos_map.clear()
        cursos_vals = []
        for c in cursos:
            label = f"{c.get('nombre', 'Curso')} [ID: {c.get('id')}]"
            self.cursos_map[label] = {
                "id": c.get('id'), "num_estudiantes": c.get('num_estudiantes')
            }
            cursos_vals.append(label)
        self.combo_curso.configure(values=cursos_vals or ["Sin cursos registrados"])
        if cursos_vals:
            self.combo_curso.set(cursos_vals[0])
            self.al_seleccionar_curso(cursos_vals[0])
        else:
            self.combo_curso.set("Sin cursos registrados")
            self.al_seleccionar_curso("")

        # 5. Cargar Horarios Registrados en el historial
        historial_ok = self.refrescar_historial_horarios()
        faltantes = [nombre for nombre, opciones in (
            ("docentes", docentes_vals), ("aulas", aulas_vals),
            ("materias", materias_vals), ("cursos", cursos_vals)
        ) if not opciones]
        self.btn_crear.configure(state="disabled" if faltantes or not historial_ok else "normal")
        if not historial_ok:
            self.lbl_mensaje.configure(
                text="No se pudo cargar el historial de horarios. Revisa tu conexión y pulsa Actualizar Opciones.",
                text_color="#b42333",
            )
        elif faltantes:
            self.lbl_mensaje.configure(
                text="Faltan datos reales: " + ", ".join(faltantes) + ".",
                text_color="orange"
            )
        else:
            self.lbl_mensaje.configure(text="Datos sincronizados correctamente.", text_color="#15803d")

    def refrescar_historial_horarios(self):
        """Muestra los horarios ya registrados en la base de datos con nombres legibles"""
        self.historial_disponible = False
        self.textbox_horarios.delete("0.0", "end")
        self.horarios_map = {}
        aviso = "Selecciona un horario para editar o eliminar"
        self.combo_horario.configure(values=[aviso])
        self.combo_horario.set(aviso)
        try:
            horarios = self.horario_controller.obtener_horarios_registrados(estricto=True)
        except Exception:
            self.textbox_horarios.insert("end", "No se pudo cargar el historial de horarios.\n")
            return False
        self.horarios_map = {
            f"ID {h['id']} · {h.get('dia', '')} {str(h.get('hora_inicio', ''))[:5]}-{str(h.get('hora_fin', ''))[:5]}": h
            for h in horarios if h.get("id") is not None
        }
        self.combo_horario.configure(values=list(self.horarios_map) or ["Selecciona un horario para editar o eliminar"])
        self.combo_horario.set("Selecciona un horario para editar o eliminar")
        self.historial_disponible = True
        if not horarios:
            self.textbox_horarios.insert("end", "No hay horarios registrados en el sistema.\n")
            return True

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

            aula_nom = self._aulas_lookup.get(aula_id, f"ID: {aula_id}")[:12]
            docente_nom = self._docentes_lookup.get(docente_id, f"ID: {docente_id}")[:20]
            materia_nom = self._materias_lookup.get(materia_id, f"ID: {materia_id}")[:28]
            curso_nom = self._cursos_lookup.get(curso_id, f"ID: {curso_id}")[:18]

            linea = f"{dia:<10} | {hora_str:<13} | {aula_nom:<12} | {docente_nom:<20} | {materia_nom:<28} | {curso_nom:<18}\n"
            self.textbox_horarios.insert("end", linea)
        return True

    def _resolver_id(self, valor, mapa):
        """Acepta únicamente una opción cargada desde la base de datos."""
        if valor in mapa:
            res = mapa[valor]
            return res["id"] if isinstance(res, dict) else res
        return None

    @staticmethod
    def _etiqueta_por_id(mapa, identificador):
        for etiqueta, valor in mapa.items():
            id_guardado = valor.get("id") if isinstance(valor, dict) else valor
            if str(id_guardado) == str(identificador):
                return etiqueta
        return None

    def seleccionar_horario(self, opcion):
        horario = self.horarios_map.get(opcion)
        if not horario:
            return
        self.btn_crear.configure(state="disabled")
        self.combo_dia.set(str(horario.get("dia", "Lunes")))
        self.combo_h_inicio.set(str(horario.get("hora_inicio", ""))[:5])
        self.combo_h_fin.set(str(horario.get("hora_fin", ""))[:5])
        for combo, mapa, campo in (
            (self.combo_docente, self.docentes_map, "docente_id"),
            (self.combo_aula, self.aulas_map, "aula_id"),
            (self.combo_materia, self.materias_map, "materia_id"),
            (self.combo_curso, self.cursos_map, "curso_id"),
        ):
            etiqueta = self._etiqueta_por_id(mapa, horario.get(campo))
            if etiqueta:
                combo.set(etiqueta)
        self.al_seleccionar_aula(self.combo_aula.get())
        self.al_seleccionar_curso(self.combo_curso.get())

    def dejar_de_editar(self):
        self.combo_horario.set("Selecciona un horario para editar o eliminar")
        self.combo_dia.set("Lunes")
        self.combo_h_inicio.set("08:00")
        self.combo_h_fin.set("10:00")
        for combo, mapa in (
            (self.combo_docente, self.docentes_map),
            (self.combo_aula, self.aulas_map),
            (self.combo_materia, self.materias_map),
            (self.combo_curso, self.cursos_map),
        ):
            if mapa:
                combo.set(next(iter(mapa)))
        self.al_seleccionar_aula(self.combo_aula.get())
        self.al_seleccionar_curso(self.combo_curso.get())
        listo = self.historial_disponible and all((
            self.docentes_map, self.aulas_map, self.materias_map, self.cursos_map
        ))
        self.btn_crear.configure(state="normal" if listo else "disabled")
        self.lbl_mensaje.configure(
            text=("Listo para registrar un horario nuevo." if listo else
                  "Actualiza las opciones antes de registrar un horario nuevo."),
            text_color="#7256ac" if listo else "#b42333",
        )

    def _datos_formulario(self):
        datos = {
            "dia": self.combo_dia.get(),
            "hora_inicio": self.combo_h_inicio.get().strip(),
            "hora_fin": self.combo_h_fin.get().strip(),
            "docente_id": self._resolver_id(self.combo_docente.get(), self.docentes_map),
            "aula_id": self._resolver_id(self.combo_aula.get(), self.aulas_map),
            "materia_id": self._resolver_id(self.combo_materia.get(), self.materias_map),
            "curso_id": self._resolver_id(self.combo_curso.get(), self.cursos_map),
        }
        if any(value is None or value == "" for value in datos.values()):
            raise ValueError("Completa todos los campos con opciones registradas.")
        return datos

    def _mostrar_resultado_horario(self, exito, mensaje):
        if not exito:
            self.lbl_mensaje.configure(text=f"{mensaje}", text_color="#b42333")
        elif self.refrescar_historial_horarios():
            self.lbl_mensaje.configure(text=f"{mensaje}", text_color="#15803d")
        else:
            self.lbl_mensaje.configure(
                text=f"{mensaje} No se pudo actualizar el historial; pulsa Actualizar Opciones.",
                text_color="#9a6700",
            )

    def actualizar_horario(self):
        horario = self.horarios_map.get(self.combo_horario.get())
        if not horario:
            self.lbl_mensaje.configure(text="Selecciona un horario.", text_color="orange")
            return
        try:
            exito, mensaje = self.horario_controller.actualizar_horario(
                int(horario["id"]), **self._datos_formulario())
            self._mostrar_resultado_horario(exito, mensaje)
        except Exception as error:
            self.lbl_mensaje.configure(text=f"No se pudo actualizar: {error}", text_color="#b42333")

    def eliminar_horario(self):
        horario = self.horarios_map.get(self.combo_horario.get())
        if not horario:
            self.lbl_mensaje.configure(text="Selecciona un horario.", text_color="orange")
            return
        if not messagebox.askyesno("Eliminar horario", "¿Eliminar el horario seleccionado?", parent=self):
            return
        try:
            exito, mensaje = self.horario_controller.eliminar_horario(int(horario["id"]))
            self._mostrar_resultado_horario(exito, mensaje)
        except Exception as error:
            self.lbl_mensaje.configure(text=f"No se pudo eliminar: {error}", text_color="#b42333")

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
            self.lbl_mensaje.configure(text="Por favor completa todos los campos del horario.", text_color="orange")
            return

        docente_id = self._resolver_id(sel_docente, self.docentes_map)
        aula_id = self._resolver_id(sel_aula, self.aulas_map)
        materia_id = self._resolver_id(sel_materia, self.materias_map)
        curso_id = self._resolver_id(sel_curso, self.cursos_map)

        if docente_id is None:
            self.lbl_mensaje.configure(text="No se pudo determinar el ID del docente seleccionado.", text_color="red")
            return
        if aula_id is None:
            self.lbl_mensaje.configure(text="No se pudo determinar el ID del aula seleccionada.", text_color="red")
            return
        if materia_id is None:
            self.lbl_mensaje.configure(text="No se pudo determinar el ID de la materia seleccionada.", text_color="red")
            return
        if curso_id is None:
            self.lbl_mensaje.configure(text="No se pudo determinar el ID del curso seleccionado.", text_color="red")
            return

        try:
            # Validación y creación en la base de datos a través del controlador
            exito, mensaje = self.horario_controller.validar_y_crear_horario(
                dia=dia,
                hora_inicio=h_inicio,
                hora_fin=h_fin,
                materia_id=int(materia_id),
                docente_id=int(docente_id),
                aula_id=int(aula_id),
                curso_id=int(curso_id)
            )

            self._mostrar_resultado_horario(exito, mensaje)
        except Exception as e:
            self.lbl_mensaje.configure(text=f"Error al procesar el horario: {e}", text_color="#b42333")
