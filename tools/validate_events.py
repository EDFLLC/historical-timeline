#!/usr/bin/env python3
"""Validate data/events.json against DATA-CONVENTIONS.md.

Usage:
    python3 tools/validate_events.py            # check only
    python3 tools/validate_events.py --sort     # also rewrite sorted by date
    python3 tools/validate_events.py --strict-tags   # unknown tags become errors

Exit code 0 = no errors (warnings allowed). Exit code 1 = errors found.
"""
import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVENTS = ROOT / "data" / "events.json"
TAGS = ROOT / "tools" / "tags.txt"

CATEGORIES = {"history", "politics", "religion", "science", "tech",
              "arts", "pop", "sport", "exploration"}
REQUIRED = {"date", "category", "importance", "summary", "source"}
ALLOWED = REQUIRED | {"tags"}
MAX_SUMMARY = 40
DATE_RE = re.compile(r"^(\d{4})\.(\d{2})\.(\d{2})$")
TAG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MIN_DATE = datetime.date(1900, 1, 1)
MAX_DATE = datetime.date(2026, 12, 31)


def load_vocab():
    if not TAGS.exists():
        return set()
    out = set()
    for line in TAGS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.add(line)
    return out


def main():
    args = set(sys.argv[1:])
    do_sort = "--sort" in args
    strict_tags = "--strict-tags" in args

    try:
        data = json.loads(EVENTS.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: {EVENTS} not found")
        return 1
    except json.JSONDecodeError as e:
        print(f"ERROR: events.json is not valid JSON: {e}")
        return 1
    if not isinstance(data, list):
        print("ERROR: events.json must contain a list at the top level")
        return 1

    vocab = load_vocab()
    errors, warnings = [], []
    seen_key = {}
    seen_source_date = {}
    unknown_tags = {}

    def err(i, e, msg):
        errors.append(f"#{i + 1} {e.get('date', '?')} \"{e.get('summary', '?')}\": {msg}")

    def warn(i, e, msg):
        warnings.append(f"#{i + 1} {e.get('date', '?')} \"{e.get('summary', '?')}\": {msg}")

    for i, e in enumerate(data):
        if not isinstance(e, dict):
            errors.append(f"#{i + 1}: entry is not an object")
            continue
        missing = REQUIRED - e.keys()
        if missing:
            err(i, e, f"missing field(s): {', '.join(sorted(missing))}")
            continue
        extra = e.keys() - ALLOWED
        if extra:
            warn(i, e, f"unexpected field(s): {', '.join(sorted(extra))}")

        # date
        m = DATE_RE.match(str(e["date"]))
        if not m:
            err(i, e, "date must be YYYY.MM.DD")
        else:
            try:
                d = datetime.date(int(m[1]), int(m[2]), int(m[3]))
                if not (MIN_DATE <= d <= MAX_DATE):
                    err(i, e, "date outside 1900.01.01 to 2026.12.31")
            except ValueError:
                err(i, e, "not a real calendar date")

        # category
        if e["category"] not in CATEGORIES:
            err(i, e, f"unknown category '{e['category']}'")

        # importance
        imp = e["importance"]
        if isinstance(imp, bool) or not isinstance(imp, int) or not 1 <= imp <= 5:
            err(i, e, "importance must be an integer 1-5")

        # summary
        s = e["summary"]
        if not isinstance(s, str) or not s.strip():
            err(i, e, "summary is empty")
        else:
            if len(s) > MAX_SUMMARY:
                err(i, e, f"summary is {len(s)} chars (max {MAX_SUMMARY})")
            if s != s.strip() or s.endswith("."):
                warn(i, e, "summary has stray whitespace or a trailing period")

        # source
        src = e["source"]
        if not isinstance(src, str) or not src.startswith("https://"):
            err(i, e, "source must be an https URL")
        elif not src.startswith("https://en.wikipedia.org/wiki/"):
            warn(i, e, "source is not an English Wikipedia article")

        # tags
        tags = e.get("tags", [])
        if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
            err(i, e, "tags must be a list of strings")
        else:
            if not tags:
                warn(i, e, "no tags")
            if len(tags) > 4:
                warn(i, e, f"{len(tags)} tags (recommended 1-3)")
            if len(set(tags)) != len(tags):
                err(i, e, "duplicate tags")
            for t in tags:
                if not TAG_RE.match(t):
                    err(i, e, f"tag '{t}' must be lowercase-hyphenated")
                elif vocab and t not in vocab:
                    unknown_tags.setdefault(t, []).append(i + 1)

        # duplicates
        key = (e["date"], e["category"], str(s).lower())
        if key in seen_key:
            err(i, e, f"duplicate of entry #{seen_key[key]}")
        else:
            seen_key[key] = i + 1
        sd = (e["date"], e["category"], src)
        if sd in seen_source_date and seen_source_date[sd] != seen_key.get(key):
            warn(i, e, f"same date, lane and source as entry #{seen_source_date[sd]}; possible duplicate")
        seen_source_date.setdefault(sd, i + 1)

    # unknown tags
    for t, rows in sorted(unknown_tags.items()):
        msg = f"tag '{t}' not in tools/tags.txt (entries {', '.join(map(str, rows[:5]))}{'...' if len(rows) > 5 else ''})"
        (errors if strict_tags else warnings).append(msg)

    # ordering
    keys = [(e.get("date", ""), e.get("category", ""), e.get("summary", "")) for e in data if isinstance(e, dict)]
    is_sorted = keys == sorted(keys)
    if not is_sorted and not do_sort:
        warnings.append("events.json is not sorted by date (run with --sort)")

    if do_sort and not errors:
        data.sort(key=lambda e: (e["date"], e["category"], e["summary"]))
        EVENTS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("Sorted and rewrote data/events.json")

    for w in warnings:
        print("WARN :", w)
    for e in errors:
        print("ERROR:", e)
    print(f"\n{len(data)} events checked: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
