import pandas as pd
import re
import structure as st    # plik zawierający kryteria oceny

def read_survey():
    survey = pd.read_csv("resources/"+st.FILENAME+".csv")
    survey = st.change_survey_colnames(survey)
    return survey

def data_cleaning(survey):
    for crit in st.data_removing_criteria:
        survey = survey[survey[crit[0]] != crit[1]]

    # pd.set_option("display.max_columns", None)
    # print(survey.iloc[:, :20].describe())
    # print(survey.iloc[:, 20:].describe())

    return survey

# 

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