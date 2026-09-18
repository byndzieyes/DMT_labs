from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


MATRIX = np.array(
    [
        [0, 0, 1, 0],
        [1, 1, 0, 0],
        [0, 0, 1, 1],
        [1, 0, 0, 1],
    ],
    dtype=int,
)

OUTPUT_DIRECTORY = Path("plots")
REPORT_FILE = Path("README.md")


def validate_matrix(matrix: np.ndarray) -> None:
    """Перевіряє правильність матриці бінарного відношення."""
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Матриця відношення повинна бути квадратною.")
    if not np.isin(matrix, [0, 1]).all():
        raise ValueError("Матриця відношення повинна містити тільки 0 та 1.")


def boolean_product(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Виконує булеве множення двох матриць відношень."""
    return ((left @ right) > 0).astype(int)


def transitive_closure(matrix: np.ndarray) -> tuple[np.ndarray, list[np.ndarray]]:
    """Обчислює P ∪ P² ∪ ... до стабілізації транзитивного замикання."""
    closure = matrix.copy()
    current_power = matrix.copy()
    powers = [matrix.copy()]

    while True:
        next_power = boolean_product(current_power, matrix)
        powers.append(next_power.copy())
        expanded_closure = np.logical_or(closure, next_power).astype(int)

        if np.array_equal(expanded_closure, closure):
            break

        closure = expanded_closure
        current_power = next_power

    return closure, powers


def find_equivalence_classes(mutual_reachability: np.ndarray) -> list[list[int]]:
    """Знаходить класи еквівалентності за взаємною досяжністю."""
    unused_vertices = set(range(len(mutual_reachability)))
    classes: list[list[int]] = []

    while unused_vertices:
        representative = min(unused_vertices)
        current_class = [
            vertex
            for vertex in sorted(unused_vertices)
            if mutual_reachability[representative, vertex] == 1
        ]
        classes.append(current_class)
        unused_vertices.difference_update(current_class)

    return classes


def build_factor_matrix(matrix: np.ndarray, classes: list[list[int]]) -> np.ndarray:
    """Будує матрицю відношення між класами еквівалентності."""
    factor_matrix = np.zeros((len(classes), len(classes)), dtype=int)

    for source_index, source_class in enumerate(classes):
        for target_index, target_class in enumerate(classes):
            if any(matrix[source, target] for source in source_class for target in target_class):
                factor_matrix[source_index, target_index] = 1

    return factor_matrix


def matrix_to_markdown(title: str, matrix: np.ndarray, labels: list[str]) -> str:
    """Перетворює матрицю на підписану Markdown-таблицю."""
    lines = [f"## {title}", ""]
    lines.append("|   | " + " | ".join(labels) + " |")
    lines.append("|:---:|" + ":---:|" * len(labels))

    for label, row in zip(labels, matrix):
        lines.append(f"| **{label}** | " + " | ".join(map(str, row)) + " |")

    return "\n".join(lines)


def matrix_to_graph(matrix: np.ndarray, labels: list[str]) -> nx.DiGraph:
    """Перетворює матрицю відношення на орієнтований граф."""
    graph = nx.DiGraph()
    graph.add_nodes_from(labels)

    for row, source in enumerate(labels):
        for column, target in enumerate(labels):
            if matrix[row, column] == 1:
                graph.add_edge(source, target)

    return graph


def draw_graph(
    axis: plt.Axes,
    matrix: np.ndarray,
    labels: list[str],
    title: str,
    node_color: str,
) -> None:
    """Малює орієнтований граф на переданій області matplotlib."""
    graph = matrix_to_graph(matrix, labels)
    if len(labels) == 1:
        positions = {labels[0]: (0.0, 0.0)}
    elif len(labels) == 2:
        positions = {labels[0]: (-0.75, 0.0), labels[1]: (0.75, 0.0)}
    else:
        positions = nx.circular_layout(graph)

    nx.draw_networkx_nodes(
        graph,
        positions,
        ax=axis,
        node_size=1800,
        node_color=node_color,
        edgecolors="#172033",
        linewidths=1.8,
    )
    nx.draw_networkx_labels(
        graph,
        positions,
        ax=axis,
        font_size=12,
        font_weight="bold",
    )
    nx.draw_networkx_edges(
        graph,
        positions,
        ax=axis,
        edge_color="#3157a4",
        width=2,
        arrows=True,
        arrowsize=22,
        arrowstyle="-|>",
        connectionstyle="arc3,rad=0.12",
        node_size=1800,
    )

    axis.set_title(title, fontsize=15, fontweight="bold", pad=15)
    axis.set_xlim(-1.45, 1.45)
    axis.set_ylim(-1.35, 1.35)
    axis.set_axis_off()


def visualize_graphs(
    matrix: np.ndarray,
    factor_matrix: np.ndarray,
    classes: list[list[int]],
    element_labels: list[str],
) -> None:
    """Зберігає початковий і факторизований графи у PNG-файли."""
    OUTPUT_DIRECTORY.mkdir(exist_ok=True)

    class_labels = [f"A{index + 1}" for index in range(len(classes))]
    class_text = "   ".join(
        f"A{index + 1} = {{{', '.join(element_labels[v] for v in current_class)}}}"
        for index, current_class in enumerate(classes)
    )

    original_figure, original_axis = plt.subplots(figsize=(7, 6))
    draw_graph(
        original_axis,
        matrix,
        element_labels,
        "Граф початкового відношення P",
        "#bfdbfe",
    )
    original_figure.tight_layout()
    original_figure.savefig(OUTPUT_DIRECTORY / "original_graph.png", dpi=300, bbox_inches="tight")

    factor_figure, factor_axis = plt.subplots(figsize=(7, 6))
    draw_graph(
        factor_axis,
        factor_matrix,
        class_labels,
        "Граф фактор-відношення",
        "#bbf7d0",
    )
    factor_figure.text(0.5, 0.04, class_text, ha="center", fontsize=11)
    factor_figure.tight_layout(rect=(0, 0.07, 1, 1))
    factor_figure.savefig(OUTPUT_DIRECTORY / "factor_graph.png", dpi=300, bbox_inches="tight")
    plt.close("all")


def create_markdown_report(
    matrix: np.ndarray,
    powers: list[np.ndarray],
    closure: np.ndarray,
    reachability: np.ndarray,
    inverse_reachability: np.ndarray,
    mutual_reachability: np.ndarray,
    classes: list[list[int]],
    factor_matrix: np.ndarray,
    element_labels: list[str],
) -> str:
    """Формує Markdown-звіт з усіма результатами обчислень."""
    class_labels = [f"A{index + 1}" for index in range(len(classes))]
    sections = [
        "# Лабораторна робота №3",
        "",
        "## Агрегування та факторизація бінарного відношення",
        "",
        matrix_to_markdown("Початкова матриця відношення $P$", matrix, element_labels),
        "",
        "## Граф початкового відношення",
        "",
        "![Граф початкового відношення](plots/original_graph.png)",
        "",
    ]

    for exponent, power in enumerate(powers, start=1):
        sections.extend(
            [matrix_to_markdown(f"Матриця $P^{exponent}$", power, element_labels), ""]
        )

    sections.extend(
        [
            matrix_to_markdown("Транзитивне замикання", closure, element_labels),
            "",
            matrix_to_markdown("Матриця досяжності", reachability, element_labels),
            "",
            matrix_to_markdown(
                "Обернена матриця досяжності",
                inverse_reachability,
                element_labels,
            ),
            "",
            matrix_to_markdown(
                "Матриця взаємної досяжності",
                mutual_reachability,
                element_labels,
            ),
            "",
            "## Класи взаємної досяжності",
            "",
        ]
    )

    for index, current_class in enumerate(classes, start=1):
        members = ", ".join(element_labels[vertex] for vertex in current_class)
        sections.append(f"- $A_{index} = \\{{{members}\\}}$")

    sections.extend(
        [
            "",
            matrix_to_markdown("Матриця фактор-відношення", factor_matrix, class_labels),
            "",
            "## Граф фактор-відношення",
            "",
            "![Граф фактор-відношення](plots/factor_graph.png)",
            "",
        ]
    )

    return "\n".join(sections)


def main() -> None:
    validate_matrix(MATRIX)

    size = len(MATRIX)
    element_labels = [f"x{index + 1}" for index in range(size)]

    closure, powers = transitive_closure(MATRIX)
    identity = np.eye(size, dtype=int)
    reachability = np.logical_or(identity, closure).astype(int)
    inverse_reachability = reachability.T
    mutual_reachability = np.logical_and(reachability, inverse_reachability).astype(int)

    classes = find_equivalence_classes(mutual_reachability)
    factor_matrix = build_factor_matrix(MATRIX, classes)
    visualize_graphs(MATRIX, factor_matrix, classes, element_labels)
    report = create_markdown_report(
        MATRIX,
        powers,
        closure,
        reachability,
        inverse_reachability,
        mutual_reachability,
        classes,
        factor_matrix,
        element_labels,
    )
    REPORT_FILE.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
