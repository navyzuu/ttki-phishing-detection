"""Metrik, interval bootstrap, dan pengukuran waktu inferensi (docs/decisions.md D7 dan D8).

Kelas positif = phishing (y = 1). `skor` adalah probabilitas atau skor kelas positif.
"""
import time

import numpy as np
from sklearn.metrics import (average_precision_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)


def metrik(y, skor, ambang=0.5):
    y = np.asarray(y)
    pred = (np.asarray(skor) >= ambang).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "f1": f1_score(y, pred, zero_division=0),
        "precision": precision_score(y, pred, zero_division=0),
        "recall": recall_score(y, pred, zero_division=0),
        "roc_auc": roc_auc_score(y, skor),
        "pr_auc": average_precision_score(y, skor),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def _bootstrap(y, skor, fungsi, n_boot, rng):
    y, skor = np.asarray(y), np.asarray(skor)
    n = len(y)
    out = np.empty(n_boot)
    for i in range(n_boot):
        b = rng.integers(0, n, n)
        out[i] = fungsi(y[b], skor[b])
    return out


def _f1(y, skor):
    return f1_score(y, (skor >= 0.5).astype(int), zero_division=0)


def ci_f1(y, skor, n_boot=1000, seed=42):
    """Interval 95% persentil untuk F1."""
    d = _bootstrap(y, skor, _f1, n_boot, np.random.default_rng(seed))
    return float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def selisih_f1(y_a, skor_a, y_b, skor_b, n_boot=1000, seed=42):
    """Selisih F1 (A dikurangi B) dengan interval 95%.

    A dan B boleh memakai himpunan test berbeda (mis. random split vs split grup),
    sehingga keduanya di-resample secara independen. Selisih 'berarti' bila interval tidak mencakup nol (D7).
    """
    rng = np.random.default_rng(seed)
    da = _bootstrap(y_a, skor_a, _f1, n_boot, rng)
    db = _bootstrap(y_b, skor_b, _f1, n_boot, rng)
    d = da - db
    titik = _f1(np.asarray(y_a), np.asarray(skor_a)) - _f1(np.asarray(y_b), np.asarray(skor_b))
    lo, hi = np.percentile(d, [2.5, 97.5])
    return {"selisih": float(titik), "ci_bawah": float(lo), "ci_atas": float(hi), "mencakup_nol": bool(lo <= 0 <= hi)}


def waktu_inferensi_ms(model, urls, ekstrak=None, X_siap=None, n_url=500, ulangi=5):
    """Median waktu per URL (milidetik), satu URL per panggilan, dari `ulangi` pengulangan.

    Jika `ekstrak` diberikan: waktu = ekstraksi dari string URL + predict_proba.
    Jika tidak: `X_siap` (baris fitur siap pakai) dipakai dan hanya waktu prediksi yang diukur
    (fitur konten HTML tidak dapat diekstrak dari CSV; lihat D8).
    Mengembalikan dict dengan median, p95, dan daftar median tiap pengulangan.
    """
    per_ulang = []
    for _ in range(ulangi):
        t = []
        for i in range(min(n_url, len(urls) if ekstrak else len(X_siap))):
            t0 = time.perf_counter()
            x = np.asarray([ekstrak(urls[i])]) if ekstrak else X_siap[i:i + 1]
            model.predict_proba(x)
            t.append((time.perf_counter() - t0) * 1000)
        per_ulang.append(t)
    semua = np.concatenate(per_ulang)
    return {"median_ms": float(np.median(semua)), "p95_ms": float(np.percentile(semua, 95)),
            "median_tiap_pengulangan_ms": [float(np.median(t)) for t in per_ulang]}
