# MemoraX — Smart Memory Lab (Python Edition)

An interactive Python mini-project that demonstrates all five memory-management topics listed in the syllabus:

1. **Integration with ML Frameworks** — train a scikit-learn Random Forest to predict the next page from the previous two page labels.
2. **Memory Compression Techniques** — measure real lossless compression with Python's built-in `zlib` and inspect repeated tokens.
3. **Intelligent Prefetching** — estimate the next page using observed page-transition patterns.
4. **Memory Allocation Strategies** — compare First Fit, Best Fit, and Worst Fit.
5. **Page Replacement Algorithm** — compare FIFO, LRU, and Optimal page replacement step by step.

The application and algorithms are written in Python. Streamlit provides the interface, and Plotly provides interactive charts. It does not modify your computer's actual RAM; it is an educational simulator.

## Run the project

Recommended: Python 3.11–3.13.

### macOS / Linux

```bash
cd MemoraX_Python_Project
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit should open the project in your browser. If it doesn't, open the local URL printed in Terminal (usually `http://localhost:8501`).

### Windows PowerShell

```powershell
cd MemoraX_Python_Project
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

### Launcher shortcuts

- macOS/Linux: run `./run_mac.command` (on macOS you may need to right-click > Open once). It creates `.venv` if needed and starts the app.
- Windows: double-click `run_windows.bat`.

If the Mac launcher is not executable, run `chmod +x run_mac.command` once in Terminal.

## Project structure

```text
MemoraX_Python_Project/
├── app.py                 # Streamlit user interface and interactive charts
├── core.py                # Pure-Python algorithms, independently testable
├── requirements.txt       # Python package dependencies
├── README.md              # Setup, project scope, and explanation
├── run_mac.command        # Optional macOS/Linux launcher
├── run_windows.bat        # Optional Windows launcher
└── tests/
    └── test_core.py       # Unit tests for core algorithms
```

## Main algorithms

- **FIFO:** replaces the page that entered memory earliest.
- **LRU:** replaces the page least recently used in the past.
- **Optimal:** replaces the page whose next use is farthest in the future; it is a theoretical benchmark.
- **First/Best/Worst Fit:** allocate each process into a remaining memory block according to the selected placement rule.
- **Compression:** `zlib.compress` / `zlib.decompress` demonstrate actual lossless compression; the app checks that decompression restores the exact bytes.
- **Prefetching:** counts page transitions, with a shorter-context and overall-frequency fallback when an exact pattern is absent.
- **ML integration:** `DictVectorizer` encodes the two previous pages; `RandomForestClassifier` predicts the subsequent page and displays class probabilities.

## Unit tests

With dependencies installed, run:

```bash
python -m unittest discover -s tests -v
```

## Suggested demo

1. Open the Overview and run the quick page-replacement experiment.
2. Compare page faults across FIFO, LRU, and Optimal.
3. Change allocation sizes and compare First Fit with Best Fit.
4. Compress text with repeated sentences and inspect the byte savings.
5. Run Intelligent Prefetching on `A B C A B C A B`.
6. Open ML Integration and explain features, labels, training, and prediction.

## Limitations to explain honestly

This is a classroom simulator. Results depend on the input sequence and memory sizes. Optimal replacement has access to future references by definition. The prefetcher and ML demo use small sample histories and do not establish real-world accuracy. A real operating system would need much more complex kernel-level integration, workload testing, and performance/safety validation.
# -MemoraX
