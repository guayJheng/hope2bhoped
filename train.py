import numpy as np
import pickle
import os

from dotenv import load_dotenv
from supabase import create_client

from backend.database import SessionLocal
from backend.models import LogsDB


# -----------------------------
# DATABASE
# -----------------------------
db = SessionLocal()

# -----------------------------
# LOAD LOGS
# -----------------------------
logs = db.query(
    LogsDB.pzid,
    LogsDB.play_time,
    LogsDB.action_count,
    LogsDB.result
).all()

if len(logs) == 0:
    raise ValueError("No training data found")

# -----------------------------
# AGGREGATE PER PUZZLE
# -----------------------------
puzzle_stats = {}

for log in logs:
    pzid = log.pzid

    if pzid not in puzzle_stats:
        puzzle_stats[pzid] = {
            "times":   [],
            "actions": [],
            "results": []
        }

    puzzle_stats[pzid]["times"].append(log.play_time)
    puzzle_stats[pzid]["actions"].append(log.action_count)
    puzzle_stats[pzid]["results"].append(log.result)

# -----------------------------
# PASS 1: คำนวณ raw signals ทุก puzzle
# (Per-Puzzle Baseline -- แต่ละ puzzle มี optimal ต่างกัน)
# -----------------------------
puzzle_ids    = []
fail_rates    = []
time_scores   = []
action_scores = []

for pzid, stats in puzzle_stats.items():

    times   = np.array(stats["times"],   dtype=float)
    actions = np.array(stats["actions"], dtype=float)
    results = np.array(stats["results"], dtype=bool)

    success_times   = times[results]
    success_actions = actions[results]

    # --- Per-Puzzle Baseline ---
    # ถ้าคนผ่านน้อยเกินไป (< 3) fallback เป็น median เพื่อลด noise
    if len(success_times) >= 3:
        local_T = np.percentile(success_times,   10)
        local_A = np.percentile(success_actions, 10)
    elif len(success_times) > 0:
        local_T = np.median(success_times)
        local_A = np.median(success_actions)
    else:
        # ไม่มีใครผ่านเลย -- ใช้ median ของทุกคนแทน
        local_T = np.median(times)
        local_A = np.median(actions)

    # Signal 1: Fail Rate
    fail_rate = 1 - np.mean(results)

    # Signal 2: Time Score (normalize cap 2x)
    time_ratio = times / (local_T + 1e-8)
    time_score = float(np.clip(np.mean(time_ratio) - 1.0, 0, None))
    time_score = min(time_score / 2.0, 1.0)

    # Signal 3: Action Score (normalize cap 2x)
    action_ratio = actions / (local_A + 1e-8)
    action_score = float(np.clip(np.mean(action_ratio) - 1.0, 0, None))
    action_score = min(action_score / 2.0, 1.0)

    puzzle_ids.append(pzid)
    fail_rates.append(fail_rate)
    time_scores.append(time_score)
    action_scores.append(action_score)

fail_rates    = np.array(fail_rates)
time_scores   = np.array(time_scores)
action_scores = np.array(action_scores)

# -----------------------------
# CORRELATION-BASED WEIGHTS
# fail_rate ได้ weight = 1.0 fixed (เป็น anchor)
# time และ action ได้ weight ตาม correlation กับ fail_rate
# -----------------------------
n = len(puzzle_ids)

if n >= 3:
    corr_time   = abs(float(np.corrcoef(fail_rates, time_scores)[0, 1]))
    corr_action = abs(float(np.corrcoef(fail_rates, action_scores)[0, 1]))

    if np.isnan(corr_time):   corr_time   = 0.0
    if np.isnan(corr_action): corr_action = 0.0
else:
    corr_time   = 0.6
    corr_action = 0.4

total    = 1.0 + corr_time + corr_action
W_FAIL   = 1.0        / total
W_TIME   = corr_time  / total
W_ACTION = corr_action / total

print("=== WEIGHTS (correlation-based) ===")
print(f"  corr(fail, time)   = {corr_time:.3f}")
print(f"  corr(fail, action) = {corr_action:.3f}")
print(f"  W_FAIL   = {W_FAIL:.3f}")
print(f"  W_TIME   = {W_TIME:.3f}")
print(f"  W_ACTION = {W_ACTION:.3f}")
print(f"  sum      = {W_FAIL + W_TIME + W_ACTION:.3f}  (must be 1.0)")

# -----------------------------
# PASS 2: คำนวณ difficulty
# -----------------------------
print("\n=== PUZZLE DIFFICULTY ===")

difficulties = {}

for i, pzid in enumerate(puzzle_ids):

    difficulty = (
        W_FAIL   * fail_rates[i]    +
        W_TIME   * time_scores[i]   +
        W_ACTION * action_scores[i]
    )

    difficulties[pzid] = difficulty

    print(
        f"Puzzle {pzid}"
        f" | fail={round(fail_rates[i], 3)}"
        f" | time={round(time_scores[i], 3)}"
        f" | action={round(action_scores[i], 3)}"
        f" | difficulty={round(difficulty, 3)}"
    )

# -----------------------------
# SUMMARY
# -----------------------------
values = list(difficulties.values())

print(f"\n=== SUMMARY ===")
print(f"Hardest : Puzzle {max(difficulties, key=difficulties.get)}")
print(f"Easiest : Puzzle {min(difficulties, key=difficulties.get)}")
print(f"Average : {round(float(np.mean(values)), 3)}")

model = {
    "weights": {
        "W_FAIL":   W_FAIL,
        "W_TIME":   W_TIME,
        "W_ACTION": W_ACTION,
    },
    "base_difficulties": difficulties,
    "features": ["W_FAIL", "W_TIME", "W_ACTION"],
}

os.makedirs("../model", exist_ok=True)

tmp_path = "../model/model_new.pkl"
final_path = "../model/model_current.pkl"

with open(tmp_path, "wb") as f:
    pickle.dump(model, f)

with open(tmp_path, "rb") as f:
    _ = pickle.load(f)

# atomic
os.replace(tmp_path, final_path)

#เชื่อมต่อ Supabase และอัปโหลดโมเดลไปยัง Supabase Storage
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

with open(final_path, "rb") as f:
    supabase.storage.from_("models").upload(
        "model_current.pkl",
        f,
        {
            "content-type": "application/octet-stream",
            "upsert": "true"
        },
    )

print("Training + upload success", model)