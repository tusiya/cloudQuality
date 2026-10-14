import pandas as pd

FILENAME = "initial_version"

def read_survey():
    survey = pd.read_csv("resources/"+FILENAME+".csv")
    return survey
