# PageVault — Page Replacement Algorithm Visualizer

**This project is only for syllabus topic 5: Page Replacement Algorithm.** It does not include memory allocation, compression, prefetching, or ML integration as separate project modules.

PageVault is an interactive Python mini-project that visualizes the FIFO, LRU, and Optimal page replacement algorithms. It shows page hits, page faults, the page evicted at each step, frame contents, hit/fault rates, and side-by-side comparison charts.

## Features

- Custom page-reference string (space-, comma-, semicolon-, or newline-separated).
- Adjustable number of page frames.
- FIFO, LRU, and Optimal implementations.
- Step-by-step frame viewer and complete trace table.
- Comparison chart for hits and faults across the three algorithms.
- Downloadable CSV reports for the comparison and step trace.
- Theory explanations and viva questions inside the app.
- Automated unit tests for algorithm results and input validation.

## Run on macOS

Open Terminal in this folder and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown in Terminal, usually `http://localhost:8501`.

## Run on Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Project structure

```text
Page_Replacement_Algorithm_Project/
├── app.py              # Streamlit UI, charts, step viewer, comparison, viva guide
├── core.py             # FIFO, LRU, Optimal algorithms and parsing
├── requirements.txt    # App dependencies
├── README.md           # Installation and project documentation
├── PROJECT_REPORT.md   # Report content for submission
├── run_mac.command     # Optional macOS launcher
├── run_windows.bat     # Optional Windows launcher
└── tests/
    └── test_core.py    # Unit tests
```

## Algorithm summaries

- **FIFO (First In, First Out):** evicts the page that has been resident for the longest time.
- **LRU (Least Recently Used):** evicts the page whose most recent access happened farthest in the past.
- **Optimal:** evicts the resident page whose next use is farthest in the future. This is a theoretical benchmark because future requests are not known by ordinary operating systems.

## Default example

Reference string: `7 0 1 2 0 3 0 4 2 3 0 3 2`  
Frames: `3`

Expected page faults:

| Algorithm | Page faults | Page hits |
|---|---:|---:|
| FIFO | 10 | 3 |
| LRU | 9 | 4 |
| Optimal | 7 | 6 |

## Scope and limitations

This is a classroom simulator, not a kernel-level memory manager. It does not access or modify the computer's actual RAM. Optimal is allowed to inspect future items in the supplied reference string because its purpose is to provide a benchmark. The result is specific to the selected workload and frame count.
