from datetime import datetime
from pydantic import BaseModel, Field

class MessageIn(BaseModel):
    username: str = Field(..., max_length=50, description="Nome do usuário que envia a mensagem")
    content: str = Field(..., min_length=1, max_length=1000, description="Conteúdo da mensagem")

class MessageOut(BaseModel):
    id: str = Field(..., description="ID único da mensagem")
    room: str = Field(..., description="Sala onde a mensagem foi enviada")
    username: str = Field(..., description="Nome do usuário que enviou a mensagem")
    content: str = Field(..., description="Conteúdo da mensagem")
    created_at: datetime = Field(..., description="Data e hora de criação da mensagem")

    class Config:
        orm_mode = True  # Facilita integração com ORMs se necessário
