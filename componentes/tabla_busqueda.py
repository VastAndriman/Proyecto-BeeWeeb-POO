import tkinter as tk
from tkinter import ttk
import unicodedata

import customtkinter as ctk


def filtrar_registros(registros, campos, texto):
    def normalizar(valor):
        return "".join(
            letra for letra in unicodedata.normalize("NFD", str(valor).casefold())
            if not unicodedata.combining(letra)
        )

    consulta = normalizar(texto.strip())
    if not consulta:
        return list(registros)
    return [
        registro for registro in registros
        if consulta in normalizar(" ".join(str(registro.get(campo, "")) for campo in campos))
    ]


class TablaBusqueda(ctk.CTkFrame):
    """Tabla legible con búsqueda local; no vuelve a consultar la base al filtrar."""

    def __init__(self, master, columnas, *, on_select=None):
        super().__init__(master, fg_color="transparent")
        self.columnas = tuple(columnas)
        self.campos = tuple(campo for campo, _, _ in columnas)
        self.registros = []
        self.on_select = on_select
        self._error = None

        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", pady=(0, 9))
        self.buscar_var = tk.StringVar()
        ctk.CTkLabel(barra, text="Buscar:", text_color="#4b3f76").pack(side="left", padx=(0, 8))
        ctk.CTkEntry(
            barra, textvariable=self.buscar_var, placeholder_text="Buscar en la lista...",
            height=34,
        ).pack(side="left", fill="x", expand=True)
        self.contador = ctk.CTkLabel(barra, text="0 registros", text_color="#786f95")
        self.contador.pack(side="right", padx=(12, 0))

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "BeeWeek.Treeview", background="#ffffff", fieldbackground="#ffffff",
            foreground="#4b3f76", font=("Arial", 11), rowheight=32, borderwidth=0,
        )
        estilo.configure(
            "BeeWeek.Treeview.Heading", background="#e8e1fb", foreground="#4b3f76",
            font=("Arial", 11, "bold"), relief="flat",
        )
        estilo.map("BeeWeek.Treeview", background=[("selected", "#d6c9f3")],
                   foreground=[("selected", "#4b3f76")])

        cuerpo = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8)
        cuerpo.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(
            cuerpo, columns=self.campos, show="headings", selectmode="browse",
            style="BeeWeek.Treeview",
        )
        for campo, titulo, ancho in columnas:
            self.tree.heading(campo, text=titulo)
            self.tree.column(campo, width=ancho, minwidth=70, stretch=True)
        scrollbar = ttk.Scrollbar(cuerpo, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side="right", fill="y", padx=(0, 8), pady=8)
        self.tree.bind("<<TreeviewSelect>>", self._seleccionar)

        self.aviso = ctk.CTkLabel(self, text="", text_color="#786f95", anchor="w")
        self.aviso.pack(fill="x", pady=(6, 0))
        self.buscar_var.trace_add("write", lambda *_: self._mostrar())

    def set_rows(self, registros):
        self.registros = list(registros)
        self._error = None
        self._mostrar()

    def set_error(self, mensaje):
        self.registros = []
        self._error = mensaje
        self._mostrar()

    def _mostrar(self):
        self.tree.delete(*self.tree.get_children())
        encontrados = filtrar_registros(self.registros, self.campos, self.buscar_var.get())
        for indice, registro in enumerate(encontrados):
            self.tree.insert("", "end", iid=str(indice),
                             values=[registro.get(campo, "") for campo in self.campos])
        self._visibles = encontrados
        self.contador.configure(text=f"{len(encontrados)} registro(s)")
        if self._error:
            self.aviso.configure(text=self._error, text_color="#b42333")
        else:
            self.aviso.configure(
                text="" if encontrados else (
                    "No hay registros todavía." if not self.registros else "No hay coincidencias."
                ),
                text_color="#786f95",
            )

    def _seleccionar(self, _evento):
        if not self.on_select:
            return
        seleccion = self.tree.selection()
        if seleccion:
            self.on_select(self._visibles[int(seleccion[0])])
