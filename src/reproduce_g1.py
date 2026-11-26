"""Reproduksi baseline repo referensi G1 (pradhyumnaag30/PhiUSIIL-Phishing-URL-Detection, notebook 02_Baseline).

Protokol G1, ditiru apa adanya: CSV mentah (tanpa deduplikasi), kolom FILENAME dibuang, seluruh kolom numerik
kecuali label, train_test_split(test_size=0.3, random_state=42, stratify=y), model tanpa random_state
(LR max_iter=10000; DT; RF 200 pohon; ExtraTrees 200 pohon). Metrik dihitung dengan label=1 sebagai kelas positif,
seperti pada G1 (label=1 = legitimate).

Kami melaporkan dua pandangan atas prediksi yang sama:
  - positif_label1  : label=1 (legitimate) positif, seperti G1;
  - positif_phishing: label=0 (phishing) positif, seperti penelitian ini.
Angka README G1 tidak disalin; perbandingan dilakukan di paper dengan atribusi.
Keluaran: results/reproduksi_g1.json
"""
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from preprocessing import CSV


def metrik(y, pred, skor, positif):
    yp, pp = (y == positif).astype(int), (pred == positif).astype(int)
    return {"accuracy": accuracy_score(yp, pp), "precision": precision_score(yp, pp), "recall": recall_score(yp, pp),
            "f1": f1_score(yp, pp), "roc_auc": roc_auc_score(yp, skor)}


def main():
    df = pd.read_csv(CSV).drop("FILENAME", axis=1)
    fitur = [c for c in df.select_dtypes(include=[np.number]).columns if c != "label"]
    X, y = df[fitur], df["label"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    model = {"Logistic Regression": LogisticRegression(max_iter=10000), "Decision Tree": DecisionTreeClassifier(),
             "Random Forest": RandomForestClassifier(n_estimators=200), "Extra Trees": ExtraTreesClassifier(n_estimators=200)}
    hasil = {"lingkungan": {"python": platform.python_version(), "scikit_learn": sklearn.__version__},
             "protokol": {"baris": int(len(df)), "n_fitur": len(fitur), "n_train": int(len(ytr)), "n_test": int(len(yte)),
                          "catatan": "model tanpa random_state seperti G1; hasil DT/RF/ET dapat berbeda tipis antar run"},
             "hasil": {}}
    for nama, m in model.items():
        m.fit(Xtr, ytr)
        pred = m.predict(Xte)
        p1 = m.predict_proba(Xte)[:, list(m.classes_).index(1)]
        p0 = m.predict_proba(Xte)[:, list(m.classes_).index(0)]
        hasil["hasil"][nama] = {"positif_label1": metrik(yte.to_numpy(), pred, p1, 1),
                                "positif_phishing": metrik(yte.to_numpy(), pred, p0, 0)}
        print(nama, {k: round(v, 6) for k, v in hasil["hasil"][nama]["positif_label1"].items()}, flush=True)
    Path("results/reproduksi_g1.json").write_text(json.dumps(hasil, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
