"""Small statistical helpers and input-fact export; no budgeting decisions here."""

import csv
from math import sqrt


def mean_interval(samples, scale=1):
    """Equal-profile mean and normal 95% Monte Carlo interval.

    Each sample is (count, sum, sum of squares) for ONE fixed profile. For paired
    comparisons it describes alternative-minus-normal outcomes in the same trial.
    Integer sums avoid losing precision before calculating the sample variance.
    """
    if not samples or any(n < 2 for n, total, squares in samples):
        raise ValueError("Confidence intervals need at least two trials per profile.")
    mean = sum(total / n for n, total, squares in samples) / len(samples) * scale
    variance = sum(max(0, n * squares - total * total) / (n * (n - 1)) / n
                   for n, total, squares in samples) / len(samples) ** 2
    error = 1.959963984540054 * sqrt(variance) * scale
    return mean, mean - error, mean + error


def add_intervals(row, profile_totals):
    """Account for fixed student allocation rather than treating profiles as random."""
    risks, cash = [], []
    for totals in profile_totals:
        n = sum(totals["days"])
        failures = sum(totals["days"][1:])
        risks.append((n, failures, failures))  # a 0/1 indicator equals its square
        cash.append((n, totals["cash"], totals["cash_squared"]))
    _, low, high = mean_interval(risks)
    row.update(shortage_ci95_low=max(0, low), shortage_ci95_high=min(1, high))
    _, low, high = mean_interval(cash, scale=.01)  # centavos -> PHP
    row.update(cash_ci95_low_php=max(0, low), cash_ci95_high_php=high)
    return row


def empty_pair():
    return dict(n=0, risk=0, risk_squared=0, cash=0, cash_squared=0)


def record_pair(totals, normal, alternative):
    """Share random inputs AND measure differences within each repetition."""
    risk = int(alternative["day"] > 0) - int(normal["day"] > 0)
    cash = alternative["cash"] - normal["cash"]
    totals["n"] += 1
    totals["risk"] += risk
    totals["risk_squared"] += risk * risk
    totals["cash"] += cash
    totals["cash_squared"] += cash * cash


def comparison_row(student, scenario, profiles):
    row = dict(student=student, scenario=scenario, reference="Normal spending")
    for field, scale, unit in (("risk", 100, "pp"), ("cash", .01, "php")):
        samples = [(p["n"], p[field], p[field + "_squared"]) for p in profiles]
        mean, low, high = mean_interval(samples, scale)
        name = "shortage" if field == "risk" else "cash"
        row.update({f"{name}_difference_{unit}": mean,
                    f"{name}_difference_ci95_low_{unit}": low,
                    f"{name}_difference_ci95_high_{unit}": high})
    return row


def save_csv(path, rows):
    """Keep CSV writing in one place and explain a common Excel lock error."""
    try:
        with path.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    except PermissionError as error:
        raise PermissionError(f"Close {path.name} in Excel, then run the simulation again.") from error


def export_facts(students, columns, output):
    """Export 7 meaningful numerical attributes per profile with cell provenance."""
    units = dict(allowance="PHP/four days", food="PHP/day", transport="PHP/day",
                 optional="PHP/day", supplies="PHP/four days",
                 event_count="events/16 campus days", event_cost="PHP/event")
    rows = []
    for student in students:
        for field, column in columns.items():
            rows.append(dict(fact_id=f"{student['id']}.{field}", student=student["id"],
                attribute=field, value=student[field] if field == "event_count" else student[field] / 100,
                unit=units[field], source=f"Modified Sample Data!{chr(65 + column)}{student['row']}",
                provenance="AI-adjusted survey input; not an unchanged verified response"))
    save_csv(output / "input_facts.csv", rows)
    return len(rows)
