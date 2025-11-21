#!/usr/bin/env python3
"""
Combine multiple CSV files into a single dataset.

Features:
- Accept explicit file list or a directory + glob pattern
- Handles differing columns (outer union)
- Optional de-duplication by 'post_id' or 'content_hash' (or both)
- Parses common timestamp columns to datetime
- Writes a timestamped output by default

Examples:
  # Combine specific files
  python scripts/combine_csvs.py --files data/raw/a.csv data/raw/b.csv data/raw/c.csv \
      --dedupe post_id content_hash --output data/processed/MASTER_combined.csv

  # Combine all CSVs in a folder
  python scripts/combine_csvs.py --dir data/raw --pattern "*.csv" --dedupe post_id \
      --output data/processed/MASTER_reddit_crisis_data.csv

  # Quick run with defaults (writes timestamped file under data/processed/)
  python scripts/combine_csvs.py --dir data/raw --pattern "*.csv"
"""

from __future__ import annotations

import argparse
from pathlib import Path
from datetime import datetime
from typing import List
import sys

import pandas as pd


def find_files_by_pattern(folder: Path, pattern: str) -> List[Path]:
    return sorted([p for p in folder.glob(pattern) if p.is_file()])


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Combine multiple CSV files")
    p.add_argument("--files", nargs="*", help="Explicit CSV file paths to combine")
    p.add_argument("--dir", type=str, help="Directory containing CSV files", default=None)
    p.add_argument("--pattern", type=str, help="Glob pattern (e.g., '*.csv')", default=None)
    p.add_argument("--dedupe", nargs="*", choices=["post_id", "content_hash"],
                   help="Columns to de-duplicate on", default=[])
    p.add_argument("--output", type=str, help="Output CSV path")
    p.add_argument("--encoding", type=str, default="utf-8", help="CSV encoding")
    p.add_argument("--limit", type=int, default=None, help="Limit rows (debugging)")
    return p.parse_args()


def read_csv_safely(path: Path, encoding: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path, encoding=encoding)
    except UnicodeDecodeError:
        # Fallbacks for odd encodings
        for enc in ("utf-8-sig", "latin-1"):
            try:
                df = pd.read_csv(path, encoding=enc)
                break
            except Exception:
                continue
        else:
            raise
    df["__source_file"] = str(path)
    return df


def normalize_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    for col in ("created_utc", "timestamp", "created_at"):
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
            except Exception:
                pass
    return df


def main() -> int:
    args = parse_args()

    files: List[Path] = []
    if args.files:
        files.extend([Path(f) for f in args.files])
    if args.dir and args.pattern:
        files.extend(find_files_by_pattern(Path(args.dir), args.pattern))

    # Validate
    files = [f for f in files if f.exists()]
    if not files:
        print("No input files found. Use --files or --dir + --pattern.")
        return 1

    print(f"Combining {len(files)} files...")
    for f in files:
        print(f" - {f}")

    # Read and concat (outer join on columns)
    frames = [read_csv_safely(f, args.encoding) for f in files]
    combined = pd.concat(frames, ignore_index=True, sort=False)

    if args.limit:
        combined = combined.head(args.limit)

    # Normalize timestamps
    combined = normalize_timestamps(combined)

    # De-duplication
    before = len(combined)
    if args.dedupe:
        subset = [c for c in args.dedupe if c in combined.columns]
        if subset:
            combined = combined.drop_duplicates(subset=subset, keep="first")
    after = len(combined)

    print(f"Rows before: {before:,} | after de-dup: {after:,} | removed: {before - after:,}")

    # Output path
    if args.output:
        out_path = Path(args.output)
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = Path("data/processed") / f"MASTER_reddit_crisis_data_{ts}.csv"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")

    # Brief summary
    def safe_nunique(col: str) -> str:
        return str(combined[col].nunique()) if col in combined.columns else "N/A"

    print("\nSummary:")
    print(f"  Total rows: {len(combined):,}")
    print(f"  Unique post_id: {safe_nunique('post_id')}")
    print(f"  Unique authors: {safe_nunique('author')}")
    print(f"  Unique subreddits: {safe_nunique('subreddit')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
