"""Selisih F1 antar skenario dengan interval bootstrap 95% (docs/decisions.md D7).

Dijalankan setelah run_experiments.py final. Memakai skor test yang tersimpan di data/interim.
Selisih per seed; selisih 'berarti' bila interval tidak mencakup nol.
Keluaran: results/analysis_selisih.csv
"""
import numpy as np
import pandas as pd

from evaluation import selisih_f1
from preprocessing import SEEDS, buat_split, muat_bersih
from run_experiments import INTERIM, aturan_bentuk_url

PASANGAN = [  # (nama, A, B): selisih = F1(A) - F1(B)
    ("A-D: acak vs grup, fitur lengkap", "A", "D"),
    ("B-C: acak vs grup, URL-only", "B", "C"),
    ("A-B: lengkap vs URL-only, acak", "A", "B"),
    ("D-C: lengkap vs URL-only, grup", "D", "C"),
]


def muat(sk, model, seed):
    return np.load(INTERIM / f"y_test_{sk}_{model}_{seed}.npy"), np.load(INTERIM / f"skor_test_{sk}_{model}_{seed}.npy")


def main():
    df = muat_bersih()
    y_all = df["phish"].to_numpy()
    aturan = aturan_bentuk_url(df)
    baris = []
    for model in ("LR", "RF"):
        for nama, a, b in PASANGAN:
            for seed in SEEDS:
                ya, sa = muat(a, model, seed)
                yb, sb = muat(b, model, seed)
                baris.append({"perbandingan": nama, "model": model, "seed": seed, **selisih_f1(ya, sa, yb, sb, n_boot=1000, seed=seed)})
        # model URL-only melawan aturan satu baris, pada split yang sama
        for sk, skema in (("B", "acak"), ("C", "grup")):
            for seed in SEEDS:
                te = buat_split(df, skema, seed)[2]
                ym, sm = muat(sk, model, seed)
                baris.append({"perbandingan": f"{sk} minus ATURAN ({skema})", "model": model, "seed": seed,
                              **selisih_f1(ym, sm, y_all[te], aturan[te], n_boot=1000, seed=seed)})
    out = pd.DataFrame(baris)
    out.to_csv("results/analysis_selisih.csv", index=False)
    ring = out.groupby(["perbandingan", "model"]).agg(selisih_rata2=("selisih", "mean"), sd=("selisih", "std"),
                                                      seed_ci_tidak_mencakup_nol=("mencakup_nol", lambda s: int((~s).sum()))).round(5)
    print(ring.to_string())


if __name__ == "__main__":
    main()
