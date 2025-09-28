from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path

from .routes.messages import router as messages_router
from .routes.websocket import router as websocket_router

app = FastAPI(title="FastAPI Chat + MongoDB Atlas (Modular)")

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monta a pasta 'static' para servir CSS, JS, imagens etc.
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Rota principal para index.html
@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(Path("app/static/index.html"))

# Rotas da aplicação
app.include_router(messages_router)
app.include_router(websocket_router)
