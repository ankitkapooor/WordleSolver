import { parseWords, applyFeedback, suggest } from './solver.js';

const SHOW_ALL_LIMIT = 500;
const NEXT_COLOR = { b: 'y', y: 'g', g: 'b' };
const COLOR_NAME = { b: 'gray', y: 'yellow', g: 'green' };
const COLOR_RANK = { b: 1, y: 2, g: 3 };
const KEY_ROWS = ['qwertyuiop', 'asdfghjkl', '+zxcvbnm-']; // + Enter, - Backspace
const STORAGE_KEY = 'wordle-solver:v1';

const $ = id => document.getElementById(id);
const els = {
  board: $('board'),
  status: $('status'),
  undo: $('undo'),
  reset: $('reset'),
  submit: $('submit'),
  suggestionsTitle: $('suggestions-title'),
  count: $('count'),
  suggestions: $('suggestions'),
  allWords: $('all-words'),
  allWordsSummary: $('all-words-summary'),
  wordGrid: $('word-grid'),
  keyboard: $('keyboard'),
};

const state = {
  words: null, // full word list, once loaded
  history: [], // { guess, feedback, candidates } — candidates left after that guess
  letters: [], // active row
  colors: [], // active row feedback, one of b / y / g per letter
  message: '',
  loadFailed: false,
  animate: null, // one-shot animation for the next render: 'pop' | 'reveal' | 'shake'
};

const candidates = () => state.history.at(-1)?.candidates ?? state.words ?? [];
const lastFeedback = () => state.history.at(-1)?.feedback ?? null;
const isSolved = () => lastFeedback() === 'ggggg';

// Letters already confirmed green at each position, so retyping them starts green
function knownGreens() {
  const greens = Array(5).fill(null);
  for (const { guess, feedback } of state.history) {
    for (let i = 0; i < 5; i++) if (feedback[i] === 'g') greens[i] = guess[i];
  }
  return greens;
}

function startingColor(letter, position) {
  return knownGreens()[position] === letter ? 'g' : 'b';
}

/* ---------- Actions ---------- */

function typeLetter(letter) {
  if (!state.words || isSolved() || state.letters.length === 5) return;
  state.colors.push(startingColor(letter, state.letters.length));
  state.letters.push(letter);
  state.message = '';
  state.animate = 'pop';
  render();
}

function backspace() {
  if (!state.letters.length) return;
  state.letters.pop();
  state.colors.pop();
  state.message = '';
  render();
}

function fillWord(word) {
  if (isSolved()) return;
  state.letters = [...word];
  state.colors = state.letters.map(startingColor);
  state.message = '';
  render();
}

function cycleColor(position) {
  if (position >= state.letters.length) return;
  state.colors[position] = NEXT_COLOR[state.colors[position]];
  render();
}

function submitGuess() {
  if (!state.words || isSolved()) return;
  if (state.letters.length < 5) {
    state.message = 'Enter all 5 letters first.';
    state.animate = 'shake';
    render();
    return;
  }
  const guess = state.letters.join('');
  const feedback = state.colors.join('');
  state.history.push({ guess, feedback, candidates: applyFeedback(guess, feedback, candidates()) });
  state.letters = [];
  state.colors = [];
  state.message = '';
  state.animate = 'reveal';
  save();
  render();
}

// Put the last guess back in the active row so its colors can be fixed
function undo() {
  const last = state.history.pop();
  if (!last) return;
  state.letters = [...last.guess];
  state.colors = [...last.feedback];
  state.message = '';
  save();
  render();
}

function reset() {
  state.history = [];
  state.letters = [];
  state.colors = [];
  state.message = '';
  save();
  render();
}

/* ---------- Persistence (today's game survives a reload) ---------- */

const today = () => new Date().toLocaleDateString('en-CA');

function save() {
  try {
    const guesses = state.history.map(({ guess, feedback }) => [guess, feedback]);
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ day: today(), guesses }));
  } catch {
    // Storage unavailable (private mode, blocked); the game still works without it
  }
}

function restore() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if (saved?.day !== today() || !Array.isArray(saved.guesses)) return;
    for (const [guess, feedback] of saved.guesses) {
      if (!/^[a-z]{5}$/.test(guess) || !/^[byg]{5}$/.test(feedback)) return;
      state.history.push({ guess, feedback, candidates: applyFeedback(guess, feedback, candidates()) });
    }
  } catch {
    state.history = [];
  }
}

/* ---------- Rendering ---------- */

function el(tag, { dataset = {}, ...props } = {}, children = []) {
  const node = Object.assign(document.createElement(tag), props);
  Object.assign(node.dataset, dataset);
  node.append(...children);
  return node;
}

function lockedRow({ guess, feedback }, index, reveal) {
  const label = [...guess].map((l, i) => `${l.toUpperCase()} ${COLOR_NAME[feedback[i]]}`).join(', ');
  const row = el('div', { className: 'row', role: 'group', ariaLabel: `Guess ${index + 1}: ${label}` });
  [...guess].forEach((letter, i) => {
    const tile = el('div', { className: 'tile', ariaHidden: 'true', dataset: { color: feedback[i] } }, [letter]);
    if (reveal) {
      tile.classList.add('reveal');
      tile.style.setProperty('--i', i);
    }
    row.append(tile);
  });
  return row;
}

function activeRow() {
  const row = el('div', { className: 'row active', role: 'group', ariaLabel: 'Current guess' });
  if (state.animate === 'shake') row.classList.add('shake');
  for (let i = 0; i < 5; i++) {
    const letter = state.letters[i];
    if (!letter) {
      const next = i === state.letters.length ? ' next' : '';
      row.append(el('div', { className: `tile empty${next}`, ariaHidden: 'true' }));
      continue;
    }
    const color = state.colors[i];
    const tile = el(
      'button',
      {
        type: 'button',
        className: 'tile',
        ariaLabel: `Letter ${i + 1}, ${letter.toUpperCase()}, ${COLOR_NAME[color]}. Change color`,
        onclick: () => cycleColor(i),
        dataset: { color, focus: `tile-${i}` },
      },
      [letter],
    );
    if (state.animate === 'pop' && i === state.letters.length - 1) tile.classList.add('pop');
    row.append(tile);
  }
  return row;
}

function renderBoard() {
  const focused = document.activeElement?.dataset?.focus;
  const rows = state.history.map((entry, i) =>
    lockedRow(entry, i, state.animate === 'reveal' && i === state.history.length - 1),
  );
  if (!isSolved()) rows.push(activeRow());
  els.board.replaceChildren(...rows);
  if (focused) els.board.querySelector(`[data-focus="${focused}"]`)?.focus();
}

function statusText() {
  if (state.message) return state.message;
  if (state.loadFailed) return "Couldn't load the word list. Refresh to try again.";
  if (!state.words) return 'Loading…';
  if (isSolved()) {
    const n = state.history.length;
    return `Solved in ${n} ${n === 1 ? 'guess' : 'guesses'}!`;
  }
  if (state.letters.length === 5) return 'Tap tiles to match your colors, then press Enter.';
  if (state.letters.length) return 'Keep typing. Tap a tile to change its color.';
  return state.history.length ? 'Type your next guess.' : 'Type the first word you played.';
}

function wordButton(word, className) {
  return el('button', { type: 'button', className, onclick: () => fillWord(word) }, [word]);
}

// Suggestions only change when the candidate pool does, so they're rebuilt lazily
let suggestionsFor = null;

function renderSuggestions() {
  const pool = candidates();
  const key = state.words ? pool : null;
  if (key === suggestionsFor && suggestionsFor !== null) return;
  suggestionsFor = key;

  els.allWords.hidden = true;
  if (!state.words) {
    if (state.loadFailed) els.suggestions.replaceChildren(el('p', { className: 'note warn' }, ['Word list unavailable.']));
    return;
  }

  const n = pool.length;
  els.suggestionsTitle.textContent = isSolved() ? 'Solved' : 'Best next guesses';
  els.count.textContent = isSolved() ? '' : `${n.toLocaleString()} possible ${n === 1 ? 'answer' : 'answers'}`;

  if (isSolved()) {
    const answer = state.history.at(-1).guess;
    els.suggestions.replaceChildren(
      el('p', { className: 'note' }, ['The answer was ', el('b', {}, [answer.toUpperCase()]), '. Start a new game any time.']),
    );
    return;
  }

  if (!n) {
    els.suggestions.replaceChildren(
      el('p', { className: 'note warn' }, [
        'No words match these colors. Double-check the tiles, or undo the last guess to fix them.',
      ]),
    );
    return;
  }

  const { ranked, top, eliminator } = suggest(pool, lastFeedback(), state.words);
  const chips = el('ol', { className: 'chips' });
  top.forEach((word, i) => {
    const chip = wordButton(word, i === 0 ? 'chip best' : 'chip');
    if (eliminator?.word === word) {
      chip.classList.add('eliminator');
      chip.append(el('span', { className: 'badge' }, ['tester']));
    }
    chips.append(el('li', {}, [chip]));
  });
  const content = [chips];

  if (eliminator) {
    const tested = eliminator.differingLetters.filter(l => eliminator.word.includes(l)).map(l => l.toUpperCase());
    content.push(
      el('p', { className: 'note' }, [
        el('b', {}, [eliminator.word.toUpperCase()]),
        ` can't be the answer, but it checks ${formatList(tested)} in one go, which narrows down the ${n} words that differ by a single letter.`,
      ]),
    );
  } else if (n === 1) {
    content.push(el('p', { className: 'note' }, ["That's the only word left."]));
  }
  els.suggestions.replaceChildren(...content);

  if (n > top.length && n <= SHOW_ALL_LIMIT) {
    els.allWordsSummary.textContent = `Show all ${n} possible answers`;
    els.wordGrid.replaceChildren(...ranked.map(word => wordButton(word, 'word')));
    els.allWords.hidden = false;
  }
}

function formatList(items) {
  return items.length < 2 ? items.join('') : `${items.slice(0, -1).join(', ')} and ${items.at(-1)}`;
}

function buildKeyboard() {
  for (const keys of KEY_ROWS) {
    const row = el('div', { className: 'key-row' });
    for (const key of keys) {
      if (key === '+') {
        row.append(el('button', { type: 'button', className: 'key wide', onclick: submitGuess }, ['Enter']));
      } else if (key === '-') {
        row.append(el('button', { type: 'button', className: 'key wide', ariaLabel: 'Backspace', onclick: backspace }, ['⌫']));
      } else {
        row.append(el('button', { type: 'button', className: 'key', onclick: () => typeLetter(key), dataset: { key } }, [key]));
      }
    }
    els.keyboard.append(row);
  }
}

function renderKeyboard() {
  const best = {};
  for (const { guess, feedback } of state.history) {
    for (let i = 0; i < 5; i++) {
      const letter = guess[i];
      if (!best[letter] || COLOR_RANK[feedback[i]] > COLOR_RANK[best[letter]]) best[letter] = feedback[i];
    }
  }
  for (const key of els.keyboard.querySelectorAll('[data-key]')) {
    const color = best[key.dataset.key];
    if (color) key.dataset.color = color;
    else delete key.dataset.color;
  }
}

function render() {
  renderBoard();
  renderSuggestions();
  renderKeyboard();
  const status = statusText();
  if (els.status.textContent !== status) els.status.textContent = status;
  els.submit.disabled = !state.words || isSolved() || state.letters.length < 5;
  els.undo.disabled = !state.history.length;
  els.reset.disabled = !state.history.length && !state.letters.length;
  state.animate = null;
}

/* ---------- Input ---------- */

document.addEventListener('keydown', event => {
  if (event.metaKey || event.ctrlKey || event.altKey || event.isComposing) return;
  const { key } = event;
  if (key === 'Enter') {
    if (event.target.closest?.('button, summary, a')) return; // let focused controls handle Enter
    event.preventDefault();
    submitGuess();
  } else if (key === 'Backspace') {
    event.preventDefault();
    backspace();
  } else if (/^[a-z]$/i.test(key)) {
    typeLetter(key.toLowerCase());
  } else if (/^[1-5]$/.test(key)) {
    cycleColor(Number(key) - 1);
  }
});

// Clicking a button shouldn't keep focus on it, or the next Enter would press it again
document.addEventListener('mousedown', event => {
  if (event.target.closest('button')) event.preventDefault();
});

els.submit.addEventListener('click', submitGuess);
els.undo.addEventListener('click', undo);
els.reset.addEventListener('click', reset);

buildKeyboard();
render();

try {
  const response = await fetch('/words.txt');
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  state.words = parseWords(await response.text());
  restore();
} catch {
  state.loadFailed = true;
}
render();
