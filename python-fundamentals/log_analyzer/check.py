import json
from pathlib import Path

from analyze import load_entries, parse_line, summarize, write_report

HERE = Path(__file__).parent
entries = load_entries(HERE / "access.log")
assert len(entries) == 12
assert entries[0] == {
    "timestamp": "2026-11-01T10:00:01", "method": "GET",
    "path": "/api/users", "status": 200, "duration_ms": 12,
}
assert parse_line("2026-11-01T10:00:02 POST /api/users 201 35ms")["duration_ms"] == 35

s = summarize(entries)
assert s["total"] == 12
assert s["status_counts"] == {200: 7, 201: 1, 404: 2, 401: 1, 500: 1}
assert s["method_counts"] == {"GET": 8, "POST": 3, "DELETE": 1}
assert s["top_paths"] == [("/api/users", 4), ("/api/projects", 3)]
assert s["error_count"] == 4
assert s["error_rate"] == 0.33
assert s["avg_duration_ms"] == 49.0
assert s["slowest"]["path"] == "/api/projects/3" and s["slowest"]["duration_ms"] == 250

out = HERE.parent / "scratch" / "report.json"
write_report(s, out)
data = json.loads(out.read_text(encoding="utf-8"))
assert data["status_counts"]["200"] == 7      # JSON keys are always strings
assert data["error_rate"] == 0.33
print("DAY 1 PROJECT: ALL CHECKS PASSED")
