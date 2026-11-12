import customtkinter as ctk
from conexion.supabase_client import SupabaseConnection
from patrones_creacionales_beeweek import CreadorEstudiante

class EstudianteView(ctk.CTkFrame):
    def __init__(self, master, db_client=None):
        super().__init__(master, fg_color="transparent")
        self.db = db_client if db_client is not None else SupabaseConnection.get_client()
        self.creador_estudiante = CreadorEstudiante()

        ctk.CTkLabel(
            self, text="Gestión de Estudiantes", font=("Arial", 22, "bold")
        ).pack(anchor="w", padx=30, pady=(22, 15))

        contenido = ctk.CTkFrame(self, fg_color="transparent")
        contenido.pack(fill="both", expand=True, padx=30, pady=(0, 25))
        formulario = ctk.CTkFrame(contenido, width=340, corner_radius=10)
        formulario.pack(side="left", fill="y", padx=(0, 15))
        formulario.pack_propagate(False)
        listado = ctk.CTkFrame(contenido, corner_radius=10)
        listado.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            formulario, text="Registrar estudiante", font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=18, pady=(18, 10))

        for atributo, ejemplo in (
            ("entry_identificacion", "Identificación / Cédula"),
            ("entry_nombre", "Nombre"),
            ("entry_apellido", "Apellido"),
            ("entry_email", "Correo electrónico"),
            ("entry_matricula", "Número de matrícula"),
            ("entry_carrera", "Carrera"),
        ):
            entrada = ctk.CTkEntry(formulario, placeholder_text=ejemplo, height=34)
            entrada.pack(fill="x", padx=18, pady=5)
            setattr(self, atributo, entrada)

        self.cursos_map = {}
        self.combo_curso = ctk.CTkOptionMenu(formulario, values=["Sin curso"])
        self.combo_curso.pack(fill="x", padx=18, pady=5)

        self.btn_guardar = ctk.CTkButton(
            formulario, text="Guardar estudiante", command=self.guardar_estudiante
        )
        self.btn_guardar.pack(fill="x", padx=18, pady=(12, 5))
        self.lbl_mensaje = ctk.CTkLabel(
            formulario, text="", font=("Arial", 11), wraplength=290
        )
        self.lbl_mensaje.pack(fill="x", padx=18, pady=(0, 12))
        self.cargar_cursos()

        ctk.CTkLabel(
            listado, text="Estudiantes registrados", font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=18, pady=(18, 10))
        self.textbox = ctk.CTkTextbox(listado, font=("Courier", 11))
        self.textbox.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.cargar_estudiantes()

    def cargar_cursos(self):
        try:
            cursos = self.db.table("cursos").select("id,paralelo").execute().data or []
            self.cursos_map = {
                f"{curso['paralelo']} (ID {curso['id']})": curso["id"]
                for curso in cursos
            }
            self.combo_curso.configure(values=["Sin curso", *self.cursos_map])
            self.combo_curso.set("Sin curso")
        except Exception:
            self.cursos_map = {}
            self.combo_curso.configure(values=["Sin curso"])
            self.combo_curso.set("Sin curso")
            self.lbl_mensaje.configure(
                text="No se pudieron cargar los cursos. Puedes registrar sin curso o intentar de nuevo.",
                text_color="#b42333",
            )

    def cargar_datos_dinamicos(self):
        self.cargar_cursos()
        self.cargar_estudiantes()

    def guardar_estudiante(self):
        identificacion = self.entry_identificacion.get().strip()
        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        email = self.entry_email.get().strip()
        matricula = self.entry_matricula.get().strip()
        carrera = self.entry_carrera.get().strip()
        curso_id = self.cursos_map.get(self.combo_curso.get())
        
        if not identificacion or not nombre or not apellido or not email or not matricula or not carrera:
            self.lbl_mensaje.configure(text="Por favor completa todos los campos.", text_color="orange")
            return
            
        try:
            self.creador_estudiante.registrar(
                identificacion=identificacion,
                nombre=nombre,
                apellido=apellido,
                email=email,
                matricula=matricula,
                carrera=carrera,
                curso_id=curso_id,
                db_client=self.db,
            )
            # Limpiar campos
            self.entry_identificacion.delete(0, 'end')
            self.entry_nombre.delete(0, 'end')
            self.entry_apellido.delete(0, 'end')
            self.entry_email.delete(0, 'end')
            self.entry_matricula.delete(0, 'end')
            self.entry_carrera.delete(0, 'end')
            self.combo_curso.set("Sin curso")
            if self.cargar_estudiantes():
                self.lbl_mensaje.configure(text="¡Estudiante guardado con éxito en la nube!", text_color="#15803d")
            else:
                self.lbl_mensaje.configure(
                    text="Estudiante guardado, pero no se pudo actualizar la lista. Vuelve a sincronizar.",
                    text_color="#9a6700",
                )
        except Exception as e:
            self.lbl_mensaje.configure(text=f"Error al guardar: {e}", text_color="#b42333")

    def cargar_estudiantes(self):
        self.textbox.delete("0.0", "end")
        try:
            respuesta = self.db.table("estudiantes").select("*").execute()
            estudiantes = respuesta.data or []
            if not estudiantes:
                self.textbox.insert("end", "No hay estudiantes registrados todavía.")
                return True
            cursos = self.db.table("cursos").select("id,paralelo").execute().data or []
            nombres_curso = {str(curso["id"]): curso["paralelo"] for curso in cursos}
            for estudiante in estudiantes:
                nombre = f"{estudiante.get('nombre', '')} {estudiante.get('apellido', '')}".strip()
                matricula = estudiante.get("matricula", "")
                carrera = estudiante.get("carrera", "")
                curso = nombres_curso.get(str(estudiante.get("curso_id")), "Sin curso")
                self.textbox.insert("end", f"{matricula:<14} | {nombre:<28} | {carrera} | {curso}\n")
            return True
        except Exception as error:
            self.textbox.insert("end", f"No se pudieron cargar los estudiantes: {error}")
            return False
