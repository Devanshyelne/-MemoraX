# Mini Project Report: Page Replacement Algorithm Visualizer

## 1. Title
**PageVault — Visual Simulator for Page Replacement Algorithms**

## 2. Abstract
PageVault is a Python-based educational application that demonstrates page replacement in operating systems. The user supplies a page-reference string and a fixed number of memory frames. The simulator executes FIFO, LRU, and Optimal page replacement algorithms, records the frame state after each request, and reports page hits, page faults, hit rate, and fault rate. Interactive charts and trace tables help learners compare policies under the same workload.

## 3. Problem Statement
Physical memory is limited. When a process requests a page that is not currently resident, a page fault occurs. If all frames are occupied, the operating system must select a resident page to replace. Different replacement policies can produce different numbers of page faults. The project aims to make those differences observable and easy to understand.

## 4. Objectives
1. Implement FIFO, LRU, and Optimal page replacement in Python.
2. Visualize frame contents after each page request.
3. Calculate hit/fault counts and percentages.
4. Compare algorithm outcomes using the same input.
5. Provide a simple interactive interface and exportable results.

## 5. Technologies Used
- **Python:** algorithm implementation and simulation logic.
- **Streamlit:** interactive web interface.
- **Pandas:** tabular results and CSV reports.
- **Plotly:** interactive comparison and request charts.
- **unittest:** correctness tests for core algorithms.

## 6. Methodology
The program parses a sequence of page identifiers and initializes a configurable number of empty frames. For each requested page, it checks whether the page is already in a frame. If yes, it counts a hit. If not, it counts a fault and either uses an empty frame or selects a victim page according to the chosen algorithm. The frame state and outcome are recorded after each request. The same reference string is then evaluated with all three policies to make comparisons fair.

### FIFO
FIFO removes the resident page that entered memory earliest. In this implementation, each loaded page is associated with its insertion index.

### LRU
LRU removes the resident page whose latest access occurred earliest in the past. The simulator tracks the last-used index for each resident page.

### Optimal
Optimal removes the resident page whose next use is farthest in the remaining reference string. A page not referenced again is treated as having an infinite next-use distance. This algorithm is used as a theoretical benchmark, not as a directly deployable online policy.

## 7. Output Metrics
- **Page hit:** requested page is present in a frame.
- **Page fault:** requested page is absent and must be loaded.
- **Hit rate:** hits divided by total requests, multiplied by 100.
- **Fault rate:** faults divided by total requests, multiplied by 100.
- **Evicted page:** page removed when no empty frame remains.

## 8. Example Result
For reference string `7 0 1 2 0 3 0 4 2 3 0 3 2` with 3 frames:

| Algorithm | Page faults | Page hits |
|---|---:|---:|
| FIFO | 10 | 3 |
| LRU | 9 | 4 |
| Optimal | 7 | 6 |

These values are specific to the given reference sequence and frame count.

## 9. Conclusion
PageVault demonstrates that page-replacement policy affects the number of page faults for a given memory workload. FIFO is easy to implement, LRU uses recent history, and Optimal provides a theoretical minimum-fault benchmark when the future sequence is known. The interactive interface makes the algorithms easier to explore and compare.

## 10. Limitations and Future Scope
This is a simulation and does not change actual hardware memory or operate inside an OS kernel. Future improvements could include adding Clock/Second-Chance, generating random test sequences, and evaluating the algorithms on larger workloads.
