## Machine Learning for Housing Affordability: Clustering Development Patterns & Investigating Economic Correlations

=========================

### Executive Summary  

This project investigates the relationship between **housing development patterns and affordability outcomes in Vancouver**, focusing on how redevelopment initiatives may shape rent levels and vacancy rates over time. While new construction and renovations are often positioned as solutions to the housing crisis, they can also accelerate **gentrification and displacement**, particularly in renter-heavy neighborhoods. The goal of this project is to provide a **data-driven, transparent framework** for evaluating these dynamics.  

To this end, the project integrates two complementary data sources:  
- **Building permits (2017–2024)** from the City of Vancouver Open Data Portal  
- **Rental market data** (rents, vacancy rates) from CMHC  

The permit dataset (~25,000 entries) was **cleaned, geocoded, and enriched** with natural language processing (TF–IDF and lemmatization on project descriptions). To avoid high-dimensional sparsity, **Truncated SVD** was applied to derive compact semantic components, which were then combined with structured permit features (value, location, type).  

We applied a sweep of **unsupervised clustering methods** (K-Means, Gaussian Mixture Models, Agglomerative, HDBSCAN) and evaluated them with multiple internal metrics, emphasizing **silhouette score** and interpretability. Ultimately, **Agglomerative (Ward) clustering** was chosen for producing meaningful, stable clusters that reflected clear development archetypes.  

A novel metric of **cluster intensity (NF–ICF)** was defined to quantify neighborhood-level development activity. By aligning this with CMHC economic indicators in subsequent years, we identified **statistically significant correlations** between development patterns and affordability metrics. Examples include:   
- **Detached/duplex infill** linked to **lower short-term vacancies and slower rent growth**, but **higher large-unit vacancies after several years**  
- **Family-oriented builds** correlating with **tighter vacancies in larger rental units**  

These findings underscore the **complex and time-dependent effects of redevelopment** on affordability. Since 2017, Vancouver has experienced steadily rising rents alongside persistently low vacancy rates, highlighting the urgency of incorporating affordability considerations into policy decisions like the **Broadway Plan**.  

The final deliverables include:  
- A fully documented **GitHub repository** with cleaned data and modeling workflows  
- Jupyter notebooks covering **EDA, modeling, optimization, and interpretation**  
- An interactive **Streamlit dashboard** ([live demo](https://van-housing-permits-explorer.streamlit.app/)) to visualize clusters, explore neighborhood trends, and test correlations  

Ultimately, this project demonstrates how **machine learning and open data** can illuminate the real impacts of development, offering valuable tools for policymakers, researchers, and communities seeking to balance growth with affordability.  


### Demo  

The interactive demo is delivered as a **Streamlit web application**, designed to make the analysis transparent and accessible. Key features include:  

- **Geographic Visualizer**: Animated maps showing monthly permit activity overlaid on neighborhoods, colored by rent or vacancy metrics.  
- **Neighborhood Spotlight**: Interactive breakdowns of development clusters with side-by-side rental and vacancy trends.  
- **Cluster Visualizers**: Summaries of Builds, Renovations, and Demolitions clusters, highlighting defining features and interpretations.  
- **Correlation Summary**: Expandable panels and bar charts presenting key findings on how development clusters relate to rental outcomes.  
- **Permit Lookup Tool**: A searchable interface to inspect individual permits, with sensitive details anonymized.  

🔗 **Live Demo:** [van-housing-permits-explorer.streamlit.app](https://van-housing-permits-explorer.streamlit.app/)  




### Organization

#### Repository 

* `NOTEBOOKS`
    - contains all notebooks involved in the project

* `DOCS`
    - contains documents and presentations which summarize the project

* `.gitignore`
    - Part of Git, includes files and folders to be ignored by Git version control

* `capstone_env.yml`
    - Conda environment specification

* `README.md`
    - Project landing page (this page)

* `LICENSE`
    - Project license



### Dataset  

📂 **Full processed data folder** (Google Drive): [Link](https://drive.google.com/drive/folders/1qHuZ4MsZvvnML86mPKePkJCMyprbPVhp?usp=drive_link)  

---



### Data at a Glance  

| Dataset                     | Source                                | Years Covered | Records (approx.) | Key Fields                                         |
|-----------------------------|---------------------------------------|---------------|-------------------|---------------------------------------------------|
| **Building Permits**        | City of Vancouver Open Data           | 2017–2024     | ~25,000           | Issue date, description (NLP), project value, location, type/flags |
| **Economic Data**           | CMHC Rental Market Survey             | 2017–2024     | ~1,200 (nbhd-year) | Avg/median rents (studio–3BR+), vacancy rates, YoY changes |
| **Geographic Definitions**  | CMHC (neighbourhoods + survey zones)  | —             | 30+ neighborhoods | Neighbourhood names, zones, boundary polygons      |

🔎 **Notes:**  
- All monetary values are **CPI-adjusted to 2024 CAD**.  
- Permit dataset integrates **structured fields + NLP features** from project descriptions.  
- Economic dataset aligned to the same neighbourhood/zone definitions for correlation analysis.  



### Data in Detail


#### 1. Issued Building Permits (City of Vancouver Open Data)  
*Stored as `permits.csv` in the `PROCESSED` folder.*  

| Column Name                          | Description                                                                      | Type             | Sample Example                               |
|--------------------------------------|----------------------------------------------------------------------------------|------------------|----------------------------------------------|
| `issue_date`                         | Date the permit was officially issued                                            | Datetime         | `2023-10-30`                                 |
| `project_description`                | Short free-text summary of the permitted work                                    | String           | Interior alterations to dwelling unit        |
| `geom`                               | Permit location as GeoJSON-style point (lon/lat)                                 | String (GeoJSON) | `{"coordinates":[-123.1279186,49.271598]}`   |
| `project_value`                      | Estimated construction value (CAD, converted to 2024 CPI)                        | Float            | `120000`                                     |
| `nbhd`                               | Vancouver neighbourhood (CMHC definition)                                        | String           | Downtown                                     |
| `zone`                               | Survey zone (CMHC definition)                                                    | String           | Southeast Vancouver                          |
| `duplex_w_secondary_suite`           | Flag: duplex with secondary suite                                                | Integer {0,1}    | `0`                                          |
| `laneway_house`                      | Flag: laneway house                                                              | Integer {0,1}    | `1`                                          |
| `duplex`                             | Flag: duplex                                                                     | Integer {0,1}    | `0`                                          |
| `multiple_conversion_dwelling`       | Flag: Multiple Conversion Dwelling                                               | Integer {0,1}    | `0`                                          |
| `dwelling_unit`                      | Flag: dwelling unit (generic)                                                    | Integer {0,1}    | `1`                                          |
| `multiple_dwelling`                  | Flag: multiple dwelling (e.g., apartments)                                       | Integer {0,1}    | `0`                                          |
| `single_detached_house`              | Flag: single detached house                                                      | Integer {0,1}    | `0`                                          |
| `single_detached_house_w_sec_suite`  | Flag: single detached house with secondary suite                                 | Integer {0,1}    | `0`                                          |
| `type_of_work_demolition_deconstruction` | Flag: demolition/deconstruction                                               | Integer {0,1}    | `0`                                          |
| `type_of_work_new_building`          | Flag: new building                                                               | Integer {0,1}    | `1`                                          |
| `permit_category_new_build_low_density_housing`  | Flag: “New Build — Low Density Housing”                  | Integer {0,1}    | `0`                                          |
| `permit_category_new_build_standalone_laneway`   | Flag: “New Build — Standalone Laneway”                   | Integer {0,1}    | `0`                                          |
| `permit_category_renovation_residential_lower_complexity` | Flag: “Renovation — Residential — Lower Complexity” | Integer {0,1}    | `1`                                          |

---

#### 2. Economic Data (CMHC Rental Market Survey)  
*Stored as `full_economic_data.csv` in the `PROCESSED` folder.*  

| Column Name                | Description                                                                                 | Type    | Sample        |
|-----------------------------|---------------------------------------------------------------------------------------------|---------|---------------|
| `nbhd`                      | Vancouver neighbourhood (CMHC definition)                                                  | String  | Ambleside     |
| `zone`                      | Survey zone (CMHC definition)                                                              | String  | West Vancouver|
| `year`                      | Calendar year of observation                                                               | Integer | `2019`        |
| `avg_rent_[unit_type]`      | Average monthly rent (CAD, 2024 CPI-adjusted) for given unit type                          | Float   | `1970.49`     |
| `med_rent_[unit_type]`      | Median monthly rent (CAD, 2024 CPI-adjusted) for given unit type                           | Float   | `2033.14`     |
| `vacancy_rate_[unit_type]`  | Vacancy rate (%) for given unit type                                                        | Float   | `2.4`         |
| `avg_rent_[unit_type]_change` | YoY change in average rent (proportion, e.g., `0.05` = +5%)                              | Float   | `0.0474`      |
| `med_rent_[unit_type]_change` | YoY change in median rent (proportion)                                                    | Float   | `0.0354`      |
| `vacancy_rate_[unit_type]_change` | YoY change in vacancy rate (percentage points)                                      | Float   | `0.2`         |

---

#### 3. Geographic Definitions (CMHC)  
*Stored as `nbhds_with_zones.geojson` in the `PROCESSED` folder.*  

| Column Name | Description                                        | Type                            | Sample Example                    |
|-------------|----------------------------------------------------|---------------------------------|-----------------------------------|
| `nbhd`      | Vancouver neighbourhood (CMHC definition)          | String                          | West End/Stanley Park North       |
| `zone`      | Survey zone (CMHC definition)                      | String                          | West End/Stanley Park             |
| `geometry`  | Neighbourhood boundary geometry (polygon/multipolygon) | Geometry (Polygon/MultiPolygon) | `POLYGON ((-123.1402 49.29038...))` |

---

📊 **Note:** All monetary values converted to 2024 CAD using [CPI inflation data](https://www150.statcan.gc.ca/t1/tbl1/en/cv.action?pid=1810000501).  



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
- [X]  Sprint 3 Presentation
- [X]  Submit Sprint 3 

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
- [X]  Advanced clustering with K-Means
- [X]  Complete Hyperparameter optimization for K-Means
- [X]  Implement Gaussian Mixture Model clustering (with BIC/AIC evaluation)
- [X]  Complete hyperparameter optimization for Gaussian Mixture Model clustering
- [X]  Implement Agglomerative (Ward) clustering
- [X]  Complete hyperparameter optimization for Agglomerative clustering
- [X]  Implement DBSCAN / HDBSCAN clustering
- [X]  Complete hyperparameter optimization for DBSCAN / HDBSCAN clustering
- [X]  Compare clustering outcomes across algorithms and metrics
- [X]  Integrate clustering results with economic indicators at neighborhood level
- [X]  Statistical testing for comparing clusters and economic indicators
- [X]  Summarize results of comparing cluster frequencies to economic indicators
- [X]  Streamlit geo visualizer page
- [X]  Streamlit neighborhood spotlight
- [X]  Streamlit cluster explorer pages
- [X]  Streamlit correlation summary page
- [X]  Streamlit permit look up page
- [X]  Deploy web app










