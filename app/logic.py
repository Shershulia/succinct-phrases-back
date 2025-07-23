from fastapi import APIRouter, HTTPException
from app.db import get_db
from app.utils import get_next_cycle_time

router = APIRouter()

@router.get("/hall-of-fame")
def get_hall_of_fame():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT phrase_id, won_at, amount_at_win FROM winners ORDER BY won_at DESC")
    results = []

    for row in cursor.fetchall():
        phrase_id, won_at, amount = row
        cursor.execute("SELECT text, author_id FROM phrases WHERE id = ?", (phrase_id,))
        phrase_data = cursor.fetchone()
        if not phrase_data:
            continue
        text, author_id = phrase_data
        results.append({
            "text": text,
            "author_id": author_id,
            "won_at": won_at,
            "amount": amount
        })

    return results

@router.get("/hall-of-fame/latest")
def get_latest_phrase():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT phrase_id, won_at, amount_at_win FROM winners ORDER BY won_at DESC LIMIT 1")
    row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="No winners found")

    phrase_id, won_at, amount = row
    cursor.execute("SELECT text, author_id FROM phrases WHERE id = ?", (phrase_id,))
    phrase_data = cursor.fetchone()

    if not phrase_data:
        raise HTTPException(status_code=404, detail="Phrase not found")

    text, author_id = phrase_data

    return {
        "text": text,
        "author_id": author_id,
        "won_at": won_at,
        "amount": amount
    }

@router.get("/phrases/active")
def get_active_phrases():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, text, author_id, amount FROM phrases WHERE used_in_top = 0")
    return [
        {"id": row[0], "text": row[1], "author_id": row[2], "amount": row[3]}
        for row in cursor.fetchall()
    ]
