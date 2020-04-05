# -*- coding: utf-8 -*-
"""

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KfVp8srjYI2g8voPOUgtxbJ4vWifm-js
"""

from datetime import datetime
from datetime import date, timedelta
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import dateutil.relativedelta
from tabulate import tabulate
from pandas._libs.tslibs.offsets import relativedelta
import logging

justLines = []
dictIndi = {}
dictFam = {}
with open('Family.ged') as f:
    lines = f.read().splitlines()
    justLines.append(lines)
lines = [[el] for el in lines]
for i in range(len(lines)):
    if((len(lines[i][0].strip().split())) < 2):
        lines[i] = "Incomplete GEDCOM on Line "+str(i)
    else:
        lines[i] = lines[i][0].strip().split(" ", 2)
        if(len(lines[i]) > 2 and lines[i][1] in ['INDI', 'FAM']):
            lines[i] = "Invalid GEDCOM on Line "+str(i)
        elif(len(lines[i]) > 2 and lines[i][2] in ['INDI', 'FAM']):
            lines[i][1], lines[i][2] = lines[i][2], lines[i][1]

valid_tags = {'INDI': '0', 'NAME': '1', 'SEX': '1', 'BIRT': '1', 'DEAT': '1', 'FAMC': '1', 'FAMS': '1', 'FAM': '0',
              'MARR': '1', 'HUSB': '1', 'WIFE': '1', 'CHIL': '1', 'DIV': '1', 'DATE': '2', 'HEAD': '0',
              'TRLR': '0', 'NOTE': '0'}

gedcom_out = []
for i in range(len(lines)):

    # print("-->"+justLines[0][i])
    if(len(lines[i]) > 2):
        if(lines[i][1] in valid_tags.keys() and valid_tags[lines[i][1]] == (lines[i][0])):
            # print("<--"+lines[i][0]+"|"+lines[i][1]+"|Y|"+lines[i][2])
            gedcom_out.append((lines[i][0], lines[i][1], lines[i][2]))
        elif(lines[i][0:2] == "In"):
            # print("<--"+lines[i])
            gedcom_out.append(lines[i])
        else:
            continue
            # print("<--"+lines[i][0]+"|"+lines[i][1]+"|N|"+lines[i][2])
    elif(len(lines[i]) == 2):
        if(lines[i][1] in valid_tags.keys() and valid_tags[lines[i][1]] == (lines[i][0])):
            # print("<--"+lines[i][0]+"|"+lines[i][1]+"|Y|")
            gedcom_out.append((lines[i][0], lines[i][1]))
        else:
            # print("<--"+lines[i][0]+"|"+lines[i][1]+"|N|")
            continue
gedcom_out.pop(0)
gedcom_out.pop(-1)
gedcom_out = list(filter((('1', 'BIRT')).__ne__, gedcom_out))

flag = 0
for i in range(len(gedcom_out)):
    if(i > 500):
        break
    lst_vals = []
    j = i+1
    if(gedcom_out[i][1] == 'INDI' and gedcom_out[i][0] == '0'):
        while(gedcom_out[j][1] != 'INDI'):
            key = gedcom_out[i][2][1:-1]
            if(gedcom_out[j][1] == 'FAM' and gedcom_out[j][0] == '0'):
                flag = 1
                break
            elif(gedcom_out[j][1] == 'DEAT' and gedcom_out[j][2] == 'Y'):
                lst_vals.append(('DEAT', gedcom_out[j+1][2]))
                j += 1
            elif(gedcom_out[j][1] == 'FAMS' or gedcom_out[j][1] == 'FAMC'):
                lst_vals.append((gedcom_out[j][1], gedcom_out[j][2][1:-1]))
            else:
                lst_vals.append((gedcom_out[j][1], gedcom_out[j][2]))
            j += 1
        dictIndi.update({key: lst_vals})
        if(flag == 1):
            break

# individuals dataframe
df_indi = pd.DataFrame(columns=[
                       'ID', 'Name', 'Gender', 'Birthday', 'Age', 'Alive', 'Death', 'Child', 'Spouce'])
name, gender, birt, deat = "", "", "", ""
alive = True
for key, value in dictIndi.items():
    age = 0
    deat_count = 0
    # print(value)
    for i in range(len(value)):
        famc, fams = "", ""
        if(value[i][0] == 'NAME'):
            name = value[i][1]
        if(value[i][0] == 'SEX'):
            gender = value[i][1]
        if(value[i][0] == 'DATE'):
            birt = value[i][1]
            birt = datetime.datetime.strptime(birt, '%d %b %Y').date()
        if(value[i][0] == 'DEAT'):
            deat = value[i][1]
            deat = datetime.datetime.strptime(deat, '%d %b %Y').date()
            deat_count = deat_count + 1
        if(value[i][0] == 'FAMC'):
            famc = value[i][1]
        if(value[i][0] == 'FAMS'):
            fams = value[i][1]
        if(deat_count < 1):
            deat = 'NA'
    if (any('DEAT' in i for i in value)):
        alive = False
        age = relativedelta(deat, birt).years
    else:
        age = relativedelta(datetime.datetime.now(), birt).years
        alive = True

    df_indi = df_indi.append({'ID': key, 'Name': name, 'Gender': gender, 'Birthday': birt,
                              'Alive': alive, 'Death': deat, 'Child': famc, 'Spouce': fams, 'Age': age}, ignore_index=True)
    df_indi = (df_indi.replace(r'^\s*$', 'NA', regex=True))

flag = 0
for i in range(len(gedcom_out)):
    if(i > 1000):
        break
    lst_vals = []
    j = i+1
    if(gedcom_out[i][1] == 'FAM' and gedcom_out[i][0] == '0'):
        while(j < len(gedcom_out)):
            key = gedcom_out[i][2][1:-1]
            # husb wife child extract
            if(gedcom_out[j][1] != 'MARR' and gedcom_out[j][1] != 'DIV' and gedcom_out[j][1] != 'DATE' and gedcom_out[j][1] != 'FAM'):
                lst_vals.append((gedcom_out[j][1], gedcom_out[j][2][1:-1]))
            # married date extract
            elif(gedcom_out[j][1] == 'MARR' and len(gedcom_out[j+1]) > 2):
                lst_vals.append(('MARR', gedcom_out[j+1][2]))
            # divo date extract
            elif(gedcom_out[j][1] == 'DIV' and len(gedcom_out[j+1]) > 2):
                lst_vals.append(('DIV', gedcom_out[j+1][2]))
            # if next fam then break
            elif(gedcom_out[j][1] == 'FAM' and gedcom_out[j][0] == '0'):
                flag = 1
                break
            j += 1
        dictFam.update({key: lst_vals})

# Families dataframe
husb_id, wife_id = 0, 0
husb_name, wife_name = "", ""
child = []
df_fam = pd.DataFrame(columns=['ID', 'Married', 'Divorced',
                               'Husband ID', 'Husband Name', 'Wife ID', 'Wife Name', 'Children'])
for key, value in dictFam.items():
    child = []
    married, div = "", ""
    for i in range(len(value)):
        if(value[i][0] == 'HUSB'):
            husb_id = value[i][1]
            husb_name = dictIndi[husb_id][0][1]
        if(value[i][0] == 'WIFE'):
            wife_id = value[i][1]
            wife_name = dictIndi[wife_id][0][1]
        if(value[i][0] == 'CHIL'):
            child.append(value[i][1])
        if(value[i][0] == 'MARR'):
            married = value[i][1]
            married = datetime.datetime.strptime(married, '%d %b %Y').date()
        if(value[i][0] == 'DIV'):
            div = value[i][1]
            div = datetime.datetime.strptime(div, '%d %b %Y').date()

    df_fam = df_fam.append({'ID': key, 'Married': married, 'Divorced': div, 'Husband ID': husb_id,
                            'Husband Name': husb_name, 'Wife ID': wife_id, 'Wife Name': wife_name, 'Children': child, }, ignore_index=True)
    df_fam = (df_fam.replace(r'^\s*$', 'NA', regex=True))

print("Individuals")
print(tabulate(df_indi, headers='keys', tablefmt='psql'))
print("Families")
print(tabulate(df_fam, headers='keys', tablefmt='psql'))
print("\n")

##########__________________Vedadnya's Code__________________########################

# User Story 03 : VJ
# Birth before Death


def us03():
    df_copy = df_indi.copy()
    todayDate = datetime.datetime.strptime('2020-04-01', '%Y-%m-%d').date()
    df_copy = df_copy.replace({'Death': 'NA'}, todayDate)
    correct = []
    error = []
    for i, j in df_copy.iterrows():
        if df_copy['Death'][i] > df_copy['Birthday'][i]:
            correct.append("CORRECT: " + "INDIVIDUAL: " + "US03: " + str(i) + ": " + " " + df_copy['ID'][i] + ": " + df_copy['Name'][i] + " has a correct Birthdate: " + str(
                df_copy['Birthday'][i]) + " with respect to Deathdate: " + str(df_copy['Death'][i]))
        else:
            error.append("ERROR: " + "INDIVIDUAL: " + "US03: " + str(i) + ": " + " " + df_copy['ID'][i] + ": " + df_copy['Name'][i] + " has a future Birthdate: " + str(
                df_copy['Birthday'][i]) + " with respect to Deathdate: " + str(df_copy['Death'][i]))
    return error


us03Error = us03()
print(*us03Error, sep="\n")

# User Story 04 : VJ
# Marriage before Divorce


def us04():
    df_copy = df_fam.copy()
    correct = []
    error = []
    for i, j in df_copy.iterrows():
        if df_copy['Divorced'][i] == 'NA' or df_copy['Married'][i] == 'NA':
            continue
        if df_copy['Divorced'][i] > df_copy['Married'][i]:
            correct.append("CORRECT: " + "FAMILY: " + "US04: " + str(i) + ": " + " " + df_copy['ID'][i] + ": " + " have a correct Marriage Date : " + str(
                df_copy['Married'][i]) + " with respect to Divorced Date : " + str(df_copy['Divorced'][i]))
        else:
            error.append("ERROR: " + "FAMILY: " + "US04: " + str(i) + ": " + " " + df_copy['ID'][i] + ": " + " have a future Marriage Date : " + str(
                df_copy['Married'][i]) + " with respect to Divorced Date : " + str(df_copy['Divorced'][i]))
    return error


us04Error = us04()
print(*us04Error, sep="\n")


# User Story 17 : VJ
# No marriages to children

def us17():
    df_copy = df_fam.copy()
    error = []
    for k in range(0, df_copy.shape[0]):
        for i, j in df_copy.iterrows():
            if df_copy['Husband ID'][i] in df_copy['Children'][k]:
                if df_copy['Wife ID'][i] == df_copy['Wife ID'][k]:
                    error.append("ERROR: " + "FAMILY: " + "US17: " + str(i) + ": " + " " +
                                 df_copy['ID'][i] + ": " + "Parent " + df_copy['Husband ID'][i] + " is married to their child : " + df_copy['Wife ID'][i])
                else:
                    continue
            elif df_copy['Wife ID'][i] in df_copy['Children'][k]:
                if df_copy['Husband ID'][i] == df_copy['Husband ID'][k]:
                    error.append("ERROR: " + "FAMILY: " + "US17: " + str(i) + ": " + " " +
                                 df_copy['ID'][i] + ": " + "Parent " + df_copy['Husband ID'][i] + " is married to their child : " + df_copy['Wife ID'][i])
                else:
                    continue
            else:
                continue
    return error


us17Error = us17()
print(*us17Error, sep="\n")


# User Story 18 : VJ
# Siblings should not marry

def us18():
    df_copy = df_fam.copy()
    error = []
    for i, j in df_copy.iterrows():
        for item in df_copy['Children']:
            if df_copy['Husband ID'][i] in item:
                if df_copy['Wife ID'][i] in item:
                    error.append("ERROR: " + "FAMILY: " + "US18: " + str(i) + ": " + " " +
                                 df_copy['ID'][i] + ": " + "Siblings " + df_copy['Husband ID'][i] + " and " + df_copy['Wife ID'][i] + " are married")
                else:
                    continue
            else:
                continue
    return error


us18Error = us18()
print(*us18Error, sep="\n")

# User Story 34 : VJ
# List large age differences


def us34():
    df_copy = df_indi.copy()
    error = []
    dict = {}
    for i, j in df_copy.iterrows():
        dict[df_copy['ID'][i]] = df_copy['Age'][i]
    for i, j in df_fam.iterrows():
        if dict[df_fam['Husband ID'][i]] > dict[df_fam['Wife ID'][i]]:
            if dict[df_fam['Husband ID'][i]] > dict[df_fam['Wife ID'][i]]*2:
                error.append("ERROR FAMILY US34 : " + df_fam['Husband ID'][i] +
                             " :The Husband is more than double the age of " + df_fam['Wife ID'][i] + " :The Wife ")
        else:
            if dict[df_fam['Wife ID'][i]] > dict[df_fam['Husband ID'][i]]*2:
                error.append("ERROR FAMILY US34 : " +
                             df_fam['Wife ID'][i]+" :The Wife is more than double the age of " + df_fam['Husband ID'][i] + " :The Husband ")
    return error


us34Error = us34()
print(*us34Error, sep="\n")

# User Story 20 : VJ
# Uncles and Aunts


def us20():
    df_copy = df_fam.copy()
    correct = []
    error = []
    children = ""
    uncleAunts = ""
    for i, j in df_copy.iterrows():
        for k, l in df_copy.iterrows():
            if df_copy['Husband ID'][i] in df_copy['Children'][k] and len(df_copy['Children'][k]) > 1:
                if len(df_copy['Children'][i]) != 0:
                    for index in range(len(df_copy['Children'][i])):
                        children += " " + str(df_copy['Children'][i][index])
                    for index in range(len(df_copy['Children'][k])):
                        if str(df_copy['Children'][k][index]) != str(df_copy['Wife ID'][i]) and str(df_copy['Children'][k][index]) != str(df_copy['Husband ID'][i]):
                            uncleAunts += str(df_copy['Children'][k][index])
                    error.append("ENTRY FOUND US20 " + "Children : " + children +
                                 " have Uncle/s and Aunt/s with ID/s " + uncleAunts)
                    children = ""
                    uncleAunts = ""
            elif df_copy['Wife ID'][i] in df_copy['Children'][k] and len(df_copy['Children'][k]) > 1:
                if len(df_copy['Children'][i]) != 0:
                    for index in range(len(df_copy['Children'][i])):
                        children += " " + str(df_copy['Children'][i][index])
                    for index in range(len(df_copy['Children'][k])):
                        if str(df_copy['Children'][k][index]) != str(df_copy['Wife ID'][i]) and str(df_copy['Children'][k][index]) != str(df_copy['Husband ID'][i]):
                            uncleAunts += str(df_copy['Children'][k][index])
                    error.append("ENTRY FOUND US20 " + "Children : " + children +
                                 " have Uncle/s and Aunt/s with ID/s " + uncleAunts)
                    children = ""
                    uncleAunts = ""
    return error


us20Error = us20()
print(*us20Error, sep="\n")


##########__________________Pranav's Code__________________########################


# User Story 05: Marriage before death
def us_05_marriage_before_death():

    df_copy = df_indi.copy()
    #todayDate = datetime.datetime.today().strftime('%Y-%m-%d')
    todayDate = datetime.datetime.strptime('2020-04-01', '%Y-%m-%d').date()
    #todayDate = datetime.datetime.strptime(todayDate, '%Y-%m-%d').date()
    df_copy = df_copy.replace({'Death': 'NA'}, todayDate)
    correct = []
    wrong = []

    df_us_05 = pd.DataFrame(columns=[
                            'ID', 'Name', 'Gender', 'Birthday', 'Age', 'Alive', 'Death', 'Child', 'Spouse'])
    for index, col in df_fam.iterrows():
        husb_id = col["Husband ID"]
        marriage_date = col['Married']
        wife_id = col["Wife ID"]

        for index, col in df_copy.iterrows():
            # check if indi id matches with hus_id or wife_id
            if ((col["ID"] == husb_id) or (col["ID"] == wife_id)):
                # given condition if marriage exists, death exists
                if ((marriage_date != "NA") and (col["Death"] > marriage_date)):
                    df_us_05 = df_us_05.append(col)

    error = pd.concat([df_us_05, df_copy],
                      sort=False).drop_duplicates(keep=False)
    df_us_05['Outcome'] = True
    error['Outcome'] = False

    result = df_us_05.append(error, ignore_index=True)
    result = result.sort_values(by=['ID'], ascending=True)
    for i, j in result.iterrows():
        if j["Outcome"] is True:
            correct.append("CORRECT: " + "INDIVIDUAL: " + "US05: " + str(i) + ": " + " " +
                           j['ID'] + ": " + j['Name'] + " has a correct Marriage Date with respect to Deathdate: " + str(j['Death']))

        else:
            wrong.append("ERROR: " + "INDIVIDUAL: " + "US05: " + str(i) + ": " + " " +
                         j['ID'] + ": " + j['Name'] + " has an erroneous Marriage Date with respect to Deathdate: " + str(j['Death']))

    return wrong


us05Error = us_05_marriage_before_death()
print(*us05Error, sep="\n")


# User Story 06: divorce before death
def us_06_divorce_before_death():

    df_copy = df_indi.copy()
    #todayDate = datetime.datetime.today().strftime('%Y-%m-%d')
    todayDate = datetime.datetime.strptime('2020-04-01', '%Y-%m-%d').date()
    #todayDate = datetime.datetime.strptime(todayDate, '%Y-%m-%d').date()
    df_copy = df_copy.replace({'Death': 'NA'}, todayDate)
    correct = []
    wrong = []

    df_us_06 = pd.DataFrame(columns=[
                            'ID', 'Name', 'Gender', 'Birthday', 'Age', 'Alive', 'Death', 'Child', 'Spouse'])
    for index, col in df_fam.iterrows():
        husb_id = col["Husband ID"]
        divorce_date = col['Divorced']
        marriage_date = col['Married']
        wife_id = col["Wife ID"]

        for index, col in df_copy.iterrows():
            # check if indi id matches with hus_id or wife_id
            if ((col["ID"] == husb_id) or (col["ID"] == wife_id)):
                # given condition if divorce exists, death exists
                if ((divorce_date != "NA") and (marriage_date != "NA") and (col["Death"] > divorce_date)):
                    df_us_06 = df_us_06.append(col)

    error = pd.concat([df_us_06, df_copy],
                      sort=False).drop_duplicates(keep=False)
    df_us_06['Outcome'] = True
    error['Outcome'] = False

    result = df_us_06.append(error, ignore_index=True)
    result = result.sort_values(by=['ID'], ascending=True)
    for i, j in result.iterrows():
        if j["Outcome"] is True:
            correct.append("CORRECT: " + "INDIVIDUAL: " + "US06: " + str(i) + ": " + " " +
                           j['ID'] + ": " + j['Name'] + " has a correct Divorce Date with respect to Deathdate: " + str(j['Death']))

        else:
            wrong.append("ERROR: " + "INDIVIDUAL: " + "US06: " + str(i) + ": " + " " +
                         j['ID'] + ": " + j['Name'] + " has an erroneous Divorce Date with respect to Deathdate: " + str(j['Death']))
    return wrong


us06Error = us_06_divorce_before_death()
print(*us06Error, sep="\n")


# PN: User Story 21: correct gender for role
def US21():

    df_copy = df_indi.copy()
    wrong = []

    for index, col in df_fam.iterrows():
        husb_id = col["Husband ID"]
        wife_id = col["Wife ID"]

        for index, col in df_copy.iterrows():
            if ((col["ID"] == husb_id)):
                if (col["Gender"] == 'M'):
                    continue
                elif (col["Gender"] == 'F'):
                    wrong.append(("ERROR: FAMILY: US21: " + str(index) +
                                  ": Correct gender for role is violated for husband ID: " + col['ID'] + " and Name: " + col['Name']))

            if ((col["ID"] == wife_id)):
                if (col["Gender"] == 'F'):
                    continue
                elif (col["Gender"] == 'M'):
                    wrong.append(("ERROR: FAMILY: US21: " + str(index) +
                                  ": Correct gender for role is violated for wife ID: " + col['ID'] + " and Name: " + col['Name']))

    return wrong


us21Error = US21()
print(*us21Error, sep="\n")

# PN: User Story 22: Unique IDs


def US22():

    df_copy_indi = df_indi.copy()
    date_value = datetime.datetime.strptime('1997-03-02', '%Y-%m-%d').date()
    df_copy_indi = df_copy_indi.append(
        {'ID': 'I1', 'Name': 'Robb /Stark/', 'Gender': 'M', 'Birthday': date_value, 'Age': 22}, ignore_index=True)
    df_copy_indi = df_copy_indi.replace(np.nan, 'NA', regex=True)
    error_indi = []
    error_fam = []
    error = []

    df_copy_fam = df_fam.copy()
    df_copy_fam = df_copy_fam.append({'ID': 'F1', 'Husband ID': 'I3', 'Husband Name': 'Ned Stark',
                                      'Wife ID': 'I4', 'Wife Name': 'Cate Laniaster', 'Children': []}, ignore_index=True)
    df_copy_fam = df_copy_fam.replace(np.nan, 'NA', regex=True)

    non_unique_indi = df_copy_indi[df_copy_indi.duplicated(['ID'], keep=False)]
    non_unique_fam = df_copy_fam[df_copy_fam.duplicated(['ID'], keep=False)]

    for index, col in non_unique_indi.iterrows():
        error_indi.append(("ERROR: INDIVIDUAL: US22: " + str(index) +
                           ": Unique ID violated for : " + col['ID'] + " and Name: " + col['Name']))

    for index, col in non_unique_fam.iterrows():
        error_fam.append(("ERROR: FAMILY: US22: " + str(index)+": Unique ID violated for : " +
                          col['ID'] + ", Husband Name: " + col['Husband Name'] + " and Wife Name: " + col['Wife Name']))

    error = error_indi + error_fam

    return error


us22Error = US22()
print(*us22Error, sep="\n")

# PN: User Story 23: unique name and birth date


def US23():

    df_copy = df_indi.copy()
    row = df_copy.iloc[2:4]
    df_copy = df_copy.append(row, ignore_index=True)
    name_birthdate = []
    error = []

    for index, col in df_copy.iterrows():
        name = col['Name']
        dob = str(col['Birthday'])
        temp = (name, dob)
        name_birthdate.append(temp)

    count = dict(Counter(name_birthdate))
    for key, value in count.items():
        if value > 1:
            error.append("ERROR: INDIVIDUAL: US23: Unique name & Unique date_of_birth violated for Name: " +
                         str(key[0]) + " and Date of Birth: " + str(key[1]))
    return error


us23Error = US23()
print(*us23Error, sep="\n")

# PN: User Story 24: unique families by spouses
# No more than one family with the same spouses by name and the same marriage date should appear in a GEDCOM file


def US24():

    df_copy = df_fam.copy()
    row = df_copy.iloc[4:6]
    df_copy = df_copy.append(row, ignore_index=True)
    spouses_marriage_date = []
    error = []

    for index, col in df_copy.iterrows():
        marriage_date = col['Married']
        husband_name = col['Husband Name']
        wife_name = col['Wife Name']
        temp = (marriage_date, husband_name, wife_name)
        spouses_marriage_date.append(temp)

    count = dict(Counter(spouses_marriage_date))
    for key, value in count.items():
        if value > 1:
            error.append("ERROR: FAMILY: US24: Unique spouse names & Unique marriage_date violated for Husband Name: " +
                         str(key[1]) + " ,Wife Name: " + str(key[2]) + ", and Marriage Date: " + str(key[0]))
    return error


us24Error = US24()
print(*us24Error, sep="\n")

##########__________________Sanket's Code__________________########################

# US07 : SP
# Less then 150 years old


def US07():
    errors = []
    for i, c in df_indi.iterrows():
        if (df_indi['Age'][i] > 150):
            errors.append("ERROR: "+"INDIVIDUAL: "+"US07: "+str(i)+': '+c['ID']+": "+c['Name']+" is " +
                          str(c['Age'])+" years old which is more then 150")
            #print(*errors, sep="\n")
    if(errors):
        return(errors)
    else:
        errors.append('ERROR: US07: No records found')
        return(errors)


errorUS07 = US07()
print(*errorUS07, sep="\n")

# US08 : SP
# Birth before marriage of Parent


def US08():
    errors = []
    for index, col in df_fam.iterrows():
        id = col['ID']
        marr = col['Married']
        child = col['Children']
        div = col['Divorced']
        for i, c in df_indi.iterrows():
            if(marr != 'NA'):
                if((c['Birthday'] < marr) and (c['ID'] in child)):
                    errors.append("ERROR: "+"FAMILY: "+"US08: "+str(i)+': '+c['ID']+": "+c['Name'] +
                                  " is born before marriage of Parent")
            if(marr != 'NA' and div != 'NA'):
                check = div + dateutil.relativedelta.relativedelta(months=9)
                if((c['Birthday'] > check) and (c['ID'] in child)):
                    errors.append("ERROR: "+"FAMILY: "+"US08: "+str(i)+': ' +
                                  c['ID']+": "+c['Name']+" is born after 9 months from divorce of Parent")
    if(errors):
        return(errors)
    else:
        return("No Errors")


errorUS08 = US08()
print(*errorUS08, sep="\n")


# US35 : SP
# List recent births

def US35():
    errors = []
    dt = date.today() - timedelta(30)
    for i, c in df_indi.iterrows():
        if(c['Birthday'] > dt and c['Birthday'] < date.today()):
            errors.append("ERROR: "+"INDIVIDUAL: "+"US35: "+str(i)+': '+c['ID']+": "+c['Name'] +
                          " is born recently on "+str(c['Birthday']))
    if(errors):
        return(errors)
    else:
        return("No Errors")


errorUS35 = US35()
print(*errorUS35, sep="\n")


# US36 : SP
# List recent deaths

def US36():
    errors = []
    dt = date.today() - timedelta(30)
    for i, c in df_indi.iterrows():
        if(c['Death'] != 'NA'):
            if(c['Death'] > dt and c['Death'] < date.today()):
                errors.append("ERROR: "+"INDIVIDUAL: "+"US36: "+str(i)+': '+c['ID']+": "+c['Name'] +
                              " died recently on "+str(c['Death']))
    if(errors):
        return(errors)
    else:
        return("No Errors")


errorUS36 = US36()
print(*errorUS36, sep="\n")


# US38 : SP
# List upcoming birthdays


def US38():
    errors = []
    dt = date.today() + timedelta(30)
    for i, c in df_indi.iterrows():
        bir = c['Birthday']
        y = date.today().year
        bir = bir.replace(year=y)
        if(c['Death'] == 'NA'):
            if(bir <= dt and bir >= date.today()):
                errors.append("ERROR: "+"INDIVIDUAL: "+"US38: "+str(i)+': ' +
                              c['ID']+": "+c['Name'] + " has upcoming Birthday on "+str(c['Birthday']))
    if(errors):
        return(errors)
    else:
        return("No Errors")


errorUS38 = US38()
print(*errorUS38, sep="\n")


# US39 : SP
# List upcoming anniveraries

def US39():
    errors = []
    dt = date.today() + timedelta(30)
    for i, c in df_fam.iterrows():
        mar = c['Married']
        y = date.today().year
        mar = mar.replace(year=y)
        if(c['Divorced'] == 'NA'):
            if(mar <= dt and mar >= date.today()):
                hid = c['Husband ID']
                wid = c['Wife ID']
                hname = c['Husband Name']
                wname = c['Wife Name']
                flag = True
                for x, y in df_indi.iterrows():
                    if(y['ID'] == hid):
                        if(y['Alive'] == 'False'):
                            flag = False
                    elif(y['ID'] == wid):
                        if(y["Alive"] == 'False'):
                            flag = False
                if(flag == True):
                    errors.append("ERROR: "+"FAMILY: "+"US39: "+str(i)+": "+hname+"("+hid+")" +
                                  " and "+wname+"("+wid+")"+" has upcoming Anniversary on "+str(c['Married']))
    if(errors):
        return(errors)
    else:
        errors.append('ERROR: US39: No records found')
        return(errors)


errorUS39 = US39()
print(*errorUS39, sep="\n")


#############__________________Parth's Code__________________###############

# US01 : PP
# Dates before current date


def US01():
    error = []
    no = []
    todayDate = datetime.datetime.strptime(
        datetime.datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d').date()
    counter = 0
    for i in range(len(df_indi)):
        if(df_indi['Birthday'][i] != 'NA' and df_indi['Birthday'][i] > todayDate):
            birthday = 'ERROR: INDIVIDUAL: US01: ' + \
                str(i)+': '+df_indi.loc[i]['ID']+': '+'Birthday ' + \
                str(df_indi.loc[i]['Birthday']) + ' occurs in the future'
            error.append(birthday)
            counter += 1
        elif(df_indi['Death'][i] != 'NA' and df_indi['Death'][i] > todayDate):
            deathdate = 'ERROR: INDIVIDUAL: US01: ' + \
                str(i)+': '+df_indi.loc[i]['ID']+': '+'Deathday ' + \
                str(df_indi.loc[i]['Death']) + ' occurs in the future'
            error.append(deathdate)
            counter += 1
    for i in range(len(df_fam)):
        if(df_fam['Married'][i] != 'NA' and df_fam['Married'][i] > todayDate):
            married = 'ERROR: FAMILY: US01: '+str(i)+': '+df_fam.loc[i]['ID']+': '+'Marriage Day ' + str(
                df_fam.loc[i]['Married']) + ' between ' + df_fam.loc[i]['Husband ID']+' and '+df_fam.loc[i]['Wife ID'] + ' occurs in the future'
            error.append(married)
            counter += 1
        elif(df_fam['Divorced'][i] != 'NA' and df_fam['Divorced'][i] > todayDate):
            divorced = 'ERROR: FAMILY: US01: '+str(i)+': '+df_fam.loc[i]['ID']+': '+'Divorce Day ' + str(
                df_fam.loc[i]['Divorced']) + ' between ' + df_fam.loc[i]['Husband ID']+' and '+df_fam.loc[i]['Wife ID'] + ' occurs in the future'
            error.append(divorced)
            counter += 1
    if(counter > 0):
        return (error)
    else:
        no.append('ERROR: US01: No records found')
        return(no)


errorUS01 = US01()
print(*errorUS01, sep="\n")
# US02 : PP
# Dates Birth before marriage


def US02():
    count = 0
    error = []
    no = []
    for i in range(len(df_indi)):
        if(df_indi['Birthday'][i] != 'NA' and df_indi['Spouce'][i] != 'NA' and (df_fam[df_fam['ID'] == df_indi['Spouce'][i]]['Married'].values[0]) < (df_indi['Birthday'][i])):
            if(df_indi['Gender'][i] == 'M'):
                print_line = 'ERROR: INDIVIDUAL: US02: '+str(i)+': '+df_indi.loc[i]['ID']+': '+'Husband\'s birth date ' + str(
                    df_indi.loc[i]['Birthday']) + ' after marriage date ' + str(df_fam[df_fam['ID'] == df_indi['Spouce'][i]]['Married'].values[0])
                count += 1
                error.append(print_line)
            elif(df_indi['Gender'][i] == 'F'):
                print_line = 'ERROR: INDIVIDUAL: US02: '+str(i)+': '+df_indi.loc[i]['ID']+': '+'Wife\'s birth date ' + str(
                    df_indi.loc[i]['Birthday']) + ' after marriage date ' + str(df_fam[df_fam['ID'] == df_indi['Spouce'][i]]['Married'].values[0])
                count += 1
                error.append(print_line)
            else:
                print_line = 'ERROR: INDIVIDUAL: US02: '+str(i)+': '+df_indi.loc[i]['ID']+': '+'Individual\'s birth date ' + str(
                    df_indi.loc[i]['Birthday']) + ' after marriage date ' + str(df_fam[df_fam['ID'] == df_indi['Spouce'][i]]['Married'].values[0]) + '\n'
                count += 1
                error.append(print_line)
    if(count > 0):
        return (error)
    else:
        no.append('ERROR: US02: No records found')
        return(no)


errorUS02 = US02()
print(*errorUS02, sep="\n")

# US10 : PP
# Marriage should be at least 14 years after birth of both spouses (parents must be at least 14 years old)


def US10():
    count = 0
    error = []
    no = []
    for i in range(len(df_fam)):
        if((df_fam['Married'][i]) != 'NA'):
            if((df_fam['Married'][i] - df_indi.loc[df_indi['ID'] == df_fam['Husband ID'][i]].values[0][3]) < datetime.timedelta(168*365/12)):
                print_line = 'ERROR: FAMILY: US10: '+str(i)+': '+df_indi.loc[df_indi['ID'] == df_fam['Husband ID'][i]].values[0][0]+': '+'Father\'s birth date ' + df_indi.loc[df_indi['ID']
                                                                                                                                                                               == df_fam['Husband ID'][i]].values[0][3].strftime("%Y-%m-%d") + ' less than 14 years of marriage date ' + df_fam['Married'][i].strftime("%Y-%m-%d")
                count += 1
                error.append(print_line)
            elif((df_fam['Married'][i] - df_indi.loc[df_indi['ID'] == df_fam['Wife ID'][i]].values[0][3]) < datetime.timedelta(168*365/12)):
                print_line = 'ERROR: FAMILY: US10: '+str(i)+': '+df_indi.loc[df_indi['ID'] == df_fam['Wife ID'][i]].values[0][0]+': '+'Mother\'s birth date ' + df_indi.loc[df_indi['ID']
                                                                                                                                                                            == df_fam['Wife ID'][i]].values[0][3].strftime("%Y-%m-%d") + ' less than 14 years of marriage date ' + df_fam['Married'][i].strftime("%Y-%m-%d")
                count += 1
                error.append(print_line)

    if(count > 0):
        return (error)
    else:
        no.append('ERROR: US10: No records found')
        return(no)


errorUS10 = US10()
print(*errorUS10, sep="\n")

# US09 : PP
# Child should be born before death of mother and before 9 months after death of father


def US09():
    count = 0
    error = []
    for i in range(len(df_fam)):
        if(len(df_fam['Children'][i]) > 0):
            if(len(df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values) > 0 and df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][8] != 'NA' and df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][6] != 'NA' and len(df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][8]) > 0 and df_indi['Alive'].loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0] == False):
                logging.debug('First IF is here')
                if(df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][2] == 'F' and df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][6] < df_indi.loc[df_indi['Child'] == df_fam['ID'][i]].values[0][3]):
                    print_line = 'ERROR: FAMILY: US09: '+str(i)+': '+df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][0]+': '+'Mother\'s death date ' + df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][6].strftime(
                        "%Y-%m-%d") + ' before birthdate of child ' + df_indi.loc[df_indi['Child'] == df_fam['ID'][i]].values[0][3].strftime("%Y-%m-%d")
                    count = count + 1
                    error.append(print_line)
                elif(df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][2] == 'M' and df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][6] < ((df_indi.loc[df_indi['Child'] == df_fam['ID'][i]].values[0][3]) - datetime.timedelta(9*365/12))):
                    print_line = 'ERROR: FAMILY: US09: '+str(i)+': '+df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][0]+': '+'Father\'s death date ' + df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][6].strftime(
                        "%Y-%m-%d") + ' before birthdate of child ' + df_indi.loc[df_indi['Child'] == df_fam['ID'][i]].values[0][3].strftime("%Y-%m-%d")
                    count = count + 1
                    error.append(print_line)
    if(count > 0):
        return (error)
    else:
        error.append('ERROR: US09: No records found')
        return(error)


errorUS09 = US09()
print(*errorUS09, sep="\n")

# US11 : PP
# Marriage should not occur during marriage to another spouse


def US11():
    count = 0
    error = []
    for i in range(len(df_fam)):
        for j in range(i, len(df_fam)):
            if(df_fam['Wife Name'][i] == df_fam['Wife Name'][j] and df_fam['ID'][i] != df_fam['ID'][j]):

                iMarry = (df_fam.loc[df_fam['ID'] ==
                                     df_fam['ID'][i]].values[0])[1]
                iDiv = (df_fam.loc[df_fam['ID'] ==
                                   df_fam['ID'][i]].values[0])[2]
                jMarry = (df_fam.loc[df_fam['ID'] ==
                                     df_fam['ID'][j]].values[0])[1]
                jDiv = (df_fam.loc[df_fam['ID'] ==
                                   df_fam['ID'][j]].values[0])[2]
                if((iMarry < jMarry and iDiv == 'NA')or (iMarry < jMarry and iDiv > jMarry)):
                    print_line = 'ERROR: FAMILY: US11: '+str(i)+': '+df_fam['ID'][i] + ': '+df_fam['Wife Name'][i] + \
                        " is married to " + \
                        df_fam['Husband Name'][i] + "and " + \
                        df_fam['Husband Name'][j] + " at the same time"
                    count = count + 1
                    error.append(print_line)

            if(df_fam['Husband Name'][i] == df_fam['Husband Name'][j] and df_fam['ID'][i] != df_fam['ID'][j]):
                iMarry = (df_fam.loc[df_fam['ID'] ==
                                     df_fam['ID'][i]].values[0])[1]
                iDiv = (df_fam.loc[df_fam['ID'] ==
                                   df_fam['ID'][i]].values[0])[2]
                jMarry = (df_fam.loc[df_fam['ID'] ==
                                     df_fam['ID'][j]].values[0])[1]
                jDiv = (df_fam.loc[df_fam['ID'] ==
                                   df_fam['ID'][j]].values[0])[2]
                if((iMarry < jMarry and iDiv == 'NA')or (iMarry < jMarry and iDiv > jMarry)):
                    print_line = 'ERROR: FAMILY: US11: '+str(i)+': '+df_fam['ID'][i] + ': '+df_fam['Husband Name'][i] + \
                        " is married to " + \
                        df_fam['Wife Name'][i] + "and " + \
                        df_fam['Wife Name'][j] + " at the same time"
                    count = count + 1
                    error.append(print_line)

    if(count > 0):
        return (error)
    else:
        error.append('ERROR: US11: No records found')
        return(error)


errorUS11 = US11()
print(*errorUS11, sep="\n")

# US12 : PP
# Mother should be less than 60 years older than her children and father should be less than 80 years older than his children


def US12():
    count = 0
    error = []
    for i in range(len(df_fam)):
        if(len(df_fam['Children'][i]) > 0):
            if(len(df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values) > 0 and df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][8] != 'NA' and df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][4] != 'NA' and len(df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][8]) > 0 and df_indi['Alive'].loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0] == True):

                logging.debug('First IF is here')
                if(df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][2] == 'F' and (df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][4] - df_indi.loc[df_indi['Child'] == df_fam['ID'][i]].values[0][4]) > 60):
                    print_line = 'ERROR: FAMILY: US12: '+str(i)+': '+df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][0]+': '+'Mother\'s age ' + str(
                        df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][4]) + ' is more than 60 years older than her child ' + str(df_indi.loc[df_indi['Child'] == df_fam['ID'][i]].values[0][4])
                    count = count + 1
                    error.append(print_line)
                elif(df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][2] == 'M' and (df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][4] - df_indi.loc[df_indi['Child'] == df_fam['ID'][i]].values[0][4]) > 80):
                    print_line = 'ERROR: FAMILY: US12: '+str(i)+': '+df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][0]+': '+'Father\'s age ' + str(
                        df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][4]) + ' is more than 60 years older than his child with age' + str(df_indi.loc[df_indi['Child'] == df_fam['ID'][i]].values[0][4])
                    count = count + 1
                    error.append(print_line)
    if(count > 0):
        return (error)
    else:
        error.append('ERROR: US09: No records found')
        return(error)


errorUS12 = US12()
print(*errorUS12, sep="\n")
