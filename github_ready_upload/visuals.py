"""Presentation figures. Budgeting rules stay in simulation.py."""


def save_visuals(overall, output, student_count, trials, trace):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = [row["scenario"].replace(" ", "\n", 1) for row in overall]
    colors = ["#315B80", "#B4514D", "#32826B", "#B28330"]
    footer = f"{student_count} input profiles | {trials:,} trials each per scenario"

    # 1. How often does a required-expense shortage occur?
    figure, axis = plt.subplots(figsize=(10, 5.6), layout="constrained")
    risk_errors = [[(r["shortage_probability"] - r["shortage_ci95_low"]) * 100 for r in overall],
                   [(r["shortage_ci95_high"] - r["shortage_probability"]) * 100 for r in overall]]
    bars = axis.bar(labels, [row["shortage_probability"] * 100 for row in overall],
                    color=colors, yerr=risk_errors, capsize=5)
    axis.bar_label(bars, fmt="%.2f%%", padding=6)
    axis.set(title="Probability of a shortage over four school days",
             ylabel="Trials with a required-expense shortage (%)", ylim=(0, 100))
    figure.supxlabel(footer + "\nError bars: 95% Monte Carlo intervals (simulation noise only)", fontsize=9)
    figure.savefig(output / "comparison.png", dpi=180)
    plt.close(figure)

    # 2. How much cash is left? Failed trials contribute zero to this average.
    figure, axis = plt.subplots(figsize=(10, 5.6), layout="constrained")
    amounts = [row["mean_thursday_cash_php"] for row in overall]
    cash_errors = [[r["mean_thursday_cash_php"] - r["cash_ci95_low_php"] for r in overall],
                   [r["cash_ci95_high_php"] - r["mean_thursday_cash_php"] for r in overall]]
    bars = axis.bar(labels, amounts, color=colors, yerr=cash_errors, capsize=5)
    axis.bar_label(bars, labels=[f"PHP {amount:.2f}" for amount in amounts], padding=6)
    axis.set(title="Average cash remaining on Thursday", ylabel="Mean cash (PHP)",
             ylim=(0, max(amounts, default=0) * 1.22 + 1))
    figure.supxlabel(footer + "\nIncludes zero cash for failed trials | Error bars: 95% Monte Carlo intervals", fontsize=9)
    figure.savefig(output / "remaining_cash.png", dpi=180)
    plt.close(figure)

    # 3. Mutually exclusive first-shortage days, plus successful four-day trials.
    figure, axis = plt.subplots(figsize=(10, 6), layout="constrained")
    bottom = [0.] * len(overall)
    day_colors = ["#AE4747", "#D47B40", "#D8B44A", "#8270A5", "#32826B"]
    categories = ["Monday", "Tuesday", "Wednesday", "Thursday", "No shortage"]
    for category, color in zip(categories, day_colors):
        key = "no_shortage_probability" if category == "No shortage" else f"first_shortage_{category.lower()}_probability"
        values = [row[key] * 100 for row in overall]
        bars = axis.barh(labels, values, left=bottom, color=color, label=category, height=.6)
        axis.bar_label(bars, labels=[f"{v:.1f}%" if v >= 5 else "" for v in values],
                       label_type="center", fontsize=10, color="white" if category != "Wednesday" else "#222222")
        bottom = [left + width for left, width in zip(bottom, values)]
    axis.set(title="When does the first shortage happen?", xlabel="All trials (%)", xlim=(0, 100))
    axis.invert_yaxis()
    axis.legend(loc="upper center", bbox_to_anchor=(.5, -.16), ncol=5, frameon=False)
    figure.supxlabel("Each row totals 100%; each failed trial is counted on its first shortage day only.\n"
                       "Labels shown for segments of at least 5%; exact values are in results.csv.", fontsize=9)
    figure.savefig(output / "first_shortage_day.png", dpi=180)
    plt.close(figure)

    # 4. Explain one exact path using the same simulation code as the experiment.
    figure, axis = plt.subplots(figsize=(12, 5.2))
    axis.axis("off")
    axis.set_title("Worked example: protecting a PHP 20 reserve", fontsize=17, pad=48)
    axis.text(.5, 1.05, "Illustrative fixed example: PHP 100 allowance, PHP 15 required/day, PHP 20 optional desire/day.\n"
              "Usual spending every day; no unexpected expenses. All amounts below are PHP.",
              transform=axis.transAxes, ha="center", fontsize=10)
    headers = ["Day", "Cash\nbefore", "Required\ncost", "Optional\ndesired", "Optional\npaid", "Reserve\nafter", "Cash\nafter"]
    cells = [[row[0]] + [f"{value:.2f}" for value in row[1:]] for row in trace]
    table = axis.table(cellText=cells, colLabels=headers, cellLoc="center", bbox=[0, .28, 1, .64])
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    for (row, column), cell in table.get_celld().items():
        cell.set_edgecolor("#D8E1E8")
        if row == 0:
            cell.set_facecolor("#315B80")
            cell.set_text_props(color="white", weight="bold")
        else:
            cell.set_facecolor("#F0F5F7" if row % 2 else "white")
    axis.text(0, .15, "Wednesday: required costs use PHP 5 of the reserve; optional purchases stop.\n"
              "Thursday: the remaining PHP 15 reserve covers essentials. Finishing at PHP 0 is success.\n"
              "The reserve is already part of the allowance; it never adds extra money.",
              transform=axis.transAxes, fontsize=11, va="top", linespacing=1.6)
    figure.subplots_adjust(left=.04, right=.96, top=.76, bottom=.05)
    figure.savefig(output / "worked_example.png", dpi=180)
    plt.close(figure)
