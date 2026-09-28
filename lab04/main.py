import math
import random
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


SAMPLE_SIZE = 3000
STUDENT_NUMBER = 5
RANDOM_SEED = 5
LAB_DIR = Path(__file__).resolve().parent
REPORT = LAB_DIR / "README.md"
PLOT = LAB_DIR / "plots" / "frequency.png"


def generate_sample(number: int, seed: int) -> list[int]:
    rng = random.Random(seed)
    return [rng.randint(1, 5 * number) for _ in range(SAMPLE_SIZE)]


def calculate_means(sample: list[int]) -> dict[str, float | list[int]]:
    if not sample or any(x <= 0 for x in sample):
        raise ValueError("Вибірка має містити додатні числа.")
    n = len(sample)
    ordered = sorted(sample)
    frequencies = Counter(sample)
    max_frequency = max(frequencies.values())
    modes = sorted(x for x, frequency in frequencies.items() if frequency == max_frequency)
    median = (
        float(ordered[n // 2]) if n % 2
        else (ordered[n // 2 - 1] + ordered[n // 2]) / 2
    )
    return {
        "arithmetic": math.fsum(sample) / n,
        "modes": modes,
        "median": median,
        "quadratic": math.sqrt(math.fsum(x * x for x in sample) / n),
        "geometric": math.exp(math.fsum(math.log(x) for x in sample) / n),
        "harmonic": n / math.fsum(1 / x for x in sample),
    }


def save_plot(sample: list[int], maximum: int) -> None:
    frequencies = Counter(sample)
    values = range(1, maximum + 1)
    PLOT.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(max(10, min(18, maximum * 0.32)), 5))
    axis.bar(values, [frequencies.get(x, 0) for x in values], color="#3b82f6")
    axis.set(xlabel="Значення числа", ylabel="Частота появи", title="Частоти значень у вибірці")
    axis.set_xlim(0.5, maximum + 0.5)
    if maximum <= 40:
        axis.set_xticks(list(values))
    axis.grid(axis="y", alpha=0.25)
    axis.set_axisbelow(True)
    figure.tight_layout()
    figure.savefig(PLOT, dpi=180)
    plt.close(figure)


def format_sample(sample: list[int]) -> str:
    return "\n".join(
        " ".join(map(str, sample[i:i + 30])) for i in range(0, len(sample), 30)
    )


def build_report(sample: list[int], number: int, seed: int) -> str:
    maximum = 5 * number
    frequencies = Counter(sample)
    means = calculate_means(sample)
    modes = means["modes"]
    assert isinstance(modes, list)
    mode_text = ", ".join(map(str, modes))
    frequency_rows = "\n".join(
        f"| {x} | {frequencies.get(x, 0)} |" for x in range(1, maximum + 1)
    )
    return f"""# Лабораторна робота №4

## Методи обчислення середніх величин

**Номер у журналі:** {number}  
**Обсяг вибірки:** {len(sample)} чисел  
**Діапазон генерації:** від 1 до {maximum} включно  
**Зерно генератора:** {seed} (для повторення результату)

## Частоти значень

![Графік частот](plots/frequency.png)

| Значення числа | Частота появи |
|---:|---:|
{frequency_rows}

## Середні величини

| Показник | Значення |
|---|---:|
| Середнє арифметичне | {means['arithmetic']:.6f} |
| Мода | {mode_text} |
| Медіана | {means['median']:.6f} |
| Середнє квадратичне | {means['quadratic']:.6f} |
| Середнє геометричне | {means['geometric']:.6f} |
| Середнє гармонічне | {means['harmonic']:.6f} |

Медіана для парної вибірки — середнє двох центральних чисел відсортованого ряду. Якщо в рядку моди кілька чисел, вони мають однакову найбільшу частоту.

## Згенерована вибірка

<details>
<summary>Показати всі {len(sample)} чисел у порядку генерації</summary>

```text
{format_sample(sample)}
```

</details>

## Проранжована вибірка

<details>
<summary>Показати всі {len(sample)} чисел за зростанням</summary>

```text
{format_sample(sorted(sample))}
```

</details>

## Висновки

Для вибірки з {len(sample)} цілих чисел від 1 до {maximum} обчислено шість показників центру. Середнє арифметичне ({means['arithmetic']:.3f}) і медіана ({means['median']:.3f}) описують центр вибірки різними способами; мода ({mode_text}) показує найчастіше значення. Для додатних чисел справджується співвідношення: гармонічне ≤ геометричне ≤ арифметичне ≤ квадратичне. Отримано {means['harmonic']:.3f} ≤ {means['geometric']:.3f} ≤ {means['arithmetic']:.3f} ≤ {means['quadratic']:.3f}.
"""


def main() -> None:
    sample = generate_sample(STUDENT_NUMBER, RANDOM_SEED)
    save_plot(sample, 5 * STUDENT_NUMBER)
    REPORT.write_text(build_report(sample, STUDENT_NUMBER, RANDOM_SEED), encoding="utf-8")
    print(f"Звіт: {REPORT}")
    print(f"Графік: {PLOT}")


if __name__ == "__main__":
    main()
