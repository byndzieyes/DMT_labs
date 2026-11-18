from itertools import product
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parent


def morra_payoff(first, second):
    shown_first, guess_first = first
    shown_second, guess_second = second
    first_correct = guess_first == shown_second
    second_correct = guess_second == shown_first
    if first_correct == second_correct:
        return 0
    total = shown_first + shown_second
    return total if first_correct else -total


def create_games():
    strategies = list(product(range(1, 4), repeat=2))
    morra_labels = [f'({shown}, {guess})' for shown, guess in strategies]
    directions = ['Ліворуч', 'Центр', 'Праворуч']
    piles = [1, 2]
    return [
        {
            'name': 'Трипальцева гра Морра',
            'rules': (
                'Кожен гравець одночасно показує 1, 2 або 3 пальці та вгадує, '
                'скільки пальців покаже суперник. Стратегія (s, g): '
                's — показане число, g — припущення про число суперника. '
                'Кожен має 3 × 3 = 9 чистих стратегій.\n\n'
                'Якщо вгадав лише перший, його виграш дорівнює сумі показаних '
                'обома пальців; якщо лише другий — від’ємній сумі. '
                'Якщо вгадали обидва або жоден — нічия, виграш 0. '
                'Наприклад, (1, 2) проти (2, 3) дає першому +3, '
                'а (1, 2) проти (2, 1) дає 0.'
            ),
            'rows': morra_labels,
            'columns': morra_labels,
            'matrix': [[morra_payoff(a, b) for b in strategies] for a in strategies],
        },
        {
            'name': 'Власна гра 1. Пенальті',
            'rules': (
                'Перший гравець — нападник, другий — воротар. Нападник обирає '
                'напрямок удару, а воротар незалежно обирає напрямок захисту: '
                'ліворуч, по центру або праворуч. Напрямки задано в одній '
                'спільній системі відліку.\n\n'
                'Якщо напрямки збігаються, воротар відбиває м’яч: виграш '
                'нападника −1. Інакше забито гол: виграш нападника +1. '
                'Виграш воротаря має протилежний знак.'
            ),
            'rows': directions,
            'columns': directions,
            'matrix': [[-1 if a == b else 1 for b in directions] for a in directions],
        },
        {
            'name': 'Власна гра 2. Вибір купки',
            'rules': (
                'На столі дві купки: 1 та 2 монети. Гравці одночасно обирають '
                'по одній купці. Якщо обрали різні, кожен забирає свою. '
                'Якщо одну й ту саму — ніхто нічого не отримує.\n\n'
                'Виграш першого визначаємо як кількість отриманих ним монет '
                'мінус кількість монет другого. Виграш другого — протилежна '
                'різниця. Це відносний результат, а не кількість забраних монет. '
                'Наприклад, вибір 1 проти 2 дає першому 1 − 2 = −1.'
            ),
            'rows': ['1 монета', '2 монети'],
            'columns': ['1 монета', '2 монети'],
            'matrix': [[0 if a == b else a - b for b in piles] for a in piles],
        },
    ]


def solve(matrix):
    row_minima = [min(row) for row in matrix]
    column_maxima = [max(column) for column in zip(*matrix)]
    lower = max(row_minima)
    upper = min(column_maxima)
    saddle_points = [
        (i, j)
        for i, row in enumerate(matrix)
        for j, value in enumerate(row)
        if value == row_minima[i] == column_maxima[j]
    ]
    return row_minima, column_maxima, lower, upper, saddle_points


def describe_game(game):
    minima, maxima, lower, upper, points = solve(game['matrix'])
    headers = ['Перший / Другий', *game['columns'], 'Мінімум рядка']
    lines = [f"## {game['name']}", '', game['rules'], '', '### Матриця виграшів', '',
             '| ' + ' | '.join(headers) + ' |',
             '| ' + ' | '.join(['---'] * len(headers)) + ' |']
    for label, row, minimum in zip(game['rows'], game['matrix'], minima):
        lines.append('| ' + ' | '.join(map(str, [label, *row, minimum])) + ' |')
    lines.append('| Максимум стовпця | ' + ' | '.join(map(str, maxima)) + ' | — |')
    lines.extend([
        '', '### Пошук сідлових точок', '',
        f"Мінімуми рядків: {', '.join(map(str, minima))}.", '',
        f'Нижня ціна гри: α = max(мінімуми рядків) = **{lower}**.', '',
        f"Максимуми стовпців: {', '.join(map(str, maxima))}.", '',
        f'Верхня ціна гри: β = min(максимуми стовпців) = **{upper}**.', '',
    ])
    if points:
        lines.extend([f'**α = β = {lower}: сідлова точка існує.**', ''])
        for i, j in points:
            lines.append(
                f'- Клітинка ({i + 1}, {j + 1}): перший обирає '
                f"«{game['rows'][i]}», другий — «{game['columns'][j]}». "
                f'Виграш першого {lower}, другого {-lower}.'
            )
        lines.extend(['', f'Ціна гри v = {lower}. Зазначені пари стратегій '
                      'утворюють рівновагу: жодному гравцю невигідно '
                      'одноосібно змінювати свій вибір.'])
    else:
        lines.append('**α < β: сідлової точки немає. Рівновага в чистих '
                     'стратегіях відсутня.** Ціну гри у змішаних стратегіях '
                     'ця програма не обчислює.')
    return '\n'.join(lines)


def main():
    games = create_games()
    introduction = '''# Лабораторна робота №10

Матричні ігри, сідлова точка. Варіант 5.

## Принцип розрахунку

Рядки — чисті стратегії першого гравця, стовпці — другого.
Кожна клітинка містить виграш першого; виграш другого має протилежний знак.
Перший максимізує цей виграш, другий мінімізує.

α = maxᵢ minⱼ hᵢⱼ; β = minⱼ maxᵢ hᵢⱼ.
Сідлова точка одночасно мінімальна у своєму рядку та максимальна у своєму
стовпці. Вона існує тоді й лише тоді, коли α = β.
Номери клітинок у результатах починаються з 1.
'''
    report = introduction + '\n\n' + '\n\n'.join(map(describe_game, games)) + '\n'
    output = LAB_DIR / 'README.md'
    output.write_text(report, encoding='utf-8')
    for game in games:
        _, _, lower, upper, points = solve(game['matrix'])
        print(f"{game['name']}: α = {lower}, β = {upper}; "
              f"сідлових точок: {len(points)}.")
    print('Результати:', output)


if __name__ == '__main__':
    main()
