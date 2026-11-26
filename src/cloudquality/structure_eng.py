FILENAME = "initial_version"  # name of the file containing respondents' data, located in the resources folder

criteria = ["Functionality", "Performance", "User Satisfaction", "Reliability", "Flexibility", "Security"]

subcriteria = {
    "Functionality": ["Functional completeness", "Functional correctness"],
    "Performance": ["Time behavior", "Interaction efficiency"],
    "User Satisfaction": ["Ease of use", "Operability understandability", "Operability learnability"],
    "Reliability": ["User error resistance", "Reliability"],
    "Flexibility": ["Interoperability", "Configurability"],
    "Security": ["Confidentiality"]
}

subsubcriteria = {
    "Functional completeness": ["Functional coverage"],
    "Functional correctness": ["Functional correctness"],
    "Time behavior": ["Correct response time"],
    "Interaction efficiency": ["Number of steps required to complete a task"],
    "Ease of use": ["User task success"],
    "Operability understandability": ["Monitorability"],
    "Operability learnability": ["Self-descriptiveness of the user interface", "Default value setting"],
    "User error resistance": ["Ability to cancel actions", "User error protection"],
    "Reliability": ["Service availability"],
    "Interoperability": ["Coexistence with other services", "Data format compatibility"],
    "Configurability": ["Functional customizability", "User interface configurability"],
    "Confidentiality": ["Access control"]
}


def change_survey_colnames(survey):
    # Rating columns start with "O", weight columns start with "W", followed by a number and a space
    cols = list(survey.columns)

    cols[1] = "Age"
    cols[2] = "Group"
    cols[3] = "Usage Frequency"
    cols[4] = "Digital Competence"

    cols[5] = "O1 Functional coverage"
    cols[6] = "O2 Functional correctness"
    cols[7] = "O3 Average response time"
    cols[8] = "O4 Number of steps required to complete a task"
    cols[9] = "O5 User task success"
    cols[10] = "O6 Monitorability"
    cols[11] = "O7 Self-descriptiveness of the user interface"
    cols[12] = "O8 Default value setting"
    cols[13] = "O9 Ability to cancel actions"
    cols[14] = "O10 User error protection"
    cols[15] = "O11 Service availability"
    cols[16] = "O12 Coexistence with other services"
    cols[17] = "O13 Data format compatibility"
    cols[18] = "O14 Functional customizability"
    cols[19] = "O15 User interface configurability"
    cols[20] = "O16 Access control"

    cols[21] = "W1 Self-descriptiveness of the user interface vs Default value setting"
    cols[22] = "W2 Ability to cancel actions vs User error protection"
    cols[23] = "W3 Coexistence with other services vs Data format compatibility"
    cols[24] = "W4 Functional customizability vs User interface configurability"

    cols[25] = "W5 Functional completeness vs Functional correctness"
    cols[26] = "W6 Time behavior vs Interaction efficiency"
    cols[27] = "W7 Ease of use vs Operability understandability"
    cols[28] = "W8 Ease of use vs Operability learnability"
    cols[29] = "W9 Operability understandability vs Operability learnability"
    cols[30] = "W10 User error resistance vs Reliability"
    cols[31] = "W11 Interoperability vs Configurability"

    cols[32] = "W12 Functionality vs Performance"
    cols[33] = "W13 Functionality vs User Satisfaction"
    cols[34] = "W14 Functionality vs Reliability"
    cols[35] = "W15 Functionality vs Flexibility"
    cols[36] = "W16 Functionality vs Security"
    cols[37] = "W17 Performance vs User Satisfaction"
    cols[38] = "W18 Performance vs Reliability"
    cols[39] = "W19 Performance vs Flexibility"
    cols[40] = "W20 Performance vs Security"
    cols[41] = "W21 User Satisfaction vs Reliability"
    cols[42] = "W22 User Satisfaction vs Flexibility"
    cols[43] = "W23 User Satisfaction vs Security"
    cols[44] = "W24 Reliability vs Flexibility"
    cols[45] = "W25 Reliability vs Security"
    cols[46] = "W26 Flexibility vs Security"

    survey.columns = cols
    survey = survey.drop(columns=survey.columns[[0]])

    return survey


data_removing_criteria = [
    ["Age", "Under 18"],  # column name, value
    ["Group", "I do not use it at all"]
]