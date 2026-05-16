from pydantic import BaseModel
import numpy as np

#Pydantic model for request body
class LogBase(BaseModel):
    pzid: int
    play_time: float
    action_count: int
    hit_count: int
    result: bool

# class PuzzleBase(BaseModel):
#     pzid: int
#     name: str
#     base_diff: float
#     total_hit: int
#     dmg_per_hit: float

# class HitRecordBase(BaseModel):
#     pzid: int
#     prob_hit: float

class LogInputBase(BaseModel):
    pzid: int
    play_time: float
    action_count: int 
    hit_count: int
    result: bool

#input model
class LogCreate(LogBase):
    pass

class LogInputBase(LogInputBase):
    pass

# Response
class PuzzleResponse(BaseModel):
    pzid: int
    name: str
    base_diff: float
    total_hit: int
    dmg_per_hit: float

class LogResponse(BaseModel):
    lid: int
    pzid: int
    play_time: float
    action_count: int
    hit_count: int
    result: bool
    class Config:
        from_attributes = True

class HitRecordResponse(BaseModel):
    pzid: int
    prob_hit: float
    class Config:
        from_attributes = True


class GetNextPuzzleResponse(BaseModel):
    pzid: int
    name: str
    base_diff: float
    total_hit: int
    dmg_per_hit: float
    next_puzzle_diff: float

