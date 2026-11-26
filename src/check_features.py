"""Bandingkan fitur hasil ekstrak() dengan kolom CSV pada 20.000 baris acak (tanpa memakai label).

Keluaran: results/feature_agreement.json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from features import NAMA_FITUR, ekstrak
from preprocessing import CSV

df = pd.read_csv(CSV).sample(20000, random_state=0)
mine = pd.DataFrame([ekstrak(u) for u in df["URL"]], columns=NAMA_FITUR, index=df.index)
hasil = {}
for c in NAMA_FITUR:
    a, b = mine[c].astype(float), df[c].astype(float)
    korelasi = float(np.corrcoef(a, b)[0, 1]) if a.std() > 0 and b.std() > 0 else None
    hasil[c] = {"cocok_persis": round(float((a.round(6) == b.round(6)).mean()), 4),
                "korelasi": None if korelasi is None else round(korelasi, 4)}
Path("results/feature_agreement.json").write_text(json.dumps(hasil, indent=2), encoding="utf-8")
for c, v in hasil.items():
    print(f"{c:30s} cocok persis {v['cocok_persis']:.4f}  korelasi {v['korelasi']}")
