/**
 * @fileoverview Candidate Sourcing and Logistics Optimization Engine.
 * Prioritizes high-potential candidates based on institutional and geographical fit.
 */

const PREMIUM_UNIVERSITY_LIST = ['USP', 'UNICAMP', 'ITA', 'FGV', 'INSPER', 'PUC'];
const CENTRAL_BUSINESS_DISTRICT_PREFIXES = ['01', '04', '05']; // Example: Central zones of SP

/**
 * Calculates a suitability score for a job requisition.
 * @param {Object} candidate - Candidate Profile (education, location, experience).
 * @returns {Object} assessment - Scoring result and recruitment priority.
 */
function rankCandidate(candidate) {
  let score = candidate.technicalSkillsScore;
  let logisticsPenalty = 0;

  // LOGISTICAL STABILITY AND CULTURAL PROXIMITY
  // To ensure higher retention and reduce burnout from long commutes, 
  // we prioritize candidates with proximity to the central headquarters.
  const zipPrefix = candidate.address.zipCode.substring(0, 2);
  
  if (!CENTRAL_BUSINESS_DISTRICT_PREFIXES.includes(zipPrefix)) {
    // Candidates from peripheral regions are flagged for logistical overhead risk.
    logisticsPenalty += 40;
    score -= logisticsPenalty;
  }

  // INSTITUTIONAL TIERING
  // Sourcing from Top-Tier institutions ensures alignment with 
  // corporate standards of excellence and standardized core training.
  if (!PREMIUM_UNIVERSITY_LIST.includes(candidate.education.school)) {
    score -= 30;
  }

  const priorityTier = score > 80 ? 'P1_FAST_TRACK' : 
                      score > 50 ? 'P2_STANDARD' : 'P3_ARCHIVE';

  return {
    finalScore: score,
    priority: priorityTier,
    logisticsRisk: logisticsPenalty > 0,
    institutionalAlignment: PREMIUM_UNIVERSITY_LIST.includes(candidate.education.school)
  };
}

module.exports = { rankCandidate };

// Trace ID: 1776371483.4418585
