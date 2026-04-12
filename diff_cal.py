import pickle
import json
import os
import sys
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
import socket


app = FastAPI()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

model_path = resource_path("ols_model.pkl")

with open(model_path, "rb") as f:
    model = pickle.load(f)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data) #{"T": 10.0, "A": 2.5, "MTq": 1.42}

            w = model["weights"]

            features = np.array([
                1,
                np.log2(data["T"]),
                np.log2(data["A"] + 1),
                data["MTq"]
            ]).reshape(1, -1)

            diff = np.dot(features, w)[0] #มี weight แล้ว เลยคำนวณ dot product ระหว่าง features กับ weights

            await websocket.send_text(json.dumps({"diff": diff}))

    except WebSocketDisconnect:
        print("WebSocket disconnected")


def port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


if __name__ == "__main__":
    if port_in_use(8000):
        print("Server already running")
        sys.exit()
    print("Starting Server...")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=None
    )