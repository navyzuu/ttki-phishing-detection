"""Grafik dan tabel paper dari results/ (tanpa menjalankan ulang eksperimen).

Keluaran: figures/gambar1_alur.png, gambar2_f1.png, gambar3_selisih.png dan results/tables/*.csv
Palet: biru #257de0 (split acak) dan oranye #f47230 (split grup); tervalidasi buta warna
(scripts/validate_palette.js). Kontras oranye di bawah 3:1, sehingga identitas juga dibawa
oleh label langsung, bentuk penanda, dan tabel angka.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

BIRU, ORANYE, TEKS, ABU = "#257de0", "#f47230", "#191919", "#8a8a8a"
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"], "font.size": 9,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": ABU,
                     "text.color": TEKS, "axes.labelcolor": TEKS, "xtick.color": TEKS, "ytick.color": TEKS})
FIG, TAB = Path("figures"), Path("results/tables")
FIG.mkdir(exist_ok=True)
TAB.mkdir(parents=True, exist_ok=True)
koma = lambda x, n=4: f"{x:.{n}f}".replace(".", ",")


def gambar1():
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    ax.set_xlim(0, 10.3); ax.set_ylim(0, 4.9); ax.axis("off")
    L, T, G = 2.25, 1.3, 0.4
    xs = [0.05 + i * (L + G) for i in range(4)]
    atas = [["Data mentah PhiUSIIL", "235.795 baris, 54 fitur", "unduh 26/11/2026"],
            ["Pembersihan", "425 URL duplikat dibuang", "→ 235.370 URL"],
            ["Fitur dan grup", "18 URL-only, 50 semua", "grup eTLD+1: 175.509"],
            ["Split 70:15:15", "acak atau per eTLD+1", "seed 42 sampai 46"]]
    bawah = [["Tuning pada validation", "seed 42; konfigurasi", "dibekukan lewat commit"],
             ["Pelatihan pada train", "Logistic Regression", "dan Random Forest"],
             ["Evaluasi test (sekali)", "F1, recall, ROC-AUC", "interval bootstrap"],
             ["Waktu inferensi", "ekstraksi + prediksi", "satu URL per panggilan"]]
    ya, yb = 3.35, 0.35
    def kotak(x, y, teks):
        ax.add_patch(FancyBboxPatch((x, y), L, T, boxstyle="round,pad=0.02,rounding_size=0.08", fc="#f2f2f2", ec=ABU, lw=0.8))
        ax.text(x + L / 2, y + T / 2, chr(10).join(teks), ha="center", va="center", fontsize=6.6, linespacing=1.3)
    def panah(a, b):
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=8, lw=0.9, color=TEKS))
    for i in range(4):
        kotak(xs[i], ya, atas[i])
        kotak(xs[3 - i], yb, bawah[i])  # baris bawah dibaca dari kanan ke kiri
    for i in range(3):
        panah((xs[i] + L + 0.02, ya + T / 2), (xs[i + 1] - 0.02, ya + T / 2))
        panah((xs[3 - i] - 0.02, yb + T / 2), (xs[2 - i] + L + 0.02, yb + T / 2))
    panah((xs[3] + L / 2, ya - 0.02), (xs[3] + L / 2, yb + T + 0.02))
    fig.savefig(FIG / "gambar1_alur.png", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def gambar2(m):
    t = m[m.bagian == "test"]
    kat = [("A", "A\nacak,\nlengkap"), ("D", "D\ngrup,\nlengkap"), ("B", "B\nacak,\nURL-only"), ("C", "C\ngrup,\nURL-only")]
    warna = {"A": BIRU, "B": BIRU, "D": ORANYE, "C": ORANYE}
    aturan = t[t.model == "ATURAN"].f1.mean()
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.0), sharey=True)
    for ax, model, mk in zip(axes, ("LR", "RF"), ("o", "s")):
        for i, (sk, lab) in enumerate(kat):
            v = t[(t.skenario == sk) & (t.model == model)].f1.to_numpy()
            ax.scatter(np.full(len(v), i) + np.linspace(-0.15, 0.15, len(v)), v, s=14, marker=mk, color=warna[sk], alpha=0.55, linewidths=0)
            ax.plot([i - 0.28, i + 0.28], [v.mean()] * 2, color=warna[sk], lw=2.2, solid_capstyle="butt")
        ax.axhline(aturan, color=TEKS, lw=0.9, ls=(0, (4, 3)))
        ax.set_xticks(range(4)); ax.set_xticklabels([l for _, l in kat], fontsize=7.5)
        ax.set_title({"LR": "Logistic Regression", "RF": "Random Forest"}[model], fontsize=9, loc="left")
        ax.set_ylim(0.978, 1.0012); ax.grid(axis="y", color="#e6e6e6", lw=0.6); ax.set_axisbelow(True)
    axes[0].set_ylabel("F1 (kelas phishing), data test")
    axes[1].annotate(chr(10).join(["seed 44: seluruh grup web.app", "(5.718 URL phishing) masuk test"]), xy=(2.93, 0.9812), xytext=(2.82, 0.9812), ha="right",
                     fontsize=6.5, va="center", arrowprops=dict(arrowstyle="-", lw=0.6, color="#555"))
    axes[0].text(-0.45, aturan + 0.0005, f"aturan satu baris (F1 {koma(aturan, 3)})", fontsize=6.8, va="bottom")
    axes[0].text(0.97, 0.03, "garis tebal = rata-rata 5 seed; titik = seed", transform=axes[0].transAxes, ha="right", fontsize=6.5, color="#555")
    fig.legend([plt.Line2D([], [], color=BIRU, lw=3), plt.Line2D([], [], color=ORANYE, lw=3)], ["split acak", "split grup eTLD+1"],
               loc="lower center", ncol=2, frameon=False, fontsize=8, bbox_to_anchor=(0.5, -0.04))
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(FIG / "gambar2_f1.png", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def gambar3(a):
    urut = ["A-D: acak vs grup, fitur lengkap", "B-C: acak vs grup, URL-only", "B minus ATURAN (acak)", "C minus ATURAN (grup)"]
    label = {urut[0]: "A − D (acak − grup, fitur lengkap)", urut[1]: "B − C (acak − grup, URL-only)",
             urut[2]: "B − aturan satu baris (split acak)", urut[3]: "C − aturan satu baris (split grup)"}
    fig, ax = plt.subplots(figsize=(6.4, 3.1))
    y0 = 0
    for pb in urut[::-1]:
        for model, warna, mk, off in (("LR", BIRU, "o", 0.17), ("RF", ORANYE, "s", -0.17)):
            d = a[(a.perbandingan == pb) & (a.model == model)].sort_values("seed")
            for k, (_, r) in enumerate(d.iterrows()):
                y = y0 + off + (k - 2) * 0.045
                ax.plot([r.ci_bawah, r.ci_atas], [y, y], color=warna, lw=0.9, alpha=0.75)
                ax.scatter([r.selisih], [y], s=12, marker=mk, color=warna, linewidths=0, zorder=3)
        y0 += 1
    ax.axvline(0, color=TEKS, lw=0.9)
    ax.set_yticks(range(4)); ax.set_yticklabels([label[p] for p in urut[::-1]], fontsize=7.5)
    ax.set_xlabel("selisih F1 dengan interval bootstrap 95% per seed (nol = tanpa selisih)")
    ax.grid(axis="x", color="#e6e6e6", lw=0.6); ax.set_axisbelow(True)
    ax.legend([plt.Line2D([], [], color=BIRU, marker="o", lw=1), plt.Line2D([], [], color=ORANYE, marker="s", lw=1)],
              ["Logistic Regression", "Random Forest"], frameon=False, fontsize=7.5, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG / "gambar3_selisih.png", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def tabel(m, audit, split, lat):
    # Tabel 1: karakteristik dataset dan split
    t1 = pd.DataFrame([
        ["Baris mentah", audit["baris"], ""],
        ["URL unik setelah dedup", split["baris_setelah_dedup"], ""],
        ["Proporsi phishing (setelah dedup)", koma(split["proporsi_phishing_total"] * 100, 2) + "%", "kelas positif"],
        ["Fitur numerik (leksikal / turunan korpus / konten HTML)", "50 (18 / 4 / 28)", ""],
        ["Grup eTLD+1 unik", split["grup_unik"], "608 baris tanpa eTLD+1 memakai host penuh"],
    ], columns=["Item", "Nilai", "Catatan"])
    for sk, nama in (("acak", "Split acak (seed 42)"), ("grup", "Split grup eTLD+1 (seed 42)")):
        s = split[sk]["42"]
        t1.loc[len(t1)] = [nama + ": train / validation / test",
                           f"{s['train']['baris']} / {s['validation']['baris']} / {s['test']['baris']}",
                           f"phishing test {koma(s['test']['proporsi_phishing'] * 100, 1)}%; grup tumpang tindih train-test: {split[sk]['42']['grup_tumpang_tindih']['train_test']}"]
    t1.to_csv(TAB / "tabel1_dataset.csv", index=False, encoding="utf-8-sig")
    # Tabel 2: hasil utama
    t = m[m.bagian == "test"]
    g = t.groupby(["skenario", "model"])
    t2 = pd.DataFrame({"F1": g.f1.mean().map(lambda x: koma(x, 4)) + " ± " + g.f1.std().map(lambda x: koma(x, 4)),
                       "Precision": g.precision.mean().map(lambda x: koma(x, 4)),
                       "Recall": g.recall.mean().map(lambda x: koma(x, 4)),
                       "ROC-AUC": g.roc_auc.mean().map(lambda x: koma(x, 4)),
                       "False negative (rata-rata)": g.fn.mean().map(lambda x: koma(x, 1)),
                       "n test (rata-rata)": g.n.mean().map(lambda x: f"{x:.0f}")}).reset_index()
    t2.to_csv(TAB / "tabel2_hasil.csv", index=False, encoding="utf-8-sig")
    # Tabel 3: waktu inferensi
    r = lat["hasil"]
    t3 = pd.DataFrame([[f"{sk} ({v['fitur']})", nm, v["mencakup"], koma(v["median_ms"], 3), koma(v["p95_ms"], 3)]
                       for k, v in r.items() for sk, nm in [tuple(k.split("|"))]],
                      columns=["Skenario (fitur)", "Model", "Cakupan waktu", "Median (ms)", "p95 (ms)"])
    t3.loc[len(t3)] = ["B (ekstraksi saja)", "-", "ekstraksi 18 fitur dari string URL", koma(lat["ekstraksi_saja_url_only_ms"]["median"], 3), koma(lat["ekstraksi_saja_url_only_ms"]["p95"], 3)]
    t3.to_csv(TAB / "tabel3_latensi.csv", index=False, encoding="utf-8-sig")
    # Tabel 4: ancaman validitas
    t4 = pd.DataFrame([
        ["Artefak bentuk URL", "100% URL legitimate berbentuk https://www.<domain> tanpa path; aturan satu baris F1 ≈ 0,995", "F1 URL-only tinggi tidak membuktikan deteksi phishing nyata", "Aturan dilaporkan sebagai baseline diagnostik (post-hoc)"],
        ["Definisi fitur leksikal", "Kolom CSV tidak dapat direproduksi persis dari string URL", "A dan B berbeda juga pada definisi fitur", "Tingkat kecocokan dilaporkan (results/feature_agreement.json)"],
        ["Fitur turunan korpus", "URLSimilarityIndex = 100 pada seluruh URL legitimate (AUC satu fitur 0,996)", "Skenario fitur lengkap mendekati sempurna", "Dilaporkan; tidak dipakai pada skenario URL-only"],
        ["Efek langit-langit", "F1 skenario A dan D ≈ 1,0", "Selisih antar split tidak dapat dideteksi", "Interval bootstrap dan lima seed"],
        ["Biaya konten HTML", "Pengambilan halaman tidak dapat direproduksi dari CSV", "Waktu skenario A hanya batas bawah", "Dicatat sebagai keterbatasan; tidak mengakses URL phishing"],
        ["Satu dataset", "Hanya PhiUSIIL", "Generalisasi terbatas; tidak ada hold-out temporal", "Tidak menarik kesimpulan tentang domain baru di dunia nyata"],
    ], columns=["Ancaman", "Bukti", "Dampak", "Penanganan"])
    t4.to_csv(TAB / "tabel4_validitas.csv", index=False, encoding="utf-8-sig")


def main():
    m = pd.read_csv("results/metrics.csv")
    a = pd.read_csv("results/analysis_selisih.csv")
    audit = json.loads(Path("results/audit_summary.json").read_text(encoding="utf-8"))
    split = json.loads(Path("results/split_check.json").read_text(encoding="utf-8"))
    lat = json.loads(Path("results/latency.json").read_text(encoding="utf-8"))
    gambar1(); gambar2(m); gambar3(a); tabel(m, audit, split, lat)
    for f in sorted(list(FIG.glob("gambar*.png")) + list(TAB.glob("*.csv"))): print(f)


if __name__ == "__main__":
    main()
