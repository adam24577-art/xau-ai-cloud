from fastapi import FastAPI, Header
from pydantic import BaseModel
import sqlite3
import random
from datetime import datetime

app = FastAPI()

DB_NAME = "trades.db"
API_KEY = "CHANGE_ME"


class PredictRequest(BaseModel):
    symbol: str
    setup: str
    direction: str
    ltf_structure: str
    htf_structure: str
    phase: str
    atr: float
    spread: float
    bos_body: float
    engulf_body: float
    body_dominance: float
    risk_reward: float
    hour: int


class TrainRequest(PredictRequest):
    comment: str
    net_profit: float
    win: bool


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        setup TEXT,
        direction TEXT,
        phase TEXT,
        atr REAL,
        spread REAL,
        bos_body REAL,
        engulf_body REAL,
        body_dominance REAL,
        risk_reward REAL,
        hour INTEGER,
        comment TEXT,
        net_profit REAL,
        win INTEGER,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


@app.get("/")
def home():
    return {"status": "AI CLOUD RUNNING"}


@app.post("/predict")
def predict(
    req: PredictRequest,
    x_api_key: str = Header(default="")
):
    if x_api_key != API_KEY:
        return {
            "decision": "BLOCK",
            "score": 0,
            "reason": "INVALID API KEY",
            "samples": 0,
            "model_version": "1.0"
        }

    score = 50

    if req.phase.startswith("BULLISH") or req.phase.startswith("BEARISH"):
        score += 10

    if req.atr >= 1.5:
        score += 10

    if req.spread <= 7:
        score += 10

    if req.body_dominance >= 70:
        score += 10

    score += random.randint(-5, 5)

    allow = score >= 60

    return {
        "decision": "ALLOW" if allow else "BLOCK",
        "score": score,
        "reason": "INITIAL AI FILTER",
        "samples": 0,
        "model_version": "1.0"
    }


@app.post("/train")
def train(
    req: TrainRequest,
    x_api_key: str = Header(default="")
):
    if x_api_key != API_KEY:
        return {"status": "INVALID API KEY"}

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO trades (
        symbol,
        setup,
        direction,
        phase,
        atr,
        spread,
        bos_body,
        engulf_body,
        body_dominance,
        risk_reward,
        hour,
        comment,
        net_profit,
        win,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        req.symbol,
        req.setup,
        req.direction,
        req.phase,
        req.atr,
        req.spread,
        req.bos_body,
        req.engulf_body,
        req.body_dominance,
        req.risk_reward,
        req.hour,
        req.comment,
        req.net_profit,
        int(req.win),
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()

    return {
        "status": "TRAINED",
        "profit": req.net_profit
    }
