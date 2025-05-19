import streamlit as st
from wordle_v2 import load_words, apply_feedback, score_letters, score_words

# Page configuration
st.set_page_config(page_title="Wordle Solver", layout="centered")

# Custom CSS for Wordle-like styling
st.markdown("""
<style>
    .tile-container {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin: 20px 0;
    }
    
    .tile {
        width: 60px;
        height: 60px;
        border: 2px solid #d3d6da;
        border-radius: 3px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        font-weight: bold;
        text-transform: uppercase;
        cursor: pointer;
        user-select: none;
        transition: all 0.1s ease;
    }
    
    .tile-black {
        background-color: #787c7e;
        border-color: #787c7e;
        color: white;
    }
    
    .tile-yellow {
        background-color: #c9b458;
        border-color: #c9b458;
        color: white;
    }
    
    .tile-green {
        background-color: #6aaa64;
        border-color: #6aaa64;
        color: white;
    }
    
    .tile-empty {
        background-color: white;
        border-color: #d3d6da;
        color: black;
    }
    
    .tile:hover {
        transform: scale(1.05);
    }
    
    .history-tile {
        width: 30px;
        height: 30px;
        border: 1px solid #d3d6da;
        border-radius: 3px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: bold;
        text-transform: uppercase;
        margin: 1px;
    }
    
    .suggestion-word {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 5px;
        padding: 8px 12px;
        margin: 4px;
        display: inline-block;
        font-family: monospace;
        font-weight: bold;
    }
    
    .centered-content {
        max-width: 500px;
        margin: 0 auto;
    }
    
    .stButton>button {
        background-color: #6aaa64;
        color: white;
        border: none;
        border-radius: 3px;
        padding: 8px 20px;
        font-weight: bold;
    }
    
    .stButton>button:hover {
        background-color: #5a9a54;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "candidates" not in st.session_state:
    st.session_state.candidates = load_words()
if "history" not in st.session_state:
    st.session_state.history = []
if "current_guess" not in st.session_state:
    st.session_state.current_guess = ["", "", "", "", ""]
if "current_feedback" not in st.session_state:
    st.session_state.current_feedback = ["b", "b", "b", "b", "b"]

# Title
st.markdown("<div class='centered-content'>", unsafe_allow_html=True)
st.title("🟩 Wordle Solver Assistant")
st.write("Enter your 5-letter guess and click tiles to set their colors based on Wordle's feedback.")

# Input for the guess word
guess_input = st.text_input("Enter your 5-letter guess:", max_chars=5, key="guess_input").lower()

# Update current_guess when input changes
if len(guess_input) <= 5:
    for i in range(5):
        if i < len(guess_input):
            st.session_state.current_guess[i] = guess_input[i]
        else:
            st.session_state.current_guess[i] = ""

# Function to get tile class based on feedback
def get_tile_class(feedback):
    if feedback == "g":
        return "tile-green"
    elif feedback == "y":
        return "tile-yellow"
    elif feedback == "b":
        return "tile-black"
    else:
        return "tile-empty"

# Create clickable tiles
st.markdown("**Click tiles to change colors:** Gray → Yellow → Green → Gray")

# Create the tile interface using columns
cols = st.columns(5)
for i in range(5):
    with cols[i]:
        # Display the tile
        letter = st.session_state.current_guess[i].upper() if st.session_state.current_guess[i] else ""
        tile_class = get_tile_class(st.session_state.current_feedback[i])
        
        # Create a clickable button for each tile
        if st.button(f"{letter}", key=f"tile_{i}", help=f"Click to change color for position {i+1}"):
            # Cycle through feedback states: b -> y -> g -> b
            current = st.session_state.current_feedback[i]
            if current == "b":
                st.session_state.current_feedback[i] = "y"
            elif current == "y":
                st.session_state.current_feedback[i] = "g"
            else:
                st.session_state.current_feedback[i] = "b"
            st.rerun()

# Display current feedback as colored tiles using HTML
feedback_html = "<div class='tile-container'>"
for i in range(5):
    letter = st.session_state.current_guess[i].upper() if st.session_state.current_guess[i] else ""
    tile_class = get_tile_class(st.session_state.current_feedback[i])
    feedback_html += f"<div class='tile {tile_class}'>{letter}</div>"
feedback_html += "</div>"
st.markdown(feedback_html, unsafe_allow_html=True)

# Legend
st.markdown("""
**Legend:**
- 🔲 Gray: Letter not in word
- 🟨 Yellow: Letter in word, wrong position  
- 🟩 Green: Letter in word, correct position
""")

# Control buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Reset", key="reset_btn"):
        st.session_state.candidates = load_words()
        st.session_state.history = []
        st.session_state.current_guess = ["", "", "", "", ""]
        st.session_state.current_feedback = ["b", "b", "b", "b", "b"]
        st.success("Solver reset!")
        st.rerun()

with col2:
    if st.button("✅ Submit Guess", key="submit_btn"):
        # Validate input
        guess = "".join(st.session_state.current_guess)
        feedback = "".join(st.session_state.current_feedback)
        
        if len(guess) != 5:
            st.error("Please enter a complete 5-letter word.")
        elif not guess.replace(" ", ""):
            st.error("Please enter a valid word.")
        else:
            # Apply feedback and update candidates
            st.session_state.candidates = apply_feedback(guess, feedback, st.session_state.candidates)
            st.session_state.history.append((guess, feedback))
            
            # Reset for next guess
            st.session_state.current_guess = ["", "", "", "", ""]
            st.session_state.current_feedback = ["b", "b", "b", "b", "b"]
            st.success(f"Guess submitted! {len(st.session_state.candidates)} candidates remaining.")
            st.rerun()

# Show history with visual tiles
if st.session_state.history:
    st.subheader("📝 Guess History")
    for i, (g, f) in enumerate(st.session_state.history, 1):
        # Create a visual representation of each guess
        history_html = f"<div style='margin: 10px 0;'><strong>{i}.</strong> "
        for j in range(5):
            letter = g[j].upper()
            tile_class = get_tile_class(f[j])
            history_html += f"<span class='history-tile {tile_class}'>{letter}</span>"
        history_html += "</div>"
        st.markdown(history_html, unsafe_allow_html=True)

# Show top suggestions
if st.session_state.candidates:
    st.subheader("💡 Top Suggestions")
    scores = score_letters(st.session_state.candidates)
    suggestions = score_words(st.session_state.candidates, scores)[:5]
    
    # Display suggestions as styled words
    suggestions_html = "<div>"
    for word in suggestions:
        suggestions_html += f"<span class='suggestion-word'>{word.upper()}</span>"
    suggestions_html += "</div>"
    st.markdown(suggestions_html, unsafe_allow_html=True)
    
    st.caption(f"Showing top {len(suggestions)} out of {len(st.session_state.candidates)} remaining candidates")
else:
    st.warning("⚠️ No candidates remaining. Try resetting or checking your input.")

st.markdown("</div>", unsafe_allow_html=True)
