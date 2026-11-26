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
- Tiga bagian: train, validation, test, dengan rasio 70:15:15 (usulan, menunggu persetujuan kelompok).
- *Random split*: stratifikasi menurut kelas, seed 42; diulang pada seed 42 sampai 46.
- Split per eTLD+1: seluruh URL satu kelompok berada pada satu bagian; seed 42 sampai 46.
- Imputer, scaler, dan seleksi fitur hanya di-fit pada train.

## D7. Model, tuning, dan evaluasi
- Baseline: Logistic Regression dan Random Forest. Hyperparameter dipilih hanya pada validation dengan grid kecil yang dicatat sebelum dijalankan.
- Test dihitung sekali setelah dokumen ini dan konfigurasi dibekukan.
- Metrik: F1 (kelas positif phishing), precision, recall, ROC-AUC, PR-AUC, matriks konfusi, jumlah false negative. Interval 95% dengan *bootstrap* pada test.
- Ukuran efek: selisih F1 antara *random split* dan split eTLD+1 dengan interval *bootstrap*; selisih dianggap berarti bila interval 95% tidak mencakup nol. Ambang praktis tambahan [ditentukan kelompok sebelum test].

## D8. Pengukuran waktu inferensi
- Waktu total = ekstraksi fitur dari string URL (implementasi sendiri di `src/`) + prediksi, per URL, median dari beberapa pengulangan pada mesin yang sama.
- Fitur konten HTML tidak dapat diekstrak dari CSV; tidak ada URL phishing yang diakses. Biayanya dicatat sebagai keterbatasan, bukan diestimasi tanpa dasar.

## D9. Pertanyaan yang belum diputuskan
- Rasio split 70:15:15 dan jumlah pengulangan seed.
- Ambang praktis selisih F1 dan latensi.
- Lisensi kode repositori (LICENSE).

## Perubahan
(Belum ada.)
