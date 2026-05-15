import subprocess,sys,os,pickle,requests
from typing import List
import numpy as np
from pathlib import Path
from sqlalchemy import func, select,   text
from sqlalchemy.orm import Session

from fastapi import FastAPI, Depends, BackgroundTasks


# from .database import Base, engine, SessionLocal, get_db
# from .schema import LogInputBase, PuzzleResponse, LogCreate, LogResponse, HitRecordResponse, Avg_AB_Response, GetNextPuzzleResponse
# from .models import HitRecordDB, LogsDB, PuzzlesDB, AvgABDB, StatDataDB

from backend.database import Base, engine, get_db
from backend.schema import LogInputBase, PuzzleResponse, LogCreate, LogResponse, HitRecordResponse, Avg_AB_Response, GetNextPuzzleResponse
from backend.models import HitRecordDB, LogsDB, PuzzlesDB, AvgABDB, StatDataDB

model = None
weights = None
w0 = w1 = w2 = None

BASE_DIR = Path(__file__).resolve().parent.parent
TRAIN_PATH = BASE_DIR / "train.py"

# def run_train():
#     subprocess.run([sys.executable, str(TRAIN_PATH)], check=True)
#     load_model()  # reload หลัง train เสร็จ

def load_model():
    global model, weights, w0, w1, w2

    response = requests.get(os.getenv("MODEL_URL"))
    response.raise_for_status()

    model = pickle.loads(response.content)
    weights = model["weights"]

    w0, w1, w2 = weights
    print("Model loaded:", weights)

load_model()

print("Model loaded with weights:", weights)

def sigmoid(x):
    return 1 / (1 + np.exp(-x))
    
def z_dist(w1, w2, w3, zT, zA, zMTq):
    return np.sqrt(
        w1 * (zT ** 2) +
        w2 * (zA ** 2) +
        w3 * (zMTq ** 2)
    )


app = FastAPI()

@app.get("/wake-up")
def wake_up():
    return {"status": "ok"}

# @app.get("/train-model")
# def train_model(background_tasks: BackgroundTasks):
#     background_tasks.add_task(run_train)
#     return {"status": "training started"}

@app.get("/reload-model")
def reload_model_endpoint():
    load_model()
    return {"status": "reloaded"}

@app.get("/get-puzzles", response_model=List[PuzzleResponse])
def get_puzzles(db: Session = Depends(get_db)):
    db_item = db.query(PuzzlesDB).all()
    return db_item


@app.get("/get-logs", response_model=List[LogResponse])
def get_logs(db: Session = Depends(get_db)):
    db_item = db.query(LogsDB).all()
    return db_item

@app.get("/get-avg-ab/{pzid}", response_model=Avg_AB_Response)
def get_avg_ab(pzid: int ,db: Session = Depends(get_db)):
    db_item = db.query(AvgABDB).filter(AvgABDB.pzid == pzid).first()
    return db_item


@app.get("/get-hit-record/{pzid}", response_model=HitRecordResponse)
def get_hit_record(pzid: int ,db: Session = Depends(get_db)):
    db_item = db.query(HitRecordDB).filter(HitRecordDB.pzid == pzid).first()
    return db_item


@app.post("/add-log", response_model=LogResponse) 
def add_log(log: LogCreate, db: Session = Depends(get_db)):
    # db_item = Log(pzid=log.pzid, play_time=log.play_time,...)
    db_item = LogsDB(**log.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.post("/get-next-puzzle", response_model=GetNextPuzzleResponse)
def get_next_puzzle(
    body: LogInputBase,
    db: Session = Depends(get_db)
):

    # current puzzle
    current_puzzle = (
        db.query(PuzzlesDB).filter(PuzzlesDB.pzid == body.pzid).first()
    )
    if not current_puzzle:
        return {"status_code": 404, "detail": "Puzzle not found"}

    # prob_hit
    prob_hit = (
        db.query(HitRecordDB.prob_hit)
        .filter(HitRecordDB.pzid == body.pzid)
        .first()[0]
    )
    if prob_hit is None:
        return {"status_code": 404, "detail": "Hit record not found"}
    
    #stat_data
    stat_data = (
        db.query(StatDataDB).filter(StatDataDB.pzid == body.pzid).first()
    )
    if stat_data is None:
        return {"status_code": 404, "detail": "Stat data not found"}

    # z-score

    def z_score(x, mean, std):
        if std is None or std == 0:
            return 0
        return (x - mean) / std

    #cal mtp
    mt_list = []
    avg_ab = (
        db.query(AvgABDB).filter(AvgABDB.pzid == body.pzid).first()
    )
    if avg_ab is None:
        return {"detail": "AvgAB not found"}

    avg_a_list = avg_ab.list_avg_a
    avg_b_list = avg_ab.list_avg_b

    for a, b, fid in zip(avg_a_list, avg_b_list, body.fitts_ids):
        mt = a + (b * fid)
        mt_list.append(mt)
    mtp = np.percentile(mt_list, 75)

    #ค่าของ feature,ค่าเฉลี่ย,ส่วนเบี่ยงเบนมาตรฐาน
    z_a = z_score(body.action_count, stat_data.avg_a, stat_data.sd_a)
    z_t = z_score(body.play_time, stat_data.avg_t, stat_data.sd_t)
    z_mtp = z_score(mtp, stat_data.avg_mtp, stat_data.sd_mtp)

    #P(fail)
    p_fail = sigmoid(0.5 * ( z_dist(w1,w2,w3,z_t,z_a,z_mtp) - 1.0))
    
    #expected_total_damage

    expected_total_damage = prob_hit * current_puzzle.total_hit * current_puzzle.dmg_per_hit
    
    # risk scaler
    risk_scaler = (
        1 + 1.5 * (1 - p_fail) * (expected_total_damage / 100))
    
    # next puzzle diff
    next_puzzle_diff = current_puzzle.base_diff * risk_scaler

    # next puzzle

    next_puzzle = (
        db.query(PuzzlesDB)
        .filter(PuzzlesDB.pzid != body.pzid)
        .order_by(func.abs(PuzzlesDB.base_diff - next_puzzle_diff))
        .first()
    )
    if not next_puzzle:
        db_item = {"status_code": 404, "detail": "Next puzzle not found"}
    else:
        db_item = {
        "pzid": next_puzzle.pzid,
        "name": next_puzzle.name,
        "base_diff": next_puzzle.base_diff,
        "total_hit": next_puzzle.total_hit,
        "dmg_per_hit": next_puzzle.dmg_per_hit,
        "next_puzzle_diff": float(next_puzzle_diff)
    }
    print("w:", w0 , w1 , w2 , w3)
    print(risk_scaler)
    return db_item

#สร้างตารางในฐานข้อมูล
Base.metadata.create_all(bind=engine)