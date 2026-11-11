"""Drafter app for comparing illustrative renewable energy project budgets."""

from dataclasses import dataclass
from math import isfinite

from drafter import (
    Button, CheckBox, Div, Header, Label, Link, Page, PageContent, SelectBox, Table, TextBox,
    add_website_css_file, add_website_file, hide_debug_information, route,
    set_site_information, set_website_framed, set_website_title, start_server,
)


TECHNOLOGIES = ("Solar PV", "Battery storage (BESS)", "Solar + storage")
STATES = ("Delaware", "Maryland", "New Jersey", "Pennsylvania", "Texas", "California")
SOLAR_PER_MW = 1_200_000
BATTERY_PER_MWH = 300_000
BATTERY_HOURS = 4
# Each immutable row holds material, quantity per mile, unit, and illustrative unit price.
MATERIALS = (
    ("Aluminum conductor", 9_000, "lb", 1.40),
    ("Steel structures", 24_000, "lb", 0.65),
    ("Concrete", 35, "yd³", 160.00),
)
LAZARD = "https://www.lazard.com/media/5tlbhyla/lazards-lcoeplus-june-2025-_vf.pdf"


@dataclass
class Project:
    """Capture the inputs for one screening estimate."""

    location: str
    technology: str
    capacity: float
    budget: float
    miles: float


@dataclass
class State:
    """Store the current estimate and the visitor's saved comparison cases."""

    location: str
    technology: str
    capacity: float
    budget: float
    miles: float
    projects: list[Project]


def initial_state() -> State:
    """Return a fresh state for a visitor or a test."""
    return State("Delaware", TECHNOLOGIES[0], 50, 80, 0, [])


def material_cost(miles: float) -> float:
    """Compute the raw material subtotal in dollars."""
    subtotal = 0.0
    for _, quantity, _, price in MATERIALS:
        subtotal += miles * quantity * price
    return subtotal


def project_cost(technology: str, capacity: float) -> float:
    """Compute modeled project capital costs in dollars."""
    cost = 0.0
    if technology in (TECHNOLOGIES[0], TECHNOLOGIES[2]):
        cost += capacity * SOLAR_PER_MW
    if technology in (TECHNOLOGIES[1], TECHNOLOGIES[2]):
        cost += capacity * BATTERY_HOURS * BATTERY_PER_MWH
    return cost


def combined_cost(project: Project) -> float:
    """Return project capital plus the separate materials allowance in dollars."""
    return project_cost(project.technology, project.capacity) + material_cost(project.miles)


def money(dollars: float) -> str:
    """Format a screening estimate to the nearest dollar."""
    return f"${dollars:,.0f}"


def page(state: State, title: str, content: list[PageContent]) -> Page:
    """Give every view the same navigation and readable content area."""
    navigation = Div(
        Button("Home", index), Button("New estimate", planner),
        Button(f"Saved cases ({len(state.projects)})", compare),
        Button("Transmission", transmission), Button("Assumptions", assumptions),
        classes="navigation",
    )
    return Page(state, [
        Div("GRID COST PLANNER", classes="brand"),
        navigation,
        Div(Header(title), *content, classes="panel"),
    ])


@route
def index(state: State) -> Page:
    """Show the purpose of the planner and link to the form."""
    return page(state, "Plan a renewable energy project", [
        "Screen utility-scale solar, four-hour battery storage, and solar-plus-storage against your budget.",
        "Compare scenarios and see how a transmission materials allowance affects the amount left to spend.",
        Button("Build an estimate", planner, classes="primary"),
    ])


def estimate_form(
    state: State, location: str, technology: str, capacity: str, budget: str, miles: str, error: str = "",
) -> Page:
    """Render the form with the visitor's entered values after a validation error."""
    if location not in STATES:
        location = state.location
    if technology not in TECHNOLOGIES:
        technology = state.technology
    fields = []
    if error:
        fields.append(Div(error, classes="error", role="alert"))
    fields.extend([
        Div(
            Div(Label("U.S. state", "location"), SelectBox("location", list(STATES), location)),
            Div(Label("Technology", "technology"), SelectBox("technology", list(TECHNOLOGIES), technology)),
            Div(Label("Capacity (MW)", "capacity"), TextBox("capacity", capacity)),
            Div(Label("Budget ($ millions)", "budget"), TextBox("budget", budget)),
            Div(Label("Transmission upgrade miles", "miles"), TextBox("miles", miles)),
            classes="fields",
        ),
        "Enter 0 miles for no transmission allowance. The selected state labels the case.",
        Button("Calculate estimate", calculate, classes="primary"),
    ])
    return page(state, "New project estimate", fields)


@route
def planner(state: State) -> Page:
    """Open the estimate form with the last valid inputs."""
    return estimate_form(
        state, state.location, state.technology, str(state.capacity), str(state.budget), str(state.miles),
    )


@route
def calculate(state: State, location: str, technology: str, capacity: str, budget: str, miles: str) -> Page:
    """Validate inputs, update the current estimate, and show the results."""
    # Exception handling catches a failed numeric conversion and returns the same form with guidance.
    try:
        capacity_mw, budget_millions, upgrade_miles = float(capacity), float(budget), float(miles)
    except ValueError:
        return estimate_form(state, location, technology, capacity, budget, miles, "Enter numbers such as 25 or 1.5.")

    error = ""
    if location not in STATES or technology not in TECHNOLOGIES:
        error = "Select a state and technology from the lists."
    elif not isfinite(capacity_mw) or not 0 < capacity_mw <= 10_000:
        error = "Enter a capacity greater than 0 and no greater than 10,000 MW."
    elif not isfinite(budget_millions) or not 0 < budget_millions <= 100_000:
        error = "Enter a budget greater than 0 and no greater than 100,000 million dollars."
    elif not isfinite(upgrade_miles) or not 0 <= upgrade_miles <= 1_000:
        error = "Enter transmission mileage from 0 to 1,000."
    if error:
        return estimate_form(state, location, technology, capacity, budget, miles, error)
    state.location = location
    state.technology = technology
    state.capacity = capacity_mw
    state.budget = budget_millions
    state.miles = upgrade_miles
    return results(state)


def results(state: State) -> Page:
    """Summarize project cost and show alternatives at the same project capacity."""
    budget_dollars = state.budget * 1_000_000
    materials = material_cost(state.miles)
    capital = project_cost(state.technology, state.capacity)
    difference = budget_dollars - capital - materials
    if difference >= 0:
        status = f"Within modeled budget by {money(difference)}."
    else:
        status = f"Over modeled budget by {money(-difference)}."
    alternatives = []
    for technology in TECHNOLOGIES:
        if technology != state.technology:
            total = project_cost(technology, state.capacity) + materials
            if total <= budget_dollars:
                alternatives.append(f"{technology} screens within budget at {money(total)}.")
    if not alternatives:
        available = max(0.0, budget_dollars - materials)
        maximum = available / project_cost(state.technology, 1)
        alternatives.append(
            f"No other technology fits at this size. Selected technology budget limit: {maximum:,.3g} MW."
        )
    return page(state, "Estimate results", [
        f"{state.location} · {state.technology} · {state.capacity:g} MW",
        Div(status, classes="status"),
        Table([
            ["Project capital allowance", money(capital)],
            ["Transmission raw materials only", money(materials)],
            ["Modeled budget subtotal", money(capital + materials)],
            ["Your budget", money(budget_dollars)],
        ], ["Cost component", "USD"]),
        "Transmission labor, engineering, land, permitting, and other installation costs are excluded.",
        Header("Alternatives", level=2),
        "Alternatives use the same MW and transmission miles. Solar and storage serve different operating needs.",
        *[Div(message) for message in alternatives],
        Button("Save for comparison", save_case, classes="primary"),
        Button("Edit inputs", planner),
    ])


@route
def save_case(state: State) -> Page:
    """Save a snapshot once and open the comparison page."""
    project = Project(state.location, state.technology, state.capacity, state.budget, state.miles)
    # Dataclasses compare their field values, so repeated saves do not create duplicate rows.
    if project not in state.projects:
        state.projects.append(project)
    return compare(state)


@route
def compare(state: State) -> Page:
    """Compare saved scenarios by reading each project's capacity, costs, and budget."""
    if not state.projects:
        return page(state, "Saved cases", ["Calculate and save an estimate to start a comparison."])
    rows = []
    for project in state.projects:
        total = combined_cost(project)
        rows.append([
            project.location, project.technology, f"{project.capacity:g}", f"{project.miles:g}",
            money(total), money(project.budget * 1_000_000 - total),
        ])
    return page(state, "Saved cases", [
        "Budget balance is budget minus the modeled subtotal. Saved cases live in this browser session.",
        Div(Table(rows, ["State", "Technology", "MW", "Line miles", "Subtotal", "Budget balance"]), classes="scroll"),
        CheckBox("confirmed", False), Label("Confirm clearing all saved cases", "confirmed"),
        Button("Clear saved cases", clear_cases),
    ])


@route
def clear_cases(state: State, confirmed: bool = False) -> Page:
    """Clear the saved comparison only when the visitor checks the confirmation box."""
    if confirmed:
        state.projects.clear()
    return compare(state)


@route
def transmission(state: State) -> Page:
    """Break down the current estimate's raw transmission materials by line item."""
    rows = []
    for material, quantity, unit, price in MATERIALS:
        rows.append([material, f"{quantity:,} {unit}", f"${price:,.2f}/{unit}", money(quantity * price * state.miles)])
    return page(state, "Transmission materials", [
        f"Current estimate: {state.miles:g} line miles. Raw materials subtotal: {money(material_cost(state.miles))}.",
        Div(Table(rows, ["Material", "Per mile", "Illustrative price", "Subtotal"]), classes="scroll"),
        "Quantities and prices describe a fictional upgrade. Actual scope requires an interconnection study.",
        "Freight, fabrication, labor, land, engineering, permitting, taxes and contingency are excluded.",
    ])


@route
def assumptions(state: State) -> Page:
    """Explain the cost model and link to the dated external LCOE reference."""
    return page(state, "Assumptions and benchmarks", [
        Header("Screening cost model", level=2),
        "Solar: $1.2 million per MW AC. Battery: $300,000 per MWh at four hours.",
        "Hybrid: solar and battery each use the entered MW. "
        "A 50 MW hybrid models 50 MW AC PV plus 50 MW / 200 MWh BESS.",
        "Capital rates and transmission inputs are classroom assumptions. States share the same rates.",
        "The model excludes land, financing, tax credits, operating costs, replacement and site-specific grid work.",
        Header("Lazard LCOE+ v18.0 · June 2025", level=2),
        Table([
            ["Utility solar PV", "$38–$78/MWh"],
            ["Utility solar PV + storage", "$50–$131/MWh"],
            ["Standalone battery", "Storage uses LCOS, a separate metric."],
        ], ["Technology", "Unsubsidized benchmark"]),
        "LCOE estimates lifetime cost per MWh of electricity generated. These ranges are reference values only.",
        Link("Read the Lazard report", LAZARD),
    ])


def run() -> None:
    """Configure the site and start Drafter."""
    set_website_title("Grid Cost Planner")
    set_site_information(
        author="Salvador Sosa",
        description="University of Delaware CISC 106 renewable energy project screening tool.",
        sources="Lazard LCOE+ v18.0, Drafter documentation, and illustrative classroom assumptions.",
        planning=Link("Planning document", "PLANNING.md"),
        links=[LAZARD],
    )
    set_website_framed(False)
    hide_debug_information()
    add_website_css_file("style.css")
    add_website_file("PLANNING.md")
    start_server(initial_state())


if __name__ == "__main__":
    run()
