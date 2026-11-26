"""Ablation POST-HOC: URL-only (18 fitur hasil ekstraksi) + 4 fitur turunan korpus (docs/decisions.md D4).

Dijalankan SETELAH data test dibuka pada eksperimen utama, sehingga seluruh hasil dilabeli post-hoc.
Aturan sama dengan eksperimen utama: hyperparameter dipilih hanya pada validation (seed 42),
konfigurasi dibekukan lewat commit, lalu test dihitung sekali.

  python src/run_ablation.py tuning   -> results/config_ablasi.json
  python src/run_ablation.py final    -> results/metrics_ablasi.csv  (menolak jalan bila config belum di-commit)
Skenario: E = split acak, F = split grup eTLD+1 (keduanya 22 fitur).
"""
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

from evaluation import metrik
from preprocessing import CORPUS_DERIVED, SEEDS, buat_split, muat_bersih
from run_experiments import GRID, INTERIM, buat_model, matriks_fitur

SKENARIO = {"E": "acak", "F": "grup"}
CONFIG = Path("results/config_ablasi.json")
HASIL = Path("results/metrics_ablasi.csv")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def fitur(df):
    return np.hstack([matriks_fitur(df, "url_only"), df[CORPUS_DERIVED].to_numpy(dtype=float)])


def tuning():
    df = muat_bersih()
    y, X = df["phish"].to_numpy(), fitur(df)
    out = {"post_hoc": True, "seed_tuning": 42, "dibuat": time.strftime("%Y-%m-%d %H:%M:%S"), "terpilih": {}, "f1_validation_semua": {}}
    for sk, skema in SKENARIO.items():
        tr, va, _ = buat_split(df, skema, 42)  # indeks test diabaikan
        for nama, grid in GRID.items():
            s = []
            for p in grid:
                m = buat_model(nama, p, 42).fit(X[tr], y[tr])
                s.append(f1_score(y[va], m.predict(X[va])))
                log(f"tuning {sk} {nama} {p} F1 validation = {s[-1]:.5f}")
            i = int(np.argmax(s))
            out["terpilih"][f"{sk}|{nama}"] = grid[i]
            out["f1_validation_semua"][f"{sk}|{nama}"] = [round(v, 6) for v in s]
    CONFIG.write_text(json.dumps(out, indent=2), encoding="utf-8")
    log("config tertulis:", CONFIG)


def beku():
    ada = subprocess.run(["git", "ls-files", "--error-unmatch", str(CONFIG)], capture_output=True).returncode == 0
    bersih = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", str(CONFIG)]).returncode == 0
    return ada and bersih


def final():
    if not beku():
        sys.exit("DITOLAK: results/config_ablasi.json belum di-commit atau berubah.")
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))["terpilih"]
    df = muat_bersih()
    y, X = df["phish"].to_numpy(), fitur(df)
    baris = []
    for sk, skema in SKENARIO.items():
        for seed in SEEDS:
            tr, va, te = buat_split(df, skema, seed)
            for nama in GRID:
                m = buat_model(nama, cfg[f"{sk}|{nama}"], seed).fit(X[tr], y[tr])
                for bagian, idx in (("validation", va), ("test", te)):
                    skor = m.predict_proba(X[idx])[:, 1]
                    if bagian == "test":
                        np.save(INTERIM / f"skor_test_{sk}_{nama}_{seed}.npy", skor)
                        np.save(INTERIM / f"y_test_{sk}_{nama}_{seed}.npy", y[idx])
                    baris.append({"skenario": sk, "split": skema, "fitur": "url_only+korpus", "model": nama, "seed": seed,
                                  "bagian": bagian, "n": len(idx), "n_phishing": int(y[idx].sum()),
                                  "params": json.dumps(cfg[f"{sk}|{nama}"]), "post_hoc": True, **metrik(y[idx], skor)})
                log(f"selesai {sk} {nama} seed {seed}")
    pd.DataFrame(baris).to_csv(HASIL, index=False)
    log("tertulis:", HASIL)


if __name__ == "__main__":
    {"tuning": tuning, "final": final}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: sys.exit("pakai: tuning | final"))()
