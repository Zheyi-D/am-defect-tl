# Author: jellyfishhamburger | Task: T6 supplementary tests | PR: pending
# Status: original implementation. Standard library only, so CI can run without torch.
"""Contract tests for the T1/T2 artifacts: numbers must match results/, files must exist.

Run:
    python -m unittest discover -s tests -v
    python -m unittest tests.test_analysis_outputs -v
"""

from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def leaderboard() -> list[dict]:
    p = RESULTS / "leaderboard.csv"
    if not p.exists():
        raise unittest.SkipTest("results/leaderboard.csv does not exist")
    with p.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def run_module(*args: str, timeout: int = 120) -> subprocess.CompletedProcess:
    # On Windows, text=True decodes subprocess output with the system code page (GBK),
    # which raises UnicodeDecodeError on non-ASCII output. Force UTF-8 for both sides.
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          env=env, timeout=timeout)


class TestExportedTables(unittest.TestCase):
    """T2: exported tables must match leaderboard.csv cell by cell."""

    def test_tables_match_leaderboard(self):
        proc = run_module("-m", "analysis.export_tables", "--check")
        self.assertEqual(proc.returncode, 0,
                         msg=f"export_tables --check failed\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}")
        self.assertIn("0 mismatches", proc.stdout)

    def test_each_table_has_markdown_and_latex(self):
        proc = run_module("-m", "analysis.export_tables")
        self.assertEqual(proc.returncode, 0, msg=proc.stderr[-2000:])
        tables = sorted((ROOT / "reports" / "tables").glob("*.md"))
        self.assertGreaterEqual(len(tables), 5)
        for md in tables:
            tex = md.with_suffix(".tex")
            self.assertTrue(tex.exists(), f"{tex.name} is missing")
            self.assertIn("\\begin{tabular}", tex.read_text(encoding="utf-8"))


class TestDashboard(unittest.TestCase):
    """Dashboard: embedded data must match leaderboard.csv and the page must have no external links."""

    def test_dashboard_embeds_all_runs(self):
        rows = leaderboard()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "index.html"
            proc = run_module("tools/build_dashboard.py", "--out", str(out))
            self.assertEqual(proc.returncode, 0, msg=proc.stderr[-2000:])
            html = out.read_text(encoding="utf-8")

        self.assertEqual(len(re.findall(r'src="https?://', html)), 0, "page must not load external scripts")
        self.assertEqual(len(re.findall(r'href="https?://', html)), 0, "page must not load external stylesheets")

        m = re.search(r"const DATA = (\{.*?\});\n</script>", html, re.S)
        self.assertIsNotNone(m, "embedded DATA not found")
        data = json.loads(m.group(1))
        self.assertEqual(len(data["runs"]), len(rows))

        by_id = {r["run_id"]: r for r in rows}
        for run in data["runs"]:
            self.assertIn(run["id"], by_id)
            self.assertAlmostEqual(run["acc"]["test"], float(by_id[run["id"]]["accuracy"]), places=9)


class TestFigureIndex(unittest.TestCase):
    """T1: every figure listed in INDEX.md must actually exist."""

    def test_index_files_exist(self):
        index = RESULTS / "figures" / "INDEX.md"
        if not index.exists():
            self.skipTest("results/figures/INDEX.md does not exist (run analysis.make_figures first)")
        text = index.read_text(encoding="utf-8")
        linked = re.findall(r"\((fig_[A-Za-z0-9_\-]+\.png)\)", text)
        self.assertGreaterEqual(len(linked), 5, "INDEX.md should list at least 5 figures")
        for name in linked:
            self.assertTrue((RESULTS / "figures" / name).exists(), f"{name} is listed in INDEX but does not exist")


if __name__ == "__main__":
    unittest.main()
