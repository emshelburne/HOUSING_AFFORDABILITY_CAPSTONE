## Machine Learning for Housing Affordability: Clustering Development Patterns
=========================

### Executive Summary

This project investigates the drivers of housing affordability in Vancouver, focusing on the intersection of development initiatives (e.g., the Broadway Plan) and neighborhood-level socioeconomic dynamics. While redevelopment is often presented as a solution to the housing crisis, it can accelerate gentrification and displacement, particularly in renter-heavy areas. The data science opportunity lies in analyzing historical building permits alongside economic indicators (rent, income, vacancy, project values) to detect development patterns and anticipate affordability risks. Using natural language processing on permit descriptions, dimensionality reduction techniques, and a sweep of clustering algorithms (K-Means, Gaussian Mixture, Agglomerative, etc.), this project aims to uncover distinct development archetypes. These clusters will then be linked to affordability outcomes over time, offering a transparent, data-driven foundation for evaluating how redevelopment may reshape housing markets. Ultimately, the goal is to build interpretable models and visual tools that empower policymakers and communities with actionable insights.


### Current Status (as of Sprint 2 submission)

The project integrates two complementary data streams: permit-level development activity from the City of Vancouver’s Open Data Portal and housing market indicators from CMHC. The permit dataset (~25,000 entries) has been cleaned and transformed with attention to type conversions, missing values, and geospatial parsing, enabling robust exploratory analysis. Natural language processing has been applied to extract keywords from project descriptions, with inverse document frequency vectorization and filtering to highlight signals of high-value or large-scale developments. These features, along with permit metadata (e.g., value, location, type of work), are clustered using multiple unsupervised methods, with hyperparameters tuned through inertia, silhouette, Davies–Bouldin, and Calinski–Harabasz scores, as well as interpretability checks. Parallel work is ongoing on CMHC economic data, where hierarchical geographic imputation was developed to address missing values at granular geographic levels. This data set is now completely cleaned, preprocessed, and converted to 2024 CAD using CPI as an inflation index. My next step is to refine these clusters for interpretability and stability, and then compare project intensity (the proportion of a given category of development project) against economic metrics in different neighborhoods a few years down the line.

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


##### Data Dictionary for Issued Building Permits table from City of Vancouver: Open Data (as stored in permits.csv in the PROCESSED folder of above google drive)


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


##### Data Dictionary for economic data from CMHC (as stored in full_economic_data.csv in the PROCESSED folder of above google drive)


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


##### Data Dictionary for Geographic Definitions from CMHC (as stored in nbhds_with_zones.geojson in the PROCESSED folder of above google drive)


| Column Name | Description                                                                    | Type                            | Sample                                                |
| ----------- | ------------------------------------------------------------------------------ | ------------------------------- | ----------------------------------------------------- |
| `nbhd`      | Vancouver neighbourhood as defined by CMHC.                                    | String                          | West End/Stanley Park North                           |
| `zone`      | Survey zone as defined by CMHC.                                                | String                          | West End/Stanley Park                                 |
| `geometry`  | Neighbourhood boundary geometry as a Polygon/MultiPolygon in the GeoDataFrame. | Geometry (Polygon/MultiPolygon) | `POLYGON ((-123.1402 49.29038, -123.13862 49.28...))` |




Link to CPI inflation conversion source used for all above data: https://www150.statcan.gc.ca/t1/tbl1/en/cv.action?pid=1810000501


### To do:


#### Non-programming

- [X]  Sprint 0
- [X]  Locate and download data sources
- [X]  Set up git repo
- [X]  Sprint 1 Presentation
- [X]  Create data dictionary for housing permit data
- [X]  Create data dictionary for economic CMHC data
- [X]  Submit Sprint 1
- [X]  Sprint 2 Presentation
- [X]  Submit Sprint 2
-  [  ]  Collect references on clustering evaluation metrics (silhouette, Davies–Bouldin, Calinski–Harabasz, ARI, BIC/AIC, etc.)
-  [  ]  Collect references on clustering algorithms and their use in urban/economic studies
-  [ ]  Submit Sprint 3 
-  [ ]  Final submission 

#### Programming

- [X]  Complete first round of cleaning building permit data (from City of Vancouver Open Data Portal)
- [X]  Complete second round of cleaning building permit data (from City of Vancouver Open Data Portal)
- [X]  Acquire CMHC geographic shapefiles
- [X]  Restrict CMHC geographic shapefiles to Vancouver tracts, neighborhoods, and zones
- [X]  Create geographic hierarchy through spatial joins
- [X]  Impute economic data hierarchically
- [X]  Clean economic data (from CMHC)
- [X]  Exploratory data analysis of building permit data
- [X]  Exploratory data analysis of economic data
- [X]  Baseline NLP
- [X]  Baseline clustering with K-Means
- [   ]  Advanced clustering with K-Means
- [   ]  Implement Gaussian Mixture Model clustering (with BIC/AIC evaluation)
- [   ]  Implement Agglomerative (Ward) clustering
- [   ]  Implement DBSCAN / HDBSCAN clustering
- [   ]  Compare clustering outcomes across algorithms and metrics
- [   ]  Integrate clustering results with economic indicators at neighborhood level
- [   ]  Cluster neighborhoods by economic state (e.g., rent, vacancy profiles)
- [   ]  Cluster permits paired with neighborhood data as “development decisions”









