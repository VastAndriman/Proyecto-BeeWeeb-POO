"""Operaciones de aulas independientes de los widgets de la interfaz."""

from conexion.supabase_client import SupabaseConnection
from modelos.aula import Aula


class AulasController:
    def __init__(self, db_client=None):
        self.db = db_client if db_client is not None else SupabaseConnection.get_client()

    @staticmethod
    def _validar(numero, capacidad, tipo):
        numero = str(numero).strip()
        tipo = str(tipo).strip()
        try:
            capacidad = int(str(capacidad).strip())
        except (TypeError, ValueError):
            raise ValueError("La capacidad debe ser un número entero.") from None
        if not numero or not tipo or capacidad <= 0:
            raise ValueError("Completa número y tipo; la capacidad debe ser mayor que cero.")
        return numero, capacidad, tipo

    def listar(self):
        return self.db.table("aulas").select("*").execute().data or []

    def crear(self, numero, capacidad, tipo):
        numero, capacidad, tipo = self._validar(numero, capacidad, tipo)
        Aula(numero, capacidad, tipo, db_client=self.db).guardar()

    def actualizar(self, aula_id, numero, capacidad, tipo):
        numero, capacidad, tipo = self._validar(numero, capacidad, tipo)
        self.db.table("aulas").update({
            "numero": numero, "capacidad": capacidad, "tipo": tipo,
        }).eq("id", int(aula_id)).execute()

    def eliminar(self, aula_id):
        self.db.table("aulas").delete().eq("id", int(aula_id)).execute()
