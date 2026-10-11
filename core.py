"""Core page-replacement algorithms for Page Replacement Lab.

This module contains no UI code, so the algorithms can be tested independently.
"""
from __future__ import annotations

import math
import re
from typing import Any

ALGORITHMS = ("FIFO", "LRU", "Optimal")


def parse_reference_string(raw: str) -> list[str]:
    """Parse a page-reference string separated by spaces, commas, or newlines."""
    if not isinstance(raw, str):
        raise TypeError("Reference string must be text.")
    pages = [token for token in re.split(r"[\s,;]+", raw.strip()) if token]
    if not pages:
        raise ValueError("Enter at least one page reference, for example: 7 0 1 2 0 3.")
    if len(pages) > 250:
        raise ValueError("Please use 250 page references or fewer for this classroom simulator.")
    return pages


def simulate_page_replacement(
    reference_string: list[str], frame_count: int, algorithm: str
) -> dict[str, Any]:
    """Simulate FIFO, LRU, or Optimal page replacement.

    Each trace row shows the frame contents *after* the current request is handled.
    """
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Unknown algorithm {algorithm!r}. Choose from {', '.join(ALGORITHMS)}.")
    if not isinstance(frame_count, int) or frame_count < 1 or frame_count > 12:
        raise ValueError("Frame count must be an integer between 1 and 12.")
    if not reference_string:
        raise ValueError("Reference string cannot be empty.")

    frames: list[str | None] = [None] * frame_count
    loaded_at: dict[str, int] = {}
    last_used: dict[str, int] = {}
    hits = 0
    faults = 0
    trace: list[dict[str, Any]] = []

    for index, page in enumerate(reference_string):
        evicted: str | None = None
        if page in frames:
            result = "HIT"
            hits += 1
        else:
            result = "FAULT"
            faults += 1
            empty_slot = next((slot for slot, value in enumerate(frames) if value is None), None)
            if empty_slot is not None:
                chosen_slot = empty_slot
            else:
                if algorithm == "FIFO":
                    chosen_slot = min(
                        range(frame_count), key=lambda slot: loaded_at[frames[slot]]  # type: ignore[index]
                    )
                elif algorithm == "LRU":
                    chosen_slot = min(
                        range(frame_count), key=lambda slot: last_used[frames[slot]]  # type: ignore[index]
                    )
                else:  # Optimal: farthest next use; never-used-again pages are best victims.
                    future = reference_string[index + 1 :]
                    next_use: dict[str, float] = {}
                    for resident in frames:
                        assert resident is not None
                        try:
                            next_use[resident] = future.index(resident)
                        except ValueError:
                            next_use[resident] = math.inf
                    chosen_slot = max(
                        range(frame_count), key=lambda slot: next_use[frames[slot]]  # type: ignore[index]
                    )

            evicted = frames[chosen_slot]
            frames[chosen_slot] = page
            loaded_at[page] = index

        last_used[page] = index
        row: dict[str, Any] = {
            "Step": index + 1,
            "Requested page": page,
            "Result": result,
            "Evicted page": evicted if evicted is not None else "—",
            "Frames after request": " | ".join(value if value is not None else "—" for value in frames),
            "frame_values": frames.copy(),
        }
        for slot, value in enumerate(frames, start=1):
            row[f"Frame {slot}"] = value if value is not None else "—"
        trace.append(row)

    total = len(reference_string)
    return {
        "algorithm": algorithm,
        "frame_count": frame_count,
        "reference_count": total,
        "hits": hits,
        "faults": faults,
        "hit_rate": hits / total * 100,
        "fault_rate": faults / total * 100,
        "final_frames": frames,
        "steps": trace,
    }


def compare_algorithms(reference_string: list[str], frame_count: int) -> list[dict[str, Any]]:
    """Return comparable summary metrics for all supported algorithms."""
    results = [simulate_page_replacement(reference_string, frame_count, name) for name in ALGORITHMS]
    best_faults = min(item["faults"] for item in results)
    for item in results:
        item["faults_saved_vs_fifo"] = results[0]["faults"] - item["faults"]
        item["best_fault_count"] = item["faults"] == best_faults
    return results
