"""Analisis post-hoc (deskriptif): asal false negative pada seed dengan F1 terendah (skenario C, Random Forest).

Keluaran: results/analysis_outlier_seed44.json
"""
import json

import numpy as np

from preprocessing import buat_split, muat_bersih

df = muat_bersih()
te = buat_split(df, "grup", 44)[2]
y = np.load("data/interim/y_test_C_RF_44.npy")
s = np.load("data/interim/skor_test_C_RF_44.npy")
assert (y == df["phish"].to_numpy()[te]).all()
d = df.iloc[te].assign(fn=((y == 1) & (s < 0.5)))
fn = d[d.fn]
g = fn.groupby("grup").size().sort_values(ascending=False)
top = g.index[0]
sub = d[d.grup == top]
hasil = {"fn_total": int(len(fn)), "grup_teratas": top, "fn_dari_grup_teratas": int(g.iloc[0]),
         "pangsa_fn_grup_teratas": round(float(g.iloc[0] / len(fn)), 3),
         "baris_grup_di_test": int(len(sub)), "phishing_di_grup_di_test": int(sub["phish"].sum()),
         "ukuran_grup_di_seluruh_data": int((df["grup"] == top).sum()),
         "grup_penyumbang_fn_berikutnya": {k: int(v) for k, v in g.iloc[1:5].items()}}
open("results/analysis_outlier_seed44.json", "w", encoding="utf-8").write(json.dumps(hasil, indent=2, ensure_ascii=False))
print(json.dumps(hasil, indent=2, ensure_ascii=False))
