# Laporan Pembagian Kontribusi dan Pernyataan Kejujuran Akademik (DRAF)

**Status: draf untuk dikoreksi.** Isi di bawah menguraikan apa yang tercatat di riwayat pekerjaan. Setiap baris harus dikoreksi oleh anggota yang bersangkutan sebelum dikumpulkan.

Mata kuliah: Tata Tulis Karya Ilmiah (TTKI), Topik P1. Repositori: https://github.com/navyzuu/ttki-phishing-detection

## 1. Anggota dan peran

| Anggota | Peran yang diusulkan (Bab 7) |
|---|---|
| Anggota 1: Navyz Abdillah Zikhav | Koordinator eksperimen; keputusan arah penelitian |
| Anggota 2: Adryan Fahmi Ramadhan | Audit teknis independen, reproduksi, koordinator literatur dan QA dokumen (issue #1) |

## 2. Rincian kontribusi per tahap

Kolom "Asisten AI" mencatat pekerjaan yang dilakukan oleh asisten AI atas permintaan anggota. Kolom lain mencatat arahan, bahan, serta pekerjaan anggota sendiri. Tanda `—` pada kolom Anggota 2 menandai kontribusi yang masih perlu dikonfirmasi.

| Tahap | Pekerjaan | Anggota 1 | Anggota 2 | Asisten AI |
|---|---|---|---|---|
| Pemilihan topik | Memilih P1 (phishing URL) dan dataset PhiUSIIL | memilih | — | - |
| Literatur | Menelusuri dan memverifikasi metadata makalah lewat basis data publik; membaca bagian relevan makalah akses terbuka | memutuskan kebijakan sumber gratis; menyetujui daftar | meminta pemeriksaan sumber terbuka dalam Issue #1 | menelusuri dan meringkas sumber, mencocokkan klaim draf, memperbarui `tingkat_baca`, serta memeriksa 14 entri RIS yang diimpor ke Zotero |
| Rumusan masalah | Menyusun RQ dan hipotesis setelah menemukan bahwa studi 2026 sudah menjalankan sebagian | memilih posisi "replikasi kritis" | — | mengusulkan opsi, menyusun teks |
| Data | Mengunduh dataset dari Kaggle | mengunduh | meminta verifikasi salinan Kaggle untuk reproduksi | mengunduh ulang CSV, memeriksa SHA-256 dan lisensi, serta menjalankan `src/audit_data.py` |
| Metodologi | Keputusan split, kelompok fitur, metrik, pembekuan konfigurasi (`docs/decisions.md`) | menyetujui keputusan terbuka (rasio split, lisensi) | — | merancang dan menulis |
| Kode | `src/*.py`, notebook, `environment-freeze.txt` | meninjau hasil | meminta audit pipeline, fitur, dan split | menulis dan menjalankan kode, serta mengaudit pemisahan train, validation, dan test |
| Eksperimen | Tuning, fase final, ablation, waktu inferensi, dan reproduksi | memberi arahan | meminta reproduksi audit data, split, dan notebook | menjalankan dan melaporkan eksperimen. Untuk Issue #1, mencocokkan dua hasil JSON serta menjalankan tiga notebook |
| Penulisan | Draf paper IMRAD (`paper/draft.docx`) | meninjau, menyetujui pembingkaian | menyediakan Buku Petunjuk Proyek TTKI untuk audit Bab 10.2 | menulis draf dari `results/`, memeriksa checklist, dan memverifikasi jumlah halaman |
| Repositori | Membuat repositori publik, lisensi, issue | menyetujui visibilitas publik | meminta pengerjaan Issue #1 dan pembaruan laporan di PR #2 | mengerjakan penyiapan repositori, melaporkan audit di Issue #1, dan mengajukan perubahan di PR #2 |
| Peer review | Minggu 5 | [diisi] | menunggu sesi peer review bersama | menyiapkan tabel respons reviewer |

## 3. Pemakaian asisten AI

Asisten AI dipakai selama pekerjaan ini untuk: menelusuri dan memverifikasi metadata literatur; membaca makalah akses terbuka; menulis dan menjalankan kode; menyusun draf proposal, naskah, dan dokumentasi. Seluruh angka pada naskah berasal dari eksperimen yang dijalankan pada repositori ini (berkas `results/`). Rujukan diperiksa terhadap DOI atau sumber aslinya; beberapa makalah hanya dibaca sebagian dan hal ini dicatat pada `references/literature_matrix.csv`. Anggota bertanggung jawab atas isi akhir.

Untuk bagian Anggota 2, bukti pekerjaan yang dijalankan dengan bantuan AI tercatat di [audit teknis](https://github.com/navyzuu/ttki-phishing-detection/issues/1#issuecomment-7184908006), [reproduksi](https://github.com/navyzuu/ttki-phishing-detection/issues/1#issuecomment-7185134388), dan [literatur serta QA](https://github.com/navyzuu/ttki-phishing-detection/issues/1#issuecomment-7185134841).

[Anggota: tambahkan bagian mana yang Anda periksa sendiri dan bagian mana yang Anda tulis ulang.]

## 4. Pernyataan kejujuran akademik

Kami menyatakan bahwa: (1) hasil eksperimen pada naskah berasal dari pelaksanaan eksperimen pada repositori ini dan tidak disalin dari repositori lain; (2) rujukan yang dicantumkan telah diperiksa dan dikutip sebatas bagian yang dibaca; (3) pemakaian asisten AI dilaporkan pada bagian 3; (4) setiap anggota mampu menjelaskan seluruh metode dan hasil.

| Nama | Tanda tangan | Tanggal |
|---|---|---|
| Navyz Abdillah Zikhav | | |
| Adryan Fahmi Ramadhan | | |
