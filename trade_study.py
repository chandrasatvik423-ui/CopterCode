from pipeline import run_pipeline
from rich.console import Console
from rich.table import Table

console = Console()

def run_trade_study(prompt_a: str, prompt_b: str):
    console.print(f"\n[bold blue]⚖️ Executing Trade Study...[/bold blue]")
    console.print(f"  [cyan]Option A:[/cyan] {prompt_a}")
    console.print(f"  [cyan]Option B:[/cyan] {prompt_b}\n")
    
    # Run pipelines sequentially
    res_a = run_pipeline(prompt_a)
    res_b = run_pipeline(prompt_b)
    
    table = Table(title="Astro-Forge Design Trade Study")
    table.add_column("Metric", justify="right", style="white", no_wrap=True)
    table.add_column(f"Option A\n({prompt_a})", style="magenta")
    table.add_column(f"Option B\n({prompt_b})", style="green")
    
    def safe_get(res, *keys, default="N/A"):
        d = res
        for k in keys:
            if isinstance(d, dict) and k in d:
                d = d[k]
            else:
                return default
        return d

    table.add_row("Status", res_a.get("status", "N/A"), res_b.get("status", "N/A"))
    table.add_row("Topology", safe_get(res_a, "topology", "name"), safe_get(res_b, "topology", "name"))
    
    # Mass
    mass_a = safe_get(res_a, "mass", "takeoff_mass_g")
    mass_b = safe_get(res_b, "mass", "takeoff_mass_g")
    table.add_row("Takeoff Mass (g)", str(mass_a), str(mass_b))
    
    # Physics
    twr_a = safe_get(res_a, "screening", "thrust_to_weight_ratio")
    twr_b = safe_get(res_b, "screening", "thrust_to_weight_ratio")
    table.add_row("Thrust-to-Weight", str(twr_a), str(twr_b))
    
    sf_a = safe_get(res_a, "screening", "governing_safety_factor")
    sf_b = safe_get(res_b, "screening", "governing_safety_factor")
    table.add_row("Safety Factor", str(sf_a), str(sf_b))
    
    # Geometry
    width_a = safe_get(res_a, "screening", "last_evaluated_width_mm")
    width_b = safe_get(res_b, "screening", "last_evaluated_width_mm")
    table.add_row("Arm Width (mm)", str(width_a), str(width_b))
    
    # Cost
    cost_a = safe_get(res_a, "manufacturing", "material_cost_usd")
    cost_b = safe_get(res_b, "manufacturing", "material_cost_usd")
    table.add_row("Frame Material Cost ($)", str(cost_a), str(cost_b))

    console.print(table)
    
    # Engineering Recommendation Logic
    console.print("\n[bold yellow]💡 Engineering Insight:[/bold yellow]")
    if isinstance(twr_a, (int, float)) and isinstance(twr_b, (int, float)):
        if twr_a > twr_b:
            console.print(f"Option A ({prompt_a}) provides superior agility with a higher Thrust-to-Weight ratio.")
        elif twr_b > twr_a:
            console.print(f"Option B ({prompt_b}) provides superior agility with a higher Thrust-to-Weight ratio.")
        else:
            console.print("Both configurations offer similar dynamic performance.")
    else:
        console.print("One or both configurations failed to generate a valid flight candidate. Adjust prompts to clear the structural screening.")

if __name__ == "__main__":
    console.print("\n[bold yellow]📡 ASTRO-FORGE TRADE STUDY ENGINE[/bold yellow]")
    a = console.input("Configuration A (e.g., 'standard racing drone'): ")
    b = console.input("Configuration B (e.g., 'micro drone'): ")
    run_trade_study(a, b)