class UsuariosController:
    """Gestiona cuentas mediante operaciones verificadas en Supabase."""

    ROLES = ("Administrador", "Docente", "Estudiante")

    def __init__(self, db_client):
        self.db = db_client

    def listar(self):
        return self.db.listar_usuarios_admin()

    def cambiar_rol(self, usuario_id, rol):
        if rol not in self.ROLES:
            raise ValueError("Selecciona un rol valido")
        return self.db.cambiar_rol_usuario(usuario_id, rol)

    def listar_fichas_docentes(self):
        return self.db.table("docentes").select("id,nombre,apellido,usuario_id").execute().data or []

    def vincular_docente(self, usuario_id, docente_id):
        return self.db.vincular_cuenta_docente(usuario_id, docente_id)
