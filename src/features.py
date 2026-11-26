"""Ekstraksi fitur leksikal langsung dari string URL (18 fitur, nama mengikuti kolom PhiUSIIL).

Satu fungsi (`ekstrak`) dipakai untuk melatih model URL-only dan untuk mengukur waktu
ekstraksi, sehingga keduanya konsisten. Definisi PhiUSIIL tidak didokumentasikan dan
sebagian tidak dapat direproduksi persis dari string URL; tingkat kecocokan dengan
kolom CSV dilaporkan oleh src/check_features.py (lihat docs/decisions.md, Perubahan 2).
"""
import re

import tldextract

_EXT = tldextract.TLDExtract(suffix_list_urls=(), cache_dir=None)
_IP = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")
_PCT = re.compile(r"%[0-9a-fA-F]{2}")

NAMA_FITUR = [
    "URLLength", "DomainLength", "IsDomainIP", "TLDLength", "NoOfSubDomain",
    "HasObfuscation", "NoOfObfuscatedChar", "ObfuscationRatio",
    "NoOfLettersInURL", "LetterRatioInURL", "NoOfDegitsInURL",
    "DegitRatioInURL", "NoOfEqualsInURL", "NoOfQMarkInURL",
    "NoOfAmpersandInURL", "NoOfOtherSpecialCharsInURL",
    "SpacialCharRatioInURL", "IsHTTPS",
]


def _host(url):
    sisa = url.split("://", 1)[-1]
    host = re.split(r"[/?#]", sisa, maxsplit=1)[0]
    host = host.rsplit("@", 1)[-1]
    return re.sub(r":\d+$", "", host).lower()


def ekstrak(url):
    """Kembalikan daftar 18 nilai fitur (urutan = NAMA_FITUR) dari satu string URL."""
    n = len(url)
    host = _host(url)
    label = host.split(".")
    tld = label[-1] if host else ""
    huruf = sum(c.isalpha() for c in url)
    angka = sum(c.isdigit() for c in url)
    sama, tanya, dan = url.count("="), url.count("?"), url.count("&")
    lain = sum((not c.isalnum()) and c not in "=?&/." for c in url)
    pct = len(_PCT.findall(url))
    return [
        n,
        len(host),
        int(bool(_IP.match(host))),
        len(tld),
        max(host.count(".") - 1, 0),
        int(pct > 0),
        pct,
        3 * pct / n if n else 0.0,
        huruf,
        huruf / n if n else 0.0,
        angka,
        angka / n if n else 0.0,
        sama,
        tanya,
        dan,
        lain,
        (sama + tanya + dan + lain) / n if n else 0.0,
        int(url.lower().startswith("https")),
    ]
