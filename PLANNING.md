# Grid Cost Planner · CISC 106 project plan

## Problem and user

A student screening an energy project needs to see whether an illustrative solar, storage,
or hybrid scenario fits a capital budget and what other configurations fit at the same MW.

## Navigation and state

| Route | Purpose |
| --- | --- |
| `index` | Introduce the tool |
| `planner` | Show the estimate form |
| `calculate` | Validate inputs, update five fields, and show the results |
| `save_case` | Append a unique Project snapshot to the saved list |
| `compare` | Loop through saved Project values to compute the comparison table |
| `clear_cases` | Empty the saved list after confirmation |
| `transmission` | Show raw material quantities and costs for the current line length |
| `assumptions` | Document inputs, exclusions, and Lazard LCOE references |

`State` holds location, technology, capacity in MW, budget in millions of dollars,
line miles, and a list of `Project` instances. Each snapshot holds the five inputs.
The form uses two dropdowns and three text fields. The saved view adds a checkbox.
Each navigation action renders a Drafter Page. The six distinct views are home,
input, results, saved comparison, transmission, and assumptions.

## Model and example

- Capital: solar MW AC × $1.2M/MW plus any battery MW × 4 h × $300k/MWh.
- Raw materials: mileage × sum of (quantity per mile × unit price).
- Budget balance: budget in dollars minus capital and the materials allowance.
- For a 50 MW hybrid and two line miles, capital is $120M, materials total $67,600,
  and an $80M budget falls short by $40,067,600. Solar and storage each screen at
  $60,067,600 at the same power rating.
- State names identify cases. State-specific prices and grid conditions require further data.
- Test valid, invalid, over-budget, and zero-mile inputs, plus save and clear behavior.

Source for the historical LCOE references is [Lazard LCOE+ v18.0, June 2025](https://www.lazard.com/media/5tlbhyla/lazards-lcoeplus-june-2025-_vf.pdf).
