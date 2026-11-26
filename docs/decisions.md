# Catatan Keputusan Metodologi

**Status: DRAF.** Dokumen ini dibekukan (di-commit) sebelum model pertama dilatih dan sebelum data uji dievaluasi. Perubahan sesudah itu dicatat di bagian "Perubahan" dengan alasan, bukan menimpa keputusan awal.

Dasar: audit data (`src/audit_data.py`, hasil di `results/audit_summary.json`). Audit hanya statistik deskriptif; belum ada model yang dilatih.

## D1. Arah label dan kelas positif
- Pada berkas asli, `label = 1` berarti legitimate (134.850 baris) dan `label = 0` berarti phishing (100.945 baris). Dasar: situs `label = 1` berupa domain yang lazim sah, dan seluruhnya bernilai `URLSimilarityIndex = 100`.
- **Kelas positif dalam semua tabel adalah phishing.** Kolom bantu `phish = (label == 0)` dipakai di seluruh kode.
- Dokumen awal proyek (CLAUDE.md, proposal lama) menyebut arah sebaliknya; itu keliru.

## D2. Duplikat URL
- 425 URL muncul dua kali (850 baris), seluruhnya berkelas phishing, tanpa konflik label.
- Keputusan: pertahankan kemunculan pertama, buang sisanya. Hasil: 235.370 URL (phishing 100.520; proporsi 42,71%).

## D3. Kolom yang tidak dipakai sebagai fitur
`FILENAME`, `URL`, `Domain`, `TLD`, `Title` (identitas atau teks bebas), dan `label`. `Domain` hanya dipakai membentuk kelompok split. `TLD` mentah dikecualikan pada versi awal karena kardinalitas tinggi; `TLDLength` tetap dipakai.

## D4. Kelompok fitur (50 fitur numerik)
Pengelompokan berdasarkan asal fitur, bukan berdasarkan kekuatan prediksinya.
- **Leksikal murni URL (18):** URLLength, DomainLength, IsDomainIP, TLDLength, NoOfSubDomain, HasObfuscation, NoOfObfuscatedChar, ObfuscationRatio, NoOfLettersInURL, LetterRatioInURL, NoOfDegitsInURL, DegitRatioInURL, NoOfEqualsInURL, NoOfQMarkInURL, NoOfAmpersandInURL, NoOfOtherSpecialCharsInURL, SpacialCharRatioInURL, IsHTTPS.
- **Turunan korpus (4):** URLSimilarityIndex, CharContinuationRate, TLDLegitimateProb, URLCharProb. Nilainya dihitung terhadap korpus URL lain, sehingga tidak dapat dihitung dari satu URL secara mandiri. Dicatat bahwa pada data ini seluruh URL legitimate bernilai `URLSimilarityIndex = 100`.
- **Konten HTML (28):** sisanya (LineOfCode, NoOfJS, NoOfExternalRef, dan seterusnya); memerlukan pengambilan halaman.
- "URL-only" = 18 fitur leksikal. "Semua fitur" = ke-50 fitur. Turunan korpus diuji sebagai ablation terpisah (URL-only + turunan korpus).

## D5. Pembentukan kelompok untuk split per domain
- Kunci kelompok: eTLD+1 dari `Domain` memakai `tldextract` 5.4.0 dengan daftar sufiks bawaan (hanya sufiks ICANN, tanpa jaringan).
- Platform hosting publik (`web.app` 5.754 baris, `firebaseapp.com` 5.594, `repl.co` 3.754, dan seterusnya) menjadi satu kelompok besar. Ini pilihan konservatif. Sensitivitas dengan sufiks privat (`include_psl_private_domains=True`) dilaporkan sebagai analisis tambahan.
- 608 baris dengan eTLD+1 kosong (kemungkinan alamat IP): kunci kelompok diganti nilai `Domain` penuh.
- 67 kelompok berukuran >100 baris menampung 40.636 baris (17,2%); ukuran dan proporsi kelas tiap bagian split dilaporkan.

## D6. Split dan seed
- Tiga bagian: train, validation, test, dengan rasio 70:15:15 (diputuskan 26 November 2026).
- *Random split*: stratifikasi menurut kelas, seed 42; diulang pada seed 42 sampai 46.
- Split per eTLD+1: seluruh URL satu kelompok berada pada satu bagian; seed 42 sampai 46. Implementasi: `StratifiedGroupKFold` 20 lipatan, diacak lalu dirakit 14/3/3 (lihat Perubahan 1).
- Imputer, scaler, dan seleksi fitur hanya di-fit pada train.

## D7. Model, tuning, dan evaluasi
- Baseline: Logistic Regression dan Random Forest. Hyperparameter dipilih hanya pada validation dengan grid kecil yang dicatat sebelum dijalankan.
- Test dihitung sekali setelah dokumen ini dan konfigurasi dibekukan.
- Metrik: F1 (kelas positif phishing), precision, recall, ROC-AUC, PR-AUC, matriks konfusi, jumlah false negative. Interval 95% dengan *bootstrap* pada test.
- Ukuran efek: selisih F1 antara *random split* dan split eTLD+1 dengan interval *bootstrap*; selisih dianggap berarti bila interval 95% tidak mencakup nol. Tidak ada ambang praktis tambahan; besar selisih dilaporkan apa adanya. Waktu inferensi dibandingkan dengan cara yang sama (interval *bootstrap* atas pengulangan).

## D8. Pengukuran waktu inferensi
- Waktu total = ekstraksi fitur dari string URL (implementasi sendiri di `src/`) + prediksi, per URL, median dari beberapa pengulangan pada mesin yang sama.
- Fitur konten HTML tidak dapat diekstrak dari CSV; tidak ada URL phishing yang diakses. Biayanya dicatat sebagai keterbatasan, bukan diestimasi tanpa dasar.

## D9. Status keputusan (26 November 2026)
- Rasio split 70:15:15 dan seed 42 sampai 46: diputuskan.
- Ambang praktis selisih F1 dan latensi: tidak ada; hanya kriteria interval 95% (D7).
- Lisensi kode: MIT (`LICENSE`). Dataset tetap berlisensi sendiri (`data/README.md`).
- Masih kosong dan tidak menghalangi eksperimen: identitas Anggota 2 dan teks lisensi dari halaman Kaggle.

## Perubahan

### 1. Split per eTLD+1 dibuat berstratifikasi (26 November 2026, sebelum model apa pun dilatih)
- Temuan (`results/split_check.json`, `src/check_splits.py`): dengan `GroupShuffleSplit` biasa, proporsi phishing pada test berkisar 35,4% sampai 54,1% antar seed, dan ukuran test 31.752 sampai 43.948 baris, karena grup raksasa (`web.app`, `firebaseapp.com`, dan seterusnya) jatuh acak ke satu bagian.
- Alasan: F1 bergantung pada proporsi kelas, sehingga selisih F1 *random split* vs split grup akan tercampur dengan perbedaan proporsi, bukan hanya efek domain.
- Keputusan: skema utama `grup` memakai `StratifiedGroupKFold` (20 lipatan, dirakit 14/3/3). Hasil: test berproporsi phishing 42,4% sampai 43,6% (total 42,71%), ukuran bagian sekitar 70/15/15, tumpang tindih grup nol pada semua seed.
- Versi naif tetap tersedia sebagai `grup_shuffle` untuk analisis sensitivitas (sebanding dengan GroupShuffleSplit pada studi terdahulu).
- Biaya: pembuatan split per grup lambat (menit per seed); hasil di-cache di `data/interim/` (tidak masuk repositori) dan dapat dibuat ulang dari seed.

### 2. Fitur URL-only dihitung ulang dari string URL (26 November 2026, sebelum model apa pun dilatih)
- Temuan (`src/check_features.py`, `results/feature_agreement.json`, 20.000 baris acak): 18 kolom leksikal PhiUSIIL tidak dapat direproduksi persis dari string URL. `URLLength` berbeda 1 karakter dari panjang URL pada 79% baris, jumlah huruf memakai definisi yang tidak jelas, dan korelasi rasio berbeda dari tebakan definisi (LetterRatioInURL 0,51; SpacialCharRatioInURL 0,57; ObfuscationRatio 0,67). Fitur domain, TLD, subdomain, digit, dan IsDomainIP cocok 99,6% sampai 100%.
- Masalah: waktu ekstraksi (bagian RQ) hanya dapat diukur dengan fungsi ekstraksi sendiri, dan model yang dilatih pada kolom CSV tidak identik dengan fitur hasil fungsi itu.
- Keputusan: skenario URL-only (B, C) dan ablation memakai 18 fitur hasil `src/features.py` (nama mengikuti PhiUSIIL, definisi dituliskan di kode). Fungsi yang sama dipakai untuk melatih dan mengukur waktu. Skenario "semua fitur" (A, D) tetap memakai 50 kolom CSV.
- Konsekuensi: A dan B tidak hanya berbeda pada kelompok fitur, tetapi juga pada definisi 18 fitur leksikalnya; hal ini dilaporkan sebagai keterbatasan, bersama tingkat kecocokan per fitur.

### 3. Catatan sebelum fase final (26 November 2026; setelah tuning pada validation, sebelum data test dibuka)
- Konfigurasi hasil tuning (`results/config_beku.json`) dibekukan lewat commit. Aturan seri: bila beberapa konfigurasi memiliki F1 validation sama, dipilih yang pertama pada grid (paling sederhana). Ini terjadi pada Random Forest skenario A dan D (semua konfigurasi F1 = 1,00000) dan Logistic Regression A dan D (C = 1,0 dan 10,0 seri). Pada skenario B dan C, nilai C terbaik Logistic Regression ada di tepi grid (10,0); tidak diperluas agar grid tidak dibentuk setelah melihat hasil.
- Temuan pada validation (seed 42): F1 skenario A dan D 0,9998 sampai 1,0000; skenario B dan C sekitar 0,99 (Random Forest 0,9938 acak vs 0,9934 grup). Selisih acak vs grup sangat kecil.
- **Artefak dataset (analisis deskriptif pada seluruh data):** 100% URL legitimate (134.850) berbentuk `https://www.<domain>` tanpa path; hanya 1,0% URL phishing (1.036 dari 100.520) berbentuk sama. Aturan satu baris tanpa parameter ("bukan bentuk itu = phishing") memberi F1 0,9948 pada seluruh data. Akibatnya F1 URL-only sekitar 0,99 tidak membuktikan kemampuan mendeteksi phishing sungguhan; fitur leksikal sebagian besar memisahkan kelas lewat bentuk URL yang dihasilkan cara pengumpulan data.
- Keputusan: aturan tersebut dimasukkan sebagai baseline diagnostik tanpa pelatihan (`ATURAN`, skenario `R_acak` dan `R_grup`) dan dilaporkan dengan label analisis post-hoc. Aturan dirumuskan setelah melihat statistik deskriptif data, bukan hasil test.
- Konsekuensi untuk paper: temuan ini dilaporkan di Pembahasan dan keterbatasan; klaim ketahanan terhadap domain baru tidak ditarik dari split internal (sejalan dengan buku, hlm. 6).

## Log eksekusi
- 26 November 2026, 11:09: `python src/run_experiments.py final` dijalankan satu kali dengan `results/config_beku.json` hasil commit `ee8f601`. Data test baru dibuka pada eksekusi ini. Hasil tersimpan di `results/metrics.csv` (100 baris) dan tidak diubah sesudahnya. Tidak ada konfigurasi, fitur, atau split yang diubah setelah melihat hasil test.
- 26 November 2026, sesudah test dibuka: dua analisis post-hoc deskriptif (dilabeli demikian di paper). (1) Aturan satu baris bentuk URL (Perubahan 3). (2) Pada skenario C Random Forest seed 44, F1 test 0,9812 (seed lain 0,993 sampai 0,996) dengan 534 false negative; 452 di antaranya (84,6%) berasal dari grup `web.app`, yang seluruhnya (5.718 URL, semuanya phishing) jatuh ke test pada seed itu (`src/analyze_outlier.py`, `results/analysis_outlier_seed44.json`). Tidak ada konfigurasi yang diubah karena temuan ini.
- 26 November 2026: reproduksi baseline repo referensi G1 (`src/reproduce_g1.py`, `results/reproduksi_g1.json`). SHA-256 `Dataset/Dataset.csv` di G1 identik dengan berkas kita. Protokol G1 ditiru apa adanya (50 fitur numerik, split stratified 70:30 seed 42, tanpa deduplikasi, model tanpa seed; scikit-learn 1.9.1 dan bukan 1.7.2). Hasil cocok sampai enam desimal dengan yang dipublikasikan di README G1 (Logistic Regression F1 0,999913; Decision Tree dan Random Forest 1,000000; Extra Trees 0,999975). Perbedaan metodologis yang dicatat: G1 memakai `label = 1` (legitimate) sebagai kelas positif, tidak mendeduplikasi URL, tidak memakai validation set, dan tidak mengelompokkan menurut domain. Dengan phishing sebagai kelas positif, F1 Logistic Regression 0,999884.
- 26 November 2026, sesudah test utama dibuka: ablation post-hoc skenario E (split acak) dan F (split grup) dengan 18 fitur URL hasil ekstraksi ditambah 4 fitur turunan korpus (`src/run_ablation.py`, konfigurasi dibekukan di commit `b7082aa` sebelum test ablation dibuka; `results/metrics_ablasi.csv`). Hyperparameter dipilih hanya pada validation. F1 test rata-rata lima seed: E LR 0,9998 dan RF 1,0000; F LR 0,9995 dan RF 0,9999. Selisih terhadap B dan C (`src/analyze_ablation.py`, `results/analysis_ablasi.csv`): E−B +0,0089 (LR) dan +0,0056 (RF), F−C +0,0077 dan +0,0078; interval 95% tidak mencakup nol pada 5 dari 5 seed untuk keempatnya. Selisih acak vs grup pada skenario ini: LR +0,0003 (2 dari 5 seed berbeda nyata), RF +0,00006 (0 dari 5). Seluruh angka ini dilaporkan sebagai analisis post-hoc.
