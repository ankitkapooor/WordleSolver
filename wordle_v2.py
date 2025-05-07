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

# Main solver loop
def wordle_solver():
    wordlist = load_words()
    candidates = wordlist.copy()
    attempts = 0

    while candidates and attempts < 6:
        guess = input("Enter your guess: ").strip().lower()
        feedback = input("Enter feedback (b/g/y): ").strip().lower()

        if len(guess) != 5 or len(feedback) != 5:
            print("Invalid input length. Try again.")
            continue

        candidates = apply_feedback(guess, feedback, candidates)
        letter_scores = score_letters(candidates)
        top_words = score_words(candidates, letter_scores)[:5]

        print("Top 5 suggestions:", ", ".join(top_words))
        attempts += 1

    if not candidates:
        print("No valid words remain. Check your feedback or guess.")
    else:
        print("Solver finished in", attempts, "attempts.")

# Run the solver
if __name__ == "__main__":
    wordle_solver()
