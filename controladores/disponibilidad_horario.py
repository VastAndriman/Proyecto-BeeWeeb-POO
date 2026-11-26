"""Vista previa local; Supabase conserva la validación definitiva al guardar."""

from datetime import time


def evaluar_disponibilidad(*, dia, inicio, fin, aula_id, docente_id, curso_id,
                           estudiantes, capacidad, horarios, estado="Publicado",
                           excluir_id=None):
    try:
        inicio_h = time.fromisoformat(str(inicio).strip())
        fin_h = time.fromisoformat(str(fin).strip())
        cantidad = int(estudiantes)
        aforo = int(capacidad)
    except (TypeError, ValueError):
        return False, "Selecciona horas, aula y curso válidos."
    if inicio_h >= fin_h:
        return False, "La hora de fin debe ser posterior a la de inicio."
    if cantidad <= 0 or cantidad > aforo:
        return False, f"Aforo insuficiente: {cantidad} estudiantes para {aforo} puestos."
    if estado == "Cancelado":
        return False, "Un horario cancelado no se puede editar."
    if estado == "Borrador":
        return True, "Borrador: el cruce se comprobará al publicarlo."
    for horario in horarios:
        if horario.get("dia") != dia or horario.get("estado", "Publicado") != "Publicado":
            continue
        if excluir_id is not None and str(horario.get("id")) == str(excluir_id):
            continue
        try:
            otro_inicio = time.fromisoformat(str(horario.get("hora_inicio")))
            otro_fin = time.fromisoformat(str(horario.get("hora_fin")))
        except (TypeError, ValueError):
            continue
        if not (inicio_h < otro_fin and otro_inicio < fin_h):
            continue
        for campo, valor, nombre in (
            ("docente_id", docente_id, "docente"),
            ("aula_id", aula_id, "aula"),
            ("curso_id", curso_id, "curso"),
        ):
            if valor is not None and str(horario.get(campo)) == str(valor):
                return False, f"Cruce: el {nombre} ya tiene una clase en ese horario."
    return True, "Disponible según los datos cargados. Se validará al guardar."
