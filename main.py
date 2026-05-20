"""
main.py
-------
CLI entry point for the Disaster Rescue Multi-Agent System (Symbolic FOL Edition).

Usage
-----
    python main.py                    # run with defaults from config.py
    python main.py --tasks 15         # generate 15 tasks
    python main.py --no-delay         # skip simulated execution delays
    python main.py --seed 0           # use a specific random seed
    python main.py --grid 30          # use a 30x30 grid
    python main.py --interactive      # interactive mode with live parameter menu
"""

from __future__ import annotations

import argparse
import os
import sys
import random
import re

# Force UTF-8 output on Windows so Unicode box-drawing chars render correctly
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() not in ("utf-8", "utf8"):
    sys.stderr.reconfigure(encoding="utf-8")

from colorama import init as colorama_init, Fore, Style

colorama_init(autoreset=True)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Disaster Rescue Multi-Agent System — Symbolic FOL Edition"
    )
    parser.add_argument(
        "--tasks", type=int, default=None,
        help="Number of tasks to generate (default: value in config.py)"
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Random seed for task generation (default: value in config.py)"
    )
    parser.add_argument(
        "--grid", type=int, default=None,
        help="Grid size NxN (default: value in config.py)"
    )
    parser.add_argument(
        "--out", type=str, default=None,
        help="Output JSON path (default: results/run_001.json)"
    )
    parser.add_argument(
        "--no-delay", action="store_true",
        help="Disable simulated execution delays for robot agents"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true",
        help="Run in interactive mode with parameter menu"
    )
    return parser.parse_args()

def interactive_mode() -> None:

    from config import NUM_TASKS, RANDOM_SEED, GRID_SIZE
    from simulation import run_simulation

    settings = {
        "tasks": NUM_TASKS,
        "seed": RANDOM_SEED,
        "grid": GRID_SIZE,
        "delay": False,
        # If set to empty/None, simulation will auto-name under results/
        "out": "",
    }

    def _next_run_path(path: str) -> str | None:

        normalized = path.replace("\\", "/")
        m = re.search(r"(^|/)results/run_(\d{3})\.json$", normalized)
        if not m:
            return None
        n = int(m.group(2))
        return os.path.join("results", f"run_{n + 1:03d}.json")

    def print_header():
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "  DISASTER RESCUE SIMULATION — INTERACTIVE MODE")
        print(Fore.CYAN + "  Symbolic FOL Edition")
        print(Fore.CYAN + "=" * 60)

    def print_menu():
        print(Fore.WHITE + "\nCurrent Settings")
        print(Fore.WHITE + "-" * 60)
        print(f"  Tasks        : {Fore.YELLOW}{settings['tasks']}{Style.RESET_ALL}")
        print(f"  Seed         : {Fore.YELLOW}{settings['seed']}{Style.RESET_ALL}")
        print(f"  Grid         : {Fore.YELLOW}{settings['grid']}x{settings['grid']}{Style.RESET_ALL}")
        print(f"  Delay        : {Fore.YELLOW}{'On' if settings['delay'] else 'Off'}{Style.RESET_ALL}")
        out_label = settings["out"] if settings["out"] else "(auto: results/t{tasks}_g{grid}_s{seed}_<id>.json)"
        print(f"  JSON output  : {Fore.YELLOW}{out_label}{Style.RESET_ALL}")
        print(Fore.WHITE + "-" * 60)
        print(Fore.CYAN + "  [E] Edit settings (tasks/seed/grid/delay/output)")
        print(Fore.CYAN + "  [R] Random seed (quick)")
        print(Fore.GREEN + "  [S] Run simulation")
        print(Fore.RED + "  [Q] Quit")
        print()

    def get_input(prompt: str, default: str = "") -> str:
        try:
            return input(prompt).strip() or default
        except (EOFError, KeyboardInterrupt):
            return "q"

    def settings_menu() -> None:
        while True:
            print(Fore.CYAN + "\n" + "=" * 60)
            print(Fore.CYAN + "  SETTINGS")
            print(Fore.CYAN + "=" * 60)
            print(Fore.WHITE + f"  [1] Tasks       : {Fore.YELLOW}{settings['tasks']}{Style.RESET_ALL}   (min=3, max=50)")
            print(Fore.WHITE + f"  [2] Seed        : {Fore.YELLOW}{settings['seed']}{Style.RESET_ALL}   (any integer, e.g. 42)")
            print(Fore.WHITE + f"  [3] Grid        : {Fore.YELLOW}{settings['grid']}x{settings['grid']}{Style.RESET_ALL}   (min=10, max=100)")
            print(Fore.WHITE + f"  [4] Delay       : {Fore.YELLOW}{'On' if settings['delay'] else 'Off'}{Style.RESET_ALL}   (toggle)")
            out_label = settings["out"] if settings["out"] else "(auto)"
            print(Fore.WHITE + f"  [5] JSON output : {Fore.YELLOW}{out_label}{Style.RESET_ALL}")
            print(Fore.WHITE + "                 : (recommended: results/run_001.json → auto-increments)")
            print()
            print(Fore.CYAN + "  [R] Random seed")
            print(Fore.CYAN + "  [B] Back")
            print()

            choice = get_input(Fore.WHITE + "Select option: ").lower()

            if choice == "1":
                try:
                    new_tasks = int(get_input(f"   Tasks (3-50) [{settings['tasks']}]: ", str(settings['tasks'])))
                    if 3 <= new_tasks <= 50:
                        settings['tasks'] = new_tasks
                        print(Fore.GREEN + f"   Tasks set to {new_tasks}")
                    else:
                        print(Fore.RED + "   Tasks must be between 3 and 50")
                except ValueError:
                    print(Fore.RED + "   Invalid number")

            elif choice == "2":
                try:
                    new_seed = int(get_input(f"   Seed (any integer) [{settings['seed']}]: ", str(settings['seed'])))
                    settings['seed'] = new_seed
                    print(Fore.GREEN + f"   Seed set to {new_seed}")
                except ValueError:
                    print(Fore.RED + "   Invalid number")

            elif choice == "3":
                try:
                    new_grid = int(get_input(f"   Grid size (10-100) [{settings['grid']}]: ", str(settings['grid'])))
                    if 10 <= new_grid <= 100:
                        settings['grid'] = new_grid
                        print(Fore.GREEN + f"   Grid set to {new_grid}x{new_grid}")
                    else:
                        print(Fore.RED + "   Grid must be between 10 and 100")
                except ValueError:
                    print(Fore.RED + "   Invalid number")

            elif choice == "4":
                settings['delay'] = not settings['delay']
                print(Fore.GREEN + f"   Delay {'enabled' if settings['delay'] else 'disabled'}")

            elif choice == "5":
                new_out = get_input(
                    f"   JSON output path [{settings['out'] or 'auto'}]\n"
                    "   Leave empty for auto-naming under results/\n"
                    "   Example: results/t10_g20_s42_20260317-143000_ab12cd.json\n"
                    "   Or:      results/run_001.json (manual naming)\n"
                    "   New path: ",
                    settings["out"],
                )
                settings["out"] = new_out.strip()
                out_label = settings["out"] if settings["out"] else "(auto)"
                print(Fore.GREEN + f"   JSON output set to {out_label}")

            elif choice == "r":
                settings['seed'] = random.randint(1, 9999)
                print(Fore.GREEN + f"   Random seed: {settings['seed']}")

            elif choice == "b":
                return

            else:
                print(Fore.RED + "   Invalid option")

    print_header()

    while True:
        print_menu()
        choice = get_input(Fore.WHITE + "Select option: ").lower()

        if choice == "e":
            settings_menu()

        elif choice == "r":
            settings['seed'] = random.randint(1, 9999)
            print(Fore.GREEN + f"   Random seed: {settings['seed']}")

        elif choice == "s":
            print(Fore.CYAN + "\n" + "=" * 60)
            print(Fore.CYAN + f"  Running: tasks={settings['tasks']}, seed={settings['seed']}")
            print(Fore.CYAN + "=" * 60)

            try:
                export_path = settings["out"] or None
                result = run_simulation(
                    num_tasks=settings['tasks'],
                    grid_size=settings['grid'],
                    seed=settings['seed'],
                    simulate_delay=settings['delay'],
                    export_path=export_path,
                )
                print(Fore.GREEN + "\nSimulation complete!")
                dashboard = os.path.abspath(os.path.join("report", "index.html"))
                json_out = result.get("export_paths", {}).get("export_path", settings["out"] or "")
                json_out_abs = os.path.abspath(json_out)
                print(Fore.CYAN + f"\nDashboard: {dashboard}")
                print(Fore.CYAN + f"JSON:       {json_out_abs}")
                print(Fore.CYAN + f"Latest:     {os.path.abspath(os.path.join('results', 'latest.json'))}")

                next_path = _next_run_path(settings["out"])
                if next_path is not None:
                    settings["out"] = next_path
            except Exception as exc:
                print(Fore.RED + f"\n[ERROR] {exc}")

            input(Fore.WHITE + "\nPress Enter to continue...")
            print_header()

        elif choice == "q":
            print(Fore.YELLOW + "\nGoodbye!")
            break

        else:
            print(Fore.RED + "   Invalid option")


def main() -> None:
    args = parse_args()

    if args.interactive:
        interactive_mode()
        return

    from config import NUM_TASKS, RANDOM_SEED, GRID_SIZE
    from simulation import run_simulation

    num_tasks      = args.tasks if args.tasks is not None else NUM_TASKS
    seed           = args.seed  if args.seed  is not None else RANDOM_SEED
    grid_size      = args.grid  if args.grid  is not None else GRID_SIZE
    simulate_delay = not args.no_delay
    export_path    = args.out if args.out is not None else None

    print(f"\nStarting simulation — Symbolic FOL Edition")

    try:
        result = run_simulation(
            num_tasks=num_tasks,
            grid_size=grid_size,
            seed=seed,
            simulate_delay=simulate_delay,
            export_path=export_path,
        )
    except Exception as exc:
        print(f"\n[ERROR] {exc}")
        sys.exit(1)

    dashboard = os.path.abspath(os.path.join("report", "index.html"))
    json_out = result.get("export_paths", {}).get("export_path", export_path or "")
    print(f"\nDashboard: {dashboard}")
    print(f"JSON:      {os.path.abspath(json_out)}")
    print(f"Latest:    {os.path.abspath(os.path.join('results', 'latest.json'))}")
    print("\nSimulation complete.")

if __name__ == "__main__":
    main()
