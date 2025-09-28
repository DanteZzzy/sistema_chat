from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from bson import ObjectId
from .config import MONGO_URL, MONGO_DB

_client: Optional[AsyncIOMotorClient] = None

def db() -> AsyncIOMotorClient:
    """
    Retorna a instância do banco de dados MongoDB configurada usando Motor (assíncrono).

    Esta função cria a conexão com o MongoDB apenas uma vez (singleton) e reutiliza a mesma
    instância em chamadas subsequentes.

    Raises:
        RuntimeError: Se MONGO_URL não estiver definido no arquivo .env.

    Returns:
        AsyncIOMotorClient: Instância do banco de dados assíncrono.
    """
    global _client
    if _client is None:
        if not MONGO_URL:
            raise RuntimeError("Defina MONGO_URL no .env (string do MongoDB Atlas).")
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[MONGO_DB]

def iso(dt: datetime) -> str:
    """
    Converte um objeto datetime em uma string no formato ISO 8601, garantindo timezone UTC.

    Args:
        dt (datetime): Objeto datetime a ser convertido.

    Returns:
        str: Data/hora no formato ISO 8601 com timezone UTC.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()

def serialize(doc: dict) -> dict:
    """
    Converte um documento do MongoDB em um dicionário serializável para JSON.

    - Converte o campo "_id" para string.
    - Converte o campo "created_at" para ISO 8601 caso seja datetime.

    Args:
        doc (dict): Documento retornado pelo MongoDB.

    Returns:
        dict: Documento serializável para envio via API ou WebSocket.
    """
    d = dict(doc)
    if "_id" in d:
        d["_id"] = str(d["_id"])
    if "created_at" in d and isinstance(d["created_at"], datetime):
        d["created_at"] = iso(d["created_at"])
    return d
