
import re

import pandas as pd
import matplotlib.pyplot as plt


# ==================================================
# HELPERS
# ==================================================

def finish_plot(fig, show=True):
    """Display a figure and close it afterwards."""

    fig.tight_layout()

    if show:
        plt.show()

    plt.close(fig)


def get_demographic_columns(survey):
    """Return columns that are not opinion/heuristic columns."""

    return [
        col for col in survey.columns
        if not re.match(r"^[OW]\d", str(col))
    ]


# ==================================================
# SURVEY VISUALIZATIONS
# ==================================================


def plot_demographics(survey, show=True):
    """Display demographic distributions in two wide columns."""

    columns = get_demographic_columns(survey)

    if not columns:
        print("No demographic columns found.")
        return

    n_columns = 2
    n_rows = (len(columns) + 1) // 2

    fig, axes = plt.subplots(
        n_rows,
        n_columns,
        figsize=(16, 4.5 * n_rows),
        squeeze=False
    )

    axes = axes.flatten()

    for ax, column in zip(axes, columns):
        counts = survey[column].value_counts(dropna=False)

        if column == "Wiek":
            counts.plot(kind="bar", ax=ax, width=0.7)
            ax.set_xlabel("Age group")
            ax.tick_params(axis="x", rotation=0)

        else:
            labels = [
                f"Category {i + 1}"
                for i in range(len(counts))
            ]

            bars = ax.bar(labels, counts.values, width=0.6)

            legend_labels = [
                f"{label}: {value}"
                for label, value in zip(counts.index, counts.values)
            ]

            ax.legend(
                bars,
                legend_labels,
                title=column,
                loc="upper center",
                bbox_to_anchor=(0.5, -0.15),
                ncol=1 if column in columns[-2:] else 2,
                fontsize=9,
                title_fontsize=10,
                frameon=False
            )

            ax.set_xlabel("Category")

        ax.set_title(column, fontsize=12)
        ax.set_ylabel("Respondents")
        ax.tick_params(axis="both", labelsize=9)
        ax.set_ylim(bottom=0)

    for ax in axes[len(columns):]:
        ax.set_visible(False)

    fig.suptitle("Respondent demographic distribution", fontsize=15)

    # Reserve room for legends without shrinking the plots horizontally
    fig.subplots_adjust(
        left=0.08,
        right=0.95,
        top=0.92,
        bottom=0.12,
        hspace=0.65,
        wspace=0.25
    )

    if show:
        plt.show()

    plt.close(fig)


def plot_opinion_statistics(opinions, show=True):
    """Display descriptive statistics and opinion visualizations."""

    numeric = opinions.select_dtypes(include="number")

    if numeric.empty:
        print("No numeric opinion columns found.")
        return

    # Descriptive statistics
    description = numeric.describe().T
    description["median"] = numeric.median()

    print("\nOpinion statistics:")
    display(description)

    # Average scores
    means = numeric.mean().sort_values()

    fig, ax = plt.subplots(figsize=(9, 5))

    means.plot(kind="barh", ax=ax)

    ax.set_title("Average score per criterion")
    ax.set_xlabel("Average score")
    ax.set_ylabel("Criterion")

    finish_plot(fig, show)

    # Score distributions
    fig, ax = plt.subplots(figsize=(10, 5))

    numeric.boxplot(ax=ax)

    ax.set_title("Opinion score distributions")
    ax.set_ylabel("Score")
    ax.tick_params(axis="x", rotation=45)

    finish_plot(fig, show)

    # Correlations
    if numeric.shape[1] > 1:
        correlation = numeric.corr()

        fig, ax = plt.subplots(figsize=(9, 8))

        image = ax.imshow(
            correlation,
            vmin=-1,
            vmax=1,
            cmap="coolwarm"
        )

        ax.set_xticks(range(len(correlation.columns)))
        ax.set_yticks(range(len(correlation.columns)))

        ax.set_xticklabels(
            correlation.columns,
            rotation=90,
            fontsize=8
        )
        ax.set_yticklabels(
            correlation.columns,
            fontsize=8
        )

        fig.colorbar(image, ax=ax, label="Correlation")
        ax.set_title("Correlation between criteria")

        finish_plot(fig, show)

    return description


def plot_ahp_weights(weights, show=True):
    """Display AHP weights grouped by parent criterion."""

    if isinstance(weights, str):
        weights = pd.read_csv(weights)

    weights = weights.copy()
    weights["weight"] = pd.to_numeric(weights["weight"])

    for parent, group in weights.groupby("parent_name"):
        group = group.sort_values("weight")

        fig, ax = plt.subplots(figsize=(9, 4))

        ax.barh(group["child_name"], group["weight"])

        ax.set_title(f"AHP weights: {parent}")
        ax.set_xlabel("Weight")
        ax.set_ylabel("Criterion")

        finish_plot(fig, show)


def generate_demographic_visualizations(survey, show=True):
    """Display demographics of the selected respondents."""

    print("\nGenerating respondent demographics...")
    print(f"Selected respondents: {len(survey)}")

    for column in get_demographic_columns(survey):
        counts = survey[column].value_counts(dropna=False)

        print(f"\n{column}")
        print(counts)

    plot_demographics(survey, show)


# ==================================================
# MODEL COMPARISON VISUALIZATIONS
# ==================================================

def calculate_model_differences(comparison):
    """
    Calculate pairwise differences between model scenarios.

    Rows: criteria
    Columns: model scenarios
    """

    differences = {}

    columns = list(comparison.columns)

    for i, model_a in enumerate(columns):
        for model_b in columns[i + 1:]:
            differences[f"{model_a} vs {model_b}"] = (
                comparison[model_a] - comparison[model_b]
            )

    return pd.DataFrame(differences, index=comparison.index)


def plot_model_comparison(comparison, show=True):
    """Display comparison of model evaluation scenarios."""

    fig, ax = plt.subplots(figsize=(11, 5))

    comparison.plot(
        kind="bar",
        ax=ax,
        width=0.8
    )

    ax.set_title("Comparison of model evaluation scenarios")
    ax.set_xlabel("Criterion")
    ax.set_ylabel("Quality score")
    ax.tick_params(axis="x", rotation=30)
    ax.legend(title="Scenario", fontsize=8)

    finish_plot(fig, show)


def plot_model_differences(differences, show=True):
    """Display a heatmap of differences between model scenarios."""

    fig, ax = plt.subplots(figsize=(10, 5))

    image = ax.imshow(
        differences,
        aspect="auto",
        cmap="coolwarm"
    )

    ax.set_xticks(range(len(differences.columns)))
    ax.set_yticks(range(len(differences.index)))

    ax.set_xticklabels(
        differences.columns,
        rotation=30,
        ha="right",
        fontsize=8
    )
    ax.set_yticklabels(differences.index)

    fig.colorbar(image, ax=ax, label="Score difference")
    ax.set_title("Differences between model scenarios")

    finish_plot(fig, show)


def generate_model_comparison_visualizations(comparison, show=True):
    """
    Display visualizations comparing model scenarios.

    comparison must be a DataFrame:
    - rows = criteria
    - columns = model scenarios
    """

    # print("\nGenerating model comparison visualizations...")

    # differences = calculate_model_differences(comparison)

    plot_model_comparison(comparison, show)
    # plot_model_differences(differences, show)

    # return differences
