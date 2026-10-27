"""The ten verification cases in Project Model.md. Run: python -m unittest -v."""

import unittest
import contextlib
import csv
import io
from math import sqrt
from pathlib import Path
import tempfile
from unittest.mock import patch

import simulation as sim
import analysis


def student(**changes):
    values = dict(allowance=100, food=0, transport=0, optional=0, supplies=0, event_cost=0)
    values.update(changes)
    count = values.pop("event_count", 0)
    return {**{name: sim.cents(value) for name, value in values.items()}, "event_count": count}


def week(profile, scenario="Normal spending"):
    return sim.simulate_week(profile, scenario, [(0.5, 0.99)] * 4)


class VerificationCases(unittest.TestCase):
    def test_01_zero_expenses(self):
        result = week(student())
        self.assertEqual((result["day"], result["cash"]), (0, 10000))

    def test_02_exact_coverage(self):
        result = week(student(transport=25))
        self.assertEqual((result["day"], result["cash"]), (0, 0))

    def test_03_thursday_shortfall(self):
        result = week(student(allowance=99, transport=25))
        self.assertEqual((result["day"], result["shortfall"], result["cash"]), (4, 100, 0))

    def test_04_monday_failure_terminates(self):
        result = week(student(allowance=20, transport=25, optional=5))
        self.assertEqual((result["day"], result["shortfall"], result["cash"]), (1, 500, 0))
        self.assertEqual(result["desired"], 500)  # only Monday's desire, no later days

    def test_05_optional_purchase_is_limited(self):
        self.assertEqual(sim.pay_day(10000, 0, 1000, 20000), (0, 0, 9000, 0))

    def test_06_essentials_can_use_reserve(self):
        self.assertEqual(sim.pay_day(10000, 2000, 8500, 1000), (1500, 1500, 0, 0))

    def test_07_optional_cannot_use_reserve(self):
        self.assertEqual(sim.pay_day(10000, 2000, 3000, 6000), (2000, 2000, 5000, 0))

    def test_08_lower_allowance_and_centavo_allocation(self):
        profile = student(transport=20)
        normal, lower = week(profile), week(profile, "Lower allowance")
        self.assertEqual((normal["day"], lower["day"]), (0, 0))
        self.assertEqual((normal["cash"], lower["cash"]), (2000, 0))
        self.assertEqual(week(student(allowance=1.03, supplies=1.03))["cash"], 0)
        self.assertEqual(sim.percent(5, 50), 3)  # half-centavo rounds up
        for invalid in (-1, "NaN", "Infinity", ".001"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                sim.cents(invalid)

    def test_09_interacting_strategies(self):
        profile = student(food=15, optional=20)
        normal = week(profile)
        self.assertEqual((normal["day"], normal["shortfall"]), (4, 1500))
        for scenario in ("Controlled spending", "Emergency reserve"):
            result = week(profile, scenario)
            self.assertEqual((result["day"], result["cash"]), (0, 0))
        trace = []
        traced = sim.simulate_week(profile, "Emergency reserve", [(0.5, 0.99)] * 4, trace)
        self.assertEqual(traced, week(profile, "Emergency reserve"))
        self.assertEqual([row[4] for row in trace], [20, 20, 0, 0])
        self.assertEqual([row[5] for row in trace], [20, 20, 15, 0])
        self.assertEqual([row[6] for row in trace], [65, 30, 15, 0])
        balance, reserve = 10000, 2000
        for expected_reserve in (2000, 2000, 1500, 0):
            balance, reserve, _, _ = sim.pay_day(balance, reserve, 1500, 2000)
            self.assertEqual(reserve, expected_reserve)  # no reserve replenishment

    def test_10_random_boundaries(self):
        profile = student(allowance=500, event_count=1, event_cost=100)
        draws = [(0.5, .0624), (0.5, .0625), (0.5, .99), (0.5, .99)]
        self.assertEqual(sim.simulate_week(profile, "Normal spending", draws)["cash"], 40000)
        for uniform, expected in ((0, 80), (.249999, 80), (.25, 100), (.749999, 100), (.75, 120), (.999999, 120)):
            self.assertEqual(sim.spending_multiplier(uniform), expected)
        zero_events = student(allowance=100, event_cost=100)
        self.assertEqual(sim.simulate_week(zero_events, "Normal spending", [(0.5, 0)] * 4)["cash"], 10000)


class SupportingChecks(unittest.TestCase):
    def test_model_input_rejections(self):
        for field, value in (("food", -1), ("event_count", -1), ("event_count", 17),
                             ("event_count", .5), ("event_count", True)):
            profile = student()
            profile[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                sim.validate_student(profile)
        with self.assertRaises(ValueError):
            sim.validate_student(student(event_count=1, event_cost=0))
        sim.validate_student(student(event_count=16, event_cost=100))
        with self.assertRaises(ValueError):
            sim.cents("not a number")

    def test_fixed_profile_interval_against_hand_calculation(self):
        # Profile 1: [0,1,0,1], sample variance=1/3; profile 2: all zeros.
        mean, low, high = analysis.mean_interval([(4, 2, 2), (4, 0, 0)])
        error = 1.959963984540054 * sqrt((1 / 3) / 4) / 2
        self.assertAlmostEqual(mean, .25)
        self.assertAlmostEqual(low, .25 - error)
        self.assertAlmostEqual(high, .25 + error)
        with self.assertRaises(ValueError):
            analysis.mean_interval([(1, 0, 0)])

    def test_paired_comparison_sign_units_and_covariance(self):
        paired = analysis.empty_pair()
        for outcome in (dict(day=0, cash=10000), dict(day=4, cash=0)):
            analysis.record_pair(paired, outcome, outcome)
        row = analysis.comparison_row("TEST", "Identical policy", [paired])
        for key, value in row.items():
            if "difference" in key:
                self.assertEqual(value, 0)  # identical pairs have no difference variance
        better = analysis.empty_pair()
        for _ in range(2):
            analysis.record_pair(better, dict(day=4, cash=0), dict(day=0, cash=1000))
        row = analysis.comparison_row("TEST", "Better policy", [better])
        self.assertEqual(row["shortage_difference_pp"], -100)
        self.assertEqual(row["cash_difference_php"], 10)

    def test_fact_export_and_source_cells(self):
        students = sim.load_students()
        with tempfile.TemporaryDirectory() as folder:
            count = analysis.export_facts(students, sim.INPUT_COLUMNS, Path(folder))
            with (Path(folder) / "input_facts.csv").open(encoding="utf-8-sig", newline="") as file:
                facts = list(csv.DictReader(file))
        self.assertEqual(count, len(students) * 7)
        self.assertGreater(count, 100)
        self.assertEqual(len({row["fact_id"] for row in facts}), count)
        self.assertEqual(facts[0]["source"], "Modified Sample Data!D2")
        self.assertEqual(facts[5]["source"], "Modified Sample Data!K2")
        # Compare against actual cells independently of the parsed profile dictionaries.
        workbook = sim.load_workbook(sim.WORKBOOK, read_only=True, data_only=True)
        try:
            sheet = workbook["Modified Sample Data"]
            for fact in (facts[0], facts[len(facts) // 2], facts[-1]):
                cell = fact["source"].split("!")[1]
                self.assertEqual(float(fact["value"]), float(sheet[cell].value))
        finally:
            workbook.close()

    def test_whole_program_outputs_reconciliation_and_reproducibility(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with patch.object(sim, "FOLDER", root), patch.object(sim, "TRIALS", 20), contextlib.redirect_stdout(io.StringIO()):
                sim.main()
                output = root / "results"
                expected = ("results.csv", "comparisons.csv", "input_facts.csv", "run_settings.txt",
                            "comparison.png", "remaining_cash.png", "first_shortage_day.png", "worked_example.png")
                self.assertTrue(all((output / name).is_file() for name in expected))
                for name in expected[4:]:
                    self.assertEqual((output / name).read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
                saved_results = (output / "results.csv").read_bytes()
                saved_pairs = (output / "comparisons.csv").read_bytes()
                with (output / "results.csv").open(encoding="utf-8-sig", newline="") as file:
                    results = list(csv.DictReader(file))
                self.assertEqual(len(results), 84)
                for row in results:
                    day_total = float(row["no_shortage_probability"]) + sum(float(row[f"first_shortage_{d.lower()}_probability"]) for d in sim.DAYS)
                    self.assertAlmostEqual(day_total, 1)
                    self.assertLessEqual(float(row["shortage_ci95_low"]), float(row["shortage_probability"]) + 1e-12)
                    self.assertGreaterEqual(float(row["shortage_ci95_high"]), float(row["shortage_probability"]) - 1e-12)
                with patch.object(sim, "save_visuals"):
                    sim.main()  # same seed/settings -> byte-identical numerical outputs
                self.assertEqual(saved_results, (output / "results.csv").read_bytes())
                self.assertEqual(saved_pairs, (output / "comparisons.csv").read_bytes())


if __name__ == "__main__":
    unittest.main()
