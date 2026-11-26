"""Filtros del historial sobre datos ya cargados, sin consultar la red."""

import unicodedata


def _normalizar(valor):
    texto = unicodedata.normalize("NFKD", str(valor or "").casefold())
    return "".join(letra for letra in texto if not unicodedata.combining(letra))


def filtrar_horarios(horarios, texto="", dia="Todos los días",
                     estado="Todos los estados", nombres=None):
    nombres = nombres or {}
    consulta = _normalizar(texto).strip()
    resultado = []
    for horario in horarios:
        if dia != "Todos los días" and horario.get("dia") != dia:
            continue
        if estado != "Todos los estados" and horario.get("estado", "Publicado") != estado:
            continue
        contenido = [horario.get("dia"), horario.get("estado", "Publicado"),
                     horario.get("hora_inicio"), horario.get("hora_fin")]
        for campo, mapa in nombres.items():
            identificador = horario.get(f"{campo}_id")
            contenido.append(mapa.get(str(identificador), ""))
        if consulta and consulta not in _normalizar(" ".join(map(str, contenido))):
            continue
        resultado.append(horario)
    return resultado
