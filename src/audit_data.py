"""Audit awal dataset PhiUSIIL (Bab 5.1 Buku Petunjuk TTKI).

Hanya statistik deskriptif; tidak ada model yang dilatih dan tidak ada
keputusan split yang diambil dari skrip ini.

Pemakaian (dari akar repositori):
    python src/audit_data.py
Keluaran: results/audit_summary.json
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import tldextract
from sklearn.metrics import roc_auc_score

CSV = Path("data/raw/PhiUSIIL_Phishing_URL_Dataset.csv")
OUT = Path("results/audit_summary.json")

LEXICAL = [
    "URLLength", "DomainLength", "IsDomainIP", "TLDLength", "NoOfSubDomain",
    "HasObfuscation", "NoOfObfuscatedChar", "ObfuscationRatio",
    "NoOfLettersInURL", "LetterRatioInURL", "NoOfDegitsInURL",
    "DegitRatioInURL", "NoOfEqualsInURL", "NoOfQMarkInURL",
    "NoOfAmpersandInURL", "NoOfOtherSpecialCharsInURL",
    "SpacialCharRatioInURL", "IsHTTPS",
]
CORPUS_DERIVED = ["URLSimilarityIndex", "CharContinuationRate", "TLDLegitimateProb", "URLCharProb"]
IDENT_TEXT = ["FILENAME", "URL", "Domain", "TLD", "Title"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def main():
    df = pd.read_csv(CSV)
    # label asli: 1 = legitimate, 0 = phishing (diverifikasi dari domain contoh dan URLSimilarityIndex)
    df["phish"] = (df["label"] == 0).astype(int)
    num = df.select_dtypes("number").drop(columns=["label", "phish"])
    content = [c for c in num.columns if c not in LEXICAL + CORPUS_DERIVED]

    ext = tldextract.TLDExtract(suffix_list_urls=(), cache_dir=None)  # daftar sufiks bawaan, tanpa jaringan
    hosts = df["Domain"].str.lower().drop_duplicates()
    peta = {h: ext(h).top_domain_under_public_suffix for h in hosts}
    df["etld1"] = df["Domain"].str.lower().map(peta)
    g = df.groupby("etld1").agg(n=("phish", "size"), ph=("phish", "mean"))

    auc = {c: roc_auc_score(df["phish"], num[c]) for c in num.columns}
    auc = {c: round(max(a, 1 - a), 4) for c, a in auc.items()}

    ringkasan = {
        "berkas": str(CSV),
        "sha256": sha256(CSV),
        "baris": int(len(df)),
        "kolom": int(df.shape[1] - 2),  # tanpa kolom bantu phish dan etld1
        "missing_total": int(df.drop(columns=["etld1"]).isna().sum().sum()),
        "inf_total": int(np.isinf(num).sum().sum()),
        "label_asli": {"1_legitimate": int((df.label == 1).sum()), "0_phishing": int((df.label == 0).sum())},
        "proporsi_phishing": round(float(df["phish"].mean()), 4),
        "url_duplikat_baris": int(df["URL"].duplicated(keep=False).sum()),
        "url_unik": int(df["URL"].nunique()),
        "url_duplikat_label_konflik": int((df.groupby("URL")["label"].nunique() > 1).sum()),
        "host_unik": int(df["Domain"].nunique()),
        "etld1_unik": int(df["etld1"].nunique()),
        "etld1_kosong_baris": int((df["etld1"] == "").sum()),
        "etld1_grup_campuran": int(((g.ph > 0) & (g.ph < 1)).sum()),
        "etld1_grup_terbesar": {k: int(v) for k, v in g.sort_values("n", ascending=False).head(8)["n"].items()},
        "etld1_grup_lebih_100_baris": int((g.n > 100).sum()),
        "etld1_baris_di_grup_lebih_100": int(g[g.n > 100].n.sum()),
        "jumlah_fitur_numerik": int(num.shape[1]),
        "kelompok_fitur": {"leksikal_url": len(LEXICAL), "turunan_korpus": len(CORPUS_DERIVED), "konten_html": len(content)},
        "urlsimilarityindex_legit_sama_100": float((df.loc[df.phish == 0, "URLSimilarityIndex"] == 100).mean()),
        "urlsimilarityindex_phishing_kurang_100": float((df.loc[df.phish == 1, "URLSimilarityIndex"] < 100).mean()),
        "auc_satu_fitur_leksikal_maks": max(auc[c] for c in LEXICAL),
        "auc_satu_fitur_di_atas_0_95": {c: a for c, a in sorted(auc.items(), key=lambda x: -x[1]) if a >= 0.95},
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(ringkasan, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(ringkasan, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
