"""Verifikasi split tanpa melatih model: ukuran, rasio kelas, dan tumpang tindih grup.

Pemakaian: python src/check_splits.py
Keluaran : results/split_check.json
"""
import json
from pathlib import Path

from preprocessing import SEEDS, buat_split, muat_bersih


def ringkas(df, tr, va, te):
    out = {}
    for nama, idx in (("train", tr), ("validation", va), ("test", te)):
        s = df.iloc[idx]
        out[nama] = {"baris": int(len(s)), "proporsi_phishing": round(float(s["phish"].mean()), 4), "grup": int(s["grup"].nunique())}
    g = {n: set(df.iloc[i]["grup"]) for n, i in (("train", tr), ("validation", va), ("test", te))}
    out["grup_tumpang_tindih"] = {
        "train_validation": len(g["train"] & g["validation"]),
        "train_test": len(g["train"] & g["test"]),
        "validation_test": len(g["validation"] & g["test"]),
    }
    idx_all = set(tr) | set(va) | set(te)
    out["indeks_unik_dan_lengkap"] = (len(tr) + len(va) + len(te) == len(idx_all) == len(df))
    return out


def main():
    df = muat_bersih()
    hasil = {"baris_setelah_dedup": int(len(df)), "proporsi_phishing_total": round(float(df["phish"].mean()), 4),
             "grup_unik": int(df["grup"].nunique())}
    for skema in ("acak", "grup", "grup_shuffle"):
        hasil[skema] = {str(seed): ringkas(df, *buat_split(df, skema, seed)) for seed in SEEDS}
    Path("results").mkdir(exist_ok=True)
    Path("results/split_check.json").write_text(json.dumps(hasil, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(hasil, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
