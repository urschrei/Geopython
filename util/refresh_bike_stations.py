"""Fetch the current London cycle-hire station list from the TfL Unified API
and write it to data/nodes_london.csv in the same `id,name,lat,lon` layout
used by the legacy 2014 dataset.

The legacy file shipped with the repo uses old-style Mac CR line endings; we
write standard LF endings here, which pandas' read_csv handles transparently.

Usage:
    uv run util/refresh_bike_stations.py
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import httpx

API_URL = "https://api.tfl.gov.uk/BikePoint"
DEFAULT_OUTPUT = Path(__file__).resolve().parent.parent / "data" / "nodes_london.csv"


def _terminal_name(record: dict) -> str | None:
    """Pull TerminalName out of the additionalProperties bag.

    TfL nests it as a category=Description/key=TerminalName pair rather than
    exposing it at the top level.
    """
    for prop in record.get("additionalProperties", []):
        if prop.get("key") == "TerminalName":
            return prop.get("value")
    return None


def fetch_stations(timeout: float = 30.0) -> list[dict]:
    response = httpx.get(API_URL, timeout=timeout)
    response.raise_for_status()
    return response.json()


def write_csv(stations: list[dict], output: Path) -> int:
    rows = []
    for s in stations:
        sid = s.get("id", "")
        # TfL IDs look like "BikePoints_123"; strip the prefix to match the
        # legacy numeric format. Fall back to TerminalName if missing.
        if sid.startswith("BikePoints_"):
            sid = sid[len("BikePoints_") :]
        else:
            sid = _terminal_name(s) or sid

        rows.append((sid, s["commonName"], s["lat"], s["lon"]))

    rows.sort(key=lambda r: r[1])  # by name, matches legacy ordering

    with output.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerows(rows)
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"output CSV path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="don't keep a .bak copy of the existing file",
    )
    args = parser.parse_args()

    if args.output.exists() and not args.no_backup:
        backup = args.output.with_suffix(args.output.suffix + ".bak")
        backup.write_bytes(args.output.read_bytes())
        print(f"backed up existing file to {backup}", file=sys.stderr)

    print(f"fetching {API_URL} ...", file=sys.stderr)
    stations = fetch_stations()
    count = write_csv(stations, args.output)
    print(f"wrote {count} stations to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
