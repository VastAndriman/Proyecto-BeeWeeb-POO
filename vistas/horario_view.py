import customtkinter as ctk
from controladores.horario_controller import HorarioController

class HorarioView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # Título de la vista
        self.titulo = ctk.CTkLabel(self, text="Gestión y Validación de Horarios", font=("Arial", 20, "bold"))
        self.titulo.pack(pady=15)
        
        # Campos de entrada para el horario
        self.entry_dia = ctk.CTkEntry(self, placeholder_text="Día (ej. Lunes)")
        self.entry_dia.pack(pady=5)
        
        self.entry_h_inicio = ctk.CTkEntry(self, placeholder_text="Hora Inicio (ej. 08:00:00)")
        self.entry_h_inicio.pack(pady=5)
        
        self.entry_h_fin = ctk.CTkEntry(self, placeholder_text="Hora Fin (ej. 10:00:00)")
        self.entry_h_fin.pack(pady=5)
        
        self.entry_materia = ctk.CTkEntry(self, placeholder_text="ID Materia")
        self.entry_materia.pack(pady=5)
        
        self.entry_docente = ctk.CTkEntry(self, placeholder_text="ID Docente")
        self.entry_docente.pack(pady=5)
        
        self.entry_aula = ctk.CTkEntry(self, placeholder_text="ID Aula")
        self.entry_aula.pack(pady=5)
        
        self.entry_curso = ctk.CTkEntry(self, placeholder_text="ID Curso")
        self.entry_curso.pack(pady=5)
        
        self.entry_estudiantes = ctk.CTkEntry(self, placeholder_text="Num. Estudiantes (Aforo)")
        self.entry_estudiantes.pack(pady=5)
        
        # Botón para validar y guardar
        self.btn_crear = ctk.CTkButton(self, text="Validar y Crear Horario", command=self.crear_horario)
        self.btn_crear.pack(pady=15)
        
        # Etiqueta de mensajes de retroalimentación
        self.lbl_mensaje = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.lbl_mensaje.pack(pady=5)

    def crear_horario(self):
        dia = self.entry_dia.get()
        h_inicio = self.entry_h_inicio.get()
        h_fin = self.entry_h_fin.get()
        materia_id = self.entry_materia.get()
        docente_id = self.entry_docente.get()
        aula_id = self.entry_aula.get()
        curso_id = self.entry_curso.get()
        num_estudiantes = self.entry_estudiantes.get()
        
        if not all([dia, h_inicio, h_fin, materia_id, docente_id, aula_id, curso_id, num_estudiantes]):
            self.lbl_mensaje.configure(text="Por favor completa todos los campos.", text_color="orange")
            return
            
        try:
            # Llamamos al controlador que evalúa los cruces y el aforo automáticamente
            exito, mensaje = HorarioController.validar_y_crear_horario(
                dia=dia,
                hora_inicio=h_inicio,
                hora_fin=h_fin,
                materia_id=int(materia_id),
                docente_id=int(docente_id),
                aula_id=int(aula_id),
                curso_id=int(curso_id),
                num_estudiantes=int(num_estudiantes)
            )
            
            if exito:
                self.lbl_mensaje.configure(text=mensaje, text_color="green")
            else:
                self.lbl_mensaje.configure(text=mensaje, text_color="red")
        except Exception as e:
            self.lbl_mensaje.configure(text=f"Error: {e}", text_color="red")