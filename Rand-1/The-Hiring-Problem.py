import csv
import random
from pathlib import Path

import matplotlib.pyplot as plt


def Hire_Assistant(candidates):
    """return a list of hired candidates"""
    best_candidate = None
    hire_events = []

    for candidate in candidates:
        if best_candidate is None or candidate > best_candidate:
            best_candidate = candidate
            hire_events.append(candidate)

    return hire_events


def theoretical_expected_hires(n):
    """Calculate H_n the nth harmonic series"""
    return sum(1 / rank for rank in range(1, n + 1))


def simulate_randomized_hiring(n, trials, random_generator):
    """Returns the average number of hires across all trials. Qualities are freshly
    generated for each trial using a Uniform[0, 1) distribution. The probability
    of ties is astronomically small and can be considered 0.
    """

    total_hires = 0

    for _ in range(trials):
        qualities = (random_generator.random() for _ in range(n))
        hire_events = Hire_Assistant(qualities)
        total_hires += len(hire_events)

    return total_hires / trials


def run_experiments():
    problem_sizes = (10, 30, 100, 300, 1_000, 3_000, 10_000)
    trials = 3_000
    rng = random.Random(42)

    results = []
    print("Plot: semi-logarithmic (logarithmic x-axis, linear y-axis)")
    print("n | best hires | worst hires | theoretical_average | observed average")

    for n in problem_sizes:
        observed_average = simulate_randomized_hiring(n, trials, rng)
        theoretical_average = theoretical_expected_hires(n)

        best_hires = len(Hire_Assistant(range(n, 0, -1)))
        worst_hires = len(Hire_Assistant(range(1, n + 1)))

        results.append(
            {
                "n": n,
                "simulaties": trials,
                "geobserveerd aantal aanwervingen": observed_average,
                "theoretisch aantal aanwervingen": theoretical_average,
                "best_case": best_hires,
                "worst_case": worst_hires,
            }
        )

        print(
            f"{n} | {best_hires} | {worst_hires} | "
            f"{theoretical_average:.4f} | {observed_average:.4f}"
        )

    output_dir = Path(__file__).resolve().parent
    csv_path = output_dir / "hiring_problem_results.csv"
    plot_path = output_dir / "hiring_problem_plot.png"

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    candidate_counts = [row["n"] for row in results]
    observed_average_hires = [row["geobserveerd aantal aanwervingen"] for row in results]
    theoretical_average_hires = [row["theoretisch aantal aanwervingen"] for row in results]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(candidate_counts, observed_average_hires, "o-", label="Geobserveerd gemiddelde")
    ax.plot(
        candidate_counts, theoretical_average_hires, "--", label=r"Theoretisch gemiddelde"
    )
    ax.set_xscale("log")
    ax.set_xlabel("Aantal kandidaten, n (log schaal)")
    ax.set_ylabel("Aantal aanwervingen")
    ax.set_title("Het Hiring Problem: Geobserveerd vs. Theoretisch gemiddelde")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(plot_path, dpi=200)
    plt.close(fig)

    print(f"\nSaved results: {csv_path}")
    print(f"Saved plot: {plot_path}")


if __name__ == "__main__":
    run_experiments()
