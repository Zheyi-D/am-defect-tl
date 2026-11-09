# Author: foundation team | Task: contract tests (split leakage / metrics schema) | PR: #<number>
# Status: original implementation. Standard library only, runs in CI with zero dependencies.
"""Contract tests: keep all 8 team members on the same agreed conventions. Auto-skip when data is absent.

Run (either):
    python -m unittest discover -s tests -v
    pytest tests/test_contracts.py -v
"""

from __future__ import annotations

import csv
import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPLITS_DIR = ROOT / "splits"
RUNS_DIR = ROOT / "results" / "runs"

SPLIT_COLS = ["path", "label", "split", "source_id"]
LABELS = {"defect", "nondefect"}
SPLIT_NAMES = {"train", "val", "test"}
EXPECTED_TOTAL = {"D1": 271, "D2": 3017}  # see docs/DATA.md §1
RATIO = {"train": 0.7, "val": 0.1, "test": 0.2}
TOL = 0.06

METRIC_NAMES = [
    "accuracy", "precision", "recall", "f1", "mcc", "kappa",
    "auc", "map", "sensitivity", "specificity",
]
METRICS_TOP_KEYS = ["run_id", "model", "dataset", "optimizer", "seed", "metrics", "confusion"]


def _read_rows(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader.fieldnames or []), list(reader)


class TestSplits(unittest.TestCase):
    def _files(self) -> list[Path]:
        files = sorted(SPLITS_DIR.glob("*.csv"))
        if not files:
            self.skipTest("splits/*.csv not generated yet (foundation team task, due 10/29)")
        return files

    def test_schema(self):
        for path in self._files():
            header, rows = _read_rows(path)
            with self.subTest(file=path.name):
                self.assertEqual(header, SPLIT_COLS, f"{path.name} header must be exactly {SPLIT_COLS}")
                self.assertTrue(rows, f"{path.name} must not be empty")
                for r in rows:
                    self.assertIn(r["label"], LABELS, f"invalid label: {r['label']}")
                    self.assertIn(r["split"], SPLIT_NAMES, f"invalid split: {r['split']}")

    def test_all_three_splits_present(self):
        for path in self._files():
            _, rows = _read_rows(path)
            with self.subTest(file=path.name):
                self.assertEqual({r["split"] for r in rows}, SPLIT_NAMES)

    def test_ratio(self):
        for path in self._files():
            _, rows = _read_rows(path)
            with self.subTest(file=path.name):
                counts = Counter(r["split"] for r in rows)
                total = len(rows)
                for split, expected in RATIO.items():
                    actual = counts[split] / total
                    self.assertLess(abs(actual - expected), TOL,
                                    f"{path.name}: {split} fraction {actual:.2f} deviates from {expected}")

    def test_paths_disjoint(self):
        for path in self._files():
            _, rows = _read_rows(path)
            with self.subTest(file=path.name):
                by_split = {s: {r["path"] for r in rows if r["split"] == s} for s in SPLIT_NAMES}
                self.assertFalse(by_split["train"] & by_split["test"], "train and test overlap")
                self.assertFalse(by_split["train"] & by_split["val"], "train and val overlap")
                self.assertFalse(by_split["val"] & by_split["test"], "val and test overlap")

    def test_group_no_leak(self):
        """Core check: augmented copies sharing a source_id must not cross splits."""
        for path in self._files():
            if "group" not in path.stem:
                continue  # source_id is only required for grouped splits
            _, rows = _read_rows(path)
            with self.subTest(file=path.name):
                where = {}
                for r in rows:
                    sid = r["source_id"]
                    self.assertTrue(sid, f"{path.name}: source_id must not be empty")
                    where.setdefault(sid, set()).add(r["split"])
                leaked = {sid: s for sid, s in where.items() if len(s) > 1}
                self.assertFalse(leaked, f"source_ids crossing splits (data leakage): {list(leaked)[:5]}")

    def test_expected_total(self):
        for path in self._files():
            dim = path.stem
            if dim not in EXPECTED_TOTAL:
                continue
            _, rows = _read_rows(path)
            with self.subTest(file=path.name):
                self.assertEqual(len(rows), EXPECTED_TOTAL[dim],
                                 f"{path.name} should have {EXPECTED_TOTAL[dim]} rows (see docs/DATA.md §1)")


class TestRunArtifacts(unittest.TestCase):
    def _run_files(self) -> list[Path]:
        files = sorted(RUNS_DIR.glob("*/metrics.json"))
        if not files:
            self.skipTest("results/runs/*/metrics.json not produced yet")
        return files

    def test_metrics_schema(self):
        for path in self._run_files():
            data = json.loads(path.read_text(encoding="utf-8"))
            with self.subTest(run=path.parent.name):
                for key in METRICS_TOP_KEYS:
                    self.assertIn(key, data, f"missing top-level field {key}")
                self.assertEqual(data["run_id"], path.parent.name, "run_id must match the directory name")
                for split in SPLIT_NAMES:
                    self.assertIn(split, data["metrics"], f"missing {split} metrics")
                    for name in METRIC_NAMES:
                        value = data["metrics"][split].get(name)
                        self.assertIsNotNone(value, f"{split}.{name} is missing")
                        # Allow a 1e-6 float tolerance (historical results contain 1.0000000000000002)
                        self.assertGreaterEqual(value, -1e-6, f"{split}.{name} out of range")
                        self.assertLessEqual(value, 1.0 + 1e-6, f"{split}.{name} out of range")

    def test_confusion_shape(self):
        for path in self._run_files():
            data = json.loads(path.read_text(encoding="utf-8"))
            with self.subTest(run=path.parent.name):
                for split in SPLIT_NAMES:
                    cm = data["confusion"][split]
                    self.assertEqual(len(cm), 2, f"{split} confusion matrix should have 2 rows")
                    self.assertTrue(all(len(row) == 2 for row in cm), f"{split} rows should have 2 columns")
                    self.assertEqual(sum(sum(row) for row in cm), data.get(f"n_{split}", sum(sum(row) for row in cm)))


class TestCoverage(unittest.TestCase):
    def test_run_coverage_progress(self):
        """Report progress only; does not block PRs (the 66 runs finish over three weeks)."""
        n = len(list(RUNS_DIR.glob("*/metrics.json")))
        if n == 0:
            self.skipTest("no runs yet")
        print(f"\n[progress] completed runs: {n}/66")
        self.assertLessEqual(n, 66 * 2, "suspiciously many runs; check for duplicate run_ids")


if __name__ == "__main__":
    unittest.main(verbosity=2)
