from typing import Dict, Set
from fastapi import WebSocket

class WSManager:
    """
    Gerenciador de conexões WebSocket por sala.

    Mantém um registro das conexões ativas em cada sala, permitindo
    conectar, desconectar e enviar mensagens (broadcast) para todos
    os clientes de uma sala específica.
    """

    def __init__(self):
        """
        Inicializa o gerenciador com um dicionário vazio de salas.
        
        Estrutura:
            rooms: Dict[str, Set[WebSocket]]
                - Chave: nome da sala
                - Valor: conjunto de objetos WebSocket conectados
        """
        self.rooms: Dict[str, Set[WebSocket]] = {}

    async def connect(self, room: str, ws: WebSocket):
        """
        Conecta um cliente WebSocket a uma sala.

        Aceita a conexão e adiciona o WebSocket ao conjunto da sala.
        Se a sala ainda não existir, cria um novo conjunto.

        Args:
            room (str): Nome da sala de chat.
            ws (WebSocket): Instância da conexão WebSocket do cliente.
        """
        await ws.accept()
        self.rooms.setdefault(room, set()).add(ws)

    def disconnect(self, room: str, ws: WebSocket):
        """
        Desconecta um cliente WebSocket de uma sala.

        Remove o WebSocket do conjunto da sala e, caso não haja
        mais clientes conectados, remove a sala do dicionário.

        Args:
            room (str): Nome da sala de chat.
            ws (WebSocket): Instância da conexão WebSocket do cliente.
        """
        conns = self.rooms.get(room)
        if conns and ws in conns:
            conns.remove(ws)
            if not conns:
                self.rooms.pop(room, None)

    async def broadcast(self, room: str, payload: dict):
        """
        Envia uma mensagem para todos os clientes conectados a uma sala.

        Tenta enviar o payload para cada WebSocket da sala. Caso haja
        erro na conexão, desconecta o cliente automaticamente.

        Args:
            room (str): Nome da sala de chat.
            payload (dict): Dados a serem enviados para os clientes.
        """
        for ws in list(self.rooms.get(room, [])):
            try:
                await ws.send_json(payload)
            except Exception:
                self.disconnect(room, ws)


# Instância global do gerenciador
manager = WSManager()
