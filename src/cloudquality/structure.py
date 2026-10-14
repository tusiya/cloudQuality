criteria = ["Funcjonalność", "Wydajność", "Satysfakcja użytkowników", "Wiarygodność", "Elastyczność", "Ochrona"]

# WAGI:
# 31 - integracyjnosc vs konfiigur
# 32 - funkcjonanosc vs wydajnosc
# 33 - funkcjonaln vs prostota obslugi
# 34 - vs Wiarygodność
# 35 - vs elastycznosc
# 36 - vs kontolra dostepu
# 37 - wydajnosc vs prostota obsluga
# 38 - vs Wiarygodność
# 39 - vs elastycznosc
# 40 - kontrola dostepnych
# 41 - prostota ob vs Wiarygodność
# 42 - vs elastycznosc
# 43 - vs kontrola dostepnych
# 44 - wiaryg vs elastycznosc
# 45 - wiaryg vs kontrola
# 46 - elastycznosc vs kontrola

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
    "Wydajność czasowa": ["Średni czas reakcji", "Prawidłowy czas reakcji"], # czas reakcji jako jedno pytanie w ankiecie
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