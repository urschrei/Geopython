"""Fetch the Natural Earth 1:110m admin_0_countries shapefile into
data/natural_earth/. The file is small (~210 kB) and public domain;
contour.ipynb uses it for country borders instead of the dead Basemap.

Usage:
    uv run util/download_natural_earth.py [--scale 50m]
"""

from __future__ import annotations

import argparse
import io
import sys
import zipfile
from pathlib import Path

import httpx

DEFAULT_SCALE = "110m"
URL_TEMPLATE = (
    "https://naciscdn.org/naturalearth/{scale}/cultural/"
    "ne_{scale}_admin_0_countries.zip"
)
DEST = Path(__file__).resolve().parent.parent / "data" / "natural_earth"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scale",
        choices=("110m", "50m", "10m"),
        default=DEFAULT_SCALE,
        help="Natural Earth scale (default: 110m; coarser is smaller, finer takes longer)",
    )
    args = parser.parse_args()

    DEST.mkdir(parents=True, exist_ok=True)
    url = URL_TEMPLATE.format(scale=args.scale)
    print(f"fetching {url} ...", file=sys.stderr)
    response = httpx.get(url, timeout=60, follow_redirects=True)
    response.raise_for_status()
    print(f"got {len(response.content):,} bytes", file=sys.stderr)

    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        zf.extractall(DEST)

    written = sorted(DEST.glob(f"ne_{args.scale}_admin_0_countries.*"))
    for path in written:
        print(f"  {path.relative_to(DEST.parent.parent)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
