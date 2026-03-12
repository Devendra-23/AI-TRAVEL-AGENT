from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

console = Console()

def print_itinerary(state: dict):
    """Turns the trip state into a beautiful terminal display using the rich library."""
    # 1. Header Panel 
    rprint(Panel(f"[bold magenta]✈️ Trip Itinerary: {state.get('destination', 'Unknown')}[/bold magenta]", expand=False))

    # 2. Flight Details
    if state.get('selected_flight'):
        f = state['selected_flight']
        rprint(f"[bold cyan]Flight:[/bold cyan] {f['airline']} | ${f['price_usd']} | {f['departure']}")

    # 3. Hotel Details
    if state.get('selected_hotel'):
        h = state['selected_hotel']
        rprint(f"[bold yellow]Hotel:[/bold yellow] {h['name']} ({h['rating']}⭐) | ${h['price_per_night_usd']}/night")

    # 4. Daily Schedule Table 
    if state.get('itinerary') and 'days' in state['itinerary']:
        table = Table(title="Daily Schedule", show_header=True, header_style="bold green")
        table.add_column("Day", style="dim")
        table.add_column("Theme")
        table.add_column("Activities")

        for day in state['itinerary']['days']:
            activities = "\n".join([f"• {a['time']}: {a['name']} (${a.get('cost_usd', 0)})" for a in day.get('activities', [])])
            table.add_row(str(day['day']), day['theme'], activities)
        
        console.print(table)

    # 5. Budget Summary [cite: 87]
    if 'total_cost_usd' in state:
        color = "green" if state.get('within_budget', True) else "red"
        rprint(f"[{color}]Total Estimated Cost: ${state['total_cost_usd']}[/{color}]")