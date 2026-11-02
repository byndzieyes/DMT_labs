import json
import random
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
STUDENT_NUMBER = 5
RANDOM_SEED = 5
ORDERS = ((2, 1, 3, 4), (4, 1, 2, 3))


def generate_data(number=STUDENT_NUMBER, seed=RANDOM_SEED):
    rng = random.Random(seed)
    return [[rng.randint(0, 5) for _ in range(4)] for _ in range(number + 3)]


def optimize(points, order, concessions=None):
    if not points or any(len(p) != 4 for p in points):
        raise ValueError('Таблиця має бути непорожньою та містити чотири критерії')
    if sorted(order) != [1, 2, 3, 4]:
        raise ValueError('Порядок має містити номери критеріїв від 1 до 4 без повторів')
    concessions = [0, 0, 0] if concessions is None else list(concessions)
    if len(concessions) != 3 or any(d < 0 for d in concessions):
        raise ValueError('Потрібно задати три невід’ємні поступки')
    candidates = list(range(len(points)))
    steps = []
    for step, criterion in enumerate(order):
        index = criterion - 1
        before = candidates[:]
        best = max(points[i][index] for i in before)
        delta = concessions[step] if step < 3 else 0
        threshold = best - delta
        candidates = [i for i in before if points[i][index] >= threshold]
        steps.append(dict(criterion=criterion, before=before, best=best,
                          concession=delta, threshold=threshold,
                          remaining=candidates[:]))
    return dict(winners=candidates, steps=steps)


def names(indices):
    return ', '.join(f'A{i+1}' for i in indices)


def order_name(order):
    return ' > '.join(f'Q{i}' for i in order)


def markdown(points, results):
    headers = ' | '.join(f'A{i+1}' for i in range(len(points)))
    separator = '|' + '---|' * (len(points) + 1)
    scores = '\n'.join(
        f"| Q{j+1} | {' | '.join(str(p[j]) for p in points)} |"
        for j in range(4)
    )
    sections = []
    for label, result in results.items():
        steps = '\n'.join(
            f"| {k} | Q{s['criterion']} | {names(s['before'])} | "
            f"{s['best']} | {s['concession']} | {s['threshold']} | "
            f"{names(s['remaining'])} |"
            for k, s in enumerate(result['steps'], 1)
        )
        sections.append(f"""### {label}

| Крок | Критерій | До кроку | Максимум | Поступка | Поріг | Залишилось |
|---|---|---|---|---|---|---|
{steps}

**Результат: {names(result['winners'])}**""")
    methods = '\n\n'.join(sections)
    return f"""# Лабораторна робота №8

## Лексикографічний метод та метод послідовних поступок

Номер у журналі N = {STUDENT_NUMBER}. Альтернатив: N + 3 = {len(points)}. Критеріїв: 4.
Цілі оцінки від 0 до 5 включно; зерно генератора {RANDOM_SEED}.
Усі критерії максимізуються. Номери критеріїв задаються від 1 до 4.
Індекси альтернатив у JSON починаються з нуля.

| Критерій | {headers} |
{separator}
{scores}

{methods}
"""


def main():
    points = generate_data()
    results = {f'Лексикографічний метод {order_name(o)}': optimize(points, o)
               for o in ORDERS}
    results['Послідовні поступки Q1 > Q2 > Q3 > Q4'] = optimize(
        points, (1, 2, 3, 4), (1, 2, 3))
    data = dict(student_number=STUDENT_NUMBER, seed=RANDOM_SEED, scores=points,
                lexicographic_orders=ORDERS,
                concession_order=[1, 2, 3, 4], concessions=[1, 2, 3])
    for filename, value in [('data.json', data), ('results.json', results)]:
        (LAB_DIR / filename).write_text(json.dumps(value, ensure_ascii=False,
                                                  indent=2), encoding='utf-8')
    (LAB_DIR / 'README.md').write_text(markdown(points, results), encoding='utf-8')
    for label, result in results.items():
        print(f"{label}: {names(result['winners'])}")


if __name__ == '__main__':
    main()
