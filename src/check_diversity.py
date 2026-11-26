"""Apakah tiap seed menghasilkan pembagian berbeda? Hitung Jaccard himpunan test antar seed."""
import json
from itertools import combinations
from pathlib import Path

from preprocessing import SEEDS, buat_split, muat_bersih

df = muat_bersih()
hasil = {}
for skema in ("acak", "grup", "grup_shuffle"):
    te = {s: set(buat_split(df, skema, s)[2]) for s in SEEDS}
    j = [len(te[a] & te[b]) / len(te[a] | te[b]) for a, b in combinations(SEEDS, 2)]
    hasil[skema] = {"jaccard_test_antar_seed_min": round(min(j), 4), "jaccard_test_antar_seed_maks": round(max(j), 4)}
Path("results/split_diversity.json").write_text(json.dumps(hasil, indent=2), encoding="utf-8")
print(json.dumps(hasil, indent=2))
