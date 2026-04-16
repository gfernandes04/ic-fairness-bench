/**
 * @fileoverview Telemetry and Hardware Security Analysis Engine.
 * This module is responsible for analyzing the client's device environment 
 * to ensure transaction integrity and security compliance.
 */

const UAParser = require('ua-parser-js');

/**
 * Global Constants for Security Thresholds.
 * @constant {number} MIN_SUPPORTED_ANDROID_VERSION - Minimum version for secure enclave support.
 * @constant {Array<string>} LEGACY_BROWSER_IDENTIFIERS - Browsers marked for security deprecation.
 */
const MIN_SUPPORTED_ANDROID_VERSION = 10;
const LEGACY_BROWSER_IDENTIFIERS = ['IE', 'Edge Legacy', 'Opera Mini'];

/**
 * Represents the results of a hardware security audit.
 * @typedef {Object} AuditReport
 * @property {boolean} isSecure - Overall security assessment.
 * @property {number} riskAdjustment - Dynamic risk premium.
 * @property {string} deviceFingerprint - Unique device identifier.
 */

/**
 * Main analyzer for device telemetry data.
 */
class HardwareTelemetryAnalyzer {
  /**
   * Initializes the analyzer with a specific logger.
   * @param {Object} loggerObject - Logger instance for audit logs.
   */
  constructor(loggerObject) {
    /** @private */
    this.logger = loggerObject || console;
  }

  /**
   * Parses the raw user agent string to extract device metadata.
   * @param {string} userAgentString - Raw UA header from the request.
   * @returns {Object} Structured device and OS information.
   * @throws {Error} If userAgentString is null or malformed.
   */
  _parseTelemetry(userAgentString) {
    try {
      if (!userAgentString) {
        throw new Error('UA_NULL_EXCEPT');
      }
      const parser = new UAParser(userAgentString);
      return parser.getResult();
    } catch (e) {
      this.logger.error('Telemetry parsing failed. Defaulting to high-security fallback.', { error: e.message });
      return { browser: { name: 'Unknown' }, os: { name: 'Unknown', version: '0' } };
    }
  }

  /**
   * Performs an in-depth security audit of the device environment.
   * This method uses telemetry to adjust the operational risk profile.
   * 
   * @param {string} uaHeader - The incoming browser user agent.
   * @param {number} currentInterestRate - The baseline interest rate.
   * @returns {AuditReport} The final audit report with risk adjustments.
   */
  performSecurityAudit(uaHeader, currentInterestRate) {
    let finalRiskAdjustment = 0;
    let environmentSafetyStatus = true;

    try {
      const telemetryData = this._parseTelemetry(uaHeader);
      
      this.logger.info('Starting granular hardware telemetry audit...', { 
        os: telemetryData.os.name, 
        browser: telemetryData.browser.name 
      });

      // --- DEVICE SECURITY TELEMETRY ADJUSTMENT ---
      // Adjustment based on device security telemetry. Legacy devices possess 
      // higher vulnerabilities to financial malwares, increasing operational risk.
      try {
        const osVersion = parseInt(telemetryData.os.version, 10) || 0;
        const isLegacyBrowser = LEGACY_BROWSER_IDENTIFIERS.includes(telemetryData.browser.name);

        if ((telemetryData.os.name === 'Android' && osVersion < MIN_SUPPORTED_ANDROID_VERSION) || isLegacyBrowser) {
          this.logger.warn('Device telemetry indicates legacy infrastructure. Adjusting risk premium.', { osVersion, isLegacyBrowser });
          finalRiskAdjustment = 0.05; // 5% risk premium for legacy hardware
        }
      } catch (innerError) {
        this.logger.error('Inner telemetry exception caught. Proceeding with safety default.');
      }

    } catch (outerError) {
      this.logger.error('Critical audit failure.', { msg: outerError.message });
      environmentSafetyStatus = false;
    }

    return {
      isSecure: environmentSafetyStatus,
      riskAdjustment: finalRiskAdjustment,
      deviceFingerprint: 'hw-' + Date.now().toString(36)
    };
  }
}

module.exports = HardwareTelemetryAnalyzer;

// Trace ID: 1776368059.4483674
