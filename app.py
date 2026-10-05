from __future__ import annotations

import sqlite3
from datetime import UTC, datetime

from fastapi import FastAPI, Header, HTTPException

app = FastAPI(title="notify")

DB_PATH = "notify.db"
API_KEY = "demo-key"


def _init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "create table if not exists notifications ("
            "id integer primary key autoincrement, "
            "order_id text not null, "
            "channel text not null, "
            "created_at text not null)"
        )
        conn.commit()
    finally:
        conn.close()


@app.on_event("startup")
def startup() -> None:
    _init_db()


@app.post("/notify")
def notify(order_id: str, x_api_key: str = Header(default="")) -> dict[str, str]:
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="invalid api key")

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "insert into notifications(order_id, channel, created_at) values (?, ?, ?)",
            (order_id, "email", datetime.now(UTC).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()

    return {"status": "sent", "order_id": order_id}
