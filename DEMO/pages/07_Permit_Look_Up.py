# streamlit_page: Permit Lookup by ID

import streamlit as st
import pandas as pd
from utils.load_data import load_permits, resolve_sources
from typing import Optional, Any
import html
import re


src = resolve_sources()

permits = load_permits(src["PERMITS"])

# -----------------------------
# Load data
# -----------------------------

# Parse dates if needed
if "issue_date" in permits.columns and not pd.api.types.is_datetime64_any_dtype(permits["issue_date"]):
    permits["issue_date"] = pd.to_datetime(permits["issue_date"], errors="coerce")

# Pretty project types for display (outside utils)
type_map = {
    "demo": "Demolition",
    "demolition": "Demolition",
    "reno": "Renovation",
    "renovation": "Renovation",
    "build": "Build",
    "new_build": "Build",
    "new": "Build",
}
permits["type_pretty"] = (
    permits["type"].astype(str).str.strip().str.lower().map(type_map).fillna(
        permits["type"].astype(str).str.strip().str.title()
    )
)




# -----------------------------
# Page config & intro
# -----------------------------
st.set_page_config(page_title="Permit Lookup", page_icon="🆔", layout="wide")
st.title("🆔 Permit Lookup by ID")
st.write(
    """
    Use this page to **search for a single building permit** by its `permit_id` and view
    key details at a glance. Results include the **project value**, **issue date**,
    **neighbourhood**, **coordinates**, **cluster label**,
    **permit type**, and the full **project description**.
    """
)


# -----------------------------
# Helpers
# -----------------------------
def fmt_currency(x: Optional[float]) -> str:
    if pd.isna(x):
        return "—"
    try:
        return f"${x:,.0f}"
    except Exception:
        return str(x)

def fmt_date(d: Any) -> str:
    if pd.isna(d):
        return "—"
    if isinstance(d, pd.Timestamp):
        return d.strftime("%Y-%m-%d")
    try:
        return pd.to_datetime(d).strftime("%Y-%m-%d")
    except Exception:
        return str(d)

def coerce_description(x: Any) -> str:
    """Return a full, copyable text string for the description.
    Handles bytes, containers, HTML entities, and odd whitespace.
    """
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return "—"
    try:
        if isinstance(x, (bytes, bytearray, memoryview)):
            b = bytes(x)
            for enc in ("utf-8", "utf-16", "latin-1"):
                try:
                    x = b.decode(enc)
                    break
                except Exception:
                    continue
            else:
                x = b.decode("utf-8", "ignore")
        elif isinstance(x, (list, tuple, set)):
            x = " ".join(map(str, x))
        elif isinstance(x, dict):
            x = "; ".join(f"{k}: {v}" for k, v in x.items())
        else:
            x = str(x)
        x = html.unescape(x).replace("\r\n", "\n").replace("\r", "\n").strip()
        return x
    except Exception:
        return str(x)


EMAIL_RE = re.compile(r"""
\b
[A-Za-z0-9._%+\-]+      # user
@
[A-Za-z0-9.\-]+         # domain
\.[A-Za-z]{2,}          # TLD
\b
""", re.VERBOSE | re.IGNORECASE)

PHONE_RE = re.compile(r"""
(?<!\w)                  # left boundary (not a word char)
(?:\+?1[\s.\-]?)?        # optional country code
(?:\(?\d{3}\)?[\s.\-]?)  # area code
\d{3}[\s.\-]?\d{4}       # local number
(?:\s*(?:x|ext\.?|extension)\s*\d{1,5})?  # optional extension
(?!\w)                   # right boundary (not a word char)
""", re.VERBOSE)

def anonymize_pii(text: Optional[str]) -> Optional[str]:
    if not text:
        return text
    text = EMAIL_RE.sub("[email redacted]", text)
    text = PHONE_RE.sub("[phone redacted]", text)
    return text



# def anonymize_pii(s: str, email_token: str = "[email removed]", phone_token: str = "[phone removed]") -> str:
#     """Redact emails and North American-style phone numbers from a string."""
#     if not isinstance(s, str) or not s:
#         return s
#     # Emails
#     email_re = re.compile(r"(?i)\b[\w.+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
#     s = email_re.sub(email_token, s)
#     # Phones: 604-555-1212, (604) 555-1212, +1 604 555 1212, optional ext
#     phone_re = re.compile(r"""
#         (?xi)                              # verbose, case-insensitive
#         (?<!\w)                            # left boundary
#         (?:\+?1[\s.\-]*)?                  # optional +1
#         (?:\(?\d{3}\)?[\s.\-]*)            # area code
#         \d{3}[\s.\-]*\d{4}                 # local
#         (?:\s*(?:x|ext|extension)\s*\d{1,5})?  # extension
#         (?!\w)                             # right boundary
#     """)
#     s = phone_re.sub(phone_token, s)
#     return s

def clean_description_for_display(s: str) -> str:
    """Light, safe cleaning for display (plain text), plus PII anonymization."""
    if not isinstance(s, str):
        return "—"
    # Normalize whitespace
    s = s.replace("\r\n", "\n").replace("\r", "\n").replace("\t", "  ")
    # Remove banner-style asterisk blocks, keep single *
    s = re.sub(r"\*{3,}", "", s)
    # Guard against duplicated blob pasted twice end-to-end
    half = len(s) // 2
    if len(s) >= 40 and s[:half] == s[half:]:
        s = s[:half]
    # Collapse triple+ blank lines to double
    s = re.sub(r"\n{3,}", "\n\n", s)
    # PII anonymization
    s = anonymize_pii(s)
    return s



# -----------------------------
# Search UI
# -----------------------------
st.subheader("Search")
q = st.text_input(
    "Enter a `permit_id` (exact or partial):",
    placeholder="e.g., B2018-04595",
)

# Strategy:
# 1) If exact match exists, prefer it.
# 2) Else, show partial matches (case-insensitive contains).
results = pd.DataFrame()
if q:
    q_str = str(q).strip()
    # exact match
    exact = permits[permits["permit_id"].astype(str) == q_str]
    if not exact.empty:
        results = exact
    else:
        results = permits[permits["permit_id"].astype(str).str.contains(q_str, case=False, na=False)]

# -----------------------------
# Results rendering
# -----------------------------
if q and results.empty:
    st.warning("No permits found for that ID. Try a different value or partial search.")

elif not results.empty:
    st.caption(f"Found **{len(results)}** match(es).")

    # Prepare a compact table for multi-match selection
    table = (
        results[["permit_id", "issue_date", "nbhd", "type_pretty", "cluster_label", "project_value"]]
        .assign(issue_date=lambda d: pd.to_datetime(d["issue_date"]).dt.strftime("%Y-%m-%d"))
        .rename(
            columns={
                "permit_id": "Permit ID",
                "issue_date": "Issue Date",
                "nbhd": "Neighbourhood",
                "type_pretty": "Type",
                "cluster_label": "Cluster",
                "project_value": "Project Value",
            }
        )
    )

    if len(results) > 1:
        st.dataframe(table, use_container_width=True, hide_index=True)
        selected_id = st.selectbox(
            "Select a permit to view details:",
            options=results["permit_id"].astype(str).tolist(),
        )
        row = results[results["permit_id"].astype(str) == str(selected_id)].iloc[0]
    else:
        row = results.iloc[0]

    # Detail view
    st.subheader("Details")
    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1:
        st.metric("Permit ID", str(row["permit_id"]))
        st.metric("Project Value", fmt_currency(row.get("project_value")))
        st.metric("Issue Date", fmt_date(row.get("issue_date")))
    with c2:
        st.metric("Neighbourhood", row.get("nbhd", "—"))
        st.metric("Type", row.get("type_pretty", "—"))
        st.metric("Cluster #", str(row.get("cluster", "—")))
    with c3:
        st.metric("Cluster Label", row.get("cluster_label", "—"))
        # Coordinates (copy-friendly)
        lat = row.get("lat")
        lon = row.get("lon")
        coord_str = "" if pd.isna(lat) or pd.isna(lon) else f"{lat:.6f}, {lon:.6f}"
        st.text_input("Coordinates (lat, lon)", value=coord_str, disabled=False)
        if coord_str:
            maps_url = f"https://www.google.com/maps?q={lat},{lon}"
            st.markdown(f"[Open in Google Maps]({maps_url})")

    # Project Description (plain text, lightly cleaned & anonymized)
    st.markdown("**Project Description**")
    raw_desc = row.get("project_description")
    desc = clean_description_for_display(coerce_description(raw_desc))
    st.markdown(
        f"<div style='white-space:pre-wrap; font-family:system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; line-height:1.5'>{html.escape(desc)}</div>",
        unsafe_allow_html=True,
    )

else:
    st.info("Enter a permit ID above to search.")



# Random test examples

# 15616    R2023-00440
# 12464    D2017-03002
# 8485     B2018-08485
# 16887    R2017-01711
# 4595     B2018-04595 # Phone number test in this one
# 11089    D2022-01627
# 5061     B2023-05061
# 4629     B2017-04629
# 15865    R2020-00689
# 14934    D2021-05472