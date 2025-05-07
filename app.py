import streamlit as st
from wordle_v2 import load_words, apply_feedback, score_letters, score_words

st.set_page_config(page_title="Wordle Solver", layout="centered")

st.title("Wordle Solver Assistant")
st.write("Enter your guess and the corresponding feedback to get the next best guesses.")

# Initialize session state
if "candidates" not in st.session_state:
    st.session_state.candidates = load_words()
if "history" not in st.session_state:
    st.session_state.history = []

# Input section
guess = st.text_input("Enter your 5-letter guess:", max_chars=5).lower()
feedback = st.text_input("Enter feedback (b = black, g = green, y = yellow):", max_chars=5).lower()

col1, col2 = st.columns(2)
with col1:
    reset = st.button("Reset")
with col2:
    submit = st.button("Submit")

# Reset app state
if reset:
    st.session_state.candidates = load_words()
    st.session_state.history = []
    st.success("Solver reset.")

# Handle input and update suggestions
if submit:
    if len(guess) != 5 or len(feedback) != 5:
        st.error("Both guess and feedback must be 5 characters long.")
    else:
        st.session_state.candidates = apply_feedback(guess, feedback, st.session_state.candidates)
        st.session_state.history.append((guess, feedback))

# Show history
if st.session_state.history:
    st.subheader("Guess History")
    for i, (g, f) in enumerate(st.session_state.history, 1):
        st.markdown(f"**{i}.** `{g.upper()}` — `{f.upper()}`")

# Show top suggestions
if st.session_state.candidates:
    st.subheader("Top Suggestions")
    scores = score_letters(st.session_state.candidates)
    suggestions = score_words(st.session_state.candidates, scores)[:5]
    st.write(", ".join(suggestions))
else:
    st.warning("No candidates remaining. Try resetting or checking your input.")
