# Assessment after the simple-version coding improvements

Assessment date: 27 October 2026. Scope: the current simple Python package and
its reproducible outputs, evaluated against the shared Rubric.pdf and
Project-Outline.pdf. The project discussion confirms Python is accepted.

## Verification performed

- All **15 tests passed**: ten exact model cases and five supporting checks.
- The repaired trace interface passed case 9, including reserve progression
  PHP 20, 20, 15, 0 and ending cash PHP 65, 30, 15, 0.
- The full main experiment completed **800,000 four-day trials**: 20 profiles,
  10,000 trials per profile, four scenarios, seed 20261027.
- The entry point now generates all three charts and the worked-example table.
- Results include 84 scenario/profile rows with confidence intervals; paired
  comparisons include 63 rows; the input export contains 140 unique facts.
- The program integration test checks first-shortage probabilities reconcile
  with no-shortage probability to one and that the numerical outputs reproduce
  exactly with the same seed/settings.
- A hand-calculated example verifies the fixed-profile variance formula;
  paired tests verify signs, units, and zero difference variance for identical
  policies. Source-cell checks compare exported facts with actual workbook cells.

## Rubric assessment

| Criterion | Coding evidence now available | Assessment and limits |
|---|---|---|
| Fact base quantity and depth | `input_facts.csv`: 140 unique numerical model attributes, with student IDs, units, source cells, and provenance. | The numerical quantity exceeds 100 and the structure is explicit. Faithful representation of the adjusted workbook is checked. Authentic real-world accuracy cannot be established from the adjusted inputs. |
| Rule base complexity | `RULES_AND_TESTS.md`: 15 substantive model rules, implementation locations, and test evidence. Reserve depletion, required-cost priority, optional affordability and early termination form interacting state transitions. | The rule count and interaction evidence are available. The highest "advanced logic" band remains the instructor's judgment; no artificial recursion or claimed Prolog cuts are introduced. |
| Test queries and validation | Ten documented exact cases, plus five supporting checks; all 15 passed. Expected outputs are in the README and rule guide. | Strong verification evidence, including edge cases and combined reserve/shortage paths. This does not replace external validation against authentic data or documented expert review. |
| Program correctness and logic | Full experiment completes; all figures are connected to the entry point; reproducibility and output reconciliation pass. | Verified for the supplied workbook, fixed cases, and tested invalid inputs. The previous trace error is resolved. Open Excel output files must be closed before overwrite; CSV lock errors now explain this. |
| Code documentation and presentation | Commented functions; separate small statistical and plotting helpers; run instructions; 15-rule/test mapping; a process flowchart; three charts and a worked example. | Coding documentation is available without requiring the advanced version. A complete report organized under the ten outline sections and the group's oral presentation remain separate deliverables. |

These are evidence-based findings, not a guaranteed grade. A count of attributes
does not create additional surveyed students, and naming 15 rules alone does not
prove that every rule has the complexity required for the highest band.

## Outline coverage supplied by the code

| Outline section | Coding material now available | Remaining report/research work |
|---|---|---|
| 1. Project overview | A four-day allowance-sufficiency simulation and four policies. | Write problem context, goal and study boundary. |
| 2. Problem formulation and objectives | Explicit scenario inputs; shortage probability, first day, cash, first shortfall and optional forgone measures. | State research questions and explain why these measures answer them. |
| 3. Conceptual model | Student/day/cash/reserve/shortage states, 15-rule catalog, assumptions and flowchart. | Include and explain the model in the report. |
| 4. Data collection and input modeling | Source-cell fact export, input validation and declared spending/event distributions. | Explain collection, AI adjustments, missing daily logs and why the distributions are assumptions rather than fitted observations. |
| 5. Model translation and implementation | Straightforward Python loop with separate analysis/plotting helpers. | Justify Python and describe how the functions connect. |
| 6. Verification and validation | Ten exact cases and five supporting checks. | Include test evidence and honestly state limits of real-world validation; obtain trustworthy comparison data or an expert review if required. |
| 7. Results analysis and conclusion | Equal-profile 95% intervals and paired scenario differences, plus three comparison charts. | Interpret uncertainty, discuss optional-spending trade-offs and recommendations; do not claim population inference. |
| 8. Sample outputs | CSV files, three charts, worked example and recorded run settings. | Choose labeled screenshots of the outputs and successful test run. |
| 9. References/sources | Workbook cell provenance and references to the shared model/assignment documents. | Prepare verified IEEE-style method and data references. |
| 10. Program listing | The Python source and test files. | Include their final versions in the report listing. |

## What the group needs to study

1. `simulation.py`: how the student moves from Monday to Thursday.
2. `RULES_AND_TESTS.md`: the 15 decisions, their interactions and exact cases.
3. The three charts and worked example: what the results mean.
4. `analysis.py` at the level of explanation in the guide: intervals quantify
   simulation noise; paired comparisons use the same random situations.

There is no requirement to study the advanced implementation to run or explain
these features. The original model's broader sensitivity/convergence experiments
are not automatically run by this simple package, so it should not be described
as reproducing every experiment in that specification.
