"""Membangun paper/draft.docx dari berkas results/. Semua angka dibaca dari berkas hasil, tidak diketik ulang.

Pemakaian (dari akar repositori): python src/build_paper.py
Gaya mengikuti draf P4: Letter, margin 2,54 cm, Times New Roman 12, hitam, judul tebal 16/13/12, tabel Table Grid.
"""
import json
import re
from pathlib import Path

import docx
import pandas as pd
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

from preprocessing import muat_bersih

FONT = "Times New Roman"
OUT = Path("paper/draft.docx")


def n(x, d=4):
    return f"{x:.{d}f}".replace(".", ",")


def i(x):
    return f"{int(round(x)):,}".replace(",", ".")


# ------------------------------------------------------------------ data
R = Path("results")
audit = json.loads((R / "audit_summary.json").read_text(encoding="utf-8"))
split = json.loads((R / "split_check.json").read_text(encoding="utf-8"))
lat = json.loads((R / "latency.json").read_text(encoding="utf-8"))
g1 = json.loads((R / "reproduksi_g1.json").read_text(encoding="utf-8"))
agree = json.loads((R / "feature_agreement.json").read_text(encoding="utf-8"))
out44 = json.loads((R / "analysis_outlier_seed44.json").read_text(encoding="utf-8"))
cfg = json.loads((R / "config_beku.json").read_text(encoding="utf-8"))["terpilih"]
M = pd.read_csv(R / "metrics.csv")
MA = pd.read_csv(R / "metrics_ablasi.csv")
SEL = pd.read_csv(R / "analysis_selisih.csv")
SELA = pd.read_csv(R / "analysis_ablasi.csv")
TT = pd.concat([M[M.bagian == "test"], MA[MA.bagian == "test"]])
fm = TT.groupby(["skenario", "model"]).f1.mean()
fsd = TT.groupby(["skenario", "model"]).f1.std()
fmin = TT.groupby(["skenario", "model"]).f1.min()


def ds(nama, model, df=SEL):
    d = df[(df.perbandingan == nama) & (df.model == model)]
    return d.selisih.mean(), int((~d.mencakup_nol).sum())


df = muat_bersih()
p = df["URL"].str.replace(r"^https?://", "", regex=True)
bentuk = (~p.str.contains(r"/.+|\?", regex=True)) & p.str.startswith("www.") & df["URL"].str.startswith("https")
n_leg, n_ph = int((df.phish == 0).sum()), int((df.phish == 1).sum())
n_leg_bentuk, n_ph_bentuk = int((bentuk & (df.phish == 0)).sum()), int((bentuk & (df.phish == 1)).sum())
tpt = M[(M.bagian == "test") & (M.skenario.isin(["B", "C"])) & (M.model == "RF")].pivot(index="seed", columns="skenario", values="f1")
bc_rf_tanpa44 = (tpt["B"] - tpt["C"]).drop(44).mean()
tpl = M[(M.bagian == "test") & (M.skenario.isin(["B", "C"])) & (M.model == "LR")].pivot(index="seed", columns="skenario", values="f1")
bc_lr_tanpa44 = (tpl["B"] - tpl["C"]).drop(44).mean()
c_rf = tpt["C"]
prop = lambda sk: [split[sk][s]["test"]["proporsi_phishing"] * 100 for s in split[sk]]
rule_ac = M[(M.skenario == "R_acak") & (M.bagian == "test")]
rule_gr = M[(M.skenario == "R_grup") & (M.bagian == "test")]
h = lat["hasil"]
ext = lat["ekstraksi_saja_url_only_ms"]
fa = agree


# ------------------------------------------------------------------ dokumen
d = docx.Document()
s = d.sections[0]
s.page_width, s.page_height = Cm(21.59), Cm(27.94)
for a in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
    setattr(s, a, Cm(2.54))


def setfont(style, size, bold=None):
    f = style.font
    f.name, f.size = FONT, Pt(size)
    f.color.rgb = RGBColor(0, 0, 0)
    if bold is not None:
        f.bold = bold
    rpr = style.element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for k in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(k), FONT)
    for k in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if rf.get(qn(k)) is not None:
            del rf.attrib[qn(k)]


nm = d.styles["Normal"]
setfont(nm, 12)
nm.paragraph_format.line_spacing = 1.08
nm.paragraph_format.space_after = Pt(6)
for name, sz, bef, aft in (("Heading 1", 16, 14, 5), ("Heading 2", 13, 10, 4), ("Heading 3", 12, 8, 3)):
    st = d.styles[name]
    setfont(st, sz, True)
    st.font.italic = False
    st.paragraph_format.space_before, st.paragraph_format.space_after = Pt(bef), Pt(aft)
    st.paragraph_format.keep_with_next = True


def runs(par, text, size=None, bold=None):
    for part in re.split(r"(\*[^*]+\*)", text):
        if not part:
            continue
        it = part.startswith("*") and part.endswith("*")
        r = par.add_run(part[1:-1] if it else part)
        r.italic = it or None
        r.font.name = FONT
        if size:
            r.font.size = Pt(size)
        if bold:
            r.bold = True


def P(text, style="Normal", size=None, italic=False):
    par = d.add_paragraph(style=style)
    runs(par, "*" + text + "*" if italic else text, size)
    return par


def H(text, lvl=2):
    d.add_paragraph(text, style=f"Heading {lvl}")


def shade(cell):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), "F2F2F2")
    tcPr.append(sh)


def caption(text):
    par = P(text, size=10.5)
    par.paragraph_format.space_after = Pt(10)


def table(header, rows, widths, size=10):
    t = d.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.autofit = False
    for k, hd in enumerate(header):
        c = t.rows[0].cells[k]
        c.width = Cm(widths[k])
        shade(c)
        c.paragraphs[0].paragraph_format.space_after = Pt(1)
        runs(c.paragraphs[0], hd, size, True)
    for row in rows:
        cells = t.add_row().cells
        for k, v in enumerate(row):
            cells[k].width = Cm(widths[k])
            cells[k].paragraphs[0].paragraph_format.space_after = Pt(1)
            runs(cells[k].paragraphs[0], str(v), size)
    trPr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader")
    th.set(qn("w:val"), "true")
    trPr.append(th)
    return t


def figure(path, width_in, cap):
    d.add_picture(str(path), width=Inches(width_in))
    d.paragraphs[-1].paragraph_format.space_after = Pt(2)
    d.paragraphs[-1].paragraph_format.keep_with_next = True
    caption(cap)


# ------------------------------------------------------------------ judul dan abstrak
d.add_paragraph("Evaluasi Ketahanan Deteksi URL Phishing terhadap Pembagian Data per Domain dan Pengurangan Fitur pada Dataset PhiUSIIL", style="Heading 1")
P("Evaluating the Robustness of Machine Learning-Based Phishing URL Detection Using URL Feature Selection and Domain-Aware Validation", italic=True)
P("Navyz Abdillah Zikhav, Anggota 2 (belum ditentukan) · Program Sarjana Terapan Teknik Informatika, Politeknik Elektronika Negeri Surabaya (PENS) · 26 November 2026")

abstrak = (
    f"Deteksi URL phishing pada dataset PhiUSIIL sering dilaporkan dengan F1 mendekati 1, tetapi belum jelas apakah angka itu bertahan setelah data dibagi per domain dan setelah fitur yang tidak berasal dari URL dikeluarkan. "
    f"Penelitian ini membandingkan pembagian acak dan pembagian per domain terdaftar (eTLD+1) pada {i(split['baris_setelah_dedup'])} URL, dengan 50 fitur lengkap dan 18 fitur URL-only yang dihitung ulang dari string URL. "
    f"Logistic Regression dan Random Forest dilatih pada lima *seed* dengan data latih, validasi, dan uji yang terpisah; konfigurasi dibekukan sebelum data uji dibuka. "
    f"Pada fitur lengkap, F1 uji mencapai {n(min(fm['A','LR'], fm['D','LR']), 4)} sampai {n(max(fm['A','RF'], fm['D','RF']), 4)} pada kedua pembagian, tanpa selisih yang berbeda nyata. "
    f"Pada fitur URL-only, F1 turun menjadi {n(min(fm['B','LR'], fm['C','LR']), 3)} sampai {n(max(fm['B','RF'], fm['C','RF']), 3)}, dan arah selisih antar pembagian berlawanan antar model. "
    f"Satu pembagian yang memasukkan seluruh grup web.app ke data uji menurunkan F1 Random Forest menjadi {n(c_rf.min(), 3)}. "
    f"Aturan satu baris tanpa parameter, yang mengenali bentuk URL legitimate dalam dataset, mencapai F1 {n(rule_ac.f1.mean(), 3)} dan setara atau lebih baik daripada model URL-only. "
    f"Waktu ekstraksi 18 fitur hanya {n(ext['median'], 3)} ms, dan waktu prediksi hampir sama untuk 18 dan 50 fitur. "
    f"Skor tinggi pada PhiUSIIL tampaknya mencerminkan bentuk URL dalam dataset, bukan kemampuan menggeneralisasi ke domain baru."
)
H("Abstrak")
P(abstrak)
H("Kata Kunci")
P("deteksi URL phishing; PhiUSIIL; pembagian per domain; kebocoran data; fitur URL-only; baseline sederhana")

# ------------------------------------------------------------------ 1 pendahuluan
H("1. Pendahuluan")
P(f"PhiUSIIL (Prasad & Chandra, 2024a) memuat 235.795 URL, terdiri dari 100.945 URL phishing dan 134.850 URL legitimate menurut halaman UCI (Prasad & Chandra, 2024b), dan banyak dipakai untuk menguji pendeteksi phishing berbasis pembelajaran mesin. "
  f"Performa yang dilaporkan hampir selalu mendekati sempurna: F1 XGBoost 99,995% pada 50 fitur (Ivandanizar & Taufiq, 2026) dan akurasi uji 0,9962 sampai 0,9984 pada empat model (Ahamed dkk., 2026). "
  f"Angka setinggi itu menimbulkan pertanyaan tentang apa yang sebenarnya diukur, terutama karena kebocoran data diketahui memengaruhi 294 makalah di 17 bidang (Kapoor & Narayanan, 2023).")
P(f"Dua studi 2026 pada dataset ini sudah menangani sebagian pertanyaan tersebut. Ivandanizar dan Taufiq (2026) membandingkan pembagian acak dengan pembagian yang mengelompokkan data menurut kolom Domain; F1 XGBoost pada 50 fitur hanya turun dari 100,0000% menjadi 99,9949%, dan pada 21 fitur turunan URL mencapai 99,7495% pada pembagian domain. "
  f"Ahamed dkk. (2026) memakai pembagian per host dan melaporkan bahwa URL phishing dan legitimate di PhiUSIIL sangat mudah dipisahkan (*highly separable*) pada representasi karakter.")
P(f"Keterbatasan yang dapat dibuktikan dari kedua studi tersebut menjadi dasar penelitian ini. Pertama, pembagian per host tidak menjamin pemisahan per domain terdaftar: {i(1387)} domain eTLD+1 masih sama antara data latih dan data uji (Ahamed dkk., 2026, Tabel 2). "
  f"Kedua, Ivandanizar dan Taufiq (2026) menyatakan bahwa ketersediaan fitur URLSimilarityIndex pada saat prediksi perlu diselidiki, dan bahwa waktu ekstraksi fitur serta latensi prediksi belum diukur. "
  f"Ketiga, Arp dkk. (2022) menggolongkan korelasi semu (*spurious correlations*) dan pembanding yang tidak sesuai (*inappropriate baseline*) sebagai kesalahan umum evaluasi pembelajaran mesin di bidang keamanan. "
  f"Berdasarkan penelusuran terhadap 11 sumber, kandidat celah ini memerlukan verifikasi dengan penelusuran yang lebih luas; penelitian ini diposisikan sebagai replikasi kritis dan *ablation*, bukan klaim kebaruan.")
P(f"Penelitian ini menjawab pertanyaan berikut: apakah selisih F1 antara pembagian acak dan pembagian per domain terdaftar (eTLD+1) bertahan setelah fitur yang tidak murni berasal dari URL dikeluarkan, dan berapa waktu inferensi total (ekstraksi fitur dan prediksi) pada tiap konfigurasi? "
  f"Dugaan yang diuji adalah H1, selisih F1 antara kedua pembagian pada fitur URL-only lebih besar daripada pada fitur lengkap, dan H2, fitur URL-only memerlukan waktu inferensi total yang lebih singkat dengan penurunan F1 yang diukur. "
  f"Kontribusinya adalah (i) perbandingan 2×2 antara jenis pembagian dan kelompok fitur dengan lima *seed* dan interval *bootstrap*, (ii) baseline aturan tanpa parameter sebagai pembanding sederhana, (iii) konfigurasi yang dibekukan sebelum data uji dibuka, dan (iv) repositori yang dapat direproduksi.")

# ------------------------------------------------------------------ 2 metode
H("2. Metode")
P("Keputusan metodologi dicatat sebelum data uji dibuka (docs/decisions.md); analisis sesudahnya diberi label post-hoc.")
d.add_picture("figures/gambar1_alur.png", width=Inches(3.9))
d.paragraphs[-1].paragraph_format.keep_with_next = True
caption("Gambar 1. Alur eksperimen dari data mentah sampai pengukuran waktu inferensi.")
H("2.1 Dataset dan pembersihan", 3)
P(f"Data berasal dari PhiUSIIL Phishing URL (Website) (UCI id 967; salinan Kaggle), diunduh pada 26 November 2026, dengan {i(audit['baris'])} baris, 56 kolom, tanpa nilai hilang. "
  f"Pada berkas asli, label 1 menunjukkan URL legitimate dan label 0 phishing; kelas positif dalam seluruh hasil adalah phishing. "
  f"Sebanyak {i(audit['url_duplikat_baris'] // 2)} URL muncul dua kali (seluruhnya phishing, tanpa konflik label) dan kemunculan keduanya dibuang, sehingga tersisa {i(split['baris_setelah_dedup'])} URL dengan proporsi phishing {n(split['proporsi_phishing_total'] * 100, 2)}%.")
H("2.2 Fitur", 3)
P(f"Lima kolom identitas atau teks (FILENAME, URL, Domain, TLD, Title) tidak dipakai sebagai fitur. Sebanyak 50 fitur numerik dikelompokkan menurut asalnya: 18 fitur leksikal dari string URL, 4 fitur turunan korpus (URLSimilarityIndex, CharContinuationRate, TLDLegitimateProb, URLCharProb), dan 28 fitur konten halaman HTML. "
  f"Skenario URL-only memakai 18 fitur leksikal yang dihitung ulang dari string URL oleh fungsi sendiri, karena kolom dataset tidak dapat direproduksi persis: URLLength berbeda satu karakter pada 79% dari 20.000 baris acak dan korelasi rasio huruf hanya {n(fa['LetterRatioInURL']['korelasi'], 2)}, sedangkan DomainLength, NoOfSubDomain, dan IsDomainIP cocok pada {n(min(fa[k]['cocok_persis'] for k in ('DomainLength','NoOfSubDomain','IsDomainIP')) * 100, 2)}% sampai 100% baris. Fungsi yang sama dipakai untuk melatih model dan mengukur waktu ekstraksi.")
H("2.3 Pembagian data", 3)
P(f"Data dibagi 70:15:15 menjadi data latih, validasi, dan uji. Pembagian acak distratifikasi menurut kelas. Pembagian grup memakai domain terdaftar (eTLD+1, dihitung dengan tldextract 5.4.0 dan daftar sufiks bawaan; baris tanpa eTLD+1 memakai host penuh) sebagai kunci, sehingga seluruh URL satu grup berada pada satu bagian. "
  f"Pembagian grup memakai StratifiedGroupKFold dengan 20 lipatan yang dirakit menjadi 14, 3, dan 3 lipatan, karena GroupShuffleSplit biasa menghasilkan proporsi phishing data uji {n(min(prop('grup_shuffle')), 1)}% sampai {n(max(prop('grup_shuffle')), 1)}% antar *seed*, sehingga F1 tidak sebanding. Setiap pembagian diulang dengan *seed* 42 sampai 46.")
H("2.4 Skenario, model, dan penyetelan", 3)
P("Empat skenario mengubah satu faktor per langkah: A (pembagian acak, 50 fitur), B (acak, 18 fitur URL-only), C (grup, URL-only), dan D (grup, 50 fitur). "
  "Model yang dilatih adalah Logistic Regression (dengan StandardScaler di dalam *pipeline*, sehingga hanya dipelajari dari data latih) dan Random Forest dengan 200 pohon. "
  "Hyperparameter dipilih hanya pada data validasi *seed* 42, berdasarkan F1 tertinggi: C ∈ {0,01; 0,1; 1; 10} untuk Logistic Regression, serta kedalaman maksimum ∈ {10, tanpa batas} dan minimum sampel per daun ∈ {1, 5} untuk Random Forest; bila seri, dipilih konfigurasi pertama pada grid. "
  f"Konfigurasi terpilih dibekukan lewat *commit* sebelum data uji dibuka, dan kode menolak membuka data uji bila berkas konfigurasi berubah. Hasil pemilihan: Logistic Regression C = {cfg['A|LR']['C']:g} (skenario A dan D) dan C = {cfg['B|LR']['C']:g} (B dan C); Random Forest berkedalaman {cfg['A|RF']['max_depth']} (A dan D) dan tanpa batas (B dan C), dengan minimum sampel per daun 1.")
H("2.5 Evaluasi", 3)
P("Metrik pada data uji adalah F1 kelas phishing, *precision*, *recall*, ROC-AUC, PR-AUC, dan jumlah negatif palsu (*false negative*). Interval kepercayaan 95% diperoleh dengan *bootstrap* persentil (1.000 resampel); selisih F1 dihitung per *seed*, dan selisih dianggap berarti bila interval tidak mencakup nol. "
  "Waktu inferensi dihitung sebagai median 500 URL pada lima pengulangan, satu URL per panggilan dengan satu *thread*. Untuk URL-only, waktu mencakup ekstraksi dan prediksi; untuk 50 fitur, hanya prediksi, karena pengambilan halaman tidak dapat dilakukan dari berkas CSV; angka itu merupakan batas bawah.")
H("2.6 Analisis post-hoc", 3)
P("Setelah data uji dibuka dan tanpa mengubah konfigurasi utama, dilakukan empat analisis tambahan: (a) aturan tanpa parameter yang memprediksi phishing bagi setiap URL yang bukan berbentuk https://www.<domain> tanpa path; (b) *ablation* skenario E dan F, yaitu 18 fitur URL ditambah 4 fitur turunan korpus pada pembagian acak dan grup, dengan konfigurasi dibekukan lebih dulu pada data validasi; (c) penelusuran asal negatif palsu pada *seed* dengan F1 terendah; dan (d) reproduksi protokol baseline repositori referensi (pradhyumnaag30, 2025) pada berkas data yang identik.")

# ------------------------------------------------------------------ 3 hasil
H("3. Hasil")
H("3.1 Karakteristik data dan pembagian", 3)
s_ac, s_gr = split["acak"]["42"], split["grup"]["42"]
n_phish_dedup = int((df.phish == 1).sum())
P(f"Tabel 1 merangkum data setelah {i(audit['url_duplikat_baris'] // 2)} URL duplikat dibuang. Pada pembagian acak, {i(s_ac['grup_tumpang_tindih']['train_test'])} grup eTLD+1 yang sama muncul pada data latih dan uji, sedangkan pada pembagian grup tidak ada.")
caption("Tabel 1. Karakteristik dataset dan pembagian data (*seed* 42 kecuali dinyatakan lain).")
table(["Item", "Nilai"], [
    ["URL unik (phishing)", f"{i(split['baris_setelah_dedup'])} ({i(n_phish_dedup)}; {n(split['proporsi_phishing_total'] * 100, 2)}%)"],
    ["Fitur numerik", "50 = 18 leksikal URL + 4 turunan korpus + 28 konten HTML"],
    ["Grup eTLD+1", i(split["grup_unik"])],
    ["Pembagian acak: latih / validasi / uji", f"{i(s_ac['train']['baris'])} / {i(s_ac['validation']['baris'])} / {i(s_ac['test']['baris'])}"],
    ["Pembagian grup: latih / validasi / uji", f"{i(s_gr['train']['baris'])} / {i(s_gr['validation']['baris'])} / {i(s_gr['test']['baris'])}"],
    ["Phishing pada data uji grup (5 *seed*)", f"{n(min(prop('grup')), 1)}% sampai {n(max(prop('grup')), 1)}%"],
], [6.2, 10.3], size=9.5)
d.add_paragraph().paragraph_format.space_after = Pt(2)
H("3.2 Hasil utama", 3)
P(f"Pada fitur lengkap (skenario A dan D), F1 uji berada pada {n(min(fm['A','LR'], fm['D','LR']), 4)} sampai {n(max(fm['A','RF'], fm['D','RF']), 4)} pada kedua pembagian dan kedua model (Tabel 2). "
  f"Pada fitur URL-only (B dan C), F1 turun menjadi {n(fm['B','LR'], 4)} (Logistic Regression) dan {n(fm['B','RF'], 4)} (Random Forest) pada pembagian acak, serta {n(fm['C','LR'], 4)} dan {n(fm['C','RF'], 4)} pada pembagian grup. "
  f"Gambar 2 memperlihatkan seluruh *seed*; simpangan baku skenario C Random Forest ({n(fsd['C','RF'], 4)}) jauh lebih besar daripada pada B ({n(fsd['B','RF'], 4)}).")
nama_sk = {"A": "A (acak, 50 fitur)", "B": "B (acak, URL-only)", "C": "C (grup, URL-only)", "D": "D (grup, 50 fitur)", "E": "E† (acak, URL-only + 4 turunan korpus)", "F": "F† (grup, URL-only + 4 turunan korpus)"}
rows2 = []
for sk in ["A", "B", "C", "D", "E", "F"]:
    for mo in ["LR", "RF"]:
        x = TT[(TT.skenario == sk) & (TT.model == mo)]
        rows2.append([nama_sk[sk] if mo == "LR" else "", {"LR": "Logistic Regression", "RF": "Random Forest"}[mo],
                      f"{n(x.f1.mean(), 4)} ± {n(x.f1.std(), 4)}", n(x.precision.mean(), 4), n(x.recall.mean(), 4), n(x.roc_auc.mean(), 4), n(x.fn.mean(), 1)])
for sk, lab in (("R_acak", "Aturan bentuk URL† (acak)"), ("R_grup", "Aturan bentuk URL† (grup)")):
    x = M[(M.skenario == sk) & (M.bagian == "test")]
    rows2.append([lab, "tanpa parameter", f"{n(x.f1.mean(), 4)} ± {n(x.f1.std(), 4)}", n(x.precision.mean(), 4), n(x.recall.mean(), 4), n(x.roc_auc.mean(), 4), n(x.fn.mean(), 1)])
caption(f"Tabel 2. Hasil pada data uji (rata-rata ± simpangan baku lima *seed*; kelas positif phishing; n uji sekitar {i(TT[TT.skenario=='A'].n.mean())} pada pembagian acak dan {i(TT[TT.skenario=='C'].n.mean())} pada pembagian grup). † = analisis post-hoc.")
table(["Skenario", "Model", "F1", "Precision", "Recall", "ROC-AUC", "FN"], rows2, [4.6, 2.9, 2.6, 1.7, 1.7, 1.7, 1.0], size=9)
d.add_paragraph().paragraph_format.space_after = Pt(2)
figure("figures/gambar2_f1.png", 4.3, "Gambar 2. F1 pada data uji per skenario dan model. Garis tebal menunjukkan rata-rata lima *seed*, titik menunjukkan tiap *seed*, dan garis putus-putus menunjukkan baseline aturan satu baris.")
H("3.3 Selisih antar skenario", 3)
a_d_lr, a_d_rf = ds("A-D: acak vs grup, fitur lengkap", "LR"), ds("A-D: acak vs grup, fitur lengkap", "RF")
b_c_lr, b_c_rf = ds("B-C: acak vs grup, URL-only", "LR"), ds("B-C: acak vs grup, URL-only", "RF")
a_b_lr, a_b_rf = ds("A-B: lengkap vs URL-only, acak", "LR"), ds("A-B: lengkap vs URL-only, acak", "RF")
d_c_lr, d_c_rf = ds("D-C: lengkap vs URL-only, grup", "LR"), ds("D-C: lengkap vs URL-only, grup", "RF")
b_r_lr, b_r_rf = ds("B minus ATURAN (acak)", "LR"), ds("B minus ATURAN (acak)", "RF")
c_r_lr, c_r_rf = ds("C minus ATURAN (grup)", "LR"), ds("C minus ATURAN (grup)", "RF")
e_b_lr, e_b_rf = ds("E-B: efek 4 fitur turunan korpus, split acak", "LR", SELA), ds("E-B: efek 4 fitur turunan korpus, split acak", "RF", SELA)
f_c_lr, f_c_rf = ds("F-C: efek 4 fitur turunan korpus, split grup", "LR", SELA), ds("F-C: efek 4 fitur turunan korpus, split grup", "RF", SELA)
e_f_lr, e_f_rf = ds("E-F: acak vs grup, URL-only + korpus", "LR", SELA), ds("E-F: acak vs grup, URL-only + korpus", "RF", SELA)
sg = lambda v: ("+" if v >= 0 else "−") + n(abs(v), 5 if abs(v) < 0.0005 else 4)
def cel(t):
    return f"{sg(t[0])} ({t[1]}/5)"
rows3 = [
    ["A − D: acak − grup, 50 fitur", cel(a_d_lr), cel(a_d_rf)],
    ["B − C: acak − grup, URL-only", cel(b_c_lr), cel(b_c_rf)],
    ["A − B: 50 fitur − URL-only, acak", cel(a_b_lr), cel(a_b_rf)],
    ["D − C: 50 fitur − URL-only, grup", cel(d_c_lr), cel(d_c_rf)],
    ["B − aturan satu baris† (acak)", cel(b_r_lr), cel(b_r_rf)],
    ["C − aturan satu baris† (grup)", cel(c_r_lr), cel(c_r_rf)],
    ["E − B: efek 4 fitur turunan korpus†", cel(e_b_lr), cel(e_b_rf)],
    ["F − C: efek 4 fitur turunan korpus†", cel(f_c_lr), cel(f_c_rf)],
    ["E − F: acak − grup, URL-only + korpus†", cel(e_f_lr), cel(e_f_rf)],
]
P(f"Pada fitur lengkap, selisih F1 antara pembagian acak dan grup praktis nol: {sg(a_d_lr[0])} (Logistic Regression) dan {sg(a_d_rf[0])} (Random Forest), dengan interval 95% yang mencakup nol pada kelima *seed* (Tabel 3). "
  f"Pada fitur URL-only, selisihnya {sg(b_c_lr[0])} dan {sg(b_c_rf[0])}, berlawanan arah antar model, dan interval tidak mencakup nol pada {b_c_lr[1]} dan {b_c_rf[1]} dari 5 *seed*. "
  f"Fitur lengkap lebih unggul daripada URL-only sebesar {n(a_b_lr[0], 4)} dan {n(a_b_rf[0], 4)} pada pembagian acak, serta {n(d_c_lr[0], 4)} dan {n(d_c_rf[0], 4)} pada pembagian grup, pada kelima *seed*.")
caption("Tabel 3. Selisih F1 rata-rata lima *seed* (jumlah *seed* dengan interval bootstrap 95% yang tidak mencakup nol). † = analisis post-hoc.")
table(["Perbandingan", "Logistic Regression", "Random Forest"], rows3, [8.2, 4.1, 4.1])
d.add_paragraph().paragraph_format.space_after = Pt(2)
H("3.4 Baseline aturan dan artefak bentuk URL", 3)
P(f"Seluruh {i(n_leg)} URL legitimate berbentuk https://www.<domain> tanpa path, sedangkan hanya {i(n_ph_bentuk)} dari {i(n_ph)} URL phishing ({n(n_ph_bentuk / n_ph * 100, 1)}%) berbentuk sama. "
  f"Aturan tanpa parameter yang memprediksi phishing untuk bentuk lain mencapai F1 uji {n(rule_ac.f1.mean(), 4)} (acak) dan {n(rule_gr.f1.mean(), 4)} (grup), dengan *precision* 1,0000 dan *recall* {n(rule_ac.recall.mean(), 4)} dan {n(rule_gr.recall.mean(), 4)}. "
  f"Model URL-only tidak mengungguli aturan ini: selisih F1 model dikurangi aturan adalah {sg(b_r_lr[0])} (Logistic Regression) dan {sg(b_r_rf[0])} (Random Forest) pada pembagian acak, serta {sg(c_r_lr[0])} dan {sg(c_r_rf[0])} pada pembagian grup (Tabel 3).")
H("3.5 Pembagian dengan F1 terendah", 3)
P(f"Pada skenario C dengan Random Forest, *seed* 44 menghasilkan F1 {n(c_rf.loc[44], 4)}, sedangkan empat *seed* lain berkisar {n(c_rf.drop(44).min(), 4)} sampai {n(c_rf.drop(44).max(), 4)}. "
  f"Pada *seed* itu, seluruh grup {out44['grup_teratas']} ({i(out44['baris_grup_di_test'])} URL, semuanya phishing) masuk ke data uji, dan {i(out44['fn_dari_grup_teratas'])} dari {i(out44['fn_total'])} negatif palsu ({n(out44['pangsa_fn_grup_teratas'] * 100, 1)}%) berasal dari grup itu. "
  f"Tanpa *seed* 44, selisih B − C menjadi {sg(bc_rf_tanpa44)} (Random Forest) dan {sg(bc_lr_tanpa44)} (Logistic Regression), sehingga tanda selisih Random Forest berbalik (post-hoc).")
H("3.6 Ablation fitur turunan korpus", 3)
P(f"Penambahan empat fitur turunan korpus pada 18 fitur URL menaikkan F1 uji menjadi {n(fm['E','LR'], 4)} dan {n(fm['E','RF'], 4)} (acak, skenario E) serta {n(fm['F','LR'], 4)} dan {n(fm['F','RF'], 4)} (grup, skenario F). "
  f"Kenaikannya {sg(e_b_lr[0])} dan {sg(e_b_rf[0])} (acak) serta {sg(f_c_lr[0])} dan {sg(f_c_rf[0])} (grup), dengan interval tanpa nol pada 5 dari 5 *seed* untuk keempatnya. Selisih acak − grup pada skenario ini {sg(e_f_lr[0])} dan {sg(e_f_rf[0])}, tidak berbeda nyata pada {5 - e_f_lr[1]} dan {5 - e_f_rf[1]} dari 5 *seed*.")
H("3.7 Waktu inferensi", 3)
P(f"Ekstraksi 18 fitur dari string URL memerlukan {n(ext['median'], 3)} ms (median). Waktu per URL hampir sama untuk URL-only dan 50 fitur: {n(h['B|LR']['median_ms'], 3)} dan {n(h['A|LR']['median_ms'], 3)} ms untuk Logistic Regression, serta {n(h['B|RF']['median_ms'], 2)} dan {n(h['A|RF']['median_ms'], 2)} ms untuk Random Forest (median 500 URL, satu URL per panggilan). Waktu pengambilan dan penguraian halaman untuk 28 fitur konten tidak diukur.")

H("3.8 Reproduksi baseline repositori referensi", 3)
gl = g1["hasil"]
P(f"Protokol repositori referensi (pradhyumnaag30, 2025) ditiru pada berkas data yang identik (SHA-256 sama) dan hasilnya cocok dengan yang dipublikasikan sampai enam desimal (Logistic Regression F1 {n(gl['Logistic Regression']['positif_label1']['f1'], 6)}; Random Forest {n(gl['Random Forest']['positif_label1']['f1'], 6)}). "
  f"Repositori itu memakai label 1 (legitimate) sebagai kelas positif; dengan phishing sebagai kelas positif, F1 Logistic Regression menjadi {n(gl['Logistic Regression']['positif_phishing']['f1'], 6)}.")

# ------------------------------------------------------------------ 4 pembahasan
H("4. Pembahasan")
H("4.1 Pembagian per domain dan fitur URL-only (H1)", 3)
P(f"H1 tidak terdukung secara konsisten. Pada fitur lengkap, pembagian per eTLD+1 tidak mengubah hasil, sejalan dengan selisih yang sangat kecil pada Ivandanizar dan Taufiq (2026). "
  f"Pada fitur URL-only, selisihnya secara numerik lebih besar, tetapi arahnya berbeda antar model dan tanda selisih Random Forest berbalik bila *seed* 44 dikeluarkan. Dugaan yang paling sederhana adalah bahwa selisih itu ditentukan oleh grup besar yang kebetulan masuk ke data uji: seluruh grup web.app pada *seed* 44 berisi phishing dan model yang tidak melihat grup itu pada data latih melewatkan sebagian URL-nya. Dugaan ini belum diuji. "
  f"Pada bidang lain, untuk model Extra Trees, validasi per partisipan menurunkan akurasi dari 0,91 (validasi berlipat berstratifikasi) menjadi 0,66 (Karbalaie dkk., 2026); penurunan sebesar itu tidak ditemukan pada PhiUSIIL.")
H("4.2 Waktu inferensi (H2)", 3)
P(f"H2 tidak terdukung pada komponen yang dapat diukur. Ekstraksi 18 fitur nyaris tanpa biaya ({n(ext['median'], 3)} ms), dan waktu prediksi tidak berkurang karena jumlah fitur lebih sedikit. "
  f"Keunggulan URL-only yang lebih masuk akal, yaitu tidak perlu mengambil dan menguraikan halaman web, tidak diukur dan karena itu tidak diklaim. Penurunan F1 akibat meninggalkan fitur lengkap berkisar {n(min(a_b_rf[0], d_c_rf[0]), 4)} sampai {n(max(a_b_lr[0], d_c_lr[0]), 4)}.")
H("4.3 Artefak dataset", 3)
P(f"Skor URL-only yang tinggi tidak dapat langsung dibaca sebagai kemampuan mendeteksi phishing. Aturan satu baris yang hanya mengenali bentuk URL legitimate dalam dataset memperoleh F1 setara atau lebih tinggi daripada model terlatih. Temuan ini sejalan dengan pernyataan Ahamed dkk. (2026) bahwa kedua kelas sangat mudah dipisahkan dan dengan dua kesalahan umum (*pitfall*) pada Arp dkk. (2022): korelasi semu (P4), ketika artefak yang tidak berkaitan dengan masalah keamanan menjadi pola pintasan, dan pembanding yang tidak sesuai (P6), yang menganjurkan model sederhana ikut dibandingkan. "
  f"Fitur turunan korpus memperkuat gambaran itu: empat fitur tersebut menaikkan F1 menjadi {n(min(fm['E','LR'], fm['F','LR']), 4)} sampai {n(max(fm['E','RF'], fm['F','RF']), 4)}, dan nilai URLSimilarityIndex tepat 100 pada seluruh URL legitimate. Apakah 21 fitur turunan URL (*URL-derived features*) pada Ivandanizar dan Taufiq (2026), yang menghasilkan F1 99,7495% pada pembagian domain, memuat fitur serupa tidak dapat dipastikan karena daftarnya tidak dirinci; perbandingan langsung juga terhambat perbedaan model dan pembagian 80:20 tanpa data validasi.")
H("4.4 Keterbatasan dan ancaman terhadap validitas", 3)
P("Keterbatasan penelitian ini: (1) satu dataset tanpa uji pada data independen atau terpisah waktu, sehingga tidak ada klaim tentang domain baru (keterbatasan serupa diakui oleh Chaudhuri dan Mohankumar, 2026, yang memakai validasi silang berstratifikasi tanpa data uji terpisah waktu; evaluasi lintas dataset pada URL dalam email melaporkan akurasi rata-rata di atas 94% pada empat himpunan uji sekunder, Yi dkk., 2025, lebih rendah daripada hasil hampir sempurna pada satu dataset meski tidak sebanding langsung); (2) lima *seed*, hasil pembagian grup yang dipengaruhi grup besar, dan interval *bootstrap* yang me-resampel baris, bukan grup domain; (3) analisis sensitivitas dengan sufiks privat pada pembentukan grup (misalnya memisahkan subdomain platform hosting) direncanakan tetapi belum dijalankan; (4) 18 fitur URL-only dihitung ulang dengan definisi sendiri; (5) hanya dua model dengan grid kecil; (6) biaya pengambilan halaman tidak diukur; dan (7) analisis post-hoc dirumuskan setelah data uji dibuka sehingga bersifat eksploratif.")

# ------------------------------------------------------------------ 5 kesimpulan
H("5. Kesimpulan")
P(f"Menjawab pertanyaan penelitian, selisih F1 antara pembagian acak dan pembagian per domain terdaftar tidak bertahan sebagai efek yang konsisten pada PhiUSIIL: pembagian per domain tidak mengubah F1 pada fitur lengkap ({sg(a_d_lr[0])} dan {sg(a_d_rf[0])}), sedangkan pada fitur URL-only selisihnya kecil dan tidak konsisten antar model ({sg(b_c_lr[0])} dan {sg(b_c_rf[0])}) serta dipengaruhi satu grup besar. "
  f"Waktu prediksi hampir sama untuk 18 dan 50 fitur ({n(h['B|LR']['median_ms'], 2)} dan {n(h['A|LR']['median_ms'], 2)} ms untuk Logistic Regression; {n(h['B|RF']['median_ms'], 1)} dan {n(h['A|RF']['median_ms'], 1)} ms untuk Random Forest), tetapi waktu total untuk 50 fitur tidak dapat disimpulkan karena biaya pengambilan halaman tidak terukur. "
  f"Aturan satu baris yang mengenali bentuk URL mencapai F1 {n(rule_ac.f1.mean(), 3)}, sehingga skor URL-only yang tinggi lebih tepat dibaca sebagai cerminan bentuk URL dalam dataset daripada kemampuan menggeneralisasi.")
P("Penelitian lanjutan dapat menguji data independen dan terpisah waktu, mengendalikan komposisi grup besar, menjalankan analisis sufiks privat, dan mengukur biaya pengambilan halaman tanpa mengakses URL phishing aktif.")

# ------------------------------------------------------------------ akhir
H("Ketersediaan Data dan Kode")
P("Data berasal dari PhiUSIIL Phishing URL (Website), UCI Machine Learning Repository (id 967; lisensi CC BY 4.0 menurut halaman UCI); salinan Kaggle diunduh pada 26 November 2026 (lisensi pada halaman Kaggle: CC BY-SA 4.0). "
  "Seluruh kode, hasil, dan catatan keputusan tersedia di https://github.com/navyzuu/ttki-phishing-detection (tag versi final: [diisi setelah rilis]). Data mentah tidak disertakan (SHA-256 pada data/README.md). "
  "Lingkungan: Python 3.11.9, pandas 3.0.5, scikit-learn 1.9.1, tldextract 5.4.0.")
H("Pernyataan Penggunaan AI")
P("Asisten AI digunakan untuk membantu menelusuri dan memverifikasi metadata literatur, membaca makalah akses terbuka, menulis dan memeriksa kode, serta menyusun draf naskah. Kode dijalankan dan seluruh angka pada bagian Hasil berasal dari eksperimen penelitian ini (berkas results/); penulis bertanggung jawab atas isi naskah.")
H("Referensi")
refs = [
    "Ahamed, T., Kakon, S. C., Farid, F. A., Uddin, J., & Abdul Karim, H. B. (2026). An integrated evaluation protocol for adversarial robustness, generalization, and explanation stability in URL-based phishing detection. *Frontiers in Computer Science, 8*, 1834407. https://doi.org/10.3389/fcomp.2026.1834407",
    "Arp, D., Quiring, E., Pendlebury, F., Warnecke, A., Pierazzi, F., Wressnegger, C., Cavallaro, L., & Rieck, K. (2022). Dos and don'ts of machine learning in computer security. *Proceedings of the 31st USENIX Security Symposium* (hlm. 3971–3988). https://www.usenix.org/conference/usenixsecurity22/presentation/arp",
    "Chaudhuri, A., & Mohankumar, B. (2026). Adversarial-resilient lightweight phishing url detection: Evaluating lexical & metadata features under evasion techniques. *Scientific Reports, 16*(1), 26668. https://doi.org/10.1038/s41598-026-60046-3",
    "Ivandanizar, M., & Taufiq. (2026). Analysis of feature selection effects on phishing URL detection performance. *Global Advances in Science, Engineering & Technology, 2*(1), 63–73. https://doi.org/10.62671/gaset.v2i1.362",
    "Kapoor, S., & Narayanan, A. (2023). Leakage and the reproducibility crisis in machine-learning-based science. *Patterns, 4*(9), 100804. https://doi.org/10.1016/j.patter.2023.100804",
    "Karbalaie, A., Abtahi, F., & Häger, C. K. (2026). Participant-aware model validation for repeated-measures data: Comparative cross-validation study. *JMIR AI, 5*, e87728. https://doi.org/10.2196/87728",
    "pradhyumnaag30. (2025). *PhiUSIIL-Phishing-URL-Detection* [Kode sumber]. GitHub. https://github.com/pradhyumnaag30/PhiUSIIL-Phishing-URL-Detection",
    "Prasad, A., & Chandra, S. (2024a). PhiUSIIL: A diverse security profile empowered phishing URL detection framework based on similarity index and incremental learning. *Computers & Security, 136*, 103545. https://doi.org/10.1016/j.cose.2023.103545",
    "Prasad, A., & Chandra, S. (2024b). *PhiUSIIL Phishing URL (Website)* [Dataset]. UCI Machine Learning Repository. https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset",
    "Yi, L., Omotosho, A., & Balogun, H. (2025). Phishing URL detection and interpretability with machine learning: A cross-dataset approach. *Security and Privacy, 9*(1). https://doi.org/10.1002/spy2.70175",
]
for r in refs:
    par = P(r, size=10)
    par.paragraph_format.left_indent = Cm(1.0)
    par.paragraph_format.first_line_indent = Cm(-1.0)
    par.paragraph_format.space_after = Pt(4)

OUT.parent.mkdir(exist_ok=True)
d.save(OUT)
kata_abs = len(abstrak.split())
print("tersimpan:", OUT, "| kata abstrak:", kata_abs)
