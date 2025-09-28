from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from bson import ObjectId
from datetime import datetime, timezone
from ..database import db, serialize
from ..schemas import MessageIn, MessageOut

router = APIRouter()

@router.get("/rooms/{room}/messages")
async def get_messages(
    room: str, 
    limit: int = Query(20, ge=1, le=100), 
    before_id: Optional[str] = Query(None)
):
    """
    Retorna mensagens de uma sala específica com paginação.

    - Permite limitar a quantidade de mensagens retornadas.
    - Permite retornar mensagens anteriores a um ID específico (before_id).

    Args:
        room (str): Nome da sala.
        limit (int, optional): Quantidade máxima de mensagens a serem retornadas. Default: 20.
        before_id (Optional[str], optional): Retorna mensagens com _id menor que este valor. Default: None.

    Raises:
        HTTPException: Retorna 400 se o before_id fornecido não for válido.

    Returns:
        dict: Contendo:
            - "items": Lista de mensagens serializadas (mais antiga → mais recente).
            - "next_cursor": ID da última mensagem da página, útil para paginação.
    """
    query = {"room": room}

    if before_id:
        try:
            query["_id"] = {"$lt": ObjectId(before_id)}
        except Exception:
            raise HTTPException(status_code=400, detail="before_id inválido")

    cursor = db()["messages"].find(query).sort("_id", -1).limit(limit)
    docs = [serialize(d) async for d in cursor]

    docs.reverse()

    next_cursor = docs[-1]["_id"] if docs else None

    return {"items": docs, "next_cursor": next_cursor}


@router.post("/rooms/{room}/messages", response_model=MessageOut, status_code=201)
async def post_message(room: str, message: MessageIn):
    """
    Cria uma nova mensagem em uma sala específica.

    - Valida o conteúdo da mensagem para não ser vazio.
    - Insere a mensagem no MongoDB.
    - Retorna a mensagem criada no formato MessageOut.

    Args:
        room (str): Nome da sala.
        message (MessageIn): Objeto contendo 'username' e 'content'.

    Raises:
        HTTPException: Retorna 400 se o conteúdo da mensagem for vazio.

    Returns:
        MessageOut: Mensagem criada, incluindo ID, sala, usuário, conteúdo e data de criação.
    """
    content = message.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Mensagem vazia não é permitida")

    doc = {
        "room": room,
        "username": message.username,
        "content": content,
        "created_at": datetime.now(timezone.utc),
    }

    res = await db()["messages"].insert_one(doc)
    doc["_id"] = str(res.inserted_id)

    return {
        "id": doc["_id"],
        "room": room,
        "username": doc["username"],
        "content": doc["content"],
        "created_at": doc["created_at"]
    }


@router.delete("/rooms/{room}/messages")
async def delete_messages(room: str):
    """
    Deleta todas as mensagens de uma sala específica.

    Args:
        room (str): Nome da sala.

    Returns:
        dict: { "deleted_count": número de mensagens removidas }
    """
    res = await db()["messages"].delete_many({"room": room})
    
    return {"deleted_count": res.deleted_count}
