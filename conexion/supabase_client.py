import os
from types import SimpleNamespace
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class SupabaseConnection:
    _instance = None

    @classmethod
    def get_client(cls):
        if cls._instance is None:
            if not SUPABASE_URL or not SUPABASE_KEY:
                raise ValueError("Faltan las credenciales de Supabase en el archivo .env")
            cls._instance = BeeWeekClient(create_client(SUPABASE_URL, SUPABASE_KEY))
        return cls._instance


class BeeWeekClient:
    """Cliente de datos que exige una sesion antes de acceder a tablas academicas."""

    def __init__(self, client: Client):
        self._client = client
        self._session_token = None

    def rpc(self, name, params):
        if name not in ("beeweek_login", "beeweek_register"):
            raise ValueError("RPC no permitida en el cliente de BeeWeek")
        return self._client.rpc(name, params)

    def iniciar_sesion(self, token):
        if not isinstance(token, str) or len(token) != 64:
            raise ValueError("El servidor no entrego una sesion valida")
        self._session_token = token

    def cerrar_sesion(self):
        token = self._session_token
        self._session_token = None
        if token:
            self._client.rpc("beeweek_logout", {"p_token": token}).execute()

    def table(self, name):
        if name not in ("aulas", "materias", "docentes", "estudiantes", "cursos", "horarios"):
            raise ValueError("Tabla no permitida")
        return BeeWeekQuery(self, name)


class BeeWeekQuery:
    def __init__(self, db, name):
        self.db = db
        self.name = name
        self.columns = "*"
        self.count_requested = False
        self.filter_column = None
        self.filter_value = None
        self.payload = None

    def select(self, columns="*", count=None):
        if columns != "*" and not all(c.strip().isidentifier() for c in columns.split(",")):
            raise ValueError("Columnas no permitidas")
        self.columns = columns
        self.count_requested = count == "exact"
        return self

    def eq(self, column, value):
        if column not in ("id", "dia"):
            raise ValueError("Filtro no permitido")
        self.filter_column = column
        self.filter_value = str(value)
        return self

    def insert(self, payload):
        if not isinstance(payload, dict):
            raise ValueError("El registro debe ser un objeto")
        self.payload = payload
        return self

    def execute(self):
        token = self.db._session_token
        if not token:
            raise PermissionError("Inicia sesion para consultar datos academicos")
        if self.payload is not None:
            result = self.db._client.rpc("beeweek_insert", {
                "p_token": token, "p_table": self.name, "p_data": self.payload,
            }).execute()
            return SimpleNamespace(data=[result.data], count=None)
        result = self.db._client.rpc("beeweek_list", {
            "p_token": token, "p_table": self.name,
            "p_filter_column": self.filter_column,
            "p_filter_value": self.filter_value,
        }).execute()
        rows = result.data or []
        count = len(rows) if self.count_requested else None
        if self.columns != "*":
            selected = {c.strip() for c in self.columns.split(",")}
            rows = [{k: v for k, v in row.items() if k in selected} for row in rows]
        return SimpleNamespace(data=rows, count=count)
