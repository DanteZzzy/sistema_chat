from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime, timezone
from pydantic import ValidationError
from ..database import db, serialize
from ..websocket_manager import manager
from ..schemas import MessageIn  # Modelo de validação Pydantic

router = APIRouter()

@router.websocket("/ws/{room}")
async def ws_room(ws: WebSocket, room: str) -> None:
    """
    Gerencia a conexão WebSocket de uma sala específica de chat.

    Esta função realiza:
    - Conexão do cliente à sala.
    - Envio do histórico inicial das últimas 20 mensagens da sala.
    - Recepção de novas mensagens e validação via Pydantic.
    - Inserção das mensagens no MongoDB.
    - Broadcast das mensagens para todos os clientes conectados na mesma sala.
    - Tratamento de desconexão do cliente.

    Args:
        ws (WebSocket): Instância da conexão WebSocket do cliente.
        room (str): Nome da sala de chat à qual o cliente deseja se conectar.

    Raises:
        WebSocketDisconnect: Captura a desconexão do cliente e remove do gerenciador de conexões.
    """
    await manager.connect(room, ws)
    try:
        # Envia histórico inicial das últimas 20 mensagens (mais antigas → mais recentes)
        cursor = db()["messages"].find({"room": room}).sort("_id", -1).limit(20)
        items = [serialize(d) async for d in cursor]
        items.reverse()
        await ws.send_json({"type": "history", "items": items})

        while True:
            payload = await ws.receive_json()

            # Validação via Pydantic
            try:
                msg = MessageIn(**payload)
            except ValidationError as e:
                await ws.send_json({
                    "type": "error",
                    "message": "Dados inválidos",
                    "details": e.errors()
                })
                continue

            content = msg.content.strip()
            if not content:
                await ws.send_json({"type": "error", "message": "Mensagem vazia não é permitida"})
                continue

            doc = {
                "room": room,
                "username": msg.username,
                "content": content,
                "created_at": datetime.now(timezone.utc),
            }

            res = await db()["messages"].insert_one(doc)
            doc["_id"] = str(res.inserted_id)

            # Broadcast para todos os clientes da sala
            await manager.broadcast(room, {"type": "message", "item": serialize(doc)})

    except WebSocketDisconnect:
        manager.disconnect(room, ws)
