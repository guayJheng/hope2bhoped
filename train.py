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
with open("ols_model.pkl", "wb") as f:
    pickle.dump(model, f)


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

#connect to supabase
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

with open("ols_model.pkl", "rb") as f:
    supabase.storage.from_("models").upload(
        "ols_model.pkl",
        f,
        {"content-type": "application/octet-stream", "upsert": "true"},
        
    )

print("Upload success")



#w0 w1 w2 w3 = [2.37321274e-12 3.00000000e-01 2.00000000e-01 5.00000000e-01]
#[0.00000000000237]