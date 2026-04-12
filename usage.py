import numpy as np

def predict_difficulty(w, mtq, T, A):
    return (
        w[0] +
        w[1] * np.log2(T) +
        w[2] * np.log2(A + 1) +
        w[3] * mtq
    )

w = np.array([0.0, 0.3, 0.2, 0.5])

diff = predict_difficulty(w, mtq, T, A)
print("BaseDifficulty =", diff)