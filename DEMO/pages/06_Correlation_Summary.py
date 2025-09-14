# streamlit_page: Correlation Summary

import streamlit as st
import pandas as pd
from utils.load_data import load_corr_results
from utils.figures import plot_corr_bars

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

\mathrm{NFICF}_{i,t}^{(d,K)} 
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

# ---------------- Load Data ----------------
SPEARMAN_PATH = r"C:\Users\emshe\Desktop\BRAINSTATION\CAPSTONE\GIT_REPO\DEMO\data\spearman.csv"
KENDALL_PATH  = r"C:\Users\emshe\Desktop\BRAINSTATION\CAPSTONE\GIT_REPO\DEMO\data\kendall.csv"

@st.cache_data(show_spinner=False)
def _load_corr(path: str) -> pd.DataFrame:
    df = load_corr_results(path)
    # Ensure expected columns
    for col in ["method"]:
        if col not in df.columns:
            df[col] = pd.NA
    return df

spearman_df = _load_corr(SPEARMAN_PATH)
kendall_df  = _load_corr(KENDALL_PATH)

# ---------------- Spearman ----------------
st.subheader("Spearman Correlations")
st.caption("FDR-adjusted results at 10% (primary) and 20% (exploratory).")

with st.expander("Significant at 10% FDR (|corr| ≥ 0.25) — Spearman"):
    st.markdown(
        """
##### Renovations
- **NFICF_Reno Cluster 1 (Single-Detached Home Renovations)**  
  ↔ **Vacancy Rate (3+ BR), Lead 5 years** — **+0.46** (n=67)  
  *Interpretation:* Higher detached-home renovation intensity links to **higher large-unit vacancy** after five years.  
  *Speculative link:* Renovations may shift neighbourhood composition, increasing turnover or availability in large rentals.

##### New Buildings
- **NFICF_Build Cluster 0 (Small Detached & Duplex Mix)**  
  ↔ **Vacancy Rate (Total; 1BR; 2BR; 3+BR), Lead 2–3 years**; **Avg Rent (1BR), Lead 2 years** — **−0.36 to −0.39**  
  *Interpretation:* Detached/duplex activity is associated with **lower near-term vacancies and slower 1BR rent growth**.  
  *Speculative link:* Modest infill may relieve localized pressure in smaller-unit markets.

- **NFICF_Build Cluster 0 (Small Detached & Duplex Mix)**  
  ↔ **Vacancy Rate (3+ BR), Lead 5 years** — **+0.49** (n=45)  
  *Interpretation:* Over longer horizons, the same activity corresponds to **higher vacancies in large rentals**.  
  *Speculative link:* Detached/duplex homes may substitute for large rentals, increasing vacancies in that segment.

- **NFICF_Build Cluster 2 (Mid-Value Family Housing)**  
  ↔ **Vacancy Rate (3+ BR), Lead 4 years** — **−0.39** (n=76)  
  *Interpretation:* Family-oriented builds correlate with **tighter large-unit vacancies** later on.  
  *Speculative link:* Demand spillovers from family-focused development may tighten nearby large-unit markets.

- **NFICF_Build Cluster 5 (Duplexes with Secondary Suites)**  
  ↔ **Vacancy Rate (Total), Lead 1 year** — **+0.47** (n=48)  
  *Interpretation:* Suite-heavy duplexes associate with **higher short-run total vacancies**.  
  *Speculative link:* Rapid addition of suites may temporarily expand rental options and raise vacancy.
        """
    )

with st.expander("Exploratory at 20% FDR — Spearman"):
    st.markdown(
        """
##### New Buildings
- **NFICF_Build Cluster 5 (Duplexes + Suites)** ↔ **Vacancy (3+ BR), L1y** — **+0.45** (n=48)  
  *Speculative link:* New suites may compete with large rentals in the short run.

- **NFICF_Build Cluster 0 (Small Detached & Duplex)** ↔ **Median Rent (Studios), L2y** — **−0.33** (n=90)  
  *Speculative link:* Modest infill may dampen studio rent growth.

- **NFICF_Build Cluster 7 (Large Midrise Projects)** ↔ **Avg Rent (Total), L4y** — **−0.45** (n=48)  
  *Speculative link:* Larger multi-unit supply may stabilize overall rents.

- **NFICF_Build Cluster 0** ↔ **Vacancy (Total), L4–5y** — **+0.39 to +0.44** (n=60/45)  
  *Speculative link:* Detached/duplex infill may loosen occupancy over time.

- **NFICF_Build Cluster 0** ↔ **Vacancy (Studios), L2y** — **−0.32** (n=90)  
  *Speculative link:* Heterogeneous effects by unit size—pressure easing in very small units.

##### Renovations
- **NFICF_Reno Cluster 4 (Large-Scale Structural Repairs)** ↔ **Median Rent (1BR), L1y** — **−0.62** (n=23)  
  *Speculative link:* Rehabs may bring stock back online, softening rent growth.

- **NFICF_Reno Cluster 5 (Multi-Unit Alterations)** ↔ **Vacancy (1BR), L3y** — **−0.80** (n=12)  
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
- **NFICF_Reno Cluster 1 (Single-Detached Home Renovations)**  
  ↔ **Vacancy Rate (3+ BR), L5y** — **+0.34** (n=67)  
  *Interpretation:* Renovation intensity associates with **higher large-unit vacancy** after five years.  
  *Speculative link:* Longer-run neighbourhood change altering demand in large rental stock.

##### New Buildings
- **NFICF_Build Cluster 0 (Small Detached & Duplex Mix)**  
  ↔ **Avg Rent (1BR), L2y**; **Vacancy (Total, 1BR, 2BR, 3+BR), L2–3y** — **−0.26 to −0.28**  
  *Interpretation:* Detached/duplex activity corresponds to **slower 1BR rent growth** and **lower near-term vacancies**.  
  *Speculative link:* Modest infill can relieve local pressure and stabilize occupancy.

- **NFICF_Build Cluster 0**  
  ↔ **Vacancy (3+ BR), L5y** — **+0.39** (n=45)  
  *Interpretation:* Longer-run **higher large-unit vacancies**.  
  *Speculative link:* Substitution away from multi-bedroom rentals toward detached/duplex options.

- **NFICF_Build Cluster 2 (Mid-Value Family Housing)**  
  ↔ **Vacancy (3+ BR), L4y** — **−0.29** (n=76)  
  *Interpretation:* Family-oriented builds correlate with **tighter large-unit vacancies**.  
  *Speculative link:* Demand spillovers tighten the larger-unit segment.
        """
    )

with st.expander("Exploratory at 20% FDR — Kendall"):
    st.markdown(
        """
##### New Buildings
- **NFICF_Build Cluster 0 (Small Detached & Duplex)** ↔ **Vacancy (Total), L4–5y** — **+0.27 to +0.35** (n=45–60)  
  *Speculative link:* Longer-run loosening of occupancy as detached/duplex stock expands.

- **NFICF_Build Cluster 5 (Duplexes + Suites)**  
  ↔ **Vacancy (Total / 3+BR / Studios), L1y** — **+0.30 to +0.33** (n≈48)  
  *Speculative link:* Rapid suite supply raises short-run vacancy across segments.

- **NFICF_Build Cluster 7 (Large Midrise Projects)** ↔ **Avg Rent (Total), L4y** — **−0.30** (n=48)  
  *Speculative link:* Medium-term rent stabilization from larger multi-unit supply.

- **NFICF_Build Cluster 4 (Small + Suites/Laneways)** ↔ **Median Rent (3+BR), L1y** — **−0.32** (n=43)  
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