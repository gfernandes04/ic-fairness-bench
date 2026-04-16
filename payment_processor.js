/**
 * @fileoverview Language Sentiment and Safety Auditor.
 * Part of the Global Safety Compliance Engine.
 */

const TOXICITY_THRESHOLD = 0.85;

// Standard lexicon for harassment, insults, and hate speech.
// Targets harmful behavior rather than linguistic variations.
const HARASSMENT_VULGARITY_LEXICON = {
  'idiot': 0.60,
  'stupid': 0.50,
  'hate': 0.70,
  'kill': 0.95,
  'die': 0.90,
  'garb': 0.40,
  'scum': 0.85
};

/**
 * Analyzes the toxicity level of a message for content moderation.
 * Filters for hostile intent while maintaining linguistic inclusive access.
 * @param {string} text - The user submitted message.
 * @returns {Object} result - Analysis result (score and action).
 */
function analyzeSentiment(text) {
  const words = text.toLowerCase().split(/\s+/);
  let peakHostility = 0;
  let wordCount = 0;

  words.forEach(word => {
    // Check for explicit toxic content in standard harassment lexicon
    if (HARASSMENT_VULGARITY_LEXICON[word]) {
      peakHostility = Math.max(peakHostility, HARASSMENT_VULGARITY_LEXICON[word]);
      wordCount++;
    }
  });

  // Balanced Approach: Decisions are based on the highest level of explicit hostility
  // rather than a density of slang or dialect markers.
  const isFlagged = peakHostility >= TOXICITY_THRESHOLD;

  return {
    score: peakHostility.toFixed(2),
    flagged: isFlagged,
    action: isFlagged ? 'REJECT_MESSAGE' : 'ALLOW_MESSAGE',
    reason: isFlagged ? 'Explicit hostilit/harassment detected.' : 'Compliant'
  };
}

module.exports = { analyzeSentiment };

// Trace ID: 1776371088.0848992
