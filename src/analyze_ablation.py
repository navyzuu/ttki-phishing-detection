"""Selisih F1 ablation post-hoc (E, F) terhadap skenario utama (B, C), interval bootstrap 95%.

Keluaran: results/analysis_ablasi.csv
"""
import numpy as np
import pandas as pd

from evaluation import selisih_f1
from preprocessing import SEEDS
from run_experiments import INTERIM

PASANGAN = [
    ("E-B: efek 4 fitur turunan korpus, split acak", "E", "B"),
    ("F-C: efek 4 fitur turunan korpus, split grup", "F", "C"),
    ("E-F: acak vs grup, URL-only + korpus", "E", "F"),
]


def muat(sk, model, seed):
    return np.load(INTERIM / f"y_test_{sk}_{model}_{seed}.npy"), np.load(INTERIM / f"skor_test_{sk}_{model}_{seed}.npy")


baris = []
for model in ("LR", "RF"):
    for nama, a, b in PASANGAN:
        for seed in SEEDS:
            ya, sa = muat(a, model, seed)
            yb, sb = muat(b, model, seed)
            baris.append({"perbandingan": nama, "model": model, "seed": seed, "post_hoc": True,
                          **selisih_f1(ya, sa, yb, sb, n_boot=1000, seed=seed)})
out = pd.DataFrame(baris)
out.to_csv("results/analysis_ablasi.csv", index=False)
print(out.groupby(["perbandingan", "model"]).agg(selisih_rata2=("selisih", "mean"), sd=("selisih", "std"),
                                                 seed_ci_tanpa_nol=("mencakup_nol", lambda s: int((~s).sum()))).round(5).to_string())
