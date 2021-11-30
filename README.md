# w266-final-project

## Steps to Replicate

Code for this project was modified from the original paper our projects seeks to expand with their source code [here](https://github.com/MLforHealth/HurtfulWords/blob/master/README.md). Scripts were modified to work with our GCP instance architecture and were modified to work on the pretrained models and for the custom finetuning exercise completed. Scripts not used in this paper or data processing scripts from MIMIC (PhysioNet) that were not modified are not included in this repo. Raw and processed data elements are also not included given their size, requiring a 100GB SSD machine to house. Scripts were also optimized to improve runtime, making better use of the large GCP instances provisioned for this project.

## Data & Data Processing

Data for this project was obtained from PhysioNet for the purpose of this research project. Given the PPI associated with the clinical notes in this dataset, access is restricted for research purposes. Data must first be obtained from PhysioNet, run through PhysioNet's scripts to generate the necessary supplementary targets such as the Sequential Organ Failure Assessment (SOFA) Score, and then run through the data processing pipeline present in this repo and outlined in the original repo. 
