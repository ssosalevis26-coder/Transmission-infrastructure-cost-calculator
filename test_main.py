"""Route and model checks for Grid Cost Planner."""

from unittest import TestCase

from drafter import Page

from main import (
    TECHNOLOGIES, assumptions, calculate, clear_cases, compare, index, initial_state,
    material_cost, planner, project_cost, save_case, transmission,
)


class PlannerTests(TestCase):
    """Exercise all routes and the project's budget arithmetic."""

    def assert_page(self, page: Page, phrase: str) -> None:
        """Verify a phrase appears in the components of the returned page."""
        self.assertIsInstance(page, Page)
        self.assertIn(phrase, repr(page.content))

    def test_index(self) -> None:
        """Introduce the planner."""
        self.assert_page(index(initial_state()), "Plan a renewable energy project")

    def test_planner(self) -> None:
        """Render the budget input."""
        self.assert_page(planner(initial_state()), "Budget ($ millions)")

    def test_calculate_hybrid(self) -> None:
        """Update all five fields and report the expected shortfall."""
        state = initial_state()
        result = calculate(state, "Texas", TECHNOLOGIES[2], "60", "81", "2")
        self.assertEqual((state.location, state.technology), ("Texas", TECHNOLOGIES[2]))
        self.assertEqual((state.capacity, state.budget, state.miles), (60, 81, 2))
        self.assert_page(result, "Over modeled budget by $63,067,600")
        self.assert_page(result, "Solar PV screens within budget")

    def test_calculate_rejects_invalid_input(self) -> None:
        """Preserve the last valid case when a number is invalid."""
        for bad in ("abc", "nan", "inf", "-1", "10001"):
            state = initial_state()
            self.assert_page(calculate(state, "Texas", TECHNOLOGIES[0], bad, "80", "0"), "New project estimate")
            self.assertEqual(state, initial_state())

    def test_calculate_rejects_unknown_selections(self) -> None:
        """Recover the form after an unrecognized dropdown value."""
        self.assert_page(
            calculate(initial_state(), "Unknown", "Unknown", "50", "80", "0"),
            "Select a state and technology from the lists.",
        )

    def test_save_case(self) -> None:
        """Keep a snapshot and skip duplicate saves."""
        state = initial_state()
        self.assert_page(save_case(state), "Saved cases")
        save_case(state)
        calculate(state, "Texas", TECHNOLOGIES[1], "30", "40", "0")
        self.assertEqual(len(state.projects), 1)
        self.assertEqual(state.projects[0].location, "Delaware")

    def test_compare(self) -> None:
        """Render both the empty comparison and the calculated budget balance."""
        state = initial_state()
        self.assert_page(compare(state), "Calculate and save")
        save_case(state)
        self.assert_page(compare(state), "$20,000,000")

    def test_clear_cases(self) -> None:
        """Require the checkbox before removing saved projects."""
        state = initial_state()
        save_case(state)
        clear_cases(state, False)
        self.assertEqual(len(state.projects), 1)
        self.assert_page(clear_cases(state, True), "Calculate and save")
        self.assertEqual(state.projects, [])

    def test_transmission(self) -> None:
        """Show the materials total at two miles."""
        state = initial_state()
        state.miles = 2
        self.assert_page(transmission(state), "$67,600")
        self.assertEqual(material_cost(0), 0)

    def test_assumptions(self) -> None:
        """Expose the Lazard reference and the classroom cost model."""
        self.assert_page(assumptions(initial_state()), "Lazard LCOE+ v18.0")

    def test_capital_costs(self) -> None:
        """Verify solar, battery, and combined capital amounts."""
        self.assertEqual(project_cost(TECHNOLOGIES[0], 50), 60_000_000)
        self.assertEqual(project_cost(TECHNOLOGIES[1], 50), 60_000_000)
        self.assertEqual(project_cost(TECHNOLOGIES[2], 50), 120_000_000)
