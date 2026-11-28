from datetime import date


class AsistenciaController:
    ESTADOS = ("Presente", "Ausente", "Atrasado", "Justificado")

    def __init__(self, db_client):
        self.db = db_client

    @staticmethod
    def validar_fecha(fecha):
        try:
            valor = date.fromisoformat(fecha)
        except (TypeError, ValueError):
            raise ValueError("Escribe la fecha en formato AAAA-MM-DD") from None
        if valor > date.today():
            raise ValueError("No se puede registrar asistencia futura")
        return fecha

    def lista(self, horario_id, fecha):
        return self.db.lista_asistencia(horario_id, self.validar_fecha(fecha))

    def clases_docente(self):
        return self.db.mis_clases_docente()

    def guardar(self, horario_id, fecha, registros):
        self.validar_fecha(fecha)
        if not registros or any(r.get("estado") not in self.ESTADOS for r in registros):
            raise ValueError("Marca un estado válido para cada estudiante")
        return self.db.guardar_asistencia(horario_id, fecha, registros)

    def estudiante(self):
        return self.db.mi_asistencia()

    def administrador(self):
        return self.db.resumen_asistencia()
