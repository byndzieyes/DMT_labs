def format_md_table(title: str, matrix: list[list[int]], elements: list[str]) -> str:
    """Генерує фрагмент Markdown-таблиці для заданої матриці"""
    lines = [f"### {title}\n", "|   | " + " | ".join(elements) + " |", "|:---:|" + ":---:|"*len(elements)]
    for i, row in enumerate(matrix):
        row_str = " | ".join(map(str, row))
        lines.append(f"| **{elements[i]}** | {row_str} |")
    return "\n".join(lines) + "\n\n"

# Базова множина для Варіанта 5
elements = ['В', 'З', 'Л', 'О']
n = len(elements)

# Температурний ранг (З < В = О < Л)
temp_rank = {'З': 1, 'В': 2, 'О': 2, 'Л': 3}

# 1. Побудова матриць P та Q
P = [[1 if temp_rank[x] >= temp_rank[y] else 0 for y in elements] for x in elements]
Q = [[1 if temp_rank[x] == temp_rank[y] else 0 for y in elements] for x in elements]

# 2. Області визначення та значень
dom_P = [elements[i] for i in range(n) if any(P[i][j] == 1 for j in range(n))]
rng_P = [elements[j] for j in range(n) if any(P[i][j] == 1 for i in range(n))]

dom_Q = [elements[i] for i in range(n) if any(Q[i][j] == 1 for j in range(n))]
rng_Q = [elements[j] for j in range(n) if any(Q[i][j] == 1 for i in range(n))]

# 3. Операції над відношеннями
intersection = [[P[i][j] & Q[i][j] for j in range(n)] for i in range(n)]
union        = [[P[i][j] | Q[i][j] for j in range(n)] for i in range(n)]
difference   = [[1 if (P[i][j] == 1 and Q[i][j] == 0) else 0 for j in range(n)] for i in range(n)]
sym_diff     = [[P[i][j] ^ Q[i][j] for j in range(n)] for i in range(n)]
complement_P = [[1 - P[i][j] for j in range(n)] for i in range(n)]
inverse_P    = [[P[j][i] for j in range(n)] for i in range(n)]
composition  = [[1 if any(P[i][k] & Q[k][j] for k in range(n)) else 0 for j in range(n)] for i in range(n)]

# 4. Формування вмісту Markdown
md_content = []
md_content.append("# Лабораторна робота №2\n")
md_content.append("## Тема: Бінарні відношення та основні операції над ними\n")
md_content.append(f"**Варіант:** 5  \n**Множина носія:** `{{{', '.join(elements)}}}`  \n**Температурна шкала:** З < В = О < Л\n\n")

md_content.append("## Області визначення та значень\n")
md_content.append(f"* **Відношення P («не холодніше ніж»):**\n  * $\\delta_P = \\{{{', '.join(dom_P)}\\}}$\n  * $\\rho_P = \\{{{', '.join(rng_P)}\\}}$\n")
md_content.append(f"* **Відношення Q («так само як»):**\n  * $\\delta_Q = \\{{{', '.join(dom_Q)}\\}}$\n  * $\\rho_Q = \\{{{', '.join(rng_Q)}\\}}$\n\n")

md_content.append("## Матриці початкових відношень\n")
md_content.append(format_md_table("Матриця відношення P («не холодніше ніж»)", P, elements))
md_content.append(format_md_table("Матриця відношення Q («так само як»)", Q, elements))

md_content.append("## Результати операцій над відношеннями\n")
md_content.append(format_md_table("1. Перетин ($P \\cap Q$)", intersection, elements))
md_content.append(format_md_table("2. Об'єднання ($P \\cup Q$)", union, elements))
md_content.append(format_md_table("3. Різниця ($P \\setminus Q$)", difference, elements))
md_content.append(format_md_table("4. Симетрична різниця ($P \\Delta Q$)", sym_diff, elements))
md_content.append(format_md_table("5. Доповнення ($\\overline{P}$)", complement_P, elements))
md_content.append(format_md_table("6. Обернене відношення ($P^{-1}$)", inverse_P, elements))
md_content.append(format_md_table("7. Композиція ($P \\circ Q$)", composition, elements))

# 5. Запис у файл
output_filename = "README.md"
with open(output_filename, "w", encoding="utf-8") as f:
    f.writelines(md_content)

print(f"Звіт успішно згенеровано та збережено у файл: {output_filename}")