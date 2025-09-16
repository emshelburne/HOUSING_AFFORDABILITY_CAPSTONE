# streamlit_page: Correlation Summary

import streamlit as st
import pandas as pd
from utils.load_data import load_corr_results, resolve_sources
from utils.figures import plot_corr_bars


# ---------------- Load Data ----------------
src = resolve_sources()

spearman_df = load_corr_results(src["SPEARMAN"])
kendall_df  = load_corr_results(src["KENDALL"])




# ---------------- Header ----------------
st.header("Correlation Summary: Cluster Intensity vs. Economic Metrics for Renters")

# ---------------- Methodology ----------------
st.subheader("Methodology Overview")

st.markdown(
    """
We quantify how **development activity** in each neighbourhood–year relates to **future rental outcomes** (rents and vacancy). The pipeline:
1) **Cluster permits** (builds, demolitions, renovations) into interpretable groups.  
2) **Compute intensity scores** per neighbourhood–year using an NLP-inspired TF–IDF analogue.  
3) **Correlate** those scores with **future** rental outcomes at leads of 1–5 years.
"""
)

st.markdown("**NF–ICF (Neighborhood Frequency – Inverse City Frequency).** For development type \(d\) and cluster \(K\):")

st.latex(r"""
\begin{aligned}
\mathrm{share}_{i,t}^{(d,K)} 
   &= \frac{N_{i,t}^{(d,K)}}{N_{i,t}^{(d)}}, 
   & N_{i,t}^{(d,K)} &= \text{\# permits in neighbourhood $i$, year $t$, type $d$, cluster $K$}, \\
   && N_{i,t}^{(d)} &= \text{\# permits in neighbourhood $i$, year $t$, type $d$}. \\[1em]

\mathrm{ICF}_{d,K} 
   &= \log \!\left( \frac{N_{d}^{\mathrm{city}} + s}{N_{d,K}^{\mathrm{city}} + s} \right),
   & N_{d,K}^{\mathrm{city}} &= \text{\# permits citywide of type $d$ in cluster $K$}, \\
   && N_{d}^{\mathrm{city}} &= \text{\# permits citywide of type $d$ (all clusters)}. \\[1em]
    
\text{NF\text{-}ICF}_{i,t}^{(d,K)} 
   &= \mathrm{share}_{i,t}^{(d,K)} \times \mathrm{ICF}_{d,K}.
\end{aligned}

""")

st.markdown(
    "We set the smoothing constant to **s = 1**, ensuring that very rare clusters "
    "do not yield undefined or excessively large weights."
)


st.info(
    "We tested **Pearson**, **Spearman’s rank**, and **Kendall’s tau** correlations. Pearson yielded no statistically "
    "significant results, suggesting no strong linear relationships. Because we ran many tests across clusters, metrics, "
    "and lags, we applied **Benjamini–Hochberg FDR** at q = 10% (and also show a more lenient 20%). "
    "No associations survived **adjusted p < 0.05**, which is common in exploratory settings."
)


# ---------------- Spearman ----------------
st.subheader("Spearman Correlations")
st.caption("FDR-adjusted results at 10% (primary) and 20% (exploratory).")

with st.expander("Significant at 10% FDR (|corr| ≥ 0.25) — Spearman"):
    st.markdown(
        """
##### Renovations
- **''Reno Cluster 1 (Single-Detached Home Renovations)**  
  ↔ **Vacancy Rate (3+ BR), Lead 5 years** — **+0.46**  
  *Interpretation:* Higher detached-home renovation intensity links to **higher large-unit vacancy** after five years.  
  *Speculative link:* Renovations may shift neighbourhood composition, increasing turnover or availability in large rentals.  

##### New Buildings
- **''Build Cluster 0 (Small Detached & Duplex Mix)**  
  ↔ **Vacancy Rate (Total; 1BR; 2BR; 3+BR), Lead 2–3 years**; **Avg Rent (1BR), Lead 2 years** — **−0.36 to −0.39**  
  *Interpretation:* Detached/duplex activity is associated with **lower near-term vacancies and slower 1BR rent growth**.  
  *Speculative link:* Modest infill may relieve localized pressure in smaller-unit markets.  

- **''Build Cluster 0 (Small Detached & Duplex Mix)**  
  ↔ **Vacancy Rate (3+ BR), Lead 5 years** — **+0.49**  
  *Interpretation:* Over longer horizons, the same activity corresponds to **higher vacancies in large rentals**.  
  *Speculative link:* Detached/duplex homes may substitute for large rentals, increasing vacancies in that segment.  

- **''Build Cluster 2 (Mid-Value Family Housing)**  
  ↔ **Vacancy Rate (3+ BR), Lead 4 years** — **−0.39**  
  *Interpretation:* Family-oriented builds correlate with **tighter large-unit vacancies** later on.  
  *Speculative link:* Demand spillovers from family-focused development may tighten nearby large-unit markets.  

- **''Build Cluster 5 (Duplexes with Secondary Suites)**  
  ↔ **Vacancy Rate (Total), Lead 1 year** — **+0.47**  
  *Interpretation:* Suite-heavy duplexes associate with **higher short-run total vacancies**.  
  *Speculative link:* Rapid addition of suites may temporarily expand rental options and raise vacancy.  
        """
    )

with st.expander("Exploratory at 20% FDR (|corr| ≥ 0.25) — Spearman"):
    st.markdown(
        """
##### New Buildings
- **''Build Cluster 5 (Duplexes + Suites)**  
  ↔ **Vacancy (3+ BR), Lead 1 year** — **+0.45**  
  *Speculative link:* New suites may compete with large rentals in the short run.  

- **''Build Cluster 0 (Small Detached & Duplex)**  
  ↔ **Median Rent (Studios), Lead 2 years** — **−0.33**  
  *Speculative link:* Modest infill may dampen studio rent growth.  

- **''Build Cluster 7 (Large Midrise Projects)**  
  ↔ **Avg Rent (Total), Lead 4 years** — **−0.45**  
  *Speculative link:* Larger multi-unit supply may stabilize overall rents.  

- **''Build Cluster 0**  
  ↔ **Vacancy (Total), L4–5y** — **+0.39 to +0.44**  
  *Speculative link:* Detached/duplex infill may loosen occupancy over time.  

- **''Build Cluster 0**  
  ↔ **Vacancy (Studios), Lead 2 years** — **−0.32**  
  *Speculative link:* Heterogeneous effects by unit size—pressure easing in very small units.  

##### Renovations
- **''Reno Cluster 4 (Large-Scale Structural Repairs)**  
  ↔ **Median Rent (1BR), Lead 1 year** — **−0.62**  
  *Speculative link:* Large scale repairs may expand the rental market, softening rent growth.  

- **''Reno Cluster 5 (Multi-Unit Alterations)**  
  ↔ **Vacancy (1BR), Lead 3 years** — **−0.80**  
  *Speculative link:* Targeted upgrades in persistently occupied buildings.  
        """
    )

st.plotly_chart(
    plot_corr_bars(spearman_df, method="spearman", title="Suggestive Correlations"),
    use_container_width=True
)

st.markdown("---")

# ---------------- Kendall ----------------
st.subheader("Kendall Correlations")
st.caption("FDR-adjusted results at 10% (primary) and 20% (exploratory).")

with st.expander("Significant at 10% FDR (|corr| ≥ 0.25) — Kendall"):
    st.markdown(
        """
##### Renovations
- **''Reno Cluster 1 (Single-Detached Home Renovations)**  
  ↔ **Vacancy Rate (3+ BR), Lead 4 years** — **+0.34**  
  *Interpretation:* Renovation intensity associates with **higher large-unit vacancy** after five years.  
  *Speculative link:* Longer-run neighbourhood change altering demand in large rental stock.  

##### New Buildings
- **''Build Cluster 0 (Small Detached & Duplex Mix)**  
  ↔ **Avg Rent (1BR), Lead 2 years**; **Vacancy (Total, 1BR, 2BR, 3+BR), L2–3y** — **−0.26 to −0.28**  
  *Interpretation:* Detached/duplex activity corresponds to **slower 1BR rent growth** and **lower near-term vacancies**.  
  *Speculative link:* Modest infill can relieve local pressure and stabilize occupancy.  

- **''Build Cluster 0**  
  ↔ **Vacancy (3+ BR), Lead 4 years** — **+0.39**  
  *Interpretation:* Longer-run **higher large-unit vacancies**.  
  *Speculative link:* Substitution away from multi-bedroom rentals toward detached/duplex options.  

- **''Build Cluster 2 (Mid-Value Family Housing)**  
  ↔ **Vacancy (3+ BR), Lead 4 years** — **−0.29**  
  *Interpretation:* Family-oriented builds correlate with **tighter large-unit vacancies**.  
  *Speculative link:* Demand spillovers tighten the larger-unit segment.  
        """
    )

with st.expander("Exploratory at 20% FDR (|corr| ≥ 0.25) — Kendall"):
    st.markdown(
        """
##### New Buildings
- **''Build Cluster 0 (Small Detached & Duplex)**  
  ↔ **Vacancy (Total), L4–5y** — **+0.27 to +0.35**  
  *Speculative link:* Longer-run loosening of occupancy as detached/duplex stock expands.  

- **''Build Cluster 5 (Duplexes + Suites)**  
  ↔ **Vacancy (Total / 3+BR / Studios), Lead 1 year** — **+0.30 to +0.33** (n≈48)  
  *Speculative link:* Rapid suite supply raises short-run vacancy across segments.  

- **''Build Cluster 7 (Large Midrise Projects)**  
  ↔ **Avg Rent (Total), Lead 4 years** — **−0.30**  
  *Speculative link:* Medium-term rent stabilization from larger multi-unit supply.  

- **''Build Cluster 4 (Small + Suites/Laneways)**  
  ↔ **Median Rent (3+BR), Lead 1 year** — **−0.32**  
  *Speculative link:* Added suites/laneways may ease pressure on family-sized rentals.  
        """
    )

st.plotly_chart(
    plot_corr_bars(kendall_df, method="kendall", title="Suggestive Correlations"),
    use_container_width=True
)

# ---------------- Footer ----------------
st.caption(
    "All correlations use **future outcomes** (leads) and **FDR adjustment**. Interpret as exploratory associations, not causal effects."
)