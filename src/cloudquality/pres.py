import pandas as pd
import csv

from model_elements import (
    load_standard_quality_model,
    load_procedure_inputs_from_csv,
    load_weights_from_csv,
    CompositeElement,
    ProcedureElement,
    WeightedAverageStrategy,
    EvaluationScenario,
)

import visualizations as viz

import variants.intuition as vi

def show_options():
    base_data, options = vi.prepare_intuition()
    return base_data, options

def user_statistics(base_data, options, list):
    filtered_survey = vi.intuition(base_data, options, list)
    viz.generate_demographic_visualizations(filtered_survey)

def user_statistics_no_visual(base_data, options, list):
    vi.intuition(base_data, options, list)

def run_model():
    SYSTEM_FILE = "../../system_metrics.csv"
    SURVEY_FILE = "../../user_surveys.csv"
    WEIGHTS_FILE = "../../weights.csv"

    OUTPUT_FILE = "../../aggregation_comparison.csv"

    model = load_standard_quality_model()

    system_inputs = load_procedure_inputs_from_csv(SYSTEM_FILE)

    survey_df = pd.read_csv(SURVEY_FILE, encoding="utf-8-sig")
    survey_df = survey_df.apply(pd.to_numeric, errors="coerce")

    # Mean score for each procedure across respondents
    survey_scores = survey_df.mean().to_dict()

    ahp_weights = load_weights_from_csv(WEIGHTS_FILE)

    def complete_weights(element, supplied_weights):
        result = {}

        if not isinstance(element, CompositeElement):
            return result

        provided = supplied_weights.get(element.name, {})

        result[element.name] = {
            child.name: float(provided.get(child.name, 1.0))
            for child in element.subelements
        }

        for child in element.subelements:
            result.update(complete_weights(child, supplied_weights))

        return result

    complete_ahp_weights = complete_weights(model, ahp_weights)

    weighted_average = WeightedAverageStrategy()

    def calculate(element, scores, weights):
        """Recursively aggregate procedure scores."""

        if isinstance(element, ProcedureElement):
            if element.name not in scores:
                raise KeyError(f"Missing score for: {element.name}")
            return float(scores[element.name])

        child_scores = [
            calculate(child, scores, weights)
            for child in element.subelements
        ]

        child_weights = [
            weights[element.name][child.name]
            for child in element.subelements
        ]

        return weighted_average.aggregate(child_scores, child_weights)

    def transform_system_metrics(element):
        """Calculate transformed scores for all procedure nodes."""
        scores = {}

        def visit(node):
            if isinstance(node, ProcedureElement):
                if node.name not in system_inputs:
                    raise KeyError(f"Missing system metric: {node.name}")

                scores[node.name] = node.default_strategy.evaluate(
                    system_inputs[node.name]
                )
            else:
                for child in node.subelements:
                    visit(child)

        visit(element)
        return scores

    system_scores = transform_system_metrics(model)

    equal_weights = complete_weights(model, {})

    scenario_1 = calculate(
        model,
        system_scores,
        equal_weights
    )

    scenario_2 = calculate(
        model,
        survey_scores,
        complete_ahp_weights
    )

    scenario_3 = calculate(
        model,
        system_scores,
        complete_ahp_weights
    )
    results = {
        "System metrics + equal weights": {},
        "User surveys + AHP weights": {},
        "System metrics + AHP weights": {}
    }

    scenarios = [
        ("System metrics + equal weights", system_scores, equal_weights),
        ("User surveys + AHP weights", survey_scores, complete_ahp_weights),
        ("System metrics + AHP weights", system_scores, complete_ahp_weights),
    ]

    for label, scores, weights in scenarios:
        results[label]["Model jakości"] = calculate(model, scores, weights)

        for child in model.subelements:
            results[label][child.name] = calculate(child, scores, weights)

    return OUTPUT_FILE, results

def print_data(results, OUTPUT_FILE):
    comparison = pd.DataFrame(results)
    comparison.index.name = "Criterion"

    print(comparison.round(3).to_string())

    comparison.round(4).to_csv(
        OUTPUT_FILE,
        encoding="utf-8-sig"
    )
    return comparison

def show_stats(comparison):
    viz.generate_model_comparison_visualizations(comparison)