import json
from pathlib import Path
from statistics import NormalDist

import numpy as np


LAB_DIR = Path(__file__).resolve().parent
DATA_FILE = LAB_DIR / "data.json"
REPORT_FILE = LAB_DIR / "README.md"


def calculate_thurstone(data: dict) -> dict:
    names = data["alternatives"]
    n = len(names)
    if n < 2 or len(set(names)) != n:
        raise ValueError("Потрібні щонайменше дві різні альтернативи.")
    equations, targets, pairs = [], [], []
    seen = set()
    for item in data["comparisons"]:
        i, j, wins, total = (item[key] for key in ("i", "j", "wins", "total"))
        if not all(type(value) is int for value in (i, j, wins, total)):
            raise ValueError("Індекси та кількості мають бути цілими числами.")
        if not (1 <= i <= n and 1 <= j <= n and i != j):
            raise ValueError("Неправильні індекси альтернатив.")
        if total <= 0 or not 0 <= wins <= total:
            raise ValueError("Потрібно total > 0 та 0 <= wins <= total.")
        key = tuple(sorted((i, j)))
        if key in seen:
            raise ValueError(f"Повторне порівняння пари {key}.")
        seen.add(key)
        probability = wins / total
        if wins in (0, total):
            probability = (wins + 0.5) / (total + 1)
        z = NormalDist().inv_cdf(probability)
        row = np.zeros(n)
        row[i - 1], row[j - 1] = 1, -1
        equations.append(row)
        targets.append(z)
        pairs.append({**item, "probability": probability, "z": z})
    if len(seen) != n * (n - 1) // 2:
        raise ValueError("Потрібно задати кожну неупорядковану пару рівно один раз.")
    matrix = np.array(equations)
    target = np.array(targets)
    scores = np.linalg.lstsq(
        np.vstack([matrix, np.ones(n)]), np.append(target, 0.0), rcond=None
    )[0]
    residuals = matrix @ scores - target
    span = float(np.ptp(scores))
    display_scores = (scores - scores.min()) * 100 / span if span > 1e-12 else np.zeros(n)
    return {
        "pairs": pairs, "scores": scores, "display_scores": display_scores,
        "sse": float(residuals @ residuals),
    }


def build_report(data: dict, result: dict) -> str:
    names = data["alternatives"]
    pair_rows = "\n".join(
        f"| x{pair['i']} / x{pair['j']} | {pair['wins']}/{pair['total']} | "
        f"{pair['probability']:.3f} | {pair['z']:.4f} |"
        for pair in result["pairs"]
    )
    score_rows = "\n".join(
        f"| x{i + 1} | {name} | {result['scores'][i]:.4f} | "
        f"{result['display_scores'][i]:.2f} |"
        for i, name in enumerate(names)
    )
    correction = (
        "\nДля частот 0 або 1 застосовано поправку S = (wins + 0,5)/(total + 1).\n"
        if any(pair["wins"] in (0, pair["total"]) for pair in result["pairs"]) else ""
    )
    return f"""# Лабораторна робота №5

## Метод Терстоуна

**Дані:** `data.json`. {data.get('description', 'Походження даних не вказано.')}

### Попарні порівняння

S — частка виборів першої альтернативи пари; z = Φ⁻¹(S) — квантиль
стандартного нормального розподілу. Позначення альтернатив наведено в таблиці оцінок.

| Пара | Вибори першої / усі порівняння | S | z |
|---|---:|---:|---:|
{pair_rows}
{correction}
### Розрахунок

Припускаємо нормальний розподіл оцінок, однакові дисперсії та відсутність кореляції.
Розв'язуємо систему Mᵢ - Mⱼ = zᵢⱼ методом найменших квадратів за умови ΣMᵢ = 0.
Одиниця шкали — стандартне відхилення різниці оцінок, √(2D).

Сума квадратів залишків: **{result['sse']:.6f}**.

### Оцінки альтернатив

| Позначення | Альтернатива | Mᵢ | Шкала 0–100 |
|---|---|---:|---:|
{score_rows}

Більше Mᵢ означає вищу важливість. Шкала 0–100 — лінійне перетворення
100 · (Mᵢ - min(M))/(max(M) - min(M)), а не відсоток корисності.
Якщо всі оцінки однакові, значення цієї шкали приймаються рівними 0.
"""


def main() -> None:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8-sig"))
    result = calculate_thurstone(data)
    REPORT_FILE.write_text(build_report(data, result), encoding="utf-8")
    print(f"Результат збережено: {REPORT_FILE}")


if __name__ == "__main__":
    main()
