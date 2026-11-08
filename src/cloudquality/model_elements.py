from abc import ABC, abstractmethod
from dataclasses import dataclass
import warnings
import csv
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

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Exports the live element state into schema dictionary format."""
        pass


class ProcedureElement(ModelElement):
    def __init__(self, name: str, default_strategy: TransformationStrategy, strategy_name: str = "custom"):
        super().__init__(name)
        self.default_strategy = default_strategy
        self.strategy_name = strategy_name

    def calculate_score(self, context: Dict[str, Any], scenario: EvaluationScenario) -> float:
        if scenario.is_direct:
            quality_metrics = context.get("quality_metric_inputs", {})
            if self.name not in quality_metrics:
                raise KeyError(f"Missing quality metric input for procedure: '{self.name}'")
            val = quality_metrics[self.name]
            
            # Normalize single scalar float/int values into a list
            if isinstance(val, (int, float)):
                scores = [float(val)]
            elif isinstance(val, (list, tuple)):
                if not val:
                    raise ValueError(f"Quality metric list for procedure '{self.name}' cannot be empty.")
                scores = [float(x) for x in val]
            else:
                raise TypeError(f"Invalid input type for quality metric '{self.name}': {type(val)}")
            
            # Calculate simple average of all provided scores
            return sum(scores) / len(scores)
        else:
            procedure_inputs = context.get("procedure_inputs", {})
            if self.name not in procedure_inputs:
                raise KeyError(f"Missing raw procedure input for procedure: '{self.name}'")
            return self.default_strategy.evaluate(procedure_inputs[self.name])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": "procedure",
            "strategy": self.strategy_name
        }


class CompositeElement(ModelElement):
    def __init__(
        self, 
        name: str, 
        subelements: Optional[List[ModelElement]] = None,
        default_weights: Optional[List[float]] = None
    ):
        super().__init__(name)
        self.subelements = subelements or []
        
        # Enforce weight alignment: exactly 1 weight per child subelement
        if default_weights is None:
            self.default_weights = {child.name: 1.0 for child in self.subelements}
        else:
            self.default_weights = default_weights

    def calculate_score(self, context: Dict[str, Any], scenario: EvaluationScenario) -> float:
        if not self.subelements:
            return 0.0

        child_scores = [child.calculate_score(context, scenario) for child in self.subelements]
        # Extract weights payload for this composite
        raw_weights = context.get("weights", {}).get(self.name) or self.default_weights
        
        # 1. Handle Named Dictionary Weights (New Preferred Way)
        if isinstance(raw_weights, dict):
            weights = []
            for child in self.subelements:
                if child.name not in raw_weights:
                    raise KeyError(
                        f"Missing weight assignment for child '{child.name}' in composite '{self.name}'. "
                        f"Specified weights: {list(raw_weights.keys())}"
                    )
                weights.append(float(raw_weights[child.name]))
                
        # 2. Handle Legacy Positional Lists (Backward Compatibility)
        elif isinstance(raw_weights, (list, tuple)):
            if len(raw_weights) != len(self.subelements):
                raise ValueError(
                    f"Weight count mismatch in '{self.name}': expected {len(self.subelements)} "
                    f"weights for children {[c.name for c in self.subelements]}, got {len(raw_weights)}."
                )
            weights = [float(w) for w in raw_weights]
            
        else:
            weights = [1.0] * len(self.subelements)
        
        return scenario.aggregation_strategy.aggregate(child_scores, weights)

    def find_element(self, name: str) -> Optional[ModelElement]:
        """Recursively finds an element by name in the tree."""
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
        """Adds a child node and keeps weights synchronized."""
        self.subelements.append(element)
        self.default_weights.append(default_weight)

    def remove_subelement(self, name: str, raise_error: bool = False) -> bool:
        """Removes a child node by name and cleans up its corresponding weight."""
        for i, child in enumerate(self.subelements):
            if child.name == name:
                self.subelements.pop(i)
                self.default_weights.pop(i)
                return True

        msg = f"Cannot remove subelement '{name}': Not found in composite '{self.name}'."
        if raise_error:
            raise KeyError(msg)
        else:
            warnings.warn(msg, UserWarning)
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Recursively exports the live tree into dictionary format."""
        return {
            "name": self.name,
            "type": "composite",
            "default_weights": list(self.default_weights),
            "subelements": [child.to_dict() for child in self.subelements]
        }


# --- Standard Library Transformation Rules ---

class DostepnoscUslugiTransformation(TransformationStrategy):
    """Input: percentage value of Dostępność Usługi"""
    def evaluate(self, raw_input: Any) -> float:
        try:
            val = float(raw_input)
        except (ValueError, TypeError):
            raise TypeError(f"Invalid input type for DostepnoscUslugiTransformation: {type(raw_input)}")
        if val < 0.95: return 1.0
        elif val < 0.99: return 2.0
        elif val < 0.999: return 3.0
        elif val < 0.9999: return 4.0
        else: return 5.0

class BadanieScenariuszyTransformation(TransformationStrategy):
    """Input: List of scores from 0 to 1 
    1 means the condition (for example functionality working) is met, 0 means it is not met"""
    def evaluate(self, raw_input: Any) -> float:
        values = []
        if raw_input is None:
            raise ValueError("Input for BadanieScenariuszyTransformation cannot be None.")

        # Normalize single float/int into a list
        if isinstance(raw_input, (int, float)):
            values = [float(raw_input)]
        elif isinstance(raw_input, (list, tuple)):
            if not raw_input:
                raise ValueError("Input list for BadanieScenariuszyTransformation cannot be empty.")
            values = [float(x) for x in raw_input]
        else:
            raise TypeError(f"Invalid input type for BadanieScenariuszyTransformation: {type(raw_input)}")

        # Validate and cut values to [0.0, 1.0] range
        cut_values = [max(0.0, min(1.0, val)) for val in values]
        
        return 1+4*sum(cut_values)/len(cut_values)

class EfektywnoscInterakcjiTransformation(TransformationStrategy):
    """Input: List of steps needed to make each task"""
    def evaluate(self, raw_input: Any) -> float:
        values = []
        if raw_input is None:
            raise ValueError("Input for EfektywnoscInterakcji cannot be None.")

        # Normalize single float/int into a list
        if isinstance(raw_input, (int, float)):
            values = [float(raw_input)]
        elif isinstance(raw_input, (list, tuple)):
            if not raw_input:
                raise ValueError("Input list for EfektywnoscInterakcji cannot be empty.")
            values = [float(x) for x in raw_input]
        else:
            raise TypeError(f"Invalid input type for EfektywnoscInterakcji: {type(raw_input)}")

        score_values = [1 if val <= 0 or val >= 12 
                        else 2 if val >= 10 
                        else 3 if val >= 7 
                        else 4 if val >= 4 
                        else 5 for val in values]
    
        return sum(score_values)/len(score_values)


class WydajnoscCzasowaTransformation(TransformationStrategy):
    """Input: List of average time each task takes. If the input is None it is assumed that score is maximum"""
    def evaluate(self, raw_input: Any) -> float:
        values = []

        # Normalize single float/int into a list
        if isinstance(raw_input, (int, float)):
            values = [float(raw_input)]
        elif isinstance(raw_input, (list, tuple)):
            if not raw_input:
                raise ValueError("Input list for WydajnoscCzasowaTransformation cannot be empty.")
            values = [0 if x==None else float(x) for x in raw_input]
        else:
            raise TypeError(f"Invalid input type for WydajnoscCzasowaTransformation: {type(raw_input)}")

        score_values = [5 if val <= 1 
                        else 4 if val <= 2 
                        else 3 if val >= 5 
                        else 2 if val >= 10 
                        else 1 for val in values]

        return sum(score_values)/len(score_values)

class WydajnoscCzasowaTransformation(TransformationStrategy):
    """Input: List of average time each task takes. If the input is None it is assumed that score is maximum"""
    def evaluate(self, raw_input: Any) -> float:
        values = []

        # Normalize single float/int into a list
        if isinstance(raw_input, (int, float)):
            values = [float(raw_input)]
        elif isinstance(raw_input, (list, tuple)):
            if not raw_input:
                raise ValueError("Input list for WydajnoscCzasowaTransformation cannot be empty.")
            values = [0 if x==None else float(x) for x in raw_input]
        else:
            raise TypeError(f"Invalid input type for WydajnoscCzasowaTransformation: {type(raw_input)}")

        score_values = [5 if val <= 1 
                        else 4 if val <= 2 
                        else 3 if val >= 5 
                        else 2 if val >= 10 
                        else 1 for val in values]

        return sum(score_values)/len(score_values)


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

def collect_node_scores(
    element: ModelElement,
    context: Dict[str, Any],
    scenarios: List[EvaluationScenario],
    current_depth: int,
    max_depth: int
) -> Dict[str, Any]:
    """
    Recursively collects evaluation results for an element and its subelements
    up to max_depth.
    """
    # 1. Calculate scenario scores for the current element
    node_results = {
        "name": element.name,
        "type": "composite" if isinstance(element, CompositeElement) else "procedure",
        "scores": {
            scenario.name: element.calculate_score(context, scenario)
            for scenario in scenarios
        }
    }

    # 2. If element is a composite and we haven't reached max_depth, drill down into children
    if isinstance(element, CompositeElement) and current_depth < max_depth and element.subelements:
        node_results["subelements"] = [
            collect_node_scores(child, context, scenarios, current_depth + 1, max_depth)
            for child in element.subelements
        ]

    return node_results


def evaluate(
    model: ModelElement, 
    context: Dict[str, Any], 
    custom_scenarios: Optional[List[EvaluationScenario]] = None,
    depth: int = 1
) -> Dict[str, Any]:
    """
    Evaluates the model across scenarios up to the specified structural depth.
    - depth=1: Root scores only
    - depth=2: Root + Level 1 children
    - depth=3+: Deeper sub-trees / leaves
    """
    scenarios_to_run = list(DEFAULT_SCENARIOS)
    if custom_scenarios:
        scenarios_to_run.extend(custom_scenarios)

    return collect_node_scores(model, context, scenarios_to_run, current_depth=1, max_depth=depth)


def print_evaluation_results(result_node: Dict[str, Any], indent_level: int = 0) -> None:
    """Pretty prints evaluation results hierarchically based on depth."""
    indent = "  " * indent_level
    prefix = "└── " if indent_level > 0 else ""
    
    print(f"{indent}{prefix}[{result_node['name']}] ({result_node['type']})")
    for scenario_name, score in result_node["scores"].items():
        print(f"{indent}    │  {scenario_name}: {score:.2f}")

    if "subelements" in result_node:
        print(f"{indent}    │")
        for child_node in result_node["subelements"]:
            print_evaluation_results(child_node, indent_level + 1)


#---------Loading Input---------------
def load_quality_metrics_from_csv(file_path: str) -> Dict[str, List[float]]:
    """
    Parses a CSV where headers are procedure names and rows are respondent entries.
    Filters out empty, 'None', or invalid values automatically.
    """
    quality_metrics: Dict[str, List[float]] = {}

    with open(file_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        
        # Initialize empty lists for all column headers
        if reader.fieldnames:
            for header in reader.fieldnames:
                clean_header = header.strip()
                if clean_header:
                    quality_metrics[clean_header] = []

        for row in reader:
            for col_name, val in row.items():
                if not col_name:
                    continue
                col_name = col_name.strip()
                
                # Filter out missing cells, None strings, or spaces
                if val is None:
                    continue
                val_str = str(val).strip().strip('"\'')
                if val_str == "" or val_str.lower() in ("none", "null", "nan", "n/a"):
                    continue

                try:
                    score = float(val_str)
                    quality_metrics[col_name].append(score)
                except ValueError:
                    # Ignore unparseable non-numeric text entries
                    pass

    return quality_metrics


def load_procedure_inputs_from_csv(file_path: str) -> Dict[str, Any]:
    """
    Parses a key-value CSV for raw procedure measurements (Procedure, Value).
    """
    procedure_inputs: Dict[str, Any] = {}
    with open(file_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader, None)  # Skip header row if present
        
        for row in reader:
            if len(row) >= 2 and row[0].strip():
                proc_name = row[0].strip()
                val_str = row[1].strip()
                
                # Convert to float/int if possible, otherwise keep string
                try:
                    val = float(val_str) if "." in val_str else int(val_str)
                except ValueError:
                    val = val_str
                    
                procedure_inputs[proc_name] = val

    return procedure_inputs


def load_weights_from_csv(file_path: str) -> Dict[str, Dict[str, float]]:
    """
    Parses a long-format CSV (parent_name, child_name, weight).
    Returns a dictionary mapping each composite node to a dict of child weights.
    """
    weights: Dict[str, Dict[str, float]] = {}

    with open(file_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parent = row["parent_name"].strip()
            child = row["child_name"].strip()
            weight_val = float(row["weight"].strip())

            if parent not in weights:
                weights[parent] = {}
            weights[parent][child] = weight_val

    return weights


def build_payload_from_files(
    quality_metrics_csv: str = None,
    procedure_inputs_csv: str = None,
    weights_csv: str = None
) -> Dict[str, Any]:
    """Helper that converts all 3 input CSV files into a unified execution payload."""
    payload = {}
    
    if quality_metrics_csv:
        payload["quality_metric_inputs"] = load_quality_metrics_from_csv(quality_metrics_csv)
    if procedure_inputs_csv:
        payload["procedure_inputs"] = load_procedure_inputs_from_csv(procedure_inputs_csv)
    if weights_csv:
        payload["weights"] = load_weights_from_csv(weights_csv)

    return payload
