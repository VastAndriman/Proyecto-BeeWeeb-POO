from conexion.supabase_client import SupabaseConnection
from modelos.usuario import Usuario

class AuthController:
    _instancia_defecto = None
    _usuario_actual: Usuario | None = None

    def __init__(self, db_client=None):
        """
        Inyección de Dependencias: Permite recibir un cliente de base de datos (Supabase o Mock).
        Si no se provee, utiliza SupabaseConnection.get_client() por defecto.
        """
        self.db = db_client or SupabaseConnection.get_client()
        self.usuario_actual: Usuario | None = None

    @classmethod
    def _get_instancia_defecto(cls):
        if cls._instancia_defecto is None:
            cls._instancia_defecto = cls()
        return cls._instancia_defecto

    def get_usuario_actual(self_or_cls) -> Usuario | None:
        """Retorna el usuario actualmente autenticado en la sesión."""
        if isinstance(self_or_cls, type):
            return self_or_cls._usuario_actual
        return self_or_cls.usuario_actual or AuthController._usuario_actual

    def cerrar_sesion(self_or_cls):
        """Limpia la sesión activa."""
        if isinstance(self_or_cls, type):
            if self_or_cls._instancia_defecto:
                self_or_cls._instancia_defecto.usuario_actual = None
            self_or_cls._usuario_actual = None
            return
        self_or_cls.usuario_actual = None
        AuthController._usuario_actual = None

    def iniciar_sesion(self_or_cls, usuario_o_email: str = None, contrasena: str = None) -> tuple[bool, str, Usuario | None]:
        """
        Valida las credenciales ingresadas contra la base de datos Supabase.
        Permite iniciar sesión tanto con el nombre de usuario (username) como con el correo institucional (email).
        Soporta uso mediante instancia inyectada o llamada directa.
        """
        if isinstance(self_or_cls, type):
            return self_or_cls._get_instancia_defecto().iniciar_sesion(usuario_o_email, contrasena)

        self = self_or_cls

        if not usuario_o_email or not contrasena:
            return False, "Por favor, completa todos los campos.", None

        usuario_limpio = usuario_o_email.strip()
        contrasena_limpia = contrasena.strip()
        contrasena_hash = Usuario.hash_password(contrasena_limpia)

        try:
            client = self.db

            # Consultar si coincide por username o por email
            query = client.table("usuarios").select("*").or_(f"username.eq.{usuario_limpio},email.eq.{usuario_limpio}").execute()

            if not query.data or len(query.data) == 0:
                return False, "Credenciales incorrectas: usuario no encontrado.", None

            user_record = query.data[0]

            # Validar si el usuario está activo
            if not user_record.get("activo", True):
                return False, "Esta cuenta ha sido desactivada. Consulta con administración.", None

            # Validar contraseña (compara con hash SHA-256 o texto plano de respaldo)
            hash_almacenado = user_record.get("password_hash", "")
            if hash_almacenado != contrasena_hash and hash_almacenado != contrasena_limpia:
                return False, "Contraseña incorrecta. Inténtalo nuevamente.", None

            # Instanciar el objeto Usuario (POO)
            usuario_logueado = Usuario(
                identificacion=user_record.get("identificacion", ""),
                nombre=user_record.get("nombre", ""),
                apellido=user_record.get("apellido", ""),
                email=user_record.get("email", ""),
                rol=user_record.get("rol", "Docente"),
                username=user_record.get("username", usuario_limpio),
                id_usuario=user_record.get("id"),
                activo=user_record.get("activo", True)
            )

            self.usuario_actual = usuario_logueado
            AuthController._usuario_actual = usuario_logueado
            return True, f"¡Bienvenido, {usuario_logueado.get_nombre_completo()}!", usuario_logueado

        except Exception as e:
            return False, f"Error de conexión: {str(e)}", None

    def registrar_usuario(self_or_cls, identificacion: str, nombre: str, apellido: str, email: str, username: str, contrasena: str, rol: str = "Docente") -> tuple[bool, str]:
        """
        Registra un nuevo usuario en la base de datos Supabase con contraseña cifrada (SHA-256).
        Soporta uso por instancia inyectada o llamada directa de clase.
        """
        if isinstance(self_or_cls, type):
            return self_or_cls._get_instancia_defecto().registrar_usuario(
                identificacion, nombre, apellido, email, username, contrasena, rol
            )

        self = self_or_cls

        if not all([identificacion, nombre, apellido, email, username, contrasena]):
            return False, "Por favor, completa todos los campos del formulario."

        identificacion_limpia = identificacion.strip()
        nombre_limpio = nombre.strip()
        apellido_limpio = apellido.strip()
        email_limpio = email.strip()
        username_limpio = username.strip()
        contrasena_limpia = contrasena.strip()

        if len(contrasena_limpia) < 4:
            return False, "La contraseña debe tener al menos 4 caracteres."

        try:
            client = self.db

            # Verificar si ya existe el usuario por cédula, username o email
            existente = client.table("usuarios").select("id").or_(
                f"identificacion.eq.{identificacion_limpia},username.eq.{username_limpio},email.eq.{email_limpio}"
            ).execute()

            if existente.data and len(existente.data) > 0:
                return False, "Ya existe una cuenta con esa identificación, usuario o correo."

            nuevo_usuario = Usuario(
                identificacion=identificacion_limpia,
                nombre=nombre_limpio,
                apellido=apellido_limpio,
                email=email_limpio,
                rol=rol,
                username=username_limpio,
                activo=True
            )
            nuevo_usuario.guardar(contrasena_limpia)
            return True, "¡Cuenta creada con éxito! Ya puedes iniciar sesión."

        except Exception as e:
            return False, f"Error al registrar: {str(e)}"

