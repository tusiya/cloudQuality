import pandas as pd
import re
import structure as st    # plik zawierający kryteria oceny
import ahpy as a

def read_survey():
    survey = pd.read_csv("resources/"+st.FILENAME+".csv")
    survey = st.change_survey_colnames(survey)
    return survey

def data_cleaning(survey):
    for crit in st.data_removing_criteria:
        survey = survey[survey[crit[0]] != crit[1]]
    
    survey = survey.drop(columns=[
        "O12 Współistnienie z innymi usługami",
        "W3 Współistnienie z innymi usługami vs Zgodność formatów danych"
    ])

    return survey.reset_index(drop=True)

def choose_category(survey):
    print("\n\nABY WYBRAĆ KATEGORIE UŻYTKOWNIKÓW, PODAJ NUMERY IM ODPOWIADAJĄCE:")

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
        # print(f"\n{'─' * 50}")
        print(f"\n")
        print(col)
        print('─' * 50)

        for option_id, value in values.items():
            print(f"{option_id:>3} │ {value}")

    print(f"\n\n")

    return options

def convert_to_ahp(value):
    value = float(value)
    if value == 5:
        return 1
    elif value > 5:
        return 1 / (5 - (value - 5) / 2.5)
    else:
        return 5 - value / 2.5
    
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

def rename_opinion_columns(opinions):
    return opinions.rename(columns=st.OPINION_COLUMN_NAMES)

def intuition():
    survey = read_survey()
    survey = data_cleaning(survey)

    print(survey.shape)
    print(survey.head())

    for value in [0, 2.5, 5, 7.5, 10]:
        print(value, "->", convert_to_ahp(value))

    comparison = a.Compare(
        name="Test",
        comparisons={
            ("A", "B"): 3
        },
        precision=3
    )

    print(comparison.target_weights)


    opinions = get_opinions(survey)
    print(opinions.head())

    print("--------------------------")


    opinions = get_opinions(survey)
    opinions = convert_opinions_to_numeric(opinions)
    opinions = rename_opinion_columns(opinions)

    print(opinions.columns.tolist())

    opinions.to_csv("../../user_surveys.csv", index=False)