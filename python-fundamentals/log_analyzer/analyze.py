from pathlib import Path
from collections import Counter
import json


def parse_line(line: str) -> dict:
    line = line.split()
    return {
        "timestamp": line[0],
        "method": line[1],
        "path": line[2],
        "status": int(line[3]),
        "duration_ms": int(line[4].removesuffix("ms")),
    }


def load_entries(path: Path) -> list[dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [parse_line(line) for line in lines if line.strip()]


def summarize(entries: list[dict]) -> dict:
    return {
        "total": len(entries),
        "status_counts": Counter(entry["status"] for entry in entries),
        "method_counts": Counter(entry["method"] for entry in entries),
        "top_paths": Counter(entry["path"] for entry in entries).most_common(2),
        "error_count": sum(1 for entry in entries if entry["status"] >= 400),
        "error_rate": round(
            sum(1 for entry in entries if entry["status"] >= 400) / len(entries), 2
        )
        if len(entries) > 0
        else 0,
        "avg_duration_ms": round(
            sum(entry["duration_ms"] for entry in entries) / len(entries), 2
        )
        if len(entries) > 0
        else 0,
        "slowest": max(entries, key=lambda e: e["duration_ms"], default=None),
    }


def write_report(summary: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(summary, indent=2))
