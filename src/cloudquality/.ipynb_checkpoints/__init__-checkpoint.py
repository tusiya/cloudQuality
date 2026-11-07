# SPDX-FileCopyrightText: 2026-present Marta Szulca (tusiya) <szulcam2410@gmail.com>, Hubert Stankiewicz (limebel) <stankiewicz.huberto@gmail.com>
#
# SPDX-License-Identifier: MIT

import variants.intuition as vi

survey = vi.read_survey()
survey = vi.data_cleaning(survey)

# print(survey.shape)

# print("----------------------------------------------------\n\n-------------------------------------------------------")

categories = vi.choose_category(survey)

raw = input("Podaj numery (oddzielone przecinkami) lub Enter, aby pominąć: ")
choices = [int(x.strip()) for x in raw.split(",") if x.strip()]

for category, values in categories.items():
    ids = list(values.keys())
    for choice in categories["Wiek"]:
        print("Chosen ", choice, " in ", category)
    # print(category, min(ids), max(ids))

for i in range(len(categories)):
    print(list(categories.keys())[i], "test")

for category, values in categories.items():
    ids = list(values.keys())
    print(category, min(ids), max(ids))

categories["Wiek"][1]  # '18 - 25'
categories["Grupa"][4] # 'W ramach spotkań z klientami, pracy zdalnej, itp.'