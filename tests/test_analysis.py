"""Cross-check inference and protect player-population integrity."""
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from analyze import compare, load_players


class AnalysisTests(unittest.TestCase):
    def fixture(self):
        return pd.DataFrame({
            "version": ["gate_30"] * 100 + ["gate_40"] * 100,
            "retention_7": [True] * 50 + [False] * 50 + [True] * 30 + [False] * 70,
        })

    def test_z_test_agrees_with_independent_contingency_test(self):
        result, _ = compare(self.fixture(), "retention_7", np.random.default_rng(42))
        expected = stats.chi2_contingency([[50, 50], [30, 70]], correction=False).pvalue
        self.assertAlmostEqual(result["p_value"], expected, places=12)
        self.assertAlmostEqual(result["difference_pp"], -20)
        self.assertLess(result["ci_95_pp"][1], 0)

    def test_reversing_groups_reverses_effect_and_preserves_p_value(self):
        frame = self.fixture()
        first, _ = compare(frame, "retention_7", np.random.default_rng(42))
        frame["version"] = frame.version.map({"gate_30": "gate_40", "gate_40": "gate_30"})
        second, _ = compare(frame, "retention_7", np.random.default_rng(42))
        self.assertAlmostEqual(first["p_value"], second["p_value"])
        self.assertAlmostEqual(first["difference_pp"], -second["difference_pp"])

    def test_seed_reproduces_bootstrap(self):
        first, samples = compare(self.fixture(), "retention_7", np.random.default_rng(42))
        second, repeated = compare(self.fixture(), "retention_7", np.random.default_rng(42))
        self.assertEqual(first, second)
        np.testing.assert_array_equal(samples, repeated)

    def write_csv(self, rows):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "players.csv"
        path.write_text("userid,version,sum_gamerounds,retention_1,retention_7\n" + rows, encoding="utf-8")
        return path

    def test_loader_preserves_zero_rounds_and_extreme_observation(self):
        path = self.write_csv("1,gate_30,0,False,False\n2,gate_40,49854,True,True\n")
        frame = load_players(path)
        self.assertEqual(len(frame), 2)
        self.assertEqual(frame.sum_gamerounds.tolist(), [0, 49854])

    def test_loader_rejects_duplicate_bad_group_bad_flag_and_negative_rounds(self):
        cases = ["1,gate_40,1,True,True", "2,gate_50,1,True,True",
                 "2,gate_40,1,yes,True", "2,gate_40,-1,True,True",
                 "2,gate_40,,True,True"]
        for row in cases:
            with self.subTest(row=row):
                path = self.write_csv("1,gate_30,0,False,False\n" + row + "\n")
                with self.assertRaises(ValueError):
                    load_players(path)

    def test_sparse_binary_data_is_rejected(self):
        frame = self.fixture()
        frame["retention_7"] = True
        with self.assertRaisesRegex(ValueError, "five retained"):
            compare(frame, "retention_7", np.random.default_rng(42))


if __name__ == "__main__":
    unittest.main()
