import pickle

import numpy as np

from sklearn.ensemble import IsolationForest


# Dữ liệu môi trường bình thường
normal_data = np.array([
    [22, 50],
    [23, 52],
    [24, 55],
    [25, 58],
    [26, 60],
    [24, 57],
    [23, 53],
    [25, 56],
    [26, 59],
    [27, 61],
    [24, 54],
    [25, 55],
    [23, 51],
    [26, 57],
    [27, 60],
])


model = IsolationForest(
    n_estimators=50,
    contamination=0.1,
    random_state=42
)


model.fit(normal_data)


with open("model.pkl", "wb") as f:
    pickle.dump(model, f)


print("Model saved to model.pkl")