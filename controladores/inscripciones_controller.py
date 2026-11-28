class InscripcionesController:
    """Operaciones del alumno; la identidad y los permisos se validan en la base."""

    def __init__(self, db_client):
        self.db = db_client

    def catalogo(self):
        return self.db.catalogo_materias_estudiante()

    def inscribir(self, materia_id, curso_id):
        return self.db.inscribir_materia(materia_id, curso_id)

    def retirar(self, materia_id, curso_id):
        return self.db.retirar_materia(materia_id, curso_id)
