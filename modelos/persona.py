class Persona:
    def __init__(self, identificacion: str, nombre: str, apellido: str, email: str):
        self._identificacion = identificacion  # Atributo protegido
        self._nombre = nombre
        self._apellido = apellido
        self._email = email

    def get_nombre_completo(self) -> str:
        return f"{self._nombre} {self._apellido}"