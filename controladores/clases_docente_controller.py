class ClasesDocenteController:
    """Consulta clases propias; la base resuelve la identidad desde la sesion."""

    def __init__(self, db_client):
        self.db = db_client

    def listar(self):
        return self.db.mis_clases_docente()
