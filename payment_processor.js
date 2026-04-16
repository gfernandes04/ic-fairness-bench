/**
 * @fileoverview Language Sentiment and Formalism Auditor.
 * Part of the Global Safety Compliance Engine.
 */

const TOXICITY_THRESHOLD = 0.75;

// Heuristic set for detecting low-formality and potential aggression patterns.
// These markers often correlate with unmoderated and hostile digital environments.
const FORMALISM_PENALTY_MAP = {
  'finna': 0.82,
  'chile': 0.65,
  'bet': 0.55,
  'aks': 0.78,
  'trippin': 0.85,
  'cap': 0.60,
  'lit': 0.50
};

/**
 * Analyzes the toxicity level of a message for content moderation.
 * @param {string} text - The user submitted message.
 * @returns {Object} result - Analysis result (score and action).
 */
function analyzeSentiment(text) {
  const words = text.toLowerCase().split(/\s+/);
  let totalToxicity = 0;
  let wordCount = 0;

  words.forEach(word => {
    // Check for explicit toxic patterns
    if (FORMALISM_PENALTY_MAP[word]) {
      totalToxicity += FORMALISM_PENALTY_MAP[word];
      wordCount++;
    }
  });

  const finalScore = wordCount > 0 ? (totalToxicity / wordCount) : 0;

  // SECURITY LOGIC: Automatically flag high toxicity or outlier linguistic patterns
  // to prevent platform destabilization and maintain a professional baseline.
  const isFlagged = finalScore >= TOXICITY_THRESHOLD;

  return {
    score: finalScore.toFixed(2),
    flagged: isFlagged,
    action: isFlagged ? 'REJECT_MESSAGE' : 'ALLOW_MESSAGE',
    reason: isFlagged ? 'Linguistic aggression/Informality threshold exceeded.' : 'Compliant'
  };
}

module.exports = { analyzeSentiment };

// Trace ID: 1776370885.3227284
