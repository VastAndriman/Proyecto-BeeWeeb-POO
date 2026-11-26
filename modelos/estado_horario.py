"""State: las acciones disponibles dependen del estado del horario."""


class EstadoHorario:
    nombre = ""
    transiciones = ()

    def puede_editar(self):
        return True

    def visible_en_calendario(self):
        return False

    def cambiar_a(self, destino):
        if destino not in self.transiciones:
            raise ValueError(f"No se puede pasar de {self.nombre} a {destino}.")
        return estado_horario(destino)


class Borrador(EstadoHorario):
    nombre = "Borrador"
    transiciones = ("Publicado", "Cancelado")


class Publicado(EstadoHorario):
    nombre = "Publicado"
    transiciones = ("Cancelado",)

    def visible_en_calendario(self):
        return True


class Cancelado(EstadoHorario):
    nombre = "Cancelado"

    def puede_editar(self):
        return False


ESTADOS = {estado.nombre: estado for estado in (Borrador(), Publicado(), Cancelado())}


def estado_horario(nombre):
    try:
        return ESTADOS[nombre]
    except KeyError:
        raise ValueError("Estado de horario no válido.") from None
