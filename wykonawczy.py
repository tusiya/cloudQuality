from cloudquality.model_elements import load_standard_quality_model, evaluate, register_transformation
from cloudquality.model_elements import load_standard_quality_schema
from cloudquality.model_elements import AggregationStrategy, EvaluationScenario, TransformationStrategy
from cloudquality.model_elements import CompositeElement, ProcedureElement

# ==========================================
# USER WORKSPACE
# ==========================================



# 1. Register custom transformation rule
class LatencyTransformation(TransformationStrategy):
    def evaluate(self, raw_input: Any) -> float:
        ms = float(raw_input)
        return 5.0 if ms < 100 else (3.0 if ms < 500 else 1.0)

register_transformation("latency_rule", LatencyTransformation())

# 2. Load live model instance
model = load_standard_quality_model()

print("--- INITIAL LIVE MODEL SCHEMA ---")
print(model.to_dict())

# 3. Modify live tree nodes
niezawodnosc_node = model.find_element("Niezawodność Usługi")

if isinstance(niezawodnosc_node, CompositeElement):
    # Attempting to remove non-existent node now issues a warning!
    niezawodnosc_node.remove_subelement("Direct User Score")
    
    # Adding Latency updates subelements AND appends 1 matching weight (0.4)
    new_proc = ProcedureElement("Latency", LatencyTransformation(), strategy_name="latency_rule")
    niezawodnosc_node.add_subelement(new_proc, default_weight=0.4)

print("\n--- UPDATED LIVE MODEL SCHEMA ---")
print(model.to_dict())

# 4. Payload with inputs and weight overrides
user_payload = {
    "procedure_inputs": {
        "Dostępność Usługi": 0.98,  # Triggers score 2.0
        "Latency": 400              # Triggers score 3.0
    },
    "quality_metric_inputs": {
        "Dostępność Usługi": 4.0,
        "Latency": 3.0
    },
    "weights": {
        "Niezawodność Usługi": [0.6, 0.4],
        "System Quality Model": [1.0]
    }
}


# 3. (Optional) User defines a custom scenario
class MinimumScoreStrategy(AggregationStrategy):
    def aggregate(self, scores: List[float], weights: Optional[List[float]] = None) -> float:
        return min(scores) if scores else 0.0

# 5. Evaluate Scenarios
custom_scenario = EvaluationScenario(
    name="Scenario 4 (Minimum Bottleneck + Direct)",
    aggregation_strategy=MinimumScoreStrategy(),
    is_direct=True
)

results = evaluate(model, user_payload, custom_scenarios=[custom_scenario])

print("\n--- EVALUATION RESULTS ---")
for scenario, score in results.items():
    print(f"{scenario}: {score:.2f}")