from fastapi import WebSocket, WebSocketDisconnect
from uuid import uuid4
import random
import asyncio
from db import get_db
from utils import now
import random

clients = set()
entries = []
game_running = False

async def websocket_handler(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)

    # Отправить текущие ставки при подключении
    for entry in entries:
        await websocket.send_json({"type": "new_entry", "entry": entry})

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "place_bet":
                if any(e["author_id"] == data["author_id"] for e in entries):
                    await websocket.send_json({
                        "type": "error",
                        "message": "Вы уже сделали ставку в этой игре!"
                    })
                    continue
                try:
                    entry = {
                        "id": str(uuid4()),
                        "author_id": data["author_id"],
                        "text": data["text"],
                        "amount": float(data["amount"])
                    }
                except (KeyError, ValueError, TypeError) as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Invalid bet data: {str(e)}"
                    })
                    continue

                try:
                    entries.append(entry)

                    conn = get_db()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO phrases (id, text, author_id, amount, created_at, likes_count, used_in_top)
                        VALUES (?, ?, ?, ?, ?, 0, 0)
                    """, (
                        entry["id"], entry["text"], entry["author_id"],
                        entry["amount"], now()
                    ))
                    conn.commit()
                    conn.close()
                except Exception as db_error:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Database error: {str(db_error)}"
                    })
                    continue

                await broadcast({"type": "new_entry", "entry": entry})

                if len(entries) == 3 and not game_running:
                    asyncio.create_task(start_lottery())
    except WebSocketDisconnect:
        clients.remove(websocket)

async def broadcast(message: dict):
    disconnected = []
    for client in clients:
        try:
            await client.send_json(message)
        except:
            disconnected.append(client)
    for dc in disconnected:
        clients.remove(dc)

async def start_lottery():
    global game_running
    game_running = True

    # Отправляем сигнал начала таймера (только seconds, без фиксированного entries)
    await broadcast({
        "type": "start_timer",
        "seconds": 60
    })

    await asyncio.sleep(60)

    if not entries:
        game_running = False
        return

    # Сформировать "весовой пул" с учетом всех участников к моменту окончания таймера
    weights = [entry["amount"] for entry in entries]
    winner = random.choices(entries, weights=weights, k=1)[0]

    # Сохраняем победителя
    try:
        conn = get_db()
        cursor = conn.cursor()
        win_id = str(uuid4())

        cursor.execute("""
            INSERT INTO winners (id, phrase_id, won_at, amount_at_win)
            VALUES (?, ?, ?, ?)
        """, (win_id, winner["id"], now(), winner["amount"]))

        cursor.execute("UPDATE phrases SET used_in_top = 1 WHERE id = ?", (winner["id"],))
        conn.commit()
        conn.close()
    except Exception as db_error:
        print("Failed to save winner:", db_error)

    # Отправляем победителя и финальный список участников
    await broadcast({
        "type": "winner",
        "winner": winner,
        "entries": entries
    })

    entries.clear()
    game_running = False

