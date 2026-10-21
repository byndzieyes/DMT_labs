import json
import random
from pathlib import Path


STUDENT_NUMBER = 5
RANDOM_SEED = 5
CRITERION_COUNT = 5
LAB_DIR = Path(__file__).resolve().parent
DATA_FILE = LAB_DIR / "data.json"
REPORT_FILE = LAB_DIR / "README.md"


def generate_data(student_number: int, seed: int) -> dict:
    if student_number < 1:
        raise ValueError("Номер у журналі має бути додатним.")

    rng = random.Random(seed)
    alternative_count = 3 + student_number
    evaluations = [
        [rng.randint(1, alternative_count) for _ in range(CRITERION_COUNT)]
        for _ in range(alternative_count)
    ]
    norms = [rng.randint(1, alternative_count) for _ in range(CRITERION_COUNT)]

    raw_weights = [rng.random() + 0.01 for _ in range(CRITERION_COUNT)]
    weight_total = sum(raw_weights)
    weights = [weight / weight_total for weight in raw_weights]

    return {
        "student_number": student_number,
        "seed": seed,
        "criterion_count": CRITERION_COUNT,
        "alternatives": [f"A{i + 1}" for i in range(alternative_count)],
        "evaluations": evaluations,
        "norms": norms,
        "weights": weights,
    }


def normalize_criteria(evaluations: list[list[int]]) -> list[list[float]]:
    criterion_count = len(evaluations[0])
    minima = [min(row[j] for row in evaluations) for j in range(criterion_count)]
    maxima = [max(row[j] for row in evaluations) for j in range(criterion_count)]
    normalized = []

    for row in evaluations:
        normalized_row = []
        for j, value in enumerate(row):
            span = maxima[j] - minima[j]
            normalized_row.append((value - minima[j]) / span if span else 0.0)
        normalized.append(normalized_row)
    return normalized


def find_winners(scores: list[float], maximize: bool = True) -> list[int]:
    best = max(scores) if maximize else min(scores)
    return [i for i, score in enumerate(scores) if abs(score - best) <= 1e-12]


def calculate_results(data: dict) -> dict:
    evaluations = data["evaluations"]
    norms = data["norms"]
    weights = data["weights"]
    normalized = normalize_criteria(evaluations)

    linear = [
        sum(weights[j] * row[j] for j in range(len(weights)))
        for row in evaluations
    ]
    maximin = [
        min(row[j] / norms[j] for j in range(len(norms)))
        for row in evaluations
    ]
    normalized_linear = [
        sum(weights[j] * row[j] for j in range(len(weights)))
        for row in normalized
    ]
    normalized_maximin = [
        min(weights[j] * row[j] for j in range(len(weights)))
        for row in normalized
    ]

    return {
        "normalized": normalized,
        "linear": linear,
        "maximin": maximin,
        "normalized_linear": normalized_linear,
        "normalized_maximin": normalized_maximin,
        "winners": {
            "linear": find_winners(linear),
            "maximin": find_winners(maximin),
            "normalized_linear": find_winners(normalized_linear),
            "normalized_maximin": find_winners(normalized_maximin),
        },
    }


def winner_names(data: dict, result: dict, key: str) -> str:
    return ", ".join(data["alternatives"][i] for i in result["winners"][key])


def build_report(data: dict, result: dict) -> str:
    alternatives = data["alternatives"]
    evaluation_rows = "\n".join(
        f"| {name} | " + " | ".join(map(str, values)) + " |"
        for name, values in zip(alternatives, data["evaluations"])
    )
    normalized_rows = "\n".join(
        f"| {name} | " + " | ".join(f"{value:.3f}" for value in values) + " |"
        for name, values in zip(alternatives, result["normalized"])
    )
    score_rows = "\n".join(
        "| {name} | {linear:.4f} | {maximin:.4f} | {normalized_linear:.4f} | "
        "{normalized_maximin:.4f} |".format(
            name=name,
            linear=result["linear"][i],
            maximin=result["maximin"][i],
            normalized_linear=result["normalized_linear"][i],
            normalized_maximin=result["normalized_maximin"][i],
        )
        for i, name in enumerate(alternatives)
    )
    weight_cells = " | ".join(f"{weight:.4f}" for weight in data["weights"])
    norm_cells = " | ".join(map(str, data["norms"]))
    criterion_headers = " | ".join(
        f"Q{i + 1}" for i in range(data["criterion_count"])
    )
    criterion_separator = "---:|" * data["criterion_count"]

    return f"""# Лабораторна робота №6

## Лінійна та максимінна згортка

**Номер у журналі:** {data['student_number']}  
**Кількість альтернатив:** {len(alternatives)} (= 3 + N)  
**Кількість критеріїв:** {data['criterion_count']}  
**Діапазон генерації оцінок і нормативів:** від 1 до {len(alternatives)} включно  
**Зерно генератора:** {data['seed']} (для повторення результату)

### Вагові коефіцієнти та нормативи

| Параметр | {criterion_headers} |
|---|{criterion_separator}
| Нормативне значення Q* | {norm_cells} |
| Вага λ | {weight_cells} |

Сума ваг: **{sum(data['weights']):.6f}**. Усі ваги додатні.

### Початкові оцінки альтернатив

| Альтернатива | {criterion_headers} |
|:---:|{criterion_separator}
{evaluation_rows}

### Нормовані оцінки

Для кожного критерію застосовано перетворення (Qᵢ − Qᵢ,min) / (Qᵢ,max − Qᵢ,min), тому значення лежать у межах [0, 1]. Якщо оцінки за критерієм однакові в усіх альтернатив, його нормовані значення приймаються рівними 0.

| Альтернатива | {criterion_headers} |
|:---:|{criterion_separator}
{normalized_rows}

### Значення критеріїв згортання

| Альтернатива | Лінійне | Максимінне | Нормоване лінійне | Нормоване максимінне |
|:---:|---:|---:|---:|---:|
{score_rows}

Лінійна оцінка: Σ λᵢQᵢ. Максимінна оцінка за прикладом методички: min(Qᵢ / Qᵢ*). Нормована лінійна оцінка: Σ λᵢQᵢ,norm. Нормована максимінна оцінка: min(λᵢQᵢ,norm). Для всіх методів вибирається альтернатива з найбільшим значенням; у разі рівності наведено всі оптимальні альтернативи.

### Оптимальні альтернативи

| Метод | Оптимальна альтернатива (альтернативи) |
|---|---|
| Лінійне згортання | **{winner_names(data, result, 'linear')}** |
| Максимінне згортання | **{winner_names(data, result, 'maximin')}** |
| Нормоване лінійне згортання | **{winner_names(data, result, 'normalized_linear')}** |
| Нормоване максимінне згортання | **{winner_names(data, result, 'normalized_maximin')}** |
"""


def main() -> None:
    data = generate_data(STUDENT_NUMBER, RANDOM_SEED)
    result = calculate_results(data)
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_FILE.write_text(build_report(data, result), encoding="utf-8")

    print(f"Результат збережено: {REPORT_FILE}")
    for key, label in (
        ("linear", "Лінійне згортання"),
        ("maximin", "Максимінне згортання"),
        ("normalized_linear", "Нормоване лінійне згортання"),
        ("normalized_maximin", "Нормоване максимінне згортання"),
    ):
        print(f"{label}: {winner_names(data, result, key)}")


if __name__ == "__main__":
    main()
