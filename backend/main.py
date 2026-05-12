from typing import List

from sqlalchemy.orm import Session

from fastapi import FastAPI, Depends


# from .database import Base, engine, SessionLocal, get_db
# from .schema import PuzzleResponse, LogCreate, LogInput, LogResponse, HitRecordResponse, Avg_AB_Response
# from .models import HitRecordDB, LogsDB, PuzzlesDB, AvgABDB

from database import Base, engine, get_db
from schema import PuzzleResponse, LogCreate, LogInput, LogResponse, HitRecordResponse, Avg_AB_Response
from models import HitRecordDB, LogsDB, PuzzlesDB, AvgABDB


app = FastAPI()


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

@app.post("/get-next-puzzle", response_model=PuzzleResponse)
def get_next_puzzle(log_input: LogInput, db: Session = Depends(get_db)):
    db_item = ...
    return db_item

@app.post("/add-log", response_model=LogResponse) 
def add_log(log: LogCreate, db: Session = Depends(get_db)):
    # db_item = Log(pzid=log.pzid, play_time=log.play_time,...)
    db_item = LogsDB(**log.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

#สร้างตารางในฐานข้อมูล
Base.metadata.create_all(bind=engine)