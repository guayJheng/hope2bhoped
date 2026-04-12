from collections import defaultdict
import numpy as np

mock_data = [
    {
        'lid': 1,
        'pzid': 1,
        'fitts_id': 1.2,
        'play_time': 9.0,
        'action_count': 2,
        'list_movement_time': [0.5, 1.0],
        'list_avg_a': [0.2, 0.4],
        'list_avg_b': [0.8, 0.9]
    },
    {
        'lid': 4,
        'pzid': 1,
        'fitts_id': 2.0,
        'play_time': 13.0,
        'action_count': 2,
        'list_movement_time': [0.8, 1.0],
        'list_avg_a': [0.35, 0.4],
        'list_avg_b': [0.95, 1.05]
    },
    {
        'lid': 2,
        'pzid': 2,
        'fitts_id': 1.2,
        'play_time': 11.0,
        'action_count': 3,
        'list_movement_time': [0.6, 0.9, 1.1],
        'list_avg_a': [0.25, 0.35, 0.4],
        'list_avg_b': [0.75, 0.85, 0.95]
    },
    {
        'lid': 3,
        'pzid': 2,
        'fitts_id': 2.0,
        'play_time': 14.0,
        'action_count': 3,
        'list_movement_time': [0.7, 1.2, 1.4],
        'list_avg_a': [0.3, 0.45, 0.5],
        'list_avg_b': [0.9, 1.0, 1.1]
    },

    {
        'lid': 5,
        'pzid': 3,
        'fitts_id': 2.8,
        'play_time': 18.0,
        'action_count': 4,
        'list_movement_time': [1.0, 1.2, 1.5, 1.8],
        'list_avg_a': [0.4, 0.45, 0.5, 0.55],
        'list_avg_b': [1.0, 1.1, 1.2, 1.25]
    },
    {
        'lid': 6,
        'pzid': 3,
        'fitts_id': 2.8,
        'play_time': 20.0,
        'action_count': 4,
        'list_movement_time': [1.1, 1.3, 1.6, 2.0],
        'list_avg_a': [0.42, 0.48, 0.53, 0.6],
        'list_avg_b': [1.05, 1.15, 1.22, 1.3]
    }
]

# ------------------------------------
# หา MT ของแต่ละ log 
# ------------------------------------
for row in mock_data:
    fitts = row["fitts_id"]
    a_list = row["list_avg_a"]
    b_list = row["list_avg_b"]

    mt_list = []
    for a, b in zip(a_list, b_list):
        mt = a + b * fitts
        # mt = round(a + b * fitts, 2)
        mt_list.append(mt)

    row["MT_list"] = mt_list

print('MT',mock_data, "\n")

# ------------------------------------
# group ตาม puzzle 
# ------------------------------------
puzzle_mt = defaultdict(list)

for row in mock_data:
    puzzle_mt[row["pzid"]].append(row["MT_list"])

print('group',mock_data, "\n")

# ------------------------------------
# หาเฉลี่ย MT ของแต่ละ puzzle 
# ------------------------------------
puzzle_avg_mt = {}

for pzid, lists in puzzle_mt.items():

    max_len = max(len(l) for l in lists)

    arr = np.array([
        l + [np.nan]*(max_len-len(l))
        for l in lists
    ])

    avg = np.nanmean(arr, axis=0)

    puzzle_avg_mt[pzid] = [round(x, 2) for x in avg.tolist()]

print(puzzle_avg_mt, "\n")

# ------------------------
# หา MTq (Percentile75)
# ------------------------
puzzle_mtq = {}

for pzid, mt_list in puzzle_avg_mt.items():

    mtq = np.percentile(mt_list, 75)

    puzzle_mtq[pzid] = round(mtq,2)

print('puzzle_mtq',puzzle_mtq, "\n")

# ------------------------
# หา T และ A เฉลี่ยต่อ Puzzle
# ------------------------
puzzle_T = defaultdict(list)
puzzle_A = defaultdict(list)

for row in mock_data:
    pzid = row["pzid"]
    puzzle_T[pzid].append(row["play_time"])
    puzzle_A[pzid].append(row["action_count"])


# ------------------------
# รวมผลลัพธ์ทั้งหมด
# ------------------------
dataset = []

for pzid in sorted(puzzle_mtq.keys()):

    avg_T = round(np.mean(puzzle_T[pzid]), 2)
    avg_A = round(np.mean(puzzle_A[pzid]), 2)

    dataset.append([
        pzid,
        puzzle_mtq[pzid],
        avg_T,
        avg_A
    ])

print("pzid | MTq | T | A")
for row in dataset:
    print(row)

print("\nDataset =", dataset)