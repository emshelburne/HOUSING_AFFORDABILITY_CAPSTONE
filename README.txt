## Data-Driven Insights into Housing Trends: Forecasting Affordability Risks
=========================

### Executive Summary

This project addresses the urgent problem of housing affordability in Vancouver, particularly in the context of large-scale redevelopment plans like the Broadway Plan. While framed as a solution to the housing crisis, such plans have raised serious concerns among community members and housing advocates, who fear that high-rise developments may accelerate gentrification, displace renters, and make neighborhoods less affordable. The data science opportunity lies in using machine learning to analyze historical patterns of development and neighborhood-level economic indicators—such as rent, income, and vacancy rates—to build a predictive model that estimates how new construction may impact local affordability. By merging and processing datasets from CMHC, BC Assessment, and the City of Vancouver, this project aims to provide a rigorous, data-driven supplement to the ongoing public debate around urban development. While the project is in its early stages, the goal is to develop a publicly accessible tool or report that empowers community members and policymakers with transparent, evidence-based insights into the potential consequences of redevelopment.


### Current Status (as of Sprint 1 submission)

I am currently working with two major sources of data for this project: the City of Vancouver’s Open Data Portal and the Canada Mortgage and Housing Corporation (CMHC). From the City of Vancouver, I’ve pulled a dataset of approximately 30,000 entries related to issued building permits, specifically filtered for dwelling purposes. I have completed an initial round of cleaning on this dataset using an object-oriented approach, which involved converting data types, removing unnecessary columns, and handling null values. While this first pass resulted in a clean dataset with no missing values, further refinement is planned—particularly more thoughtful imputation and ensuring that row drops are only applied when strictly necessary. The cleaned dataset is stored as issued_building_permits_filter_dwelling_purposes_cleaned.csv in a publicly accessible Google Drive folder (see link below) and is now being used for exploratory data analysis in the notebook 03_dwelling_permits_EDA.

For the economic data from CMHC, I am working with multiple CSV files that contain different economic indicators (e.g., average rent, vacancy rate) across various years. The data needs to be merged and aligned across time, and I am again using an object-oriented approach to structure this process. At the most granular level (census tract), a significant amount of missing data is present. To address this, I plan to implement a hierarchical geographic imputation method, where missing values at the census tract level will be filled in using data from progressively broader geographic units (e.g., neighborhood, census subdivision, city). This will require associating census tracts with higher-level geographic units, which I am currently working on by building a mapping based on official census definitions. Until this geographic structure is in place and imputation is complete, I am holding off on exploratory data analysis for the CMHC dataset and focusing my efforts on the building permit data.

### Demo

... TO BE ADDED


### Methodology

... TO BE ADDED


### Organization

#### Repository 

* `DATA` 
    - contains link to copy of the dataset (stored in Google Drive)
    - TO BE ADDED: saved copy of aggregated / processed data as long as those are not too large (> 10 MB)

* `MODELS`
    - TO BE ADDED: `joblib` dump of final model(s)

* `NOTEBOOKS`
    - contains all notebooks involved in the project

* `DOCS`
    - contains reports, presentations which summarize the project

* `REFERENCES`
    - contains papers / tutorials used in the project

* `SRC`
    - Contains the project source code (refactored from the notebooks)

* `.gitignore`
    - Part of Git, includes files and folders to be ignored by Git version control

* `capstone_env.yml`
    - Conda environment specification

* `README.md`
    - Project landing page (this page)

* `LICENSE`
    - Project license

#### Dataset

... GOOGLE DRIVE LINK TO COMPLETE DATA/ FOLDER: https://drive.google.com/drive/folders/1qHuZ4MsZvvnML86mPKePkJCMyprbPVhp?usp=drive_link 


##### Data Dictionary for Issued Building Permits table from City of Vancouver: Open Data (as stored in issued_building_permits_filter_dwelling_purposes_cleaned.csv)


| Column Name              | Description                                                                                                                  | Type         | Sample                                       |
|--------------------------|------------------------------------------------------------------------------------------------------------------------------|--------------|----------------------------------------------|
| `PermitNumber`           | Unique identifier for each permit; may have multiple permits per project site.                                               | String       | BP-2023-03902                                |
| `PermitNumberCreatedDate`| Date the permit number was assigned (via staff or online process).                                                           | Datetime     | 2023-10-24                                   |
| `IssueDate`              | Date the permit was officially issued.                                                                                       | Datetime     | 2023-10-30                                   |
| `PermitElapsedDays`      | Days between permit number creation and issuance; influenced by complexity and review time.                                  | Integer      | 6                                            |
| `ProjectValue`           | Estimated construction value at issuance; used to calculate base permit fees.                                                | Float        | 120000                                       |
| `TypeOfWork`             | Type of construction (e.g., Addition / Alteration, Demolition, New Buildings).                                               | String       | Addition / Alteration                        |
| `Address`                | Full address of the property receiving the permit.                                                                           | String       | 428 BEACH CRESCENT #2001, Vancouver, BC      |
| `ProjectDescription`     | Description of work scope; field available for permits issued after 2018.                                                    | String       | Interior alterations to dwelling unit #2001. |
| `PermitCategory`         | Categorization by project complexity and scope based on multiple fields.                                                     | String       | Renovation - Residential - Lower Complexity  |
| `Applicant`              | Name of the applicant (owner, agent, or contractor).                                                                         | String       | Nader Shabdiz DBA: NSR Contracting Inc.      |
| `PropertyUse`            | General property use type (e.g., Dwelling Uses).                                                                             | String       | Dwelling Uses                                |
| `SpecificUseCategory`    | More detailed category of property use (e.g., Multiple Dwelling).                                                            | String       | Multiple Dwelling                            |
| `BuildingContractor`     | Contractor responsible for the project at issuance.                                                                          | String       | BigCity Excavation Ltd                       |
| `GeoLocalArea`           | Vancouver local planning area in which the property is located.                                                              | String       | Downtown                                     |
| `Geom`                   | GeoJSON-style geographic coordinates of the building site.                                                                   | Geo shape    | {"coordinates":[-123.1279186,49.271598]}     |
| `geo_point_2d`           | Geographic coordinates in lat-long format.                                                                                   | Geo point    | [49.271598, -123.1279186]                    |


##### Data Dictionary for economic data from CMHC

... TO BE ADDED

### To do:


#### Non-programming

- [X] Sprint 0
- [X] Locate and download data sources
- [X] Set up git repo
- [X] Sprint 1 Presentation
- [X] Create data dictionary for housing permit data
- [ ] Create data dictionary for economic CMHC data
- [ ] Submit Sprint 1
- [ ] Research models used in machine learning projects involving housing and gather references
- [ ] Read complete Broadway Plan proposal


#### Programming

- [X] Complete first round of cleaning building permit data (from City of Vancouver Open Data Portal)
- [ ] Complete second round of cleaning building permit data (from City of Vancouver Open Data Portal)
- [ ] Download and encode census dictionary in order to connect neighborhoods with census tracts hierarchically 
- [ ] Clean economic data (from CMHC)
- [X] Exploratory data analysis of building permit data
- [ ] Exploratory data analysis of economic data
- [ ] Feature engineering
- [ ] Baseline modeling


#### Supplementary

- [ ] Look for more economic data (income by census tract, etc.)






