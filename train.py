import numpy as np
import pickle

data = [
    [1, 1.42, 10.0, 2.5],
    [2, 2.43, 13.5, 2.5],
    [3, 3.93, 19.0, 4.0],
    [4, 1.10, 8.05, 2.4],
    [5, 2.80, 14.0, 3.5],
    [6, 3.50, 17.0, 3.8],
    [7, 4.50, 21.0, 5.0],
]

X = []
y = []

for row in data:

    pzid, mtq, T, A = row

    diff = (
        0.5 * mtq +
        0.3 * np.log2(T) +
        0.2 * np.log2(A + 1)
        # + np.random.normal(0, 0.2)
    )

    # feature
    X.append([
        1,
        np.log2(T),
        np.log2(A + 1),
        mtq
    ])

    # target(weight)
    y.append(diff)

X = np.array(X)
y = np.array(y)

# OLS
w = np.linalg.inv(X.T @ X) @ X.T @ y

print("w0 w1 w2 w3 =", w)

model = {
    "weights": w,
    "features": ["bias", "เวลาที่ใช้ในการแก้ Puzzle(log2_T)", "จำนวน Action(log2_A1)"
    , "ระยะเวลาระหว่าง Action(MTq)"],
}

with open("ols_model.pkl", "wb") as f:
    pickle.dump(model, f)

#w0 w1 w2 w3 = [2.37321274e-12 3.00000000e-01 2.00000000e-01 5.00000000e-01]
#[0.00000000000237]