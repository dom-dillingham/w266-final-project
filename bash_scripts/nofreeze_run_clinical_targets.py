import os
import sys
import subprocess
import shlex

cols = ['Acute and unspecified renal failure',
 'Acute cerebrovascular disease',
 'Acute myocardial infarction',
 'Cardiac dysrhythmias',
 'Chronic kidney disease',
 'Chronic obstructive pulmonary disease and bronchiectasis',
 'Complications of surgical procedures or medical care',
 'Conduction disorders',
 'Congestive heart failure; nonhypertensive',
 'Coronary atherosclerosis and other heart disease',
 'Diabetes mellitus with complications',
 'Diabetes mellitus without complication',
 'Disorders of lipid metabolism',
 'Essential hypertension',
 'Fluid and electrolyte disorders',
 'Gastrointestinal hemorrhage',
 'Hypertension with complications and secondary hypertension',
 'Other liver diseases',
 'Other lower respiratory disease',
 'Other upper respiratory disease',
 'Pleurisy; pneumothorax; pulmonary collapse',
 'Pneumonia (except that caused by tuberculosis or sexually transmitted disease)',
 'Respiratory failure; insufficiency; arrest (adult)',
 'Septicemia (except in labor)',
 'Shock',
 'any_chronic',
 'any_acute',
 'any_disease']

std_models = ['biobert_v1.0_pubmed_pmc']

# file name, col names, models
tasks = [('phenotype_first_pubmed', cols, std_models),
        ('phenotype_all_pubmed', cols, std_models),
        ('inhosp_mort_pubmed', ['inhosp_mort'], std_models)
        ]

for dfname, targetnames, models in tasks:
    for t in targetnames:
        for c,m in enumerate(models):
            subprocess.call(shlex.split('/home/dom_dillingham/HurtfulWords/bash_scripts/finetune_on_target_unfreeze.sh "%s" "%s" "%s"'%(dfname,m,t)))
