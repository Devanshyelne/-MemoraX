from __future__ import annotations

import re
import zlib
from collections import Counter, defaultdict
from typing import Any


def parse_items(raw: str) -> list[str]:
    """Parse a comma/space/newline separated sequence into clean tokens."""
    return [item.strip() for item in re.split(r"[,\s]+", raw.strip()) if item.strip()]


def run_page_replacement(reference_string: list[str], capacity: int, algorithm: str) -> dict[str, Any]:
    """Simulate FIFO, LRU, or Optimal page replacement and return each step."""
    frames: list[str | None] = [None] * capacity
    last_used: dict[str, int] = {}
    fifo_pointer = 0
    rows: list[dict[str, Any]] = []
    hits = faults = 0

    for index, page in enumerate(reference_string):
        result = "HIT" if page in frames else "FAULT"
        evicted: str | None = None
        if result == "HIT":
            hits += 1
        else:
            faults += 1
            if None in frames:
                slot = frames.index(None)
            elif algorithm == "FIFO":
                slot = fifo_pointer % capacity
                fifo_pointer += 1
            elif algorithm == "LRU":
                resident = [p for p in frames if p is not None]
                victim = min(resident, key=lambda p: last_used.get(p, -1))
                slot = frames.index(victim)
            elif algorithm == "Optimal":
                future = reference_string[index + 1:]
                resident = [p for p in frames if p is not None]
                next_use: dict[str, float] = {}
                for resident_page in resident:
                    next_use[resident_page] = float(future.index(resident_page)) if resident_page in future else float("inf")
                victim = max(resident, key=lambda p: next_use[p])
                slot = frames.index(victim)
            else:
                raise ValueError(f"Unknown page replacement algorithm: {algorithm}")
            evicted = frames[slot]
            frames[slot] = page
        last_used[page] = index

        row: dict[str, Any] = {
            "Step": index + 1,
            "Page": page,
            "Result": result,
            "Evicted": evicted or "—",
            "Frames": " · ".join(p if p is not None else "—" for p in frames),
        }
        for frame_i, value in enumerate(frames, start=1):
            row[f"Frame {frame_i}"] = value if value is not None else "—"
        rows.append(row)

    count = len(reference_string)
    return {
        "algorithm": algorithm,
        "steps": rows,
        "hits": hits,
        "faults": faults,
        "hit_rate": (hits / count * 100) if count else 0.0,
        "fault_rate": (faults / count * 100) if count else 0.0,
        "reference_count": count,
        "final_frames": frames,
    }


def simulate_allocation(block_sizes: list[int], process_sizes: list[int], strategy: str) -> dict[str, Any]:
    """Simulate variable-sized First Fit, Best Fit, or Worst Fit allocation."""
    remaining = block_sizes.copy()
    assigned: list[list[dict[str, int]]] = [[] for _ in block_sizes]
    allocations: list[dict[str, Any]] = []

    for process_index, size in enumerate(process_sizes, start=1):
        eligible = [i for i, free in enumerate(remaining) if free >= size]
        chosen: int | None = None
        if eligible:
            if strategy == "First Fit":
                chosen = eligible[0]
            elif strategy == "Best Fit":
                chosen = min(eligible, key=lambda i: remaining[i])
            elif strategy == "Worst Fit":
                chosen = max(eligible, key=lambda i: remaining[i])
            else:
                raise ValueError(f"Unknown allocation strategy: {strategy}")

        if chosen is None:
            allocations.append({"Process": f"P{process_index}", "Requested": size, "Block": "Not allocated", "Status": "FAILED", "Internal remainder": "—"})
        else:
            before = remaining[chosen]
            remaining[chosen] -= size
            assigned[chosen].append({"process": process_index, "size": size})
            allocations.append({"Process": f"P{process_index}", "Requested": size, "Block": f"B{chosen + 1}", "Status": "ALLOCATED", "Internal remainder": remaining[chosen]})

    block_rows = []
    for i, total in enumerate(block_sizes):
        used = total - remaining[i]
        names = ", ".join(f"P{x['process']} ({x['size']})" for x in assigned[i]) or "Empty"
        block_rows.append({"Block": f"B{i + 1}", "Capacity": total, "Used": used, "Free": remaining[i], "Processes": names})

    allocated = sum(1 for item in allocations if item["Status"] == "ALLOCATED")
    return {
        "allocations": allocations,
        "blocks": block_rows,
        "allocated_count": allocated,
        "failed_count": len(process_sizes) - allocated,
        "total_memory": sum(block_sizes),
        "used_memory": sum(block_sizes) - sum(remaining),
        "free_memory": sum(remaining),
    }


def compression_report(text: str) -> dict[str, Any]:
    """Use Python's zlib to measure actual compression; summarize repeated words."""
    original = text.encode("utf-8")
    compressed = zlib.compress(original, level=9)
    words = re.findall(r"[A-Za-z0-9_'-]+", text.lower())
    counts = Counter(words)
    repeated = [{"Token": word, "Occurrences": count} for word, count in counts.most_common(12) if count > 1]
    original_size, compressed_size = len(original), len(compressed)
    saved = original_size - compressed_size
    return {
        "original_bytes": original_size,
        "compressed_bytes": compressed_size,
        "saved_bytes": saved,
        "saved_percent": (saved / original_size * 100) if original_size else 0,
        "ratio": (original_size / compressed_size) if compressed_size else 0,
        "compressed_preview": compressed[:64].hex(" "),
        "round_trip_ok": zlib.decompress(compressed) == original,
        "repeated_tokens": repeated,
        "word_count": len(words),
        "unique_words": len(counts),
    }


def predict_next_page(sequence: list[str], context_size: int = 2) -> dict[str, Any]:
    """Predict the next token using context-frequency transitions with fallback."""
    if not sequence:
        return {"predictions": [], "context": [], "method": "No sequence supplied", "training_examples": 0}
    context_size = max(1, min(context_size, 3))
    transitions: dict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
    for i in range(context_size, len(sequence)):
        context = tuple(sequence[i - context_size:i])
        transitions[context][sequence[i]] += 1
    context = tuple(sequence[-context_size:]) if len(sequence) >= context_size else tuple(sequence)

    if context in transitions and transitions[context]:
        distribution = transitions[context]
        method = f"Matched last {len(context)} page(s)"
    else:
        fallback: dict[str, Counter[str]] = defaultdict(Counter)
        for i in range(1, len(sequence)):
            fallback[(sequence[i - 1],)][sequence[i]] += 1
        short_context = (sequence[-1],)
        if short_context in fallback and fallback[short_context]:
            distribution = fallback[short_context]
            context = short_context
            method = "Fallback: last-page transition"
        else:
            distribution = Counter(sequence)
            method = "Fallback: overall page frequency"

    total = sum(distribution.values()) or 1
    predictions = [{"Next page": page, "Count": count, "Probability": round(count / total * 100, 1)} for page, count in distribution.most_common()]
    return {"predictions": predictions, "context": list(context), "method": method, "training_examples": sum(sum(c.values()) for c in transitions.values())}


