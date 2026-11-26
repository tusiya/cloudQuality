import pandas as pd
import re
import structure as st    # plik zawierający kryteria oceny
import ahpy as a
from statistics import geometric_mean

def read_survey():
    survey = pd.read_csv("resources/"+st.FILENAME+".csv")
    survey = st.change_survey_colnames(survey)
    return survey

def normalize_age_group(value):
    match = re.fullmatch(r"\s*(\d+)\s*-\s*(\d+)\s*", str(value))

    if match:
        lower = int(match.group(1))
        return f"{lower} - {lower + 9 if lower != 18 else 24}"

    return value

def data_cleaning(survey):
    for crit in st.data_removing_criteria:
        survey = survey[survey[crit[0]] != crit[1]]

    survey["Wiek"] = survey["Wiek"].apply(normalize_age_group)
    
    survey = survey.drop(columns=[
        "O12 Współistnienie z innymi usługami",
        "W3 Współistnienie z innymi usługami vs Zgodność formatów danych"
    ])

    return survey.reset_index(drop=True)

def rename_opinion_columns(opinions):
    opinions = opinions.rename(columns=st.OPINION_COLUMN_NAMES)

    for model_name, survey_name in st.HEURISTIC_COLUMN_NAMES.items():
        opinions[model_name] = opinions[survey_name]

    return opinions[st.MODEL_COLUMN_ORDER]

# def choose_category_interactive(survey):
#     print("\n\nABY WYBRAĆ KATEGORIE UŻYTKOWNIKÓW, PODAJ NUMERY IM ODPOWIADAJĄCE:")

#     cols = [
#         c for c in survey.columns
#         if not re.match(r"^[OW]\d", str(c))
#     ]

#     options = {}
#     option_num = 1

#     for col in cols:
#         counts = survey[col].value_counts()
#         options[col] = {}

#         for value in counts[counts > 4].index:
#             options[col][option_num] = value
#             option_num += 1

#     for col, values in options.items():
#         # print(f"\n{'─' * 50}")
#         print(f"\n")
#         print(col)
#         print('─' * 50)

#         for option_id, value in values.items():
#             print(f"{option_id:>3} │ {value}")

#     print(f"\n\n")

#     return options

def choose_category(survey):
    print("\n\nDOSTĘPNE KATEGORIE UŻYTKOWNIKÓW:")

    cols = [
        c for c in survey.columns
        if not re.match(r"^[OW]\d", str(c))
    ]

    options = {}
    option_num = 1

    for col in cols:
        counts = survey[col].value_counts()
        options[col] = {}

        for value in counts[counts > 4].index:
            options[col][option_num] = value
            option_num += 1

    for col, values in options.items():
        print(f"\n{col}")
        print("─" * 50)

        for option_id, value in values.items():
            print(f"{option_id:>3} │ {value}")

    return options

def filter_survey_by_categories(survey, options, selections=None):
    if not selections:
        return survey.reset_index(drop=True)

    selections = set(selections)

    valid_numbers = {
        number
        for values in options.values()
        for number in values
    }

    invalid = selections - valid_numbers

    if invalid:
        raise ValueError(f"Invalid category numbers: {invalid}")

    for category, values in options.items():
        selected_values = [
            value
            for number, value in values.items()
            if number in selections
        ]

        if selected_values:
            survey = survey[survey[category].isin(selected_values)]

    print(f"\nRespondents included: {len(survey)}")

    return survey.reset_index(drop=True)

def convert_to_ahp(value):
    value = float(value)

    if value == 5:
        return 1.0
    elif value > 5:
        return 1 + 4 * (value - 5) / 5
    else:
        return 1 / (1 + 4 * (5 - value) / 5)
    
def get_opinions(survey):
    opinion_columns = [
        column for column in survey.columns
        if column.startswith("O")
    ]

    return survey[opinion_columns].copy()

def convert_opinions_to_numeric(opinions):
    answer_mapping = {
        "Bardzo źle": 1,
        "Raczej źle": 2,
        "Średnio / nie mam zdania": 3,
        "Raczej dobrze": 4,
        "Bardzo dobrze": 5
    }

    return opinions.replace(answer_mapping).fillna(3).astype(int)

# def rename_opinion_columns(opinions):
#     return opinions.rename(columns=st.OPINION_COLUMN_NAMES)

def aggregate_comparisons(survey, comparison_definitions):
    comparisons = {}

    for column, first, second in comparison_definitions:
        values = pd.to_numeric(survey[column], errors="coerce").dropna()
        ratios = values.apply(convert_to_ahp)

        comparisons[(first, second)] = geometric_mean(ratios)

    return comparisons

def create_comparison(survey, parent, definitions):
    comparisons = aggregate_comparisons(survey, definitions)

    return a.Compare(
        name=parent,
        comparisons=comparisons,
        precision=3
    )

def get_output_rows(survey):
    rows = []

    for parent, children in st.OUTPUT_HIERARCHY.items():
        if parent == "Model jakości":
            definitions = st.root_comparisons
        else:
            definitions = st.pairwise_comparisons[parent]

        comparison = create_comparison(survey, parent, definitions)

        for child in children:
            rows.append({
                "parent_name": parent,
                "child_name": child,
                "weight": comparison.target_weights[child]
            })

    return rows


def export_example_version(survey):
    rows = []

    for parent, children in st.OUTPUT_HIERARCHY.items():

        if len(children) == 1:
            weights = {children[0]: 1.0}
        else:
            definitions = (
                st.root_comparisons
                if parent == "Model jakości"
                else st.pairwise_comparisons[parent]
            )

            comparison = create_comparison(
                survey, parent, definitions
            )
            weights = comparison.target_weights

        for child in children:
            rows.append({
                "parent_name": parent,
                "child_name": child,
                "weight": weights[child]
            })

    output = pd.DataFrame(rows)
    output.to_csv("../../weights.csv", index=False, encoding="utf-8-sig")

    print(f"Exported {len(output)} hierarchy relationships.")


def export_example_version_p(survey):
    rows = []

    # Root criteria
    root = create_comparison(survey, "Model jakości", st.root_comparisons)

    for child in st.criteria:
        name = "Satysfakcja" if child == "Satysfakcja użytkowników" else child
        rows.append({
            "parent_name": "Model jakości",
            "child_name": name,
            "weight": root.target_weights[child]
        })

    # Wydajność
    comparison = create_comparison(
        survey, "Wydajność", st.pairwise_comparisons["Wydajność"]
    )

    for child in st.subcriteria["Wydajność"]:
        rows.append({
            "parent_name": "Wydajność",
            "child_name": child,
            "weight": comparison.target_weights[child]
        })

    # Satysfakcja
    comparison = create_comparison(
        survey,
        "Satysfakcja użytkowników",
        st.pairwise_comparisons["Satysfakcja użytkowników"]
    )

    labels = {
        "Łatwość użycia": "Łatwość użycia",
        "Zrozumiałość obsługi": "Zrozumiałość",
        "Łatwość opanowania obsługi": "Łatwość opanowania usługi"
    }

    for child, label in labels.items():
        rows.append({
            "parent_name": "Satysfakcja",
            "child_name": label,
            "weight": comparison.target_weights[child]
        })

    rows.append({
        "parent_name": "Satysfakcja",
        "child_name": "Odporność na błędy użytkownika",
        "weight": None
    })

    # Wiarygodność
    comparison = create_comparison(
        survey, "Wiarygodność", st.pairwise_comparisons["Wiarygodność"]
    )

    rows.append({
        "parent_name": "Wiarygodność",
        "child_name": "Niezawodność",
        "weight": comparison.target_weights["Niezawodność"]
    })

    pd.DataFrame(rows).to_csv("../../weights.csv", index=False)


def export_survey_aligned_version(survey):
    rows = []

    hierarchy = {
        "Model jakości": st.criteria,
        "Wydajność": st.subcriteria["Wydajność"],
        "Satysfakcja": st.subcriteria["Satysfakcja użytkowników"],
        "Wiarygodność": st.subcriteria["Wiarygodność"]
    }

    for parent, children in hierarchy.items():
        definitions = (
            st.root_comparisons
            if parent == "Model jakości"
            else st.pairwise_comparisons[
                "Satysfakcja użytkowników" if parent == "Satysfakcja" else parent
            ]
        )

        comparison = create_comparison(survey, parent, definitions)

        for child in children:
            rows.append({
                "parent_name": parent,
                "child_name": "Satysfakcja" if child == "Satysfakcja użytkowników" else child,
                "weight": comparison.target_weights[child]
            })

    pd.DataFrame(rows).to_csv("../../weights_survey_aligned.csv", index=False)

def export_user_surveys(survey):
    opinions = get_opinions(survey)
    opinions = convert_opinions_to_numeric(opinions)
    opinions = rename_opinion_columns(opinions)

    opinions.to_csv("../../user_surveys.csv", index=False)

def prepare_intuition():
    survey = read_survey()
    survey = data_cleaning(survey)

    options = choose_category(survey)

    return survey, options


def intuition(survey, options, selections=None):
    survey = filter_survey_by_categories(
        survey,
        options,
        selections
    )

    export_user_surveys(survey)
    export_example_version(survey)

    return survey

# def intuition_interactive():
#     survey = read_survey()
#     survey = data_cleaning(survey)

#     survey = filter_survey_by_categories(survey)

#     # print(f"\nRespondents included: {len(survey)}")

#     export_user_surveys(survey)
#     export_example_version(survey)

#     return survey