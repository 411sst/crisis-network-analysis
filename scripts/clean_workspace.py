#!/usr/bin/env python3
"""
Safe cleanup utility for Crisis Network Analysis

Usage examples:
  # Dry-run (default): show what would be deleted
  python scripts/clean_workspace.py --all --dry-run

  # Actually delete raw + processed data
  python scripts/clean_workspace.py --raw --processed --yes

  # Delete results but keep reports subfolder
  python scripts/clean_workspace.py --results --keep-reports --yes

  # Clean logs
  python scripts/clean_workspace.py --logs --yes

Targets:
  --raw, --processed, --networks, --results, --logs, --all

Safety:
  - Operates only inside the repository root (looks for README.md and src/)
  - Dry-run by default; require --yes to perform deletions
  - Can keep results/reports via --keep-reports
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
from datetime import datetime


REPO_MARKERS = ["README.md", "src", "dashboard", "config"]


def in_repo_root(root: Path) -> bool:
    return all((root / m).exists() for m in REPO_MARKERS)


def list_contents(p: Path) -> list[Path]:
    if not p.exists():
        return []
    return [child for child in p.iterdir()]


def delete_path(p: Path, dry_run: bool) -> None:
    if not p.exists():
        return
    if dry_run:
        print(f"DRY-RUN: Would delete {p}")
        return
    if p.is_dir():
        shutil.rmtree(p)
    else:
        p.unlink()
    print(f"Deleted {p}")


def clean_folder(folder: Path, *, keep_reports: bool, dry_run: bool) -> None:
    if not folder.exists():
        print(f"Skip (not found): {folder}")
        return

    if keep_reports and folder.name == "results":
        for child in list_contents(folder):
            if child.is_dir() and child.name == "reports":
                print(f"Keeping reports/: {child}")
                continue
            delete_path(child, dry_run)
    else:
        for child in list_contents(folder):
            delete_path(child, dry_run)


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean workspace data safely")
    parser.add_argument("--raw", action="store_true", help="Clean data/raw")
    parser.add_argument("--processed", action="store_true", help="Clean data/processed")
    parser.add_argument("--networks", action="store_true", help="Clean data/networks")
    parser.add_argument("--results", action="store_true", help="Clean results/")
    parser.add_argument("--logs", action="store_true", help="Clean logs/")
    parser.add_argument("--all", action="store_true", help="Clean all targets")
    parser.add_argument("--keep-reports", action="store_true", help="Keep results/reports folder")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted (default)")
    parser.add_argument("--yes", action="store_true", help="Actually perform deletions")

    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    if not in_repo_root(repo_root):
        print("Error: This script must run within the repository root (markers missing)")
        return 2

    # Resolve targets
    targets = []
    if args.all:
        args.raw = args.processed = args.networks = args.results = args.logs = True

    if args.raw:
        targets.append(repo_root / "data" / "raw")
    if args.processed:
        targets.append(repo_root / "data" / "processed")
    if args.networks:
        targets.append(repo_root / "data" / "networks")
    if args.results:
        targets.append(repo_root / "results")
    if args.logs:
        targets.append(repo_root / "logs")

    if not targets:
        print("Nothing to do. Specify one or more targets (e.g., --raw --processed) or --all")
        return 0

    print("Crisis Network Analysis - Cleanup")
    print(f"Root: {repo_root}")
    print(f"When: {datetime.now().isoformat()}")
    print("Mode: DRY-RUN" if (args.dry_run or not args.yes) else "Mode: DELETE")
    if not (args.dry_run or args.yes):
        print("(No --dry-run or --yes specified; defaulting to DRY-RUN)")

    dry_run = args.dry_run or not args.yes

    for folder in targets:
        print(f"\nTarget: {folder}")
        clean_folder(folder, keep_reports=args.keep_reports, dry_run=dry_run)

    if dry_run:
        print("\nDRY-RUN complete. Re-run with --yes to perform deletions.")
    else:
        print("\nCleanup complete.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
