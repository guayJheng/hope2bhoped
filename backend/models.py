from sqlalchemy import JSON, Column, Integer, Float, Boolean, String, ForeignKey
from .database import Base

class PuzzlesDB(Base):
    __tablename__ = "puzzles"

    pzid = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    base_diff = Column(Float)
    total_hit = Column(Integer)
    dmg_per_hit = Column(Float)

class LogsDB(Base):
    __tablename__ = "logs"

    lid = Column(Integer, primary_key=True, index=True)
    # pzid = Column(Integer)
    pzid = Column(Integer, ForeignKey("puzzles.pzid"))
    play_time = Column(Float)
    action_count = Column(Integer)
    list_movement_time = Column(JSON)
    hit_count = Column(Integer)
    fitts_ids = Column(JSON)
    result = Column(Boolean)

class AvgABDB(Base):
    __tablename__ = "avg_ab"

    pzid = Column(Integer, primary_key=True, index=True)
    list_avg_a = Column(JSON)
    list_avg_b = Column(JSON)

class HitRecordDB(Base):
    __tablename__ = "hit_record"

    pzid = Column(Integer, primary_key=True, index=True)
    prob_hit = Column(Float)

class LogInputDB(Base):
    __tablename__ = "log_input"

    pzid = Column(Integer, primary_key=True, index=True)
    play_time = Column(Float)
    action_count = Column(Integer) 
    list_movement_time = Column(JSON)
    hit_count = Column(Integer)
    fitts_ids = Column(JSON)
    result = Column(Boolean)
