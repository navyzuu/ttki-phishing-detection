# Laporan Pembagian Kontribusi dan Pernyataan Kejujuran Akademik (DRAF)

**Status: draf untuk dikoreksi.** Isi di bawah menguraikan apa yang tercatat di riwayat pekerjaan. Setiap baris harus dikoreksi oleh anggota yang bersangkutan sebelum dikumpulkan.

Mata kuliah: Tata Tulis Karya Ilmiah (TTKI), Topik P1. Repositori: https://github.com/navyzuu/ttki-phishing-detection

## 1. Anggota dan peran

| Anggota | Peran yang diusulkan (Bab 7) |
|---|---|
| Anggota 1: Navyz Abdillah Zikhav | Koordinator eksperimen; keputusan arah penelitian |
| Anggota 2: Adryan Fahmi Ramadhan | Audit teknis independen, reproduksi, koordinator literatur dan QA dokumen (issue #1) |

## 2. Rincian kontribusi per tahap

Kolom "Asisten AI" mencatat pekerjaan yang dilakukan asisten AI atas arahan anggota. Tanda `—` berarti tidak ada catatan kontribusi pada tahap itu; anggota yang bersangkutan mengisi atau mengonfirmasinya.

| Tahap | Pekerjaan | Anggota 1 | Anggota 2 | Asisten AI |
|---|---|---|---|---|
| Pemilihan topik | Memilih P1 (phishing URL) dan dataset PhiUSIIL | memilih | — | - |
| Literatur | Menelusuri dan memverifikasi metadata makalah; membaca bagian relevan makalah akses terbuka | menetapkan kebijakan sumber gratis; menyetujui daftar | memeriksa sumber akses terbuka dan memperbarui `tingkat_baca` (Issue #1 bagian B, PR #2), dengan bantuan AI | menelusuri, mengunduh, dan meringkas sumber; mencocokkan klaim draf |
| Rumusan masalah | Menyusun RQ dan hipotesis setelah menemukan bahwa studi 2026 sudah menjalankan sebagian | memilih posisi "replikasi kritis" | — | mengusulkan opsi dan menyusun teks |
| Data | Mengunduh dan mengaudit dataset | mengunduh dari Kaggle | memverifikasi salinan Kaggle (SHA-256, lisensi) (Issue #1 bagian A.2 dan B), dengan bantuan AI | mengaudit data (`src/audit_data.py`) |
| Metodologi | Keputusan split, kelompok fitur, metrik, pembekuan konfigurasi (`docs/decisions.md`) | menyetujui keputusan terbuka (rasio split, lisensi) | — | merancang dan menulis |
| Kode | `src/*.py`, notebook, `environment-freeze.txt` | meninjau hasil | mengaudit pipeline, fitur, dan split terhadap kebocoran data (Issue #1 bagian A.1), dengan bantuan AI | menulis dan menjalankan kode |
| Eksperimen | Tuning, fase final, ablation, waktu inferensi, reproduksi repositori referensi | memberi arahan | mereproduksi audit data, pembagian data, dan notebook (Issue #1 bagian A.2), dengan bantuan AI | menjalankan dan melaporkan eksperimen |
| Penulisan | Draf paper IMRAD (`paper/draft.docx`) | meninjau; menyetujui pembingkaian | mengaudit draf terhadap checklist Bab 10.2 dan mencatat temuan (Issue #1 bagian B), dengan bantuan AI | menulis draf dari `results/`; memperbaiki paper dan README berdasarkan temuan audit |
| Repositori | Repositori publik, lisensi, issue, pull request | menyetujui visibilitas publik | mengajukan PR #2 | menyiapkan repositori |
| Peer review | Minggu 5 | [diisi] | [diisi] | menyiapkan tabel respons reviewer |

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
