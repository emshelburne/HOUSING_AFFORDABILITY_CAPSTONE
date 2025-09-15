 ## This file describes access to all the raw data required to reproduce the project and instructions on setting up the `DATA/` folder. We provide publicly accessible download links to necessary files.

## GOOGLE DRIVE LINK TO COMPLETE DATA/ FOLDER: https://drive.google.com/drive/folders/1qHuZ4MsZvvnML86mPKePkJCMyprbPVhp?usp=drive_link 



## PUBLIC DATA SOURCES:


## City of Vancouver: Open Data Portal

WEBSITE: https://opendata.vancouver.ca/pages/home/ 

RAW DATA DOWNLOAD LINK: https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets/issued-building-permits/exports/csv?lang=en&refine=propertyuse%3A%22Dwelling%20Uses%22&timezone=America%2FLos_Angeles&use_labels=true&delimiter=%3B

NOTES:
 - Filtered to permits for dwelling purposes, exported as issued_building_permits_filter_dwelling_purposes.csv in DATA/PERMITS folder
 - Use issued_building_permits_filter_dwelling_purposes_cleaned.csv (available in above Google Drive) for the notebook 03_dwelling_permits_EDA.ipynb

## CMHC: Canada Mortgage and Housing Corporation

WEBSITE: https://www.cmhc-schl.gc.ca/

GOOGLE DRIVE TO DOWNLOAD COMPLETE FOLDER: https://drive.google.com/drive/folders/1ZBVOeFDkpwLdjljlS0PMae5VI1wOJrin?usp=drive_link 

NOTES: tedious to download manually
