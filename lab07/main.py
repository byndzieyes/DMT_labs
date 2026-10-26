import json
import math
import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


LAB_DIR = Path(__file__).resolve().parent
STUDENT_NUMBER = 5
RANDOM_SEED = 5
WEIGHTS = (0.3, 0.7)


def generate_data(student_number: int = 5, seed: int = 5) -> dict:
    rng = random.Random(seed)
    return {
        "student_number": student_number,
        "seed": seed,
        "coordinates": [
            [rng.randint(student_number - 3, student_number + 3) for _ in range(2)]
            for _ in range(10)
        ],
    }



def calculate_results(points: list[list[float]]) -> dict:
    dominators = [
        [j for j, other in enumerate(points)
         if all(b >= a for a, b in zip(point, other))
         and any(b > a for a, b in zip(point, other))]
        for point in points
    ]
    pareto = [i for i, indices in enumerate(dominators) if not indices]
    ideal = [max(point[j] for point in points) for j in range(2)]
    linear = [sum(w * x for w, x in zip(WEIGHTS, point)) for point in points]
    distances = [math.dist(point, ideal) for point in points]
    return {
        "dominators": dominators,
        "pareto": pareto,
        "ideal": ideal,
        "linear": linear,
        "distances": distances,
        "linear_winners": [i for i, s in enumerate(linear)
                           if math.isclose(s, max(linear), rel_tol=0, abs_tol=1e-12)],
        "ideal_winners": [i for i, d in enumerate(distances)
                          if math.isclose(d, min(distances), rel_tol=0, abs_tol=1e-12)],
    }


def names(indices: list[int]) -> str:
    return ", ".join(f"A{i + 1}" for i in indices)


def plot_results(points: list[list[float]], result: dict, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 7), layout="constrained")
    ax.scatter(*zip(*points), s=65, color="#94a3b8", label="Альтернативи", zorder=3)
    ax.scatter(*zip(*(points[i] for i in result["ideal_winners"])),
               s=180, facecolors="none", edgecolors="#dc2626", linewidths=2,
               label="Найближчі альтернативи", zorder=5)
    ideal = result["ideal"]
    ax.scatter(*ideal, marker="*", s=260, color="#f59e0b",
               edgecolors="black", label=f"Ідеальна точка {tuple(ideal)}", zorder=6)
    for i in result["ideal_winners"]:
        ax.plot([points[i][0], ideal[0]], [points[i][1], ideal[1]],
                "--", color="#dc2626", alpha=0.6)
    groups = {}
    for i, point in enumerate(points):
        groups.setdefault(tuple(point), []).append(i)
    for point, indices in groups.items():
        ax.annotate(names(indices), point, xytext=(8, 9), textcoords="offset points",
                    fontsize=10)
    ax.set(xlabel="Q1 = x1 → max", ylabel="Q2 = x2 → max",
           title="Метод ідеальної точки: порівняння альтернатив")
    ax.set_aspect("equal", adjustable="box")
    ax.margins(0.22)
    ax.grid(alpha=0.25)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), fontsize=9)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def build_report(data: dict, result: dict) -> str:
    rows = []
    for i, (x, y) in enumerate(data["coordinates"]):
        dominators = names(result["dominators"][i]) or "—"
        rows.append(f"| A{i+1} | {x:g} | {y:g} | "
                    f"{'Так' if i in result['pareto'] else 'Ні'} | {dominators} | "
                    f"{result['linear'][i]:.4f} | {result['distances'][i]:.4f} |")
    same = set(result["linear_winners"]) == set(result["ideal_winners"])
    number = data["student_number"]
    return f"""# Лабораторна робота №7

## Метод ідеальної точки

### Вхідні дані

Номер у журналі: **{number}**. Кількість альтернатив: **10**.
Координати належать [{number - 3}; {number + 3}] включно.
Ваги лінійної згортки: **0,3 та 0,7**.
Ідеальна точка: **{tuple(result['ideal'])}**.

### Таблиця результатів

| Альтернатива | x1 = Q1 | x2 = Q2 | Парето | Хто домінує | Sᵢ → max | dᵢ → min |
|:---:|---:|---:|:---:|---|---:|---:|
{chr(10).join(rows)}

### Оптимальні альтернативи

| Метод | Результат |
|---|---|
| Множина Парето | **{names(result['pareto'])}** |
| Лінійна згортка | **{names(result['linear_winners'])}**, S = {max(result['linear']):.4f} |
| Метод ідеальної точки | **{names(result['ideal_winners'])}**, d = {min(result['distances']):.4f} |

### Графічне представлення

![Альтернативи у просторі критеріїв](plots/alternatives.png)
"""


def main() -> None:
    data = generate_data(STUDENT_NUMBER, RANDOM_SEED)
    result = calculate_results(data["coordinates"])
    plot_results(data["coordinates"], result, LAB_DIR / "plots" / "alternatives.png")
    for filename, content in (("data.json", data), ("results.json", result)):
        (LAB_DIR / filename).write_text(
            json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    (LAB_DIR / "README.md").write_text(build_report(data, result), encoding="utf-8")
    print(f"Множина Парето: {names(result['pareto'])}")
    print(f"Лінійна згортка: {names(result['linear_winners'])}")
    print(f"Ідеальна точка: {tuple(result['ideal'])}")
    print(f"Метод ідеальної точки: {names(result['ideal_winners'])}")
    print(f"Звіт і графік збережено в {LAB_DIR}")


if __name__ == "__main__":
    main()
