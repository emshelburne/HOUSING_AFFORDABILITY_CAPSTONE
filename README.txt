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


##### Data Dictionary for Issued Building Permits table from City of Vancouver: Open Data (as stored in issued_building_permits_filter_dwelling_purposes_preprocessed.csv)


| Column Name                                               | Description                                                                              | Type             | Sample                                       |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ---------------- | -------------------------------------------- |
| `issue_date`                                              | Date the permit was officially issued.                                                   | Datetime         | 2023-10-30                                   |
| `project_description`                                     | Short free-text summary of the permitted work.                                           | String           | Interior alterations to dwelling unit        |
| `geom`                                                    | GeoJSON-style point for the permit location (lon/lat).                                   | String (GeoJSON) | `{"coordinates":[-123.1279186,49.271598]}`   |
| `project_value`                                           | Estimated construction value at issuance (CAD converted to 2024 CPI).                    | Float            | 120000                                       |
| `nbhd`                                                    | Vancouver neighbourhood as defined by CMHC.                                              | String           | Downtown                                     |
| `zone`                                                    | Survey zone as defined by CMHC.                                                          | String           | Southeast Vancouver                          |
| `duplex_w_secondary_suite`                                | Indicator flag: 1 if the permit involves a duplex with a secondary suite.                | Integer {0,1}    | 0                                            |
| `laneway_house`                                           | Indicator flag: 1 if the permit involves a laneway house.                                | Integer {0,1}    | 1                                            |
| `duplex`                                                  | Indicator flag: 1 if the permit involves a duplex.                                       | Integer {0,1}    | 0                                            |
| `multiple_conversion_dwelling`                            | Indicator flag: 1 if the permit involves a Multiple Conversion Dwelling.                 | Integer {0,1}    | 0                                            |
| `dwelling_unit`                                           | Indicator flag: 1 if the permit concerns a (generic) dwelling unit.                      | Integer {0,1}    | 1                                            |
| `multiple_dwelling`                                       | Indicator flag: 1 if the permit involves multiple dwelling (e.g., apartments).           | Integer {0,1}    | 0                                            |
| `single_detached_house`                                   | Indicator flag: 1 if the permit involves a single detached house.                        | Integer {0,1}    | 0                                            |
| `single_detached_house_w_sec_suite`                       | Indicator flag: 1 if the permit involves a single detached house with a secondary suite. | Integer {0,1}    | 0                                            |
| `type_of_work_demolition_deconstruction`                  | Indicator flag: 1 if the work type is demolition/deconstruction.                         | Integer {0,1}    | 0                                            |
| `type_of_work_new_building`                               | Indicator flag: 1 if the work type is a new building.                                    | Integer {0,1}    | 1                                            |
| `permit_category_new_build_low_density_housing`           | Indicator flag: 1 if categorized as “New Build — Low Density Housing.”                   | Integer {0,1}    | 0                                            |
| `permit_category_new_build_standalone_laneway`            | Indicator flag: 1 if categorized as “New Build — Standalone Laneway.”                    | Integer {0,1}    | 0                                            |
| `permit_category_renovation_residential_lower_complexity` | Indicator flag: 1 if categorized as “Renovation — Residential — Lower Complexity.”       | Integer {0,1}    | 1                                            |


##### Data Dictionary for economic data from CMHC


| Column Name                       | Description                                                                                                                  | Type    | Sample         |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------- | -------------- |
| `nbhd`                            | Vancouver neighbourhood as defined by CMHC.                                                                                  | String  | ambleside      |
| `zone`                            | Survey zone as defined by CMHC.                                                                                              | String  | West Vancouver |
| `year`                            | Calendar year of observation.                                                                                                | Integer | 2019           |
| `avg_rent_[unit_type]`            | Average monthly rent (CAD converted to 2024 CPI) for the given unit type in the neighbourhood and year.                      | Float   | 1970.49        |
| `med_rent_[unit_type]`            | Median monthly rent (CAD converted to 2024 CPI) for the given unit type in the neighbourhood and year.                       | Float   | 2033.14        |
| `vacancy_rate_[unit_type]`        | Vacancy rate (%) for the given unit type in the neighbourhood and year.                                                      | Float   | 2.4            |
| `avg_rent_[unit_type]_change`     | Year-over-year change in average rent for the given unit type; expressed as a proportion (e.g., `0.05` = +5%).               | Float   | 0.0474         |
| `med_rent_[unit_type]_change`     | Year-over-year change in median rent for the given unit type; expressed as a proportion.                                     | Float   | 0.0354         |
| `vacancy_rate_[unit_type]_change` | Year-over-year percentage-point difference in vacancy rate (current% − prior%).                                              | Float   | 0.2            |


##### Data Dictionary for Geographic Definitions from CMHC


| Column Name | Description                                                                    | Type                            | Sample                                                |
| ----------- | ------------------------------------------------------------------------------ | ------------------------------- | ----------------------------------------------------- |
| `nbhd`      | Vancouver neighbourhood as defined by CMHC.                                    | String                          | West End/Stanley Park North                           |
| `zone`      | Survey zone as defined by CMHC.                                                | String                          | West End/Stanley Park                                 |
| `geometry`  | Neighbourhood boundary geometry as a Polygon/MultiPolygon in the GeoDataFrame. | Geometry (Polygon/MultiPolygon) | `POLYGON ((-123.1402 49.29038, -123.13862 49.28...))` |




Link to CPI inflation conversion source: https://www150.statcan.gc.ca/t1/tbl1/en/cv.action?pid=1810000501

### To do:


#### Non-programming

- [X] Sprint 0
- [X] Locate and download data sources
- [X] Set up git repo
- [X] Sprint 1 Presentation
- [X] Create data dictionary for housing permit data
- [X] Create data dictionary for economic CMHC data
- [X] Submit Sprint 1
- [ ] Sprint 2 Presentation
- [ ] Submit Sprint 2

#### Programming

- [X] Complete first round of cleaning building permit data (from City of Vancouver Open Data Portal)
- [X] Complete second round of cleaning building permit data (from City of Vancouver Open Data Portal)
- [X] Acquire CMHC geographic shapefiles
- [X] Restrict CMHC geographic shapefiles to Vancouver tracts, neighborhoods, and zones
- [X] Create geographic hierarchy through special joins
- [X] Impute economic data hierarchically 
- [X] Clean economic data (from CMHC)
- [X] Exploratory data analysis of building permit data
- [X] Exploratory data analysis of economic data
- [ ] Feature engineering
- [ ] Baseline modeling








