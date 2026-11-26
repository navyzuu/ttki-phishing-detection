# Laporan Pembagian Kontribusi dan Pernyataan Kejujuran Akademik (DRAF)

**Status: draf untuk dikoreksi.** Isi di bawah menguraikan apa yang tercatat di riwayat pekerjaan. Setiap baris harus dikoreksi oleh anggota yang bersangkutan sebelum dikumpulkan. Bagian Anggota 2 sengaja kosong.

Mata kuliah: Tata Tulis Karya Ilmiah (TTKI), Topik P1. Repositori: https://github.com/navyzuu/ttki-phishing-detection

## 1. Anggota dan peran

| Anggota | Peran yang diusulkan (Bab 7) |
|---|---|
| Anggota 1: Navyz Abdillah Zikhav | Koordinator eksperimen; keputusan arah penelitian |
| Anggota 2: [diisi] | Audit teknis independen, reproduksi, koordinator literatur dan QA dokumen (issue #1) |

## 2. Rincian kontribusi per tahap

Kolom "Asisten AI" mencatat pekerjaan yang dilakukan oleh asisten AI atas permintaan anggota. Kolom lain mencatat keputusan dan pekerjaan anggota sendiri.

| Tahap | Pekerjaan | Anggota 1 | Anggota 2 | Asisten AI |
|---|---|---|---|---|
| Pemilihan topik | Memilih P1 (phishing URL) dan dataset PhiUSIIL | memilih | [diisi] | - |
| Literatur | Menelusuri dan memverifikasi metadata makalah lewat basis data publik; membaca bagian relevan makalah akses terbuka | memutuskan kebijakan sumber gratis; menyetujui daftar | [diisi] | menelusuri, mengunduh, mengekstrak, meringkas |
| Rumusan masalah | Menyusun RQ dan hipotesis setelah menemukan bahwa studi 2026 sudah menjalankan sebagian | memilih posisi "replikasi kritis" | [diisi] | mengusulkan opsi, menyusun teks |
| Data | Mengunduh dataset dari Kaggle | mengunduh | [diisi] | mengaudit (skrip `src/audit_data.py`) |
| Metodologi | Keputusan split, kelompok fitur, metrik, pembekuan konfigurasi (`docs/decisions.md`) | menyetujui keputusan terbuka (rasio split, lisensi) | [diisi] | merancang dan menulis |
| Kode | `src/*.py`, notebook, `environment-freeze.txt` | meninjau hasil | [diisi: audit independen] | menulis dan menjalankan |
| Eksperimen | Tuning, fase final, ablation, waktu inferensi, reproduksi repositori referensi | memberi arahan | [diisi: reproduksi] | menjalankan; melaporkan hasil apa adanya |
| Penulisan | Draf paper IMRAD (`paper/draft.docx`) | meninjau, menyetujui pembingkaian | [diisi] | menulis draf; angka dibaca dari `results/` |
| Repositori | Membuat repositori publik, lisensi, issue | menyetujui visibilitas publik | [diisi] | mengerjakan |
| Peer review | Minggu 5 | [diisi] | [diisi] | - |

## 3. Pemakaian asisten AI

Asisten AI dipakai selama pekerjaan ini untuk: menelusuri dan memverifikasi metadata literatur; membaca makalah akses terbuka; menulis dan menjalankan kode; menyusun draf proposal, naskah, dan dokumentasi. Seluruh angka pada naskah berasal dari eksperimen yang dijalankan pada repositori ini (berkas `results/`). Rujukan diperiksa terhadap DOI atau sumber aslinya; beberapa makalah hanya dibaca sebagian dan hal ini dicatat pada `references/literature_matrix.csv`. Anggota bertanggung jawab atas isi akhir.

[Anggota: tambahkan bagian mana yang Anda periksa sendiri dan bagian mana yang Anda tulis ulang.]

## 4. Pernyataan kejujuran akademik

Kami menyatakan bahwa: (1) hasil eksperimen pada naskah berasal dari pelaksanaan eksperimen pada repositori ini dan tidak disalin dari repositori lain; (2) rujukan yang dicantumkan telah diperiksa dan dikutip sebatas bagian yang dibaca; (3) pemakaian asisten AI dilaporkan pada bagian 3; (4) setiap anggota mampu menjelaskan seluruh metode dan hasil.

| Nama | Tanda tangan | Tanggal |
|---|---|---|
| Navyz Abdillah Zikhav | | |
| [Anggota 2] | | |
