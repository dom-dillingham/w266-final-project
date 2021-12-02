import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import KFold
import Constants
import sys
from pathlib import Path

output_folder = Path(sys.argv[1])
output_folder.mkdir(parents = True, exist_ok = True)

data_path = '~/finalproject/physionet.org/files/mimiciii/1.4'

use_cols = ['SUBJECT_ID',
            'GENDER',
            'DOB',
            'DOD']

patients = pd.read_csv(data_path + "/PATIENTS.csv")
patients_filtered = patients.loc[:, patients.columns.isin(use_cols)]

del patients


n_splits = 12
patients_filtered = patients_filtered.sample(frac = 1, random_state = 42).reset_index(drop = True)
kf = KFold(n_splits = n_splits, shuffle = True, random_state = 42)
for c,i in enumerate(kf.split(patients_filtered, groups = patients_filtered.GENDER)):
    patients_filtered.loc[i[1], 'fold'] = str(c)

use_cols = ['SUBJECT_ID',
            'HADM_ID',
            'INSURANCE',
            'LANGUAGE',
            'RELIGION',
            'ETHNICITY',
            'ADMITTIME',
            'DEATHTIME',
            'DISCHTIME',
            'HOSPITAL_EXPIRE_FLAG',
            'DISCHARGE_LOCATION',
            'DIAGNOSIS']

admissions = pd.read_csv(data_path + "/ADMISSIONS.csv")
admissions_filtered = admissions.loc[:, admissions.columns.isin(use_cols)]

del admissions

joined = pd.merge(patients_filtered, admissions_filtered,
                     on='SUBJECT_ID', how='inner')

def merge_death(row):
  if not(pd.isnull(row.DEATHTIME)):
    return pd.to_datetime(row.DEATHTIME, format='%Y-%m-%d')
  else:
    return pd.to_datetime(row.DOD, format='%Y-%m-%d')

joined['DOD_merged'] = joined.apply(merge_death, axis=1)

notes = pd.read_csv(data_path + "/NOTEEVENTS.csv")

use_cols = ['CATEGORY',
            'CHARTDATE',
            'CHARTTIME',
            'HADM_ID',
            'ROW_ID',
            'TEXT']
notes = notes.loc[:, notes.columns.isin(use_cols)]
notes_filtered = notes[notes['CATEGORY'].str.strip().isin(['Nursing/other', 'Nursing', 'Physician'])]
notes_filtered = notes_filtered[notes_filtered.HADM_ID.notnull()]

del notes

joined = pd.merge(notes_filtered, joined,
                     on='HADM_ID', how='left')

## Feature engineering based on prior work
joined.ETHNICITY.fillna(value = 'UNKNOWN/NOT SPECIFIED', inplace = True)

others_set = set()
def cleanField(string):
    mappings = {'HISPANIC OR LATINO': 'HISPANIC/LATINO',
                'BLACK/AFRICAN AMERICAN': 'BLACK',
                'UNABLE TO OBTAIN':'UNKNOWN/NOT SPECIFIED',
               'PATIENT DECLINED TO ANSWER': 'UNKNOWN/NOT SPECIFIED'}
    bases = ['WHITE', 'UNKNOWN/NOT SPECIFIED', 'BLACK', 'HISPANIC/LATINO',
            'OTHER', 'ASIAN']

    if string in bases:
        return string
    elif string in mappings:
        return mappings[string]
    else:
        for i in bases:
            if i in string:
                return i
        others_set.add(string)
        return 'OTHER'

joined['ETHNICITY_to_use'] = joined['ETHNICITY'].apply(cleanField)

joined = joined[joined.CHARTDATE >= joined.DOB]

## Need to convert to dates
joined['CHARTDATE_clean'] = pd.to_datetime(joined.CHARTDATE, format='%Y-%m-%d')
joined['DOB_clean'] = pd.to_datetime(joined.DOB, format='%Y-%m-%d')

ages = []
for i in range(joined.shape[0]):
    if joined.DOB_clean.iloc[i] < pd.to_datetime('2000-01-01', format='%Y-%m-%d'):
      ages.append(100)
    else:
      ages.append((joined.CHARTDATE_clean.iloc[i] - joined.DOB_clean.iloc[i]).days/365.24)
joined['age'] = ages
joined.loc[joined.age >= 90, 'age'] = 91.4

def map_lang(x):
    if x == 'ENGL':
        return 'English'
    if pd.isnull(x):
        return 'Missing'
    return 'Other'

joined['LANGUAGE_to_use'] = joined['LANGUAGE'].apply(map_lang)

joined.loc[(joined.CATEGORY == 'Discharge summary') |
       (joined.CATEGORY == 'Echo') |
       (joined.CATEGORY == 'ECG'), 'fold'] = 'NA'


icd = (pd.read_csv(data_path + "/DIAGNOSES_ICD.csv"))
icd_filtered = icd.groupby('HADM_ID').agg({'ICD9_CODE': lambda x: list(x.values)}).reset_index()

joined = pd.merge(joined, icd_filtered, on = 'HADM_ID')
del icd

oasis = pd.read_csv('~/finalproject/physionet.org/files/mimiciii-oasis.csv')
sofa = pd.read_csv('~/finalproject/physionet.org/files/mimiciii-sofa.csv')
sapsii = pd.read_csv('~/finalproject/physionet.org/files/mimiciii-sapsii.csv')

acuities = pd.merge(oasis, sofa, how = 'outer', on = ['subject_id', 'hadm_id', 'icustay_id'])
acuities = pd.merge(acuities, sapsii, how = 'outer', on = ['subject_id', 'hadm_id', 'icustay_id'])


use_cols = ['SUBJECT_ID',
            'HADM_ID',
            'ICUSTAY_ID',
            'INTIME',
            'OUTTIME']

icu_stays = pd.read_csv(data_path + "/ICUSTAYS.csv")
icu_stays_filtered = icu_stays.loc[:, icu_stays.columns.isin(use_cols)].set_index(['SUBJECT_ID',
                                                                                           'HADM_ID'])

#joined.to_pickle(output_folder / 'df_pre_acuities.pkl')
## Bring in icustay function from prior project code
def fill_icustay(row):
    try:
        opts = icu_stays_filtered.loc[(row['SUBJECT_ID'],int(row['HADM_ID']))]
        if pd.isnull(row['CHARTTIME']):
            charttime = row['CHARTDATE_clean'] + pd.Timedelta(days = 2)
        else:
            charttime = row['CHARTTIME']
        stay = opts[(opts['INTIME'] <= charttime)].sort_values(by = 'INTIME', ascending = True)

        if len(stay) == 0:
            return None
        return stay.iloc[-1]['ICUSTAY_ID']
    except:
        return None

joined['ICUSTAY_ID'] = joined.apply(fill_icustay, axis = 1)

joined = pd.merge(joined, acuities.drop(columns = ['subject_id','hadm_id']), left_on = 'ICUSTAY_ID', right_on = 'icustay_id',  how = 'left')

joined.to_pickle(output_folder / "df_raw.pkl")
