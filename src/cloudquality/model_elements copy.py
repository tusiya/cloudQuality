from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


# --- Strategy Interfaces ---

class AggregationStrategy(ABC):
    @abstractmethod
    def aggregate(self, scores: List[float], weights: Optional[List[float]] = None) -> float:
        pass


class SimpleAverageStrategy(AggregationStrategy):
    def aggregate(self, scores: List[float], weights: Optional[List[float]] = None) -> float:
        return sum(scores) / len(scores) if scores else 0.0


class WeightedAverageStrategy(AggregationStrategy):
    def aggregate(self, scores: List[float], weights: Optional[List[float]] = None) -> float:
        if not scores:
            return 0.0
        w = weights if (weights and len(weights) == len(scores)) else [1.0] * len(scores)
        return sum(s * weight for s, weight in zip(scores, w)) / sum(w)


class TransformationStrategy(ABC):
    @abstractmethod
    def evaluate(self, raw_input: Any) -> float:
        pass


# --- Scenario Definition ---

@dataclass
class EvaluationScenario:
    """Represents a calculation scenario combining an aggregation strategy and input mode flag."""
    name: str
    aggregation_strategy: AggregationStrategy
    is_direct: bool = False


# Standard Built-In Scenarios
DEFAULT_SCENARIOS = [
    EvaluationScenario("Scenario 1 (Transformed + Simple Avg)", SimpleAverageStrategy(), is_direct=False),
    EvaluationScenario("Scenario 2 (Direct Score + Weighted Avg)", WeightedAverageStrategy(), is_direct=True),
    EvaluationScenario("Scenario 3 (Transformed + Weighted Avg)", WeightedAverageStrategy(), is_direct=False),
]


# --- Core Model Elements ---

class ModelElement(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def calculate_score(self, context: Dict[str, Any], scenario: EvaluationScenario) -> float:
        pass


class ProcedureElement(ModelElement):
    def __init__(self, name: str, default_strategy: TransformationStrategy):
        super().__init__(name)
        self.default_strategy = default_strategy

    def calculate_score(self, context: Dict[str, Any], scenario: EvaluationScenario) -> float:
        if scenario.is_direct:
            quality_metrics = context.get("quality_metric_inputs", {})
            if self.name not in quality_metrics:
                raise KeyError(f"Missing quality metric input for procedure: '{self.name}'")
            return float(quality_metrics[self.name])
        else:
            procedure_inputs = context.get("procedure_inputs", {})
            if self.name not in procedure_inputs:
                raise KeyError(f"Missing raw procedure input for procedure: '{self.name}'")
            return self.default_strategy.evaluate(procedure_inputs[self.name])


class CompositeElement(ModelElement):
    def __init__(
        self, 
        name: str, 
        subelements: Optional[List[ModelElement]] = None,
        default_weights: Optional[List[float]] = None
    ):
        super().__init__(name)
        self.subelements = subelements or []
        self.default_weights = default_weights

    def calculate_score(self, context: Dict[str, Any], scenario: EvaluationScenario) -> float:
        if not self.subelements:
            return 0.0

        child_scores = [child.calculate_score(context, scenario) for child in self.subelements]
        weights = context.get("weights", {}).get(self.name) or self.default_weights
        
        # Delegate aggregation directly to the active scenario's strategy
        return scenario.aggregation_strategy.aggregate(child_scores, weights)

    def find_element(self, name: str) -> Optional[ModelElement]:
        """Recursively finds an element by name in the sub-tree."""
        if self.name == name:
            return self
        for child in self.subelements:
            if child.name == name:
                return child
            if isinstance(child, CompositeElement):
                found = child.find_element(name)
                if found:
                    return found
        return None

    def add_subelement(self, element: ModelElement, default_weight: float = 1.0) -> None:
        """Adds a new procedure or characteristic child node."""
        self.subelements.append(element)
        if self.default_weights is not None:
            self.default_weights.append(default_weight)

    def remove_subelement(self, name: str) -> bool:
        """Removes a child node by name from this composite."""
        for i, child in enumerate(self.subelements):
            if child.name == name:
                self.subelements.pop(i)
                if self.default_weights and len(self.default_weights) > i:
                    self.default_weights.pop(i)
                return True
        return False


# --- Standard Library Transformation Rules ---

class DostepnoscUslugiTransformation(TransformationStrategy):
    def evaluate(self, raw_input: Any) -> float:
        val = float(raw_input)
        if val < 0.95: return 1.0
        elif val < 0.99: return 2.0
        elif val < 0.999: return 3.0
        elif val < 0.9999: return 4.0
        else: return 5.0



# --- Strategy Registry ---
TRANSFORMATION_REGISTRY: Dict[str, TransformationStrategy] = {
    "dostepnosc_uslugi": DostepnoscUslugiTransformation(),
}

def register_transformation(name: str, strategy: TransformationStrategy) -> None:
    """Allows users to register custom transformation rules at runtime."""
    TRANSFORMATION_REGISTRY[name] = strategy


# --- Pre-packaged Model Factory ---
def build_model_from_dict(node_def: Dict[str, Any]) -> ModelElement:
    """Recursively builds a ModelElement tree from a dictionary/JSON schema."""
    node_type = node_def.get("type")
    name = node_def.get("name")

    if not name or not node_type:
        raise ValueError(f"Model node definition must contain 'name' and 'type': {node_def}")

    # CASE A: Leaf Procedure Element
    if node_type == "procedure":
        strategy_name = node_def.get("strategy")
        if strategy_name not in TRANSFORMATION_REGISTRY:
            raise ValueError(
                f"Unknown transformation strategy: '{strategy_name}' for procedure '{name}'. "
                f"Available strategies: {list(TRANSFORMATION_REGISTRY.keys())}"
            )
        strategy = TRANSFORMATION_REGISTRY[strategy_name]
        return ProcedureElement(name=name, default_strategy=strategy)

    # CASE B: Composite Node Element
    elif node_type == "composite":
        raw_children = node_def.get("subelements", [])
        children = [build_model_from_dict(child) for child in raw_children]
        default_weights = node_def.get("default_weights")
        return CompositeElement(name=name, subelements=children, default_weights=default_weights)

    else:
        raise ValueError(f"Unknown model node type: '{node_type}' in node '{name}'")
    

STANDARD_MODEL_SCHEMA = {
    "name": "System Quality Model",
    "type": "composite",
    "default_weights": [1.0],
    "subelements": [
        {
            "name": "Niezawodność Usługi",
            "type": "composite",
            "default_weights": [1.0],
            "subelements": [
                {
                    "name": "Dostępność Usługi",
                    "type": "procedure",
                    "strategy": "dostepnosc_uslugi"
                }
            ]
        }
    ]
}

def load_standard_quality_schema() -> Dict[str, Any]:
    """Returns a deep copy of the standard model dictionary structure."""
    import copy
    return copy.deepcopy(STANDARD_MODEL_SCHEMA)

def load_standard_quality_model() -> CompositeElement:
    """Loads and builds the default model from schema."""
    return build_model_from_dict(STANDARD_MODEL_SCHEMA)


# --- Library Execution Helper ---

def evaluate(
    model: ModelElement, 
    context: Dict[str, Any], 
    custom_scenarios: Optional[List[EvaluationScenario]] = None
) -> Dict[str, float]:
    """Runs evaluation on a model tree across default and optional custom scenarios."""
    scenarios_to_run = list(DEFAULT_SCENARIOS)
    if custom_scenarios:
        scenarios_to_run.extend(custom_scenarios)

    return {
        scenario.name: model.calculate_score(context, scenario) 
        for scenario in scenarios_to_run
    }
