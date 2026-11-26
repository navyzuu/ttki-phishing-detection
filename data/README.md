# Data

Berkas CSV tidak disertakan di repositori (lihat `.gitignore`). Unduh sendiri lalu letakkan di `data/raw/`.

| Item | Nilai |
|---|---|
| Dataset | PhiUSIIL Phishing URL (Website) |
| Kaggle | https://www.kaggle.com/datasets/kaggleprollc/phishing-url-websites-dataset-phiusiil |
| UCI | https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset (id 967) |
| Pencipta | Arvind Prasad dan Shalini Chandra (2024) |
| Berkas | `PhiUSIIL_Phishing_URL_Dataset.csv`, 56.854.345 bita |
| SHA-256 | `a236549cd369cd80bd478ff8e1779cbf44c58d5c3f79f7a51a1adbed7d06d1c6` |
| Tanggal unduh | 26 November 2026 (dikonfirmasi pengguna) |
| Lisensi (UCI) | CC BY 4.0, tertera di halaman UCI id 967 (disumbangkan 3 Maret 2024). Wajib mencantumkan kredit kepada pencipta. |
| Lisensi (Kaggle) | [salin dari halaman Kaggle; belum diverifikasi] |
| Ukuran | 235.795 baris, 56 kolom (54 fitur, `FILENAME`, `label`) |
| Target | `label`: **1 = legitimate, 0 = phishing** (diverifikasi dari data; lihat `docs/decisions.md` D1) |

Cara memverifikasi berkas: `sha256sum data/raw/PhiUSIIL_Phishing_URL_Dataset.csv` harus sama dengan nilai di atas. Hasil audit: `python src/audit_data.py` menulis `results/audit_summary.json`.

Rujukan sumber: Prasad, A., & Chandra, S. (2024). PhiUSIIL: A diverse security profile empowered phishing URL detection framework based on similarity index and incremental learning. *Computers & Security, 136*, 103545. https://doi.org/10.1016/j.cose.2023.103545
