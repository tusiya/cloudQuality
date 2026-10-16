FILENAME = "initial_version" # nazwa pliku z danymi od respondentów znajdującego się w folderze resources

criteria = ["Funcjonalność", "Wydajność", "Satysfakcja użytkowników", "Wiarygodność", "Elastyczność", "Ochrona"]

subcriteria = {
    "Funcjonalność": ["Kompletność funcjonalna", "Poprawność funkcjonalna"],
    "Wydajność": ["Wydajność czasowa", "Efektywność interakcji"],
    "Satysfakcja użytkowników": ["Łatwość użycia", "Zrozumiałość obsługi", "Łatwość opanowania obsługi"],
    "Wiarygodność": ["Odporność na błędy użytkownika", "Niezawodność"],
    "Elastyczność": ["Integracyjność", "Konfigurowalność"],
    "Ochrona": ["Poufność"]
}

subsubcriteria = {
    "Kompletność funcjonalna": ["Pokrycie funkcjonalne"],
    "Poprawność funkcjonalna": ["Poprawność funkcjonalna"],
    "Wydajność czasowa": ["Prawidłowy czas reakcji"],
    "Efektywność interakcji": ["Liczba kroków potrzebnych do wykonania zadania"],
    "Łatwość użycia":["Sukces zadania użytkownika"],
    "Zrozumiałość obsługi": ["Możliwość monitorowania"],
    "Łatwość opanowania obsługi": ["Samoopis interfejsu użytkownika", "Ustawienie wartości domyślnych"],
    "Odporność na błędy użytkownika": ["Możliwość anulowania działań", "Ochrona przed błędami użytkownika"],
    "Niezawodność": ["Dostępność usługi"],
    "Integracyjność": ["Współistnienie z innymi usługami", "Zgodność formatów danych"],
    "Konfigurowalność": ["Funkcjonalna możliwość personalizacji", "Konfigurowalność interfejsu użytkownika"],
    "Poufność": ["Kontrola dostępu"]
}

def change_survey_colnames(survey): # kolumny z ocenami zaczynają się na "O", kolumny z wagamim na "W", a następnie numer i spacja
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

    cols[21] = "W1 Samoopis interfejsu użytkownika vs Ustawienie wartości domyślnych"
    cols[22] = "W2 Możliwość anulowania działań vs Ochrona przed błędami użytkownika"
    cols[23] = "W3 Współistnienie z innymi usługami vs Zgodność formatów danych"
    cols[24] = "W4 Funkcjonalna możliwość personalizacji vs Konfigurowalność interfejsu użytkownika"

    cols[25] = "W5 Kompletność funcjonalna vs Poprawność funkcjonalna"
    cols[26] = "W6 Wydajność czasowa vs Efektywność interakcji"
    cols[27] = "W7 Łatwość użycia vs Zrozumiałość obsługi"
    cols[28] = "W8 Łatwość użycia vs Łatwość opanowania obsługi"
    cols[29] = "W9 Zrozumiałość obsługi vs Łatwość opanowania obsługi"
    cols[30] = "W10 Odporność na błędy użytkownika vs Niezawodność"
    cols[31] = "W11 Integracyjność vs Konfigurowalność"

    cols[32] = "W12 Funkcjonalność vs Wydajność"
    cols[33] = "W13 Funkcjonalność vs Satysfakcja użytkowników"
    cols[34] = "W14 Funkcjonalność vs Wiarygodność"
    cols[35] = "W15 Funkcjonalność vs Elastyczność"
    cols[36] = "W16 Funkcjonalność vs Ochrona"
    cols[37] = "W17 Wydajność vs Satysfakcja użytkowników"
    cols[38] = "W18 Wydajność vs Wiarygodność"
    cols[39] = "W19 Wydajność vs Elastyczność"
    cols[40] = "W20 Wydajność vs Ochrona"
    cols[41] = "W21 Satysfakcja użytkowników vs Wiarygodność"
    cols[42] = "W22 Satysfakcja użytkowników vs Elastyczność"
    cols[43] = "W23 Satysfakcja użytkowników vs Ochrona"
    cols[44] = "W24 Wiarygodność vs Elastyczność"
    cols[45] = "W25 Wiarygodność vs Ochrona"
    cols[46] = "W26 Elastyczność vs Ochrona"
    
    survey.columns = cols
    survey = survey.drop(columns=survey.columns[[0]])

    return survey

data_removing_criteria = [["Wiek", "Mniej niż 18"], # nazwa kolumny, wartość
                          ["Grupa", "W ogóle nie korzystam"]]