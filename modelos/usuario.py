from modelos.persona import Persona
from conexion.supabase_client import SupabaseConnection
import hashlib

class Usuario(Persona):
    def __init__(self, identificacion: str, nombre: str, apellido: str, email: str, rol: str, username: str, id_usuario: int = None, activo: bool = True):
        super().__init__(identificacion, nombre, apellido, email)
        self.__id = id_usuario
        self.__username = username
        self.__rol = rol
        self.__activo = activo

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

    @staticmethod
    def hash_password(password: str) -> str:
        """Genera el hash SHA-256 de una contraseña."""
        return hashlib.sha256(password.strip().encode("utf-8")).hexdigest()

    def guardar(self, contrasena_plana: str):
        """Persiste el nuevo usuario en Supabase con su contraseña cifrada."""
        client = SupabaseConnection.get_client()
        data = {
            "identificacion": self._identificacion,
            "nombre": self._nombre,
            "apellido": self._apellido,
            "email": self._email,
            "username": self.__username,
            "password_hash": self.hash_password(contrasena_plana),
            "rol": self.__rol,
            "activo": self.__activo
        }
        return client.table("usuarios").insert(data).execute()
