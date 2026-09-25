// Browser port of wordle_v2.py: the same filtering, scoring and elimination-word rules,
// so the solver runs entirely client-side with no Python server.

// Parse the newline-separated word list, keeping only 5-letter words
export function parseWords(text) {
  return text
    .split('\n')
    .map(line => line.trim().toLowerCase())
    .filter(line => /^[a-z]{5}$/.test(line));
}

// Score letters based on frequency in the current word pool
export function scoreLetters(wordlist) {
  const counts = {};
  for (const word of wordlist) {
    for (const ch of new Set(word)) counts[ch] = (counts[ch] || 0) + 1; // Set to avoid overcounting duplicate letters
  }
  const total = Object.values(counts).reduce((a, b) => a + b, 0);
  const scores = {};
  for (const ch in counts) scores[ch] = counts[ch] / total;
  return scores;
}

// Score each word based on letter frequency, highest first.
// Letters are summed in sorted order so anagrams tie exactly and keep word-list order.
export function scoreWords(wordlist, letterScores) {
  return wordlist
    .map(word => ({
      word,
      score: [...new Set(word)].sort().reduce((sum, ch) => sum + (letterScores[ch] || 0), 0),
    }))
    .sort((a, b) => b.score - a.score)
    .map(entry => entry.word);
}

const countOf = (word, letter) => word.split(letter).length - 1;

// Filter out invalid words based on feedback ('g' green, 'y' yellow, 'b' gray)
export function applyFeedback(guess, feedback, candidates) {
  // The answer holds at least as many of each letter as the guess marked green or yellow
  const minRequired = {};
  for (let i = 0; i < 5; i++) {
    if (feedback[i] !== 'b') minRequired[guess[i]] = (minRequired[guess[i]] || 0) + 1;
  }

  return candidates.filter(word => {
    for (let i = 0; i < 5; i++) {
      const letter = guess[i];
      const f = feedback[i];
      if (f === 'g') {
        if (word[i] !== letter) return false;
      } else if (f === 'y') {
        if (word[i] === letter || !word.includes(letter)) return false;
      } else {
        // Gray: the letter isn't here, and appears no more often than its green/yellow copies
        if (word[i] === letter) return false;
        if (countOf(word, letter) > (minRequired[letter] || 0)) return false;
      }
    }
    for (const letter in minRequired) {
      if (countOf(word, letter) < minRequired[letter]) return false;
    }
    return true;
  });
}

// With 4 greens and 1 gray, several candidates can differ by a single letter (e.g. _ATCH).
// Find a non-candidate word that tests at least 3 of those letters in one guess.
export function checkEliminationOpportunity(candidates, feedback, fullWordlist) {
  if (candidates.length <= 2) return null;

  const greenCount = [...feedback].filter(f => f === 'g').length;
  const grayCount = [...feedback].filter(f => f === 'b').length;
  if (greenCount !== 4 || grayCount !== 1) return null;

  const varyingPosition = feedback.indexOf('b');
  const differingLetters = [...new Set(candidates.map(word => word[varyingPosition]))];
  if (differingLetters.length < 3) return null;

  const candidateSet = new Set(candidates);
  let bestEliminationWord = null;
  let maxLettersCovered = 0;
  for (const word of fullWordlist) {
    if (candidateSet.has(word)) continue;
    const lettersCovered = differingLetters.filter(letter => word.includes(letter)).length;
    if (lettersCovered > maxLettersCovered && lettersCovered >= 3) {
      maxLettersCovered = lettersCovered;
      bestEliminationWord = word;
    }
  }

  if (!bestEliminationWord) return null;
  return {
    word: bestEliminationWord,
    lettersCovered: maxLettersCovered,
    differingLetters,
    varyingPosition,
  };
}

// Ranked candidates plus the top picks, led by the elimination word when there is one
export function suggest(candidates, lastFeedback, fullWordlist, limit = 5) {
  const ranked = scoreWords(candidates, scoreLetters(candidates));
  const eliminator = lastFeedback ? checkEliminationOpportunity(candidates, lastFeedback, fullWordlist) : null;
  const top = eliminator ? [eliminator.word, ...ranked.filter(w => w !== eliminator.word)] : ranked;
  return { ranked, top: top.slice(0, limit), eliminator };
}
