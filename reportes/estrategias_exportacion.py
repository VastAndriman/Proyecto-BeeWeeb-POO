"""Strategy: el mismo reporte se puede guardar en CSV o PDF."""

import csv
from abc import ABC, abstractmethod
from html import escape


class EstrategiaExportacion(ABC):
    @abstractmethod
    def guardar(self, ruta, columnas, filas):
        """Escribe el reporte en la ruta indicada."""


class ExportarCSV(EstrategiaExportacion):
    @staticmethod
    def _celda(valor):
        texto = "" if valor is None else str(valor)
        return "'" + texto if texto.lstrip().startswith(("=", "+", "-", "@")) else texto

    def guardar(self, ruta, columnas, filas):
        with open(ruta, "w", encoding="utf-8-sig", newline="") as archivo:
            escritor = csv.writer(archivo, delimiter=";")
            escritor.writerow(columnas)
            escritor.writerows([self._celda(valor) for valor in fila] for fila in filas)


class ExportarPDF(EstrategiaExportacion):
    def guardar(self, ruta, columnas, filas):
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import LongTable, Paragraph, SimpleDocTemplate, Spacer, TableStyle

        if not columnas:
            raise ValueError("El reporte no tiene columnas para exportar.")
        paginas = landscape(letter) if len(columnas) > 4 else letter
        documento = SimpleDocTemplate(
            str(ruta), pagesize=paginas, leftMargin=32, rightMargin=32,
            topMargin=38, bottomMargin=38,
        )
        estilos = getSampleStyleSheet()
        celda = ParagraphStyle(
            "BeeWeekCelda", parent=estilos["Normal"], fontName="Helvetica",
            fontSize=8.5, leading=11,
        )
        encabezado = ParagraphStyle(
            "BeeWeekEncabezado", parent=celda, fontName="Helvetica-Bold",
            textColor=colors.white,
        )

        def texto(valor, estilo):
            return Paragraph(escape("" if valor is None else str(valor)), estilo)

        datos = [[texto(valor, encabezado) for valor in columnas]]
        datos.extend([texto(valor, celda) for valor in fila] for fila in filas)
        ancho = documento.width / len(columnas)
        tabla = LongTable(datos, colWidths=[ancho] * len(columnas), repeatRows=1)
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4b3f76")),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d2cbe8")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#f3f0fb")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        documento.build([
            Paragraph("BeeWeek - Reporte institucional", estilos["Title"]),
            Spacer(1, 12), tabla,
        ])


class ExportadorReporte:
    def __init__(self, estrategia: EstrategiaExportacion):
        self.estrategia = estrategia

    def guardar(self, ruta, columnas, filas):
        self.estrategia.guardar(ruta, columnas, filas)


def guardar_csv(ruta, columnas, filas):
    """Compatibilidad con los usos existentes del exportador CSV."""
    ExportadorReporte(ExportarCSV()).guardar(ruta, columnas, filas)
