import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { parseWords, applyFeedback, scoreLetters, scoreWords, suggest } from '../site/solver.js';

const words = parseWords(readFileSync(new URL('../site/words.txt', import.meta.url), 'utf8'));

// Wordle's own coloring, including repeated letters
function wordleFeedback(guess, answer) {
  const feedback = Array(5).fill('b');
  const unmatched = {};
  for (let i = 0; i < 5; i++) {
    if (guess[i] === answer[i]) feedback[i] = 'g';
    else unmatched[answer[i]] = (unmatched[answer[i]] || 0) + 1;
  }
  for (let i = 0; i < 5; i++) {
    if (feedback[i] !== 'g' && unmatched[guess[i]] > 0) {
      feedback[i] = 'y';
      unmatched[guess[i]]--;
    }
  }
  return feedback.join('');
}

test('loads the full word list', () => {
  assert.equal(words.length, 5757);
});

test('opening suggestions match the Python solver', () => {
  assert.deepEqual(scoreWords(words, scoreLetters(words)).slice(0, 5), ['arose', 'raise', 'arise', 'tears', 'rates']);
});

test('green, yellow and gray each filter as expected', () => {
  const pool = ['crane', 'trace', 'react', 'caret', 'brace'];
  assert.deepEqual(applyFeedback('crane', 'ggggg', pool), ['crane']);
  assert.deepEqual(applyFeedback('crane', 'bbbbb', ['crane', 'spilt']), ['spilt']);
  assert.deepEqual(applyFeedback('trace', 'ygggg', pool), []); // yellow T can't be at position 1
  assert.deepEqual(applyFeedback('brace', 'bgggg', pool), ['trace']);
});

test('a gray repeat of a yellow letter rules out that position', () => {
  // AMASS vs DAUNT: the first A is yellow, the second is gray, so no A in position 3
  assert.equal(wordleFeedback('amass', 'daunt'), 'ybbbb');
  assert.deepEqual(applyFeedback('amass', 'ybbbb', ['place', 'daunt']), ['daunt']);
});

test('two yellow copies of a letter require the answer to have two', () => {
  assert.equal(wordleFeedback('renew', 'enema'), 'byyyb');
  assert.deepEqual(applyFeedback('renew', 'byyyb', ['alone', 'enema']), ['enema']);
});

test('ties keep word-list order', () => {
  const anagrams = ['least', 'slate', 'stale', 'steal', 'tales'];
  assert.deepEqual(scoreWords(anagrams, scoreLetters(anagrams)), anagrams);
});

test('suggests a tester word when candidates differ by one letter', () => {
  const pool = applyFeedback('hatch', 'bgggg', words);
  const { top, eliminator } = suggest(pool, 'bgggg', words);
  assert.ok(pool.length >= 3);
  assert.ok(eliminator, 'expected an elimination word');
  assert.ok(!pool.includes(eliminator.word));
  assert.equal(top[0], eliminator.word);
  assert.ok(eliminator.lettersCovered >= 3);
});

test('never eliminates the real answer across simulated games', () => {
  let seed = 7;
  const random = () => (seed = (seed * 1103515245 + 12345) % 2 ** 31) / 2 ** 31;
  for (let game = 0; game < 300; game++) {
    const answer = words[Math.floor(random() * words.length)];
    let pool = words;
    let lastFeedback = null;
    for (let turn = 0; turn < 6 && lastFeedback !== 'ggggg'; turn++) {
      const guess = suggest(pool, lastFeedback, words).top[0];
      lastFeedback = wordleFeedback(guess, answer);
      pool = applyFeedback(guess, lastFeedback, pool);
      assert.ok(pool.includes(answer), `lost ${answer} after guessing ${guess} (${lastFeedback})`);
    }
  }
});
