from sqlalchemy import JSON, Column, Integer, Float, Boolean, String, ForeignKey
# from .database import Base
from backend.database import Base

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
    hit_count = Column(Integer)
    result = Column(Boolean)

class AvgABDB(Base):
    __tablename__ = "avg_ab"

    pzid = Column(Integer, primary_key=True, index=True)
    list_avg_a = Column(Float)
    list_avg_b = Column(Float)

class HitRecordDB(Base):
    __tablename__ = "hit_record"

    pzid = Column(Integer, primary_key=True, index=True)
    prob_hit = Column(Float)

class LogInputDB(Base):
    __tablename__ = "log_input"

    pzid = Column(Integer, primary_key=True, index=True)
    play_time = Column(Float)
    action_count = Column(Integer) 
    hit_count = Column(Integer)
    result = Column(Boolean)

class StatDataDB(Base):
    __tablename__ = "stat_data"

    pzid = Column(Integer, primary_key=True, index=True)
    avg_t = Column(Float)
    avg_a = Column(Float)
    avg_mtp = Column(Float)
    sd_t = Column(Float)
    sd_a = Column(Float)
    sd_mtp = Column(Float)
