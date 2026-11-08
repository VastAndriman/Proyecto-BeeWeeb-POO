from tkinter import messagebox

import customtkinter as ctk

from conexion.supabase_client import SupabaseConnection


class AulasView(ctk.CTkFrame):
    def __init__(self, master, db_client=None):
        super().__init__(master, fg_color="transparent")
        self.db = db_client if db_client is not None else SupabaseConnection.get_client()
        self.aulas_por_opcion = {}

        ctk.CTkLabel(self, text="Gestión de Aulas", font=("Arial", 22, "bold"),
                     text_color="#4b3f76").pack(anchor="w", padx=25, pady=(20, 8))
        formulario = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=12)
        formulario.pack(fill="x", padx=25, pady=(0, 12))
        for columna in range(3):
            formulario.grid_columnconfigure(columna, weight=1)

        for columna, titulo in enumerate(("Número", "Capacidad", "Tipo")):
            ctk.CTkLabel(formulario, text=titulo).grid(
                row=0, column=columna, padx=15, pady=(12, 0), sticky="w")
        self.entry_numero = ctk.CTkEntry(formulario, placeholder_text="Ej. 102")
        self.entry_capacidad = ctk.CTkEntry(formulario, placeholder_text="Ej. 40")
        self.entry_tipo = ctk.CTkEntry(formulario, placeholder_text="Ej. Laboratorio")
        for columna, entrada in enumerate((self.entry_numero, self.entry_capacidad, self.entry_tipo)):
            entrada.grid(row=1, column=columna, padx=15, pady=(3, 12), sticky="ew")

        self.selector = ctk.CTkOptionMenu(formulario, values=["Selecciona un aula"],
                                          command=self._seleccionar_aula)
        self.selector.grid(row=2, column=0, columnspan=3, padx=15, pady=(0, 10), sticky="ew")
        self.selector.set("Selecciona un aula")

        acciones = ctk.CTkFrame(formulario, fg_color="transparent")
        acciones.grid(row=3, column=0, columnspan=3, padx=15, pady=(0, 14), sticky="ew")
        for texto, accion in (("Añadir aula", self.crear_aula),
                              ("Guardar cambios", self.actualizar_aula),
                              ("Eliminar aula", self.eliminar_aula)):
            ctk.CTkButton(acciones, text=texto, command=accion, fg_color="#7256ac",
                          hover_color="#5e4497").pack(side="left", padx=(0, 8))

        self.mensaje = ctk.CTkLabel(self, text="", text_color="#4b3f76")
        self.mensaje.pack(anchor="w", padx=25)
        ctk.CTkButton(self, text="Actualizar lista", command=self.cargar_aulas,
                      fg_color="#7256ac").pack(anchor="w", padx=25, pady=(4, 8))
        self.textbox = ctk.CTkTextbox(self, font=("Courier", 12))
        self.textbox.pack(fill="both", expand=True, padx=25, pady=(0, 20))
        self.cargar_aulas()

    def _seleccionar_aula(self, opcion):
        aula = self.aulas_por_opcion.get(opcion)
        if not aula:
            return
        for entrada, valor in ((self.entry_numero, aula["numero"]),
                               (self.entry_capacidad, aula["capacidad"]),
                               (self.entry_tipo, aula["tipo"])):
            entrada.delete(0, "end")
            entrada.insert(0, str(valor))

    def _datos_formulario(self):
        numero = self.entry_numero.get().strip()
        tipo = self.entry_tipo.get().strip()
        try:
            capacidad = int(self.entry_capacidad.get().strip())
        except ValueError:
            raise ValueError("La capacidad debe ser un número entero.") from None
        if not numero or not tipo or capacidad <= 0:
            raise ValueError("Completa número y tipo; la capacidad debe ser mayor que cero.")
        return {"numero": numero, "capacidad": capacidad, "tipo": tipo}

    def _id_seleccionado(self):
        aula = self.aulas_por_opcion.get(self.selector.get())
        if not aula:
            raise ValueError("Selecciona un aula de la lista.")
        return aula["id"]

    def _mostrar_error(self, error):
        detalle = str(error)
        if "23505" in detalle:
            detalle = "Ya existe un aula con ese número."
        elif "23503" in detalle:
            detalle = "Esta aula está usada por un horario; elimina o cambia ese horario primero."
        self.mensaje.configure(text=f"❌ {detalle}", text_color="#b42333")

    def cargar_aulas(self):
        self.textbox.delete("0.0", "end")
        self.aulas_por_opcion = {}
        self.selector.configure(values=["Selecciona un aula"])
        self.selector.set("Selecciona un aula")
        try:
            aulas = self.db.table("aulas").select("*").execute().data or []
            self.aulas_por_opcion = {
                f"ID {aula['id']} · Aula {aula['numero']}": aula for aula in aulas
            }
            self.selector.configure(values=list(self.aulas_por_opcion) or ["Selecciona un aula"])
            self.selector.set("Selecciona un aula")
            if not aulas:
                self.textbox.insert("0.0", "No hay aulas registradas todavía.")
                return True
            lineas = [f"{'ID':<5} | {'NÚMERO':<10} | {'CAPACIDAD':<10} | {'TIPO':<15}", "-" * 50]
            lineas.extend(f"{a['id']:<5} | {a['numero']:<10} | {a['capacidad']:<10} | {a['tipo']:<15}"
                          for a in aulas)
            self.textbox.insert("0.0", "\n".join(lineas))
            return True
        except Exception as error:
            self._mostrar_error(error)
            return False

    def crear_aula(self):
        try:
            self.db.table("aulas").insert(self._datos_formulario()).execute()
            if self.cargar_aulas():
                self.mensaje.configure(text="✅ Aula añadida.", text_color="#15803d")
            else:
                self.mensaje.configure(
                    text="✅ Aula añadida, pero no se pudo actualizar la lista. Pulsa Actualizar lista.",
                    text_color="#9a6700",
                )
        except Exception as error:
            self._mostrar_error(error)

    def actualizar_aula(self):
        try:
            aula_id = self._id_seleccionado()
            self.db.table("aulas").update(self._datos_formulario()).eq("id", aula_id).execute()
            if self.cargar_aulas():
                self.mensaje.configure(text="✅ Aula actualizada.", text_color="#15803d")
            else:
                self.mensaje.configure(
                    text="✅ Aula actualizada, pero no se pudo actualizar la lista. Pulsa Actualizar lista.",
                    text_color="#9a6700",
                )
        except Exception as error:
            self._mostrar_error(error)

    def eliminar_aula(self):
        try:
            aula_id = self._id_seleccionado()
            if not messagebox.askyesno("Eliminar aula", "¿Eliminar el aula seleccionada?", parent=self):
                return
            self.db.table("aulas").delete().eq("id", aula_id).execute()
            if self.cargar_aulas():
                self.mensaje.configure(text="✅ Aula eliminada.", text_color="#15803d")
            else:
                self.mensaje.configure(
                    text="✅ Aula eliminada, pero no se pudo actualizar la lista. Pulsa Actualizar lista.",
                    text_color="#9a6700",
                )
        except Exception as error:
            self._mostrar_error(error)
