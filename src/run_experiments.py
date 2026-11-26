"""Eksperimen skenario A sampai D (docs/decisions.md).

Fase 1  : python src/run_experiments.py tuning
          Memilih hyperparameter pada VALIDATION (seed 42). Indeks test tidak dipakai.
          Menulis results/config_beku.json. Setelah itu berkas harus di-commit.
Fase 2  : python src/run_experiments.py final
          Menolak berjalan jika config_beku.json belum di-commit atau berubah.
          Melatih tiap skenario, model, dan seed pada train, lalu mencatat metrik
          validation dan test sekali ke results/metrics.csv.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from evaluation import metrik
from features import ekstrak
from preprocessing import SEEDS, buat_split, kolom_fitur, muat_bersih

SKENARIO = {"A": ("acak", "semua"), "B": ("acak", "url_only"), "C": ("grup", "url_only"), "D": ("grup", "semua")}
GRID = {
    "LR": [{"C": c} for c in (0.01, 0.1, 1.0, 10.0)],
    "RF": [{"max_depth": d, "min_samples_leaf": m} for d in (10, None) for m in (1, 5)],
}
CONFIG = Path("results/config_beku.json")
METRIK = Path("results/metrics.csv")
INTERIM = Path("data/interim")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def matriks_fitur(df, kelompok):
    """Matriks fitur. url_only = fitur hasil src/features.py (di-cache); semua = 50 kolom CSV."""
    if kelompok == "url_only":
        f = INTERIM / "fitur_url_only.npy"
        if f.exists():
            return np.load(f)
        X = np.asarray([ekstrak(u) for u in df["URL"]], dtype=float)
        INTERIM.mkdir(parents=True, exist_ok=True)
        np.save(f, X)
        return X
    return df[kolom_fitur(df, kelompok)].to_numpy(dtype=float)


def buat_model(nama, params, seed):
    if nama == "LR":
        return make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=seed, **params))
    return RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=seed, **params)


def fase_tuning():
    df = muat_bersih()
    y = df["phish"].to_numpy()
    hasil = {"seed_tuning": 42, "dibuat": time.strftime("%Y-%m-%d %H:%M:%S"), "grid": GRID, "terpilih": {}, "f1_validation_semua": {}}
    for sk, (skema, kel) in SKENARIO.items():
        X = matriks_fitur(df, kel)
        tr, va, _ = buat_split(df, skema, 42)  # indeks test sengaja diabaikan
        for nama, grid in GRID.items():
            skor_f1 = []
            for params in grid:
                m = buat_model(nama, params, 42).fit(X[tr], y[tr])
                f1 = f1_score(y[va], m.predict(X[va]))
                skor_f1.append(f1)
                log(f"tuning {sk} {nama} {params} F1 validation = {f1:.5f}")
            i = int(np.argmax(skor_f1))
            hasil["terpilih"][f"{sk}|{nama}"] = grid[i]
            hasil["f1_validation_semua"][f"{sk}|{nama}"] = [round(s, 6) for s in skor_f1]
    CONFIG.write_text(json.dumps(hasil, indent=2), encoding="utf-8")
    log("config tertulis:", CONFIG)


def aturan_bentuk_url(df):
    """Baseline diagnostik tanpa parameter dan tanpa pelatihan (post-hoc, lihat docs/decisions.md Perubahan 3).

    Skor phishing = 1 bila URL BUKAN berbentuk https://www.<domain> tanpa path; selain itu 0.
    """
    p = df["URL"].str.replace(r"^https?://", "", regex=True)
    mirip = (~p.str.contains(r"/.+|\?", regex=True)) & p.str.startswith("www.") & df["URL"].str.startswith("https")
    return (~mirip).astype(float).to_numpy()


def config_dibekukan():
    """Pastikan config_beku.json sudah di-commit dan tidak berubah sejak commit."""
    ada = subprocess.run(["git", "ls-files", "--error-unmatch", str(CONFIG)], capture_output=True).returncode == 0
    bersih = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", str(CONFIG)]).returncode == 0
    return ada and bersih


def fase_final():
    if not config_dibekukan():
        sys.exit("DITOLAK: results/config_beku.json belum di-commit atau berubah. Bekukan dulu (commit) sebelum membuka data test.")
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))["terpilih"]
    df = muat_bersih()
    y = df["phish"].to_numpy()
    baris = []
    for sk, (skema, kel) in SKENARIO.items():
        X = matriks_fitur(df, kel)
        for seed in SEEDS:
            tr, va, te = buat_split(df, skema, seed)
            for nama in GRID:
                m = buat_model(nama, cfg[f"{sk}|{nama}"], seed).fit(X[tr], y[tr])
                for bagian, idx in (("validation", va), ("test", te)):
                    skor = m.predict_proba(X[idx])[:, 1]
                    if bagian == "test":
                        np.save(INTERIM / f"skor_test_{sk}_{nama}_{seed}.npy", skor)
                        np.save(INTERIM / f"y_test_{sk}_{nama}_{seed}.npy", y[idx])
                    baris.append({"skenario": sk, "split": skema, "fitur": kel, "model": nama, "seed": seed,
                                  "bagian": bagian, "n": len(idx), "n_phishing": int(y[idx].sum()),
                                  "params": json.dumps(cfg[f"{sk}|{nama}"]), **metrik(y[idx], skor)})
                log(f"selesai {sk} {nama} seed {seed}")
            pd.DataFrame(baris).to_csv(METRIK, index=False)  # simpan bertahap
    skor_aturan = aturan_bentuk_url(df)
    for skema in ("acak", "grup"):
        for seed in SEEDS:
            _, va, te = buat_split(df, skema, seed)
            for bagian, idx in (("validation", va), ("test", te)):
                baris.append({"skenario": "R_" + skema, "split": skema, "fitur": "bentuk_url", "model": "ATURAN", "seed": seed,
                              "bagian": bagian, "n": len(idx), "n_phishing": int(y[idx].sum()), "params": "{}",
                              **metrik(y[idx], skor_aturan[idx])})
    pd.DataFrame(baris).to_csv(METRIK, index=False)
    log("metrik tertulis:", METRIK)


if __name__ == "__main__":
    fase = sys.argv[1] if len(sys.argv) > 1 else ""
    {"tuning": fase_tuning, "final": fase_final}.get(fase, lambda: sys.exit("pakai: tuning | final"))()
