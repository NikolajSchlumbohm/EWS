# RQA Modul (Recurrence Quantification Analysis)

## Überblick
Dieses Verzeichnis enthält ein Jupyter-Notebook, Daten und Visualisierungen zur Berechnung und Auswertung rekurrenter Fixationsmuster (Eye-Tracking) mittels Recurrence Quantification Analysis (RQA). Bei der RQA gelten zwei Fixationen als rekurrent, wenn deren Etfernung <= d ist. Hier wurde d = 1/16 = 0.0625 gewählt (alle Fixationskoordinaten zwischen 0 und 1 normiert).

## Verzeichnisstruktur
```text
rqa/
├── RQA.ipynb                         # Notebook für Analyse
├── rqa_data/
│   ├── recurrence_matrix/            # kleiner Teil der Rekurrenz Matrizen (.npz), berechnet aus ews/code/preprocess/events/fixations mit der Methode create_recurrence_matrix(file_path, distance_threshold, output_dir) (alle Dateien waren zu groß, um sie ins Git Repo zu pushen)
│   ├── metrics/                      # Kennzahlen + Metriken jeder Rekurrenz Matrix in Form einer CSV (N, R, Rec etc)
│   ├── figures/                      # Generierte Abbildungen zur Auswertung
│   │   ├── Recurrence_Plot/          # Einzelne Recurrence Plots (PNG)
│   │   ├── heatmap_img/              # Heatmaps zu den Recurrence Plots
│   │   ├── Meme_vs_noMeme/           # Vergleichskategorie als Histogramm
│   │   ├── Ort_vs_noOrt/
│   │   ├── Person_vs_noPerson/
│   │   ├── Text_vs_noText/
│   │   ├── correlation_matrix.png    # Korrelationsmatrix der Metriken
│   │   └── all_metrics_histogram.png # Histogramme der Metriken
