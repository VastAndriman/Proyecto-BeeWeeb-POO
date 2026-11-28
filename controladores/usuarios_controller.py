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
