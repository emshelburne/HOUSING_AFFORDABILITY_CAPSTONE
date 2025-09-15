# Vancouver Housing Permits & Rental Market Explorer

This Streamlit app provides an interactive way to explore how patterns in **building, demolition, and renovation permits** 
relate to **Vancouver’s rental housing market**. 

---

## Project Overview
- **Data Sources:**  
  - City of Vancouver Open Data (permit records)  
  - CMHC (rent and vacancy metrics)  

- **Clustering Approach:**  
  We tested **K-Means, Gaussian Mixture Models, HDBSCAN, and Agglomerative Clustering**.  
  **Agglomerative Clustering** was found to provide the clearest, most interpretable clusters of permit activity.  

- **Custom Metric:**  
  Introduced the **NFiCF metric (Neighborhood Fraction in Cluster Frequency)** to track cluster intensity 
  in a given neighborhood over time.  

- **Economic Links:**  
  We then examined correlations between permit cluster activity and renter-focused outcomes 
  (average/median rents and vacancy rates).  

- **Important Notes:**  
  - All financial values are CPI-adjusted to **2024 CAD**.  
  - Correlations are **exploratory only**—they should not be interpreted as causal or definitive.  

---

## App Features
- **Geographic Visualizer**  
  Animated map showing monthly permits overlaid on neighborhoods shaded by rent or vacancy metrics.  

- **Neighborhood Spotlight**  
  Select a neighborhood to view animated cluster breakdowns alongside rent/vacancy trends.  

- **Cluster Visualizers**  
  Explore cluster definitions and interpretations for **Builds, Renovations, and Demolitions**.  

- **Correlation Summary**  
  Review our main findings linking permit clusters to rental outcomes, with bar charts and expandable explanations.  

- **Permit Lookup**  
  Search and inspect individual permits (emails and phone numbers anonymized for privacy).  

---

## Running the App
From inside the `app` folder, run:

```bash
streamlit run Home_Page.py
