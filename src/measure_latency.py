"""Waktu inferensi per URL (docs/decisions.md D8).

- URL-only (skenario B): ekstraksi 18 fitur dari string URL + predict_proba, satu URL per panggilan.
- Semua fitur (skenario A): hanya predict_proba dari baris fitur siap pakai. Ekstraksi 28 fitur konten HTML
  (pengambilan dan penguraian halaman) TIDAK dapat diukur dari CSV dan tidak dilakukan, sehingga angka ini
  adalah BATAS BAWAH waktu sebenarnya.
Model dilatih pada train split acak seed 42 dengan konfigurasi dari results/config_beku.json.
Prediksi memakai satu thread agar adil. Keluaran: results/latency.json
"""
import json
import platform
import sys
from pathlib import Path

import numpy as np

from evaluation import waktu_inferensi_ms
from features import ekstrak
from preprocessing import buat_split, muat_bersih
from run_experiments import CONFIG, buat_model, matriks_fitur


def main():
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))["terpilih"]
    df = muat_bersih()
    y = df["phish"].to_numpy()
    tr, _, te = buat_split(df, "acak", 42)
    urls = df["URL"].to_numpy()
    rng = np.random.default_rng(42)
    contoh = rng.choice(te, size=500, replace=False)  # URL dari test, hanya untuk mengukur waktu
    hasil = {"mesin": {"python": sys.version.split()[0], "platform": platform.platform(), "prosesor": platform.processor()},
             "catatan": "satu URL per panggilan; predict_proba satu thread; 500 URL x 5 pengulangan; median dan p95",
             "hasil": {}}
    for nama in ("LR", "RF"):
        for sk, kel in (("B", "url_only"), ("A", "semua")):
            X = matriks_fitur(df, kel)
            m = buat_model(nama, cfg[f"{sk}|{nama}"], 42).fit(X[tr], y[tr])
            if nama == "RF":
                m.set_params(n_jobs=1)
            if kel == "url_only":
                r = waktu_inferensi_ms(m, urls[contoh], ekstrak=ekstrak)
            else:
                r = waktu_inferensi_ms(m, None, X_siap=X[contoh])
            hasil["hasil"][f"{sk}|{nama}"] = {"fitur": kel, "mencakup": "ekstraksi + prediksi" if kel == "url_only" else "prediksi saja (batas bawah)", **r}
            print(sk, nama, kel, f"median {r['median_ms']:.3f} ms | p95 {r['p95_ms']:.3f} ms", flush=True)
    # waktu ekstraksi saja (URL-only) untuk memisahkan komponen
    import time
    t = []
    for u in urls[contoh]:
        t0 = time.perf_counter(); ekstrak(u); t.append((time.perf_counter() - t0) * 1000)
    hasil["ekstraksi_saja_url_only_ms"] = {"median": float(np.median(t)), "p95": float(np.percentile(t, 95))}
    print("ekstraksi saja:", hasil["ekstraksi_saja_url_only_ms"])
    Path("results/latency.json").write_text(json.dumps(hasil, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
