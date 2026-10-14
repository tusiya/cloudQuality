import pandas as pd

FILENAME = "initial_version"

def read_survey():
    survey = pd.read_csv("resources/"+FILENAME+".csv")

    cols = list(survey.columns)
    cols[1] = "Wiek"
    cols[2] = "Grupa"
    cols[3] = "Częstotliwość użytkowania"
    cols[4] = "Kompetencje cyfrowe"

    cols[5] = "O1 Pokrycie funkcjonalne"
    cols[6] = "O2 Poprawność funkcjonalna"
    cols[7] = "O3 Średni czas reakcji"
    cols[8] = "O4 Liczba kroków potrzebnych do wykonania zadania"
    cols[9] = "O5 Sukces zadania użytkownika"
    cols[10] = "O6 Możliwość monitorowania"
    cols[11] = "O7 Samoopis interfejsu użytkownika"
    cols[12] = "O8 Ustawienie wartości domyślnych"
    cols[13] = "O9 Możliwość anulowania działań"
    cols[14] = "O10 Ochrona przed błędami użytkownika"
    cols[15] = "O11 Dostępność usługi"
    cols[16] = "O12 Współistnienie z innymi usługami"
    cols[17] = "O13 Zgodność formatów danych"
    cols[18] = "O14 Funkcjonalna możliwość personalizacji"
    cols[19] = "O15 Konfigurowalność interfejsu użytkownika"
    cols[20] = "O16 Kontrola dostępu"
    
    survey.columns = cols

    survey = survey.drop(columns=survey.columns[[0]])
    return survey

