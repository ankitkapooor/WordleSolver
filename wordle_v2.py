import operator
from collections import Counter

# Load the word list once
def load_words(filepath="assets/words.csv"):
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip()[:5] for line in f if len(line.strip()) == 5]

# Score letters based on frequency in the current word pool
def score_letters(wordlist):
    letter_counts = Counter()
    for word in wordlist:
        letter_counts.update(set(word))  # Set to avoid overcounting duplicate letters
    total = sum(letter_counts.values())
    scores = {char: freq / total for char, freq in letter_counts.items()}
    return scores

# Score each word based on letter frequency
def score_words(wordlist, letter_scores):
    word_scores = {}
    for word in wordlist:
        score = sum(letter_scores.get(char, 0) for char in set(word))  # Set to avoid double count
        word_scores[word] = score
    return sorted(word_scores, key=word_scores.get, reverse=True)

# Filter out invalid words based on feedback
def apply_feedback(guess, feedback, candidates):
    new_candidates = []
    for word in candidates:
        valid = True
        for i in range(5):
            g_letter, f = guess[i], feedback[i].lower()
            if f == 'g':
                if word[i] != g_letter:
                    valid = False
                    break
            elif f == 'y':
                if g_letter not in word or word[i] == g_letter:
                    valid = False
                    break
            elif f == 'b':
                # Handle gray with care: only eliminate if the letter doesn't appear elsewhere green/yellow
                if g_letter in word:
                    # Check how many times letter is green/yellow in guess
                    min_required = sum(
                        1 for j in range(5)
                        if guess[j] == g_letter and feedback[j].lower() in ('g', 'y')
                    )
                    actual_count = word.count(g_letter)
                    if actual_count > min_required:
                        valid = False
                        break
        if valid:
            new_candidates.append(word)
    return new_candidates

# Check if we have a strategic elimination opportunity
def check_elimination_opportunity(candidates, feedback, full_wordlist):
    """
    Check if we have 4 greens, 1 black pattern with multiple candidates
    that differ by only one letter in the same position
    """
    if len(candidates) <= 2:
        return None
    
    # Count green and black positions
    green_count = sum(1 for f in feedback if f.lower() == 'g')
    black_count = sum(1 for f in feedback if f.lower() == 'b')
    
    # We need exactly 4 greens and 1 black
    if green_count != 4 or black_count != 1:
        return None
    
    # Find the position that varies (where we had the black feedback)
    varying_position = None
    for i, f in enumerate(feedback):
        if f.lower() == 'b':
            varying_position = i
            break
    
    if varying_position is None:
        return None
    
    # Get the letters that differ at this position
    differing_letters = set()
    for word in candidates:
        differing_letters.add(word[varying_position])
    
    # We need at least 3 different letters to make this worthwhile
    if len(differing_letters) < 3:
        return None
    
    # Find a word from the full wordlist that contains as many of these letters as possible
    best_elimination_word = None
    max_letters_covered = 0
    
    for word in full_wordlist:
        if word in candidates:
            continue  # Skip words that are already candidates
        
        letters_covered = sum(1 for letter in differing_letters if letter in word)
        
        # Prioritize words that cover more differing letters
        if letters_covered > max_letters_covered and letters_covered >= 3:
            max_letters_covered = letters_covered
            best_elimination_word = word
    
    if best_elimination_word and max_letters_covered >= 3:
        return {
            'word': best_elimination_word,
            'letters_covered': max_letters_covered,
            'differing_letters': differing_letters,
            'varying_position': varying_position
        }
    
    return None

# Main solver loop
def wordle_solver():
    wordlist = load_words()
    candidates = wordlist.copy()
    attempts = 0
    last_feedback = None
    
    while candidates and attempts < 6:
        guess = input("Enter your guess: ").strip().lower()
        feedback = input("Enter feedback (b/g/y): ").strip().lower()
        
        if len(guess) != 5 or len(feedback) != 5:
            print("Invalid input length. Try again.")
            continue
        
        candidates = apply_feedback(guess, feedback, candidates)
        
        # Check for strategic elimination opportunity
        elimination_opportunity = check_elimination_opportunity(candidates, feedback, wordlist)
        
        if elimination_opportunity:
            # Compute standard ranked suggestions
            letter_scores = score_letters(candidates)
            ranked_words = score_words(candidates, letter_scores)

            # Put the recommended elimination word at the front of the suggestions list
            suggestions = [elimination_opportunity['word']] + [w for w in ranked_words if w != elimination_opportunity['word']]

            # Limit to the first 5 suggestions for display
            suggestions = suggestions[:5]

            print("Top 5 suggestions:", ", ".join(word.upper() for word in suggestions))
        else:
            # Regular scoring and suggestions
            letter_scores = score_letters(candidates)
            top_words = score_words(candidates, letter_scores)[:5]
            print("Top 5 suggestions:", ", ".join(word.upper() for word in top_words))
        
        print(f"Remaining candidates: {len(candidates)}")
        
        attempts += 1
        last_feedback = feedback
    
    if not candidates:
        print("No valid words remain. Check your feedback or guess.")
    else:
        print("Solver finished in", attempts, "attempts.")

# Run the solver
if __name__ == "__main__":
    wordle_solver()
