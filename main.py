from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from db import init_db
from logic import router  # если есть обычные REST маршруты
from ws_handlers import websocket_handler

app = FastAPI()

# Добавляем CORS middleware ПЕРЕД всеми роутами
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "https://succinct-phrases-front.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

init_db()
app.include_router(router)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_handler(websocket)
