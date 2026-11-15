import json
import math
from fractions import Fraction
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
RI = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12,
      6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}


def comparison_matrix(upper, n):
    """Доповнюємо верхню частину матриці оберненими оцінками."""
    matrix = [[1.0 for _ in range(n)] for _ in range(n)]
    for i, row in enumerate(upper):
        for j, raw in enumerate(row, i+1):
            value = Fraction(str(raw))
            matrix[i][j] = float(value)
            matrix[j][i] = float(1/value)
    return matrix


def analyze(matrix, threshold=0.1):
    n = len(matrix)
    products = [math.prod(row) for row in matrix]
    geometric = [p ** (1/n) for p in products]
    total = sum(geometric)
    weights = [g/total for g in geometric]
    aw = [sum(a*w for a, w in zip(row, weights)) for row in matrix]
    ratios = [v/w for v, w in zip(aw, weights)]
    lam = sum(ratios)/n
    ci = max(0.0, (lam-n)/(n-1)) if n > 1 else 0.0
    cr = ci/RI[n] if RI[n] else None
    return dict(matrix=matrix, products=products, geometric=geometric,
                geometric_sum=total, weights=weights, aw=aw, ratios=ratios,
                lambda_max=lam, ci=ci, ri=RI[n], cr=cr,
                acceptable=cr is None or cr <= threshold)


def solve(data):
    criteria, alternatives = data['criteria'], data['alternatives']
    m, n = len(criteria), len(alternatives)
    threshold = float(data['threshold'])
    criteria_result = analyze(comparison_matrix(data['criteria_upper'], m), threshold)
    local = [analyze(comparison_matrix(u, n), threshold) for u in data['alternative_upper']]
    x = [[r['weights'][i] for r in local] for i in range(n)]
    contributions = [[v*w for v, w in zip(row, criteria_result['weights'])] for row in x]
    scores = [sum(row) for row in contributions]
    ranking = sorted(range(n), key=lambda i: (-scores[i], i))
    return dict(criteria=criteria_result, local=local, x=x, contributions=contributions,
                scores=scores, ranking=ranking,
                all_consistent=all(r['acceptable'] for r in [criteria_result, *local]))


def number(value):
    return f'{value:.6f}'


def judgment(value):
    return str(Fraction(value).limit_denominator(9))


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |',
                      '|' + '---|'*len(headers),
                      *['| ' + ' | '.join(map(str, row)) + ' |' for row in rows]])


def matrix_section(title, labels, r, threshold):
    n = len(labels)
    matrix_table = table(['Елемент', *labels], [
        [label, *map(judgment, row)] for label, row in zip(labels, r['matrix'])])
    calculations = ''
    aw_calculations = ''
    for i, label in enumerate(labels):
        factors = ' × '.join(map(judgment, r['matrix'][i]))
        calculations += (f'- {label}: P = {factors} = {number(r["products"][i])}; '
                         f'g = ({number(r["products"][i])})^(1/{n}) '
                         f'= {number(r["geometric"][i])}.\n')
        terms = ' + '.join(f'{judgment(a)} × {number(w)}'
                           for a, w in zip(r['matrix'][i], r['weights']))
        aw_calculations += f'- (Aw) для {label} = {terms} = {number(r["aw"][i])}.\n'

    weights_table = table(['Елемент', 'gᵢ', 'wᵢ = gᵢ / Σg'], [
        [label, number(g), f'{number(g)} / {number(r["geometric_sum"])} = {number(w)}']
        for label, g, w in zip(labels, r['geometric'], r['weights'])])
    consistency_table = table(['Елемент', '(Aw)ᵢ', 'wᵢ', 'λᵢ = (Aw)ᵢ / wᵢ'], [
        [label, number(a), number(w), number(l)]
        for label, a, w, l in zip(labels, r['aw'], r['weights'], r['ratios'])])
    status = 'прийнятна' if r['acceptable'] else 'неприйнятна'

    return f'''## {title}

{matrix_table}

### Обчислення локальних пріоритетів

Pᵢ = ∏aᵢⱼ; gᵢ = Pᵢ^(1/n); wᵢ = gᵢ / Σg.

{calculations}
Σg = {' + '.join(map(number, r['geometric']))} = {number(r['geometric_sum'])}.

{weights_table}

Σw = {number(sum(r['weights']))}.

### Перевірка узгодженості

{aw_calculations}
{consistency_table}

λmax ≈ ({' + '.join(map(number, r['ratios']))}) / {n} = {number(r['lambda_max'])}.

CI = ({number(r['lambda_max'])} − {n}) / ({n} − 1) = {number(r['ci'])}.

RI({n}) = {r['ri']:.2f}.

CR = {number(r['ci'])} / {r['ri']:.2f} = {number(r['cr'])}.

**Узгодженість {status}; поріг CR = {threshold:.2f}.**

'''


def markdown(data, result):
    criteria, alternatives = data['criteria'], data['alternatives']
    qlabels = [f'Q{i+1}' for i in range(len(criteria))]
    alabels = [f'A{i+1}' for i in range(len(alternatives))]
    phones_table = table(['Альтернатива', 'Профіль'], zip(alternatives, data['profiles']))
    criteria_table = table(['Критерій', 'Напрям переваги'],
                           [[c, 'Більше — краще'] for c in criteria])
    hierarchy = 'Обрати телефон\n'
    for j, criterion in enumerate(criteria):
        last_criterion = j == len(criteria)-1
        hierarchy += ('└── ' if last_criterion else '├── ') + criterion + '\n'
        indent = '    ' if last_criterion else '│   '
        for i, alternative in enumerate(alternatives):
            branch = '└── ' if i == len(alternatives)-1 else '├── '
            hierarchy += indent + branch + alternative + '\n'

    sections = matrix_section('Матриця порівнянь критеріїв', qlabels,
                              result['criteria'], data['threshold'])
    for criterion, r in zip(criteria, result['local']):
        sections += matrix_section(f'Альтернативи за критерієм {criterion}',
                                   alabels, r, data['threshold'])

    consistency_table = table(['Матриця', 'λmax (оцінка)', 'CI', 'RI', 'CR', 'Прийнятна'], [
        [label, number(r['lambda_max']), number(r['ci']), number(r['ri']),
         number(r['cr']), 'Так' if r['acceptable'] else 'Ні']
        for label, r in zip(['Критерії', *criteria], [result['criteria'], *result['local']])])
    local_table = table(['Телефон', *qlabels], [
        [a, *map(number, row)] for a, row in zip(alternatives, result['x'])])
    q = result['criteria']['weights']
    global_calculations = ''
    for i, a in enumerate(alternatives):
        terms = ' + '.join(f'{number(x)} × {number(w)}' for x, w in zip(result['x'][i], q))
        contributions = ' + '.join(map(number, result['contributions'][i]))
        global_calculations += f'''**{a}:**

s{i+1} = {terms}

= {contributions} = **{number(result['scores'][i])}**.

'''
    contributions_table = table(['Телефон', *qlabels, 'Сума sᵢ'], [
        [a, *map(number, row), number(s)]
        for a, row, s in zip(alternatives, result['contributions'], result['scores'])])
    ranking_table = table(['Місце', 'Телефон', 'Глобальний пріоритет'], [
        [rank, alternatives[i], number(result['scores'][i])]
        for rank, i in enumerate(result['ranking'], 1)])
    winner, second = result['ranking'][:2]
    order = ' > '.join(alternatives[i] for i in result['ranking'])
    strongest = sorted(range(len(criteria)), key=lambda j: -result['contributions'][winner][j])[:2]
    explanation = '; '.join(f'{criteria[j]} — {number(result["contributions"][winner][j])}'
                            for j in strongest)
    consistency = ('Усі шість матриць задовольняють обраний поріг CR.' if result['all_consistent']
                   else 'Є неузгоджені матриці: рейтинг попередній, судження слід переглянути.')

    return f'''# Лабораторна робота №9

Прийняття рішень за умов багатокритерійності методом аналітичної ієрархії.

## Постановка задачі

{data['goal']}.

{phones_table}

{criteria_table}

Для Q1 оцінюється доступність: дешевший телефон отримує більшу перевагу.
Для Q5 оцінюється бажаність тривалої підтримки оновлень.

## Ієрархія задачі

```text
{hierarchy}```

Три рівні: мета → п’ять критеріїв → п’ять альтернатив.
Кожна альтернатива оцінюється за кожним критерієм.

## Вхідні експертні судження

Елемент aᵢⱼ показує перевагу елемента рядка над елементом стовпця.
Використано шкалу Сааті 1–9 та обернені оцінки.
У data.json задано верхні частини матриць; aⱼᵢ = 1/aᵢⱼ, aᵢᵢ = 1.

Продуктивність та автономність однаково важливі; кожна вдвічі важливіша за доступність ціни.
Підтримка оновлень рівноцінна доступності ціни. Камера має найменшу вагу.
Budget виграє за доступністю, Power — за продуктивністю, Photo — за камерою,
Endurance — за автономністю, Balance — за підтримкою. Силу переваг задають матриці нижче.

Використано нормалізовані середні геометричні — наближення головного власного вектора.
λmax оцінюється як середнє (Aw)ᵢ/wᵢ. Проміжні значення не округлюються;
у звіті показано шість знаків. Поріг узгодженості CR ≤ {data['threshold']:.2f}.

{sections}## Зведена перевірка узгодженості

{consistency_table}

## Матриця локальних пріоритетів X

Рядки відповідають телефонам, стовпці — критеріям. Сума кожного стовпця дорівнює 1.

{local_table}

Вектор ваг критеріїв q = ({'; '.join(map(number, q))}).

## Обчислення глобальних пріоритетів

s = Xq; sᵢ = Σⱼ xᵢⱼqⱼ.

{global_calculations}### Внески критеріїв у загальні оцінки

{contributions_table}

Сума глобальних пріоритетів = {number(sum(result['scores']))}.

## Ранжування альтернатив

{ranking_table}
'''


def main():
    data = json.loads((LAB_DIR / 'data.json').read_text(encoding='utf-8'))
    result = solve(data)
    (LAB_DIR / 'README.md').write_text(markdown(data, result), encoding='utf-8')
    (LAB_DIR / 'results.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    for rank, i in enumerate(result['ranking'], 1):
        print(f'{rank}. {data["alternatives"][i]}: {result["scores"][i]:.6f}')
    print('CR:', ', '.join(f'{r["cr"]:.6f}' for r in [result['criteria'], *result['local']]))
    print('Звіт:', LAB_DIR / 'README.md')


if __name__ == '__main__':
    main()
