"""Pembersihan data dan pembagian split sesuai docs/decisions.md (D1 sampai D6).

Tidak ada transformasi yang dipelajari dari data di modul ini. Imputer, scaler,
dan seleksi fitur (jika ada) harus di-fit hanya pada train di dalam pipeline model.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import tldextract
from sklearn.model_selection import GroupShuffleSplit, StratifiedGroupKFold, train_test_split

CSV = Path("data/raw/PhiUSIIL_Phishing_URL_Dataset.csv")
SEEDS = (42, 43, 44, 45, 46)
RASIO = (0.70, 0.15, 0.15)  # train, validation, test (D6)

LEXICAL = [
    "URLLength", "DomainLength", "IsDomainIP", "TLDLength", "NoOfSubDomain",
    "HasObfuscation", "NoOfObfuscatedChar", "ObfuscationRatio",
    "NoOfLettersInURL", "LetterRatioInURL", "NoOfDegitsInURL",
    "DegitRatioInURL", "NoOfEqualsInURL", "NoOfQMarkInURL",
    "NoOfAmpersandInURL", "NoOfOtherSpecialCharsInURL",
    "SpacialCharRatioInURL", "IsHTTPS",
]
CORPUS_DERIVED = ["URLSimilarityIndex", "CharContinuationRate", "TLDLegitimateProb", "URLCharProb"]
DIKECUALIKAN = ["FILENAME", "URL", "Domain", "TLD", "Title", "label"]  # D3


def muat_bersih(csv=CSV, private_suffix=False, cache=Path("data/interim/df_bersih.pkl")):
    """Muat CSV, buang URL duplikat (D2), tambah kolom `phish` (D1) dan `grup` (D5). Hasil di-cache."""
    if cache is not None and not private_suffix and Path(cache).exists():
        return pd.read_pickle(cache)
    df = pd.read_csv(csv)
    df = df.drop_duplicates(subset="URL", keep="first").reset_index(drop=True)
    df["phish"] = (df["label"] == 0).astype(int)  # kelas positif = phishing

    ext = tldextract.TLDExtract(suffix_list_urls=(), cache_dir=None, include_psl_private_domains=private_suffix)
    host = df["Domain"].str.lower()
    peta = {h: ext(h).top_domain_under_public_suffix for h in host.drop_duplicates()}
    grup = host.map(peta)
    df["grup"] = grup.where(grup != "", host)  # eTLD+1 kosong: pakai host penuh (D5)
    if cache is not None and not private_suffix:
        Path(cache).parent.mkdir(parents=True, exist_ok=True)
        df.to_pickle(cache)
    return df


def kolom_fitur(df, kelompok):
    """Daftar kolom fitur: 'url_only' (18), 'semua' (50), atau 'url_plus_korpus' (22)."""
    numerik = [c for c in df.select_dtypes("number").columns if c not in ("label", "phish")]
    if kelompok == "url_only":
        return list(LEXICAL)
    if kelompok == "url_plus_korpus":
        return LEXICAL + CORPUS_DERIVED
    if kelompok == "semua":
        return numerik
    raise ValueError(f"kelompok fitur tidak dikenal: {kelompok}")


def _hitung_split(df, skema, seed):
    """Kembalikan indeks posisi (train, validation, test) sebagai array numpy.

    skema 'acak'  : stratifikasi menurut kelas.
    skema 'grup'  : seluruh baris satu eTLD+1 berada pada satu bagian.
    """
    idx = np.arange(len(df))
    y = df["phish"].to_numpy()
    sisa = RASIO[1] + RASIO[2]
    if skema == "acak":
        tr, rest = train_test_split(idx, test_size=sisa, stratify=y, random_state=seed)
        va, te = train_test_split(rest, test_size=RASIO[2] / sisa, stratify=y[rest], random_state=seed)
        return tr, va, te
    if skema == "grup":
        # Stratified group: 20 lipatan (~5% tiap lipatan), semua baris satu grup pada satu lipatan,
        # proporsi kelas tiap lipatan dijaga mendekati total. Lipatan diacak lalu dirakit 14/3/3.
        g = df["grup"].to_numpy()
        sgkf = StratifiedGroupKFold(n_splits=20, shuffle=True, random_state=seed)
        lipatan = [te for _, te in sgkf.split(idx, y, groups=g)]
        urut = np.random.RandomState(seed).permutation(len(lipatan))
        gabung = lambda ks: np.sort(np.concatenate([lipatan[k] for k in ks]))
        return gabung(urut[:14]), gabung(urut[14:17]), gabung(urut[17:])
    if skema == "grup_shuffle":
        # Versi naif (GroupShuffleSplit, seperti studi terdahulu): proporsi kelas tiap bagian tidak dijaga.
        g = df["grup"].to_numpy()
        gss = GroupShuffleSplit(n_splits=1, test_size=sisa, random_state=seed)
        tr, rest = next(gss.split(idx, y, groups=g))
        gss2 = GroupShuffleSplit(n_splits=1, test_size=RASIO[2] / sisa, random_state=seed)
        a, b = next(gss2.split(rest, y[rest], groups=g[rest]))
        return tr, rest[a], rest[b]
    raise ValueError(f"skema tidak dikenal: {skema}")


def buat_split(df, skema, seed, cache=Path("data/interim")):
    """Pembungkus _hitung_split dengan cache (split per grup lambat, sekitar beberapa menit)."""
    f = cache / f"split_{skema}_{seed}.npz"
    if f.exists():
        z = np.load(f)
        return z["tr"], z["va"], z["te"]
    tr, va, te = _hitung_split(df, skema, seed)
    cache.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(f, tr=tr, va=va, te=te)
    return tr, va, te
