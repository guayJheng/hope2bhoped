import numpy as np
import pickle
import os

from dotenv import load_dotenv
from supabase import create_client

from backend.database import SessionLocal
from backend.models import LogsDB

db = SessionLocal()

logs = db.query(
    LogsDB.pzid,
    LogsDB.play_time,
    LogsDB.action_count
).all()

data = []

if len(logs) == 0:
    raise ValueError("No training data found")

for log in logs:
    data.append([
        log.pzid,
        log.play_time,
        log.action_count
    ])

# print(data)

X = []
y = []

for row in data:

    pzid, T, A = row

    diff = (
        0.6 * np.log2(T) +
        0.4 * np.log2(A + 1)
        # + np.random.normal(0, 0.2)
    )

    # feature
    X.append([
        1,
        np.log2(T),
        np.log2(A + 1),
    ])

    # target(weight)
    y.append(diff)

X = np.array(X)
y = np.array(y)

# OLS
w = np.linalg.inv(X.T @ X) @ X.T @ y

# print("w0 w1 w2 =", w)

model = {
    "weights": w,
    "features": ["bias", "เวลาที่ใช้ในการแก้ Puzzle(log2_T)", "จำนวน Action(log2_A1)"],
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

print("Training + upload success")



#w0 w1 w2 w3 = [2.37321274e-12 3.00000000e-01 2.00000000e-01 5.00000000e-01]
#[0.00000000000237]