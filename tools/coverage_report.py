#!/usr/bin/env python3
"""Show how the dataset is distributed: lane x decade counts and importance mix.

Usage:
    python3 tools/coverage_report.py              # all events
    python3 tools/coverage_report.py --min-imp 4  # only importance >= 4
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVENTS = ROOT / "data" / "events.json"
LANES = ["history", "politics", "religion", "science", "tech",
         "arts", "pop", "sport", "exploration"]
DECADES = list(range(1900, 2030, 10))
TARGET = {5: 15, 4: 25, 3: 35, 2: 20, 1: 5}


def main():
    min_imp = 1
    if "--min-imp" in sys.argv:
        min_imp = int(sys.argv[sys.argv.index("--min-imp") + 1])

    data = json.loads(EVENTS.read_text(encoding="utf-8"))
    rows = [e for e in data if e["importance"] >= min_imp]

    grid = {lane: Counter() for lane in LANES}
    for e in rows:
        grid[e["category"]][int(e["date"][:4]) // 10 * 10] += 1

    label = f"importance >= {min_imp}" if min_imp > 1 else "all importance levels"
    print(f"\nLANE x DECADE ({label}); '.' = empty\n")
    head = f"{'':12}" + "".join(f"{str(d)[2:] + 's':>5}" for d in DECADES) + f"{'total':>7}"
    print(head)
    print("-" * len(head))
    col_tot = Counter()
    for lane in LANES:
        cells = []
        for d in DECADES:
            n = grid[lane][d]
            col_tot[d] += n
            cells.append(f"{(str(n) if n else '.'):>5}")
        print(f"{lane:12}" + "".join(cells) + f"{sum(grid[lane].values()):>7}")
    print("-" * len(head))
    print(f"{'total':12}" + "".join(f"{(str(col_tot[d]) if col_tot[d] else '.'):>5}" for d in DECADES)
          + f"{sum(col_tot.values()):>7}")

    total = len(data)
    imp = Counter(e["importance"] for e in data)
    print(f"\nIMPORTANCE MIX ({total} events)\n")
    print(f"{'level':7}{'count':>6}{'share':>8}{'target':>9}")
    for lvl in (5, 4, 3, 2, 1):
        share = 100 * imp[lvl] / total if total else 0
        print(f"{lvl:<7}{imp[lvl]:>6}{share:>7.0f}%{TARGET[lvl]:>8}%")

    print("\nIMPORTANCE-5 PER LANE (what shows on first load)\n")
    for lane in LANES:
        n = sum(1 for e in data if e["category"] == lane and e["importance"] == 5)
        print(f"{lane:12}{n:>3}  {'#' * n}")

    thin = [lane for lane in LANES
            if sum(1 for e in data if e["category"] == lane and e["importance"] == 5) < 3]
    if thin:
        print("\nLanes with fewer than 3 importance-5 events:", ", ".join(thin))
    print()


if __name__ == "__main__":
    main()
