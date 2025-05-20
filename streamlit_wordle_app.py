import streamlit as st
import pathlib, json, re

st.set_page_config(page_title="Wordle Solver Assistant", page_icon="🟩", layout="centered")

BASE_DIR = pathlib.Path(__file__).parent
html_path = BASE_DIR / "frontend" / "wordle_solver.html"
csv_path = BASE_DIR / "assets" / "words.csv"

if not html_path.exists():
    st.error(f"❌ Could not locate {html_path} – make sure you've generated the React bundle.")
    st.stop()

# Load the word list from CSV (only 5-letter words)
if csv_path.exists():
    words = [ln.strip()[:5] for ln in csv_path.read_text(encoding="utf-8").splitlines() if len(ln.strip()) == 5]
else:
    st.warning(f"⚠️ {csv_path} not found – falling back to default list.")
    words = ["apple", "table", "chair", "beach", "world", "house", "music", "water", "plant", "phone"]

# Read HTML template and inject the word list as JSON
html_src = html_path.read_text(encoding="utf-8")

# Replace the placeholder token __WORDLIST__ (must be a valid JS expression)
words_json = json.dumps(words)
html_src = re.sub(r"__WORDLIST__", words_json, html_src)

st.components.v1.html(html_src, height=1100, scrolling=True) 