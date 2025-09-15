import os, pathlib

# Make sure the first-run credentials file exists (silences email prompt)
cred = pathlib.Path.home() / ".streamlit" / "credentials.toml"
if not cred.exists():
    cred.parent.mkdir(parents=True, exist_ok=True)
    cred.write_text('[general]\nemail=""\n', encoding="utf-8")

# Also disable usage stats prompt via env (backstop)
os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "true")
os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")

import streamlit as st
st.set_page_config(page_title="Boot OK", layout="centered")
st.write(" Minimal app booted")

