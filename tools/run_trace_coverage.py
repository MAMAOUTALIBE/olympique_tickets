#!/usr/bin/env python3
"""
Exécuter la suite de tests Django sous le module trace de la bibliothèque 
standard et produire un rapport de couverture simple centré sur les applications du projet.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from trace import Trace
from typing import Dict, Iterable, List, Sequence, Set

import django
from django.core.management import call_command

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Only measure our local apps.
APP_DIRECTORIES = [
    BASE_DIR / "tickets_bah",
    BASE_DIR / "appAdmin",
]

# Exclude generated / irrelevant python files from the report.
EXCLUDED_DIR_NAMES = {"migrations", "tests", "__pycache__"}


@dataclass
class CoverageStats:
    path: Path
    statements: int
    executed: int
    missing_lines: List[int]

    @property
    def coverage(self) -> float:
        if not self.statements:
            return 100.0
        return (self.executed / self.statements) * 100.0


def iter_python_files() -> Iterable[Path]:
    for root in APP_DIRECTORIES:
        for path in root.rglob("*.py"):
            if any(part in EXCLUDED_DIR_NAMES for part in path.parts):
                continue
            yield path


def collect_executed_lines(results) -> Dict[Path, Set[int]]:
    executed: Dict[Path, Set[int]] = defaultdict(set)
    for (filename, lineno), count in results.counts.items():
        if count == 0:
            continue
        executed[Path(filename).resolve()].add(lineno)
    return executed


def analyse_file(path: Path, executed_lines: Set[int]) -> CoverageStats:
    statements = 0
    executed = 0
    missing: List[int] = []

    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        statements += 1
        if lineno in executed_lines:
            executed += 1
        else:
            missing.append(lineno)

    return CoverageStats(path=path, statements=statements, executed=executed, missing_lines=missing)


def run_tests(test_labels: Sequence[str], verbosity: int) -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "olympique_tickets_bah.settings")
    os.environ.setdefault("USE_SQLITE_FOR_TESTS", "1")
    django.setup()
    call_command("test", *test_labels, verbosity=verbosity)


def format_stats(stats: Sequence[CoverageStats]) -> str:
    header = f"{'Module':60} {'Stmts':>6} {'Exec':>6} {'Miss':>6} {'Cover':>7}"
    lines = [header, "-" * len(header)]
    for stat in stats:
        rel = stat.path.relative_to(BASE_DIR).as_posix()
        lines.append(
            f"{rel:60} {stat.statements:6d} {stat.executed:6d} {len(stat.missing_lines):6d} {stat.coverage:6.1f}%"
        )
    total_statements = sum(s.statements for s in stats)
    total_executed = sum(s.executed for s in stats)
    total_missing = total_statements - total_executed
    overall = 100.0 * total_executed / total_statements if total_statements else 100.0
    lines.append("-" * len(header))
    lines.append(
        f"{'TOTAL':60} {total_statements:6d} {total_executed:6d} {total_missing:6d} {overall:6.1f}%"
    )
    return "\n".join(lines)


def write_json(stats: Sequence[CoverageStats], destination: Path) -> None:
    data = {
        "base_dir": str(BASE_DIR),
        "files": [
            {
                "path": stat.path.relative_to(BASE_DIR).as_posix(),
                "statements": stat.statements,
                "executed": stat.executed,
                "missing": stat.missing_lines,
                "coverage": round(stat.coverage, 2),
            }
            for stat in stats
        ],
    }
    destination.write_text(
        json_dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def json_dumps(obj, **kwargs):
    """Lazy import for the builtin json module to avoid tracing it."""
    import json

    return json.dumps(obj, **kwargs)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run Django tests and report coverage using the stdlib trace module."
    )
    parser.add_argument(
        "labels",
        nargs="*",
        help="Optional test labels to pass to django's test command.",
    )
    parser.add_argument(
        "--verbosity",
        type=int,
        default=1,
        help="Verbosity level passed to the Django test command (default: 1).",
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=BASE_DIR / "trace_coverage.json",
        help="Optional path where a JSON summary should be written.",
    )

    args = parser.parse_args(argv)

    ignoredirs = {
        os.path.realpath(sys.prefix),
        os.path.realpath(sys.exec_prefix),
        os.path.realpath(BASE_DIR / ".venv"),
    }

    tracer = Trace(count=1, trace=0, ignoredirs=list(ignoredirs))
    tracer.runfunc(run_tests, args.labels, args.verbosity)
    results = tracer.results()
    executed = collect_executed_lines(results)
    stats: List[CoverageStats] = []
    for path in sorted(iter_python_files()):
        resolved = path.resolve()
        executed_lines = executed.get(resolved, set())
        stats.append(analyse_file(resolved, executed_lines))

    report = format_stats(stats)
    print(report)

    if args.json:
        write_json(stats, args.json)
        print(f"\nJSON report written to {args.json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
