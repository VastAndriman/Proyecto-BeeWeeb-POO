from modelos.persona import Persona
from conexion.supabase_client import SupabaseConnection

class Usuario(Persona):
    def __init__(self, identificacion: str, nombre: str, apellido: str, email: str, rol: str, username: str, id_usuario: int = None, activo: bool = True, db_client=None):
        super().__init__(identificacion, nombre, apellido, email)
        self.__id = id_usuario
        self.__username = username
        self.__rol = rol
        self.__activo = activo
        self.db = db_client

    def obtener_tipo(self) -> str:
        return self.__rol

    @property
    def id(self) -> int:
        return self.__id

    @property
    def username(self) -> str:
        return self.__username

    @property
    def rol(self) -> str:
        return self.__rol

    @property
    def activo(self) -> bool:
        return self.__activo

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def apellido(self) -> str:
        return self._apellido

    @property
    def email(self) -> str:
        return self._email

    def guardar(self, contrasena_plana: str):
        """Registra la cuenta mediante la función protegida de Supabase."""
        client = self.db if self.db is not None else SupabaseConnection.get_client()
        return client.rpc("beeweek_register", {
            "p_identificacion": self._identificacion,
            "p_nombre": self._nombre,
            "p_apellido": self._apellido,
            "p_email": self._email,
            "p_username": self.__username,
            "p_password": contrasena_plana,
            "p_rol": self.__rol,
        }).execute()
