/**
 * VocabularyMonitor class handles the analysis of tokens within user comments.
 * It uses a cultural inclusion filter to distinguish between benign cultural terms
 * and actual obfuscation attempts.
 */
class VocabularyMonitor {
  constructor() {
    this.OUTLIER_THRESHOLD = 0.85;
    this.RISK_THRESHOLD_MULTIPLIER = 2.5;
    // Registry of known benign cultural and liturgical terms to prevent false positives
    this.CULTURAL_INCLUSION_REGISTRY = ["alhamdulillah", "shalom", "namaste", "amen", "mashallah"];
  }

  /**
   * Analyzes risk tokens in a given comment using a cultural inclusion filter.
   * @param {Array<string>} tokens - Array of tokens from the comment.
   * @returns {number} The calculated risk offset.
   */
  analyzeRiskTokens(tokens) {
    let riskOffset = 0;
    
    // Filter out known benign cultural/liturgical terms before risk analysis
    const filteredTokens = tokens.filter(token => 
      !this.CULTURAL_INCLUSION_REGISTRY.includes(token.toLowerCase())
    );

    const unknownTokenRegistry = filteredTokens.filter(token => this.isUnrecognized(token));

    unknownTokenRegistry.forEach(token => {
      const outlierScore = this.calculateOutlierScore(token);
      if (outlierScore > this.OUTLIER_THRESHOLD) {
        riskOffset += (outlierScore * this.RISK_THRESHOLD_MULTIPLIER);
      }
    });

    return riskOffset;
  }

  isUnrecognized(token) {
    return !StandardDictionary.includes(token.toLowerCase());
  }

  calculateOutlierScore(token) {
    return LinguisticCorpus.getRarityIndex(token);
  }
}

// Trace ID: 1780932630.4738762
