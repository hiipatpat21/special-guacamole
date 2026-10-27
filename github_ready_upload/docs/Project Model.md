# Student Allowance Monte Carlo Model

This specification defines a Python simulation of whether an initial allowance can cover required school expenses from Monday through Thursday. It uses the 20 profiles in Data_20-students.xlsx as its working input dataset. The model supports exploratory scenario comparisons conditional on these inputs and assumptions.

## Research question

How do a reduced allowance, reduced optional spending, and a protected reserve affect the probability that a student cannot cover required school expenses over four on-campus days?

## Unit of simulation and scope

One trial represents one specified student's Monday–Thursday period. All four days are on campus. The full four-day allowance is available Monday morning, regardless of the profile's reported receipt frequency. No savings, borrowing, additional allowance, or income enters during the trial. Responses about seeking help describe behavior but are not monetary inputs.

Run 10,000 trials per profile per scenario: 200,000 four-day trials per scenario and 800,000 across four scenarios. Report each profile's results and the equally weighted average across the 20 profiles. This average describes the input profiles; it is not a representative population estimate.

Keep each student's allowance and expense characteristics together. Do not construct profiles by independently mixing allowance from one student with expenses from another.

## Input definitions

| Symbol | Meaning | Workbook column |
|---|---|---|
| A | Total four-day allowance | D |
| F | Usual daily food and drink expense | E |
| T | Daily round-trip transport expense | F |
| O | Usual daily optional expense, excluding food already counted | G |
| H | Total four-day regular printing and supplies expense | H |
| Low, High | Reported lowest and highest daily total expense | I, J |
| K | Number of unexpected expenses over four on-campus weeks | K |
| C | Usual cost of one unexpected expense | L |
| W | Number of shortage weeks among the last four weeks | M |
| Rreported | Reported reserve amount | O |

Columns B, C, N, and P provide eligibility and behavioral context. W and Rreported are descriptive checks, not inputs used to force a desired simulation result. A reported reserve is already part of A; never add it to the allowance.

## Random inputs

### Daily spending variation

Draw one daily spending multiplier independently on each day. Apply the same multiplier to that day's food and desired optional expense, so a higher-spending day affects both categories together.

| Daily condition | Multiplier V | Assumed probability | Cumulative probability | Random digits |
|---|---:|---:|---:|---|
| Lower spending | 0.80 | 0.25 | 0.25 | 00–24 |
| Usual spending | 1.00 | 0.50 | 0.75 | 25–74 |
| Higher spending | 1.20 | 0.25 | 1.00 | 75–99 |

Food expense is F × V. Desired optional spending before policy adjustment is O × V. Transport remains T. The expected multiplier is 1, so expected food and desired optional spending equal the profile's usual amounts before affordability limits or strategy changes.

The multipliers and probabilities are modeling assumptions, not frequencies measured by the survey. Low and High are diagnostic context, not hard bounds on generated daily totals. The questionnaire does not supply category-specific daily ranges or daily logs. Do not claim that this distribution was fitted from observations or silently clip generated totals to the reported ranges.

### Unexpected expenses

Each four-week reporting window contains 16 modeled on-campus days. Set the profile's daily unexpected-expense probability to p = K / 16. Draw an independent uniform random number U in [0,1) each day. An unexpected expense occurs if U < p, and its cost is C; otherwise its cost is zero.

This assumes at most one unexpected expense per day, a constant event probability, and a fixed event cost within a profile. The expected four-week event count is 16p = K. K / 16 estimates an event rate; using it as a Bernoulli probability additionally assumes no multiple-event days. The current profiles have K between 0 and 3, so p is between 0 and 0.1875. Future inputs with K > 16 require revising the event model, not silently capping p.

A zero recorded event count gives zero baseline probability for that profile. It does not establish that unexpected expenses can never occur. Test an additional assumed probability such as 0.05 per day for zero-count profiles in sensitivity analysis.

Use uniform draws rather than rounding p to a whole percentage. This preserves probabilities such as 1 / 16 = 0.0625. Emergency occurrence is assumed independent across days and independent of the daily spending multiplier, conditional on the profile.

### Regular printing and supplies

Allocate H equally across four days. This preserves the reported four-day total without inventing a purchase-day pattern. Use integer centavos and distribute any division remainder deterministically so the four daily amounts sum exactly to H. These expenses exclude unexpected printing and supplies, as clarified by the project team.

## Scenarios

| Scenario | Starting allowance | Desired optional expense | Initial protected reserve |
|---|---|---|---|
| Normal spending | A | O × V | 0 |
| Lower allowance | 0.80 × A | O × V | 0 |
| Controlled spending | A | 0.50 × O × V | 0 |
| Emergency reserve | A | O × V | 0.20 × A |

The 20% allowance reduction, 50% optional reduction, and 20% reserve are experiment settings selected for this model. They are not survey findings. The reserve scenario applies a consistent policy to every profile rather than copying different reported reserve habits into the comparison. Normal spending is a defined baseline without a protected reserve; it is not an exact reconstruction of each respondent's behavior.

## Daily state and payment procedure

Track day, cash balance B, protected reserve R, first shortage day, and first shortage amount. Initially B equals the scenario allowance, and R equals the scenario reserve.

For each day:

1. Generate the daily multiplier and unexpected-expense outcome.
2. Calculate required expense E = food + transport + allocated regular supplies + unexpected expense.
3. If E > B, record a shortage on this day, with first shortage amount E − B. Allocate the available cash toward required costs, set B and R to zero, and terminate this trial. Do not claim the first shortage amount is the complete four-day deficit.
4. Otherwise pay E and update B = B − E. Required costs may draw from the reserve when ordinary money is insufficient. Update R = min(previous R, B). This spends ordinary funds first and reduces the reserve only when necessary. Do not replenish a used reserve during the trial.
5. Calculate the scenario's desired optional expense. Actual optional expense is min(desired optional expense, B − R). It is always nonnegative. Deduct it from B. Optional purchases cannot draw on the protected reserve.
6. Continue to the next day, or finish after Thursday.

A trial succeeds if all four days' required expenses are fully covered. Exactly zero cash after all Thursday required expenses is success. Not being able to afford an optional purchase is not a shortage. Required expense is evaluated as a daily total; the model does not predict which particular essential purchase goes unpaid or the intraday order of purchases.

## Fifteen explicit model rules

These rules document the model's behavior. They should be mapped to implementation and tests; their count alone does not demonstrate the rubric's advanced-logic requirement.

1. Credit the full scenario allowance once on Monday and prohibit later inflows.
2. Preserve the joint expense and allowance characteristics of each student profile.
3. Apply one daily spending condition jointly to food and desired optional purchases; leave transport fixed.
4. Allocate regular printing and supplies across four days while preserving the exact total.
5. Convert the profile's four-week event count into a daily event probability under the stated single-event assumption.
6. Charge the usual unexpected-expense amount only when the event is triggered.
7. Prioritize all required expenses over optional purchases.
8. Permit required expenses to use protected reserve funds after ordinary funds are exhausted.
9. Reduce a depleted reserve permanently during that trial; do not refill it.
10. Prohibit optional purchases from using protected reserve funds or exceeding ordinary available cash.
11. Apply the allowance-reduction scenario to starting funds while preserving expense-generation inputs.
12. Apply the controlled-spending scenario to optional purchases while preserving essential needs.
13. Record the first required-expense shortfall and terminate a failed trial with no remaining cash.
14. Treat optional purchases forgone as a spending adjustment, and treat exact coverage of all four days as success.
15. Reject invalid model inputs, including negative amounts, noninteger event counts, K > 16, or an event count above zero with no positive event-cost estimate; flag inconsistent reserve or low/high values for review rather than silently changing them.

## Outputs

- Four-day shortage probability, overall and by profile.
- Probability of first shortage on each day, plus probability of no shortage. These five categories sum to one.
- Most frequent first shortage day among failed trials; report 'no shortages' if none occur.
- Average Thursday cash across all trials, assigning zero to failed trials under the payment/termination rule. Also report the average among successful trials separately.
- Average first shortage amount among failed trials, clearly distinguished from total unmet four-day needs.
- Average optional purchases forgone relative to generated desired optional spending, evaluated on days reached before termination; do not interpret missing post-failure days as observed zero demand.
- Scenario differences in shortage probability and remaining cash, with 95% Monte Carlo confidence intervals.

Reuse the same underlying daily random draws for a profile and repetition across all four scenarios, including draws generated in advance for days after an early failure. This permits paired scenario comparisons. Record the random seed. For the equally weighted overall estimate, combine the 20 profile estimates with equal weights and account for the fixed profile allocation when calculating Monte Carlo uncertainty. These intervals describe simulation noise conditional on inputs and assumptions, not uncertainty about the validity of the AI-adjusted data.

## Verification cases

Use fixed daily inputs so expected answers are exact. Random distribution checks are additional to these deterministic cases.

| Case | Fixed setup | Expected result |
|---|---|---|
| 1 | A = 100; all expenses zero; normal scenario | Success; ending cash 100 |
| 2 | A = 100; required expense 25 daily; no optional expense | Success; ending cash zero |
| 3 | A = 99; required expense 25 daily; no optional expense | First shortage Thursday; shortage amount 1 |
| 4 | A = 20; Monday required expense 25 | First shortage Monday; shortage amount 5; terminate |
| 5 | A = 100; Monday required expense 10; optional desire 200; no reserve | Actual Monday optional expense 90; cash zero; no Monday required-expense shortage |
| 6 | Before payment B = 100 and R = 20; required expense 85; optional desire 10 | Required expense covered; B = 15, R = 15; optional purchase zero |
| 7 | Before payment B = 100 and R = 20; required expense 30; optional desire 60 | Optional purchase 50; B = 20, R = 20 |
| 8 | A = 100; daily required expense 20; no optional expense | Normal and lower-allowance scenarios both succeed; ending cash 20 and zero respectively |
| 9 | A = 100; daily required expense 15; V = 1 each day; O = 20 | Normal first fails Thursday by 15; controlled and reserve both succeed with cash zero |
| 10 | K = 1, C = 100; compare U = 0.0624 and U = 0.0625 | First draw triggers cost 100; second triggers zero, because the rule is U < 0.0625 |

Verify multiplier interval boundaries, zero emergency cases, centavo allocation, input rejection, and reproducibility as additional checks. Confirm the program terminates and that recorded day probabilities reconcile to one. Use a small hand-calculated four-day trace before running the full experiment.

## Sensitivity analysis and validation

Repeat selected comparisons with daily spending variation of ±10% and ±30%, keeping probabilities 25%, 50%, 25%. Also test reserve rates of 10%, 20%, and 30%, and the zero-count event-probability assumption described above. Report whether the strategy ranking changes. These are assumptions under examination, not new observed data.

The adjusted data supports verification and internal plausibility checks. It cannot independently establish agreement with authentic student behavior. Reported shortage frequencies in the same AI-adjusted workbook may be compared descriptively but must not be presented as independent real-world validation or used to tune the model until it matches. If trustworthy unchanged observations become available later, use them for external validation.

## Relationship to the Monte Carlo lesson

Monte Carlo Lesson Reference.pdf pages 7–10 describe repeated random sampling, probability distributions, cumulative probabilities, random-number intervals, and summarizing simulated outcomes. This model follows that procedure:

1. Define uncertain daily spending and unexpected expenses.
2. Specify their probabilities and cumulative thresholds.
3. Generate uniform random numbers and map them to outcomes.
4. Apply the daily payment and budgeting rules.
5. Repeat four-day trials and calculate probabilities and averages.

Use a sample trace with columns for day, random numbers, selected multiplier, emergency outcome, required expense, optional expense, reserve, and ending cash. The lesson's later Monte Carlo Tree Search procedure, including selection, expansion, simulation, and backpropagation, is a separate method and is not part of this project.
