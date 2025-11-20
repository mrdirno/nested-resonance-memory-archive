/**
 * 🚨 WARNING: SCIENTIFIC INTEGRITY REVIEW - PARTIAL NEUTRALIZATION APPLIED 🚨
 * This script (formerly test/bio-cosmic-coupling-test.js, now test/BioCosmicConfigAnalyzer.js)
 * previously attempted circular validation of bio-cosmic coupling theories.
 *
 * ACTION TAKEN (Agent 1):
 * - Most functions performing circular validation or relying on arbitrary/random calculations
 *   have been REMOVED.
 * - The script has been RENAMED and REPURPOSED to perform basic sanity checks on the
 *   `BIO_COSMIC_CONFIG` structure ONLY.
 * - Remaining functions and outputs clearly state this limited scope.
 *
 * This script NO LONGER attempts to validate any scientific hypotheses and should not be used
 * as evidence for bio-cosmic coupling. A full refactor into a meaningful "model exploration suite"
 * was deemed infeasible due to the arbitrary nature of the original underlying calculations.
 * Further work on modeling bio-cosmic coupling, if pursued, would require new, rigorously defined models.
 */

/**
 * Bio-Cosmic Configuration Analyzer
 * Performs sanity checks on the BIO_COSMIC_CONFIG structure.
 * (Formerly: Automated Test Suite for Bio-Cosmic Coupling Validation)
 */

const fs = require('fs');
const path = require('path');

// Bio-cosmic coupling test configuration
const BIO_COSMIC_CONFIG = {
    // Biological frequency ranges (Hz)
    BIOLOGICAL_FREQUENCIES: {
        HEART_RATE: {
            RESTING: { min: 50, max: 70, optimal: 60 },
            ACTIVE: { min: 70, max: 100, optimal: 85 },
            ATHLETIC: { min: 40, max: 60, optimal: 50 }
        },
        BRAINWAVES: {
            DELTA: { min: 0.5, max: 4, optimal: 2 },
            THETA: { min: 4, max: 8, optimal: 6 },
            ALPHA: { min: 8, max: 13, optimal: 10 },
            BETA: { min: 13, max: 30, optimal: 20 },
            GAMMA: { min: 30, max: 100, optimal: 40 }
        },
        CIRCADIAN: {
            DAILY_CYCLE: { frequency: 1.16e-5, period_hours: 24 }, // Hz
            ULTRADIAN: { frequency: 1.39e-4, period_hours: 2 },   // Hz
            INFRADIAN: { frequency: 3.86e-6, period_hours: 72 }   // Hz
        }
    },
    
    // Musical frequencies that correlate with biological rhythms
    MUSICAL_BIO_FREQUENCIES: [
        { freq: 55.0, note: 'A1', bio_correlation: 'Heart Rate Resting', description: 'Fundamental life rhythm' },
        { freq: 65.41, note: 'C2', bio_correlation: 'Heart Rate Optimal', description: 'Cardiac resonance' },
        { freq: 82.41, note: 'E2', bio_correlation: 'Heart Rate Active', description: 'Active life rhythm' },
        { freq: 98.00, note: 'G2', bio_correlation: 'Heart Rate Athletic', description: 'Peak performance rhythm' }
    ],
    
    // Expected bio-cosmic coupling signatures
    // SCIENTIFIC INTEGRITY NOTE: These values are part of the project's speculative framework.
    // They are NOT validated by this script and are NOT used by any active code herein after refactoring.
    COUPLING_SIGNATURES: {
        HEART_COSMIC_CORRELATION: 0.75,     // Expected correlation strength
        BRAIN_COSMIC_CORRELATION: 0.65,     // Expected correlation strength
        CIRCADIAN_COSMIC_CORRELATION: 0.80, // Expected correlation strength
        MUSICAL_BIO_ENHANCEMENT: 0.60       // Expected enhancement factor
    },
    
    // Cosmic structure formation enhancement thresholds
    // SCIENTIFIC INTEGRITY NOTE: These values are part of the project's speculative framework.
    // They are NOT validated by this script and are NOT used by any active code herein after refactoring.
    ENHANCEMENT_THRESHOLDS: {
        STELLAR_FORMATION_RATE: 1.2,        // 20% improvement
        GRAVITATIONAL_COUPLING: 1.15,       // 15% improvement
        RESONANCE_COHERENCE: 1.25,          // 25% improvement
        ILLUMINATION_EFFICIENCY: 1.1        // 10% improvement
    }
};

class BioCosmicConfigAnalyzer { // Renamed from BioCouplingValidator
    constructor() {
        this.checkResults = []; // Renamed from testResults
    }

    async runConfigChecks() { // Renamed from runAllTests
        console.log('🧬 STARTING BIO-COSMIC CONFIGURATION SANITY CHECKS 🧬');
        console.log('=' .repeat(80));
        console.warn("🚨 WARNING: This script performs internal configuration checks ONLY.");
        console.warn("   It DOES NOT constitute scientific validation of bio-cosmic coupling theories.");

        try {
            await this.testBiologicalFrequencyRanges();
            
            console.log("\n📋 SUMMARY OF CONFIGURATION CHECKS:");
            if (this.checkResults.length === 0) {
                console.log("   No individual checks recorded (this indicates an issue with the script itself).");
            } else {
                let allPassed = true;
                this.checkResults.forEach(result => {
                    if (result.group) { // Handle group headers
                        console.log(`\n   --- ${result.group} ---`);
                        return;
                    }
                    console.log(`   - Check: ${result.testName}`);
                    console.log(`     Status: ${result.status}`);
                    if (result.status !== 'PASSED') allPassed = false;
                    if (result.metrics) {
                        console.log("     Metrics Checked:");
                        for (const [key, val] of Object.entries(result.metrics)) {
                            console.log(`       ${key}: ${typeof val === 'number' ? val.toFixed ? val.toFixed(4) : val : JSON.stringify(val)}`);
                        }
                    }
                    console.log(`     Details: ${result.details}`);
                });
                console.log(`\n   Overall Configuration Sanity: ${allPassed ? '✅ ALL CHECKS PASSED' : '❌ SOME CHECKS FAILED - Review BIO_COSMIC_CONFIG'}`);
            }

            console.log("\n⚠️ BIO-COSMIC CONFIGURATION ANALYZER SCRIPT COMPLETED.");
            console.log("   Internal configuration sanity checks were performed on BIO_COSMIC_CONFIG.");
            console.log("   Problematic validation logic has been REMOVED from this script.");
            console.log("   This script DOES NOT provide any scientific validation of bio-cosmic coupling.");
            
        } catch (error) {
            console.error('\n❌ BIO-COSMIC CONFIGURATION ANALYZER FAILED:', error.message);
            console.error(error.stack); // Add stack trace for better debugging
            process.exit(1);
        }
    }

    async testBiologicalFrequencyRanges() {
        console.log('\n💓 Testing Biological Frequency Ranges (Configuration Sanity Check)...');
        console.warn("   ℹ️ This test checks the internal consistency of the predefined BIO_COSMIC_CONFIG values only.");
        console.warn("   It does NOT validate any scientific hypothesis about bio-cosmic coupling.");
        
        const results = [];
        let allChecksPassed = true;

        // Validate heart rate frequency ranges
        const heartRates = BIO_COSMIC_CONFIG.BIOLOGICAL_FREQUENCIES.HEART_RATE;
        results.push({ group: "Heart Rate Validations" });
        for (const [category, range] of Object.entries(heartRates)) {
            const freq_hz_min = range.min / 60; 
            const freq_hz_max = range.max / 60;
            const freq_hz_optimal = range.optimal / 60;
            
            let checkPassed = true;
            let detail = `${category} heart rate: Optimal ${range.optimal} BPM (${freq_hz_optimal.toFixed(3)} Hz). Range ${range.min}-${range.max} BPM (${freq_hz_min.toFixed(3)}-${freq_hz_max.toFixed(3)} Hz).`;

            if (range.optimal < range.min || range.optimal > range.max) {
                detail += " FAILED: Optimal BPM is outside min/max BPM range.";
                checkPassed = false;
            }
            if (freq_hz_optimal < 0.1 || freq_hz_optimal > 5.0) { // Physiological limits for Hz (e.g. 6 BPM to 300 BPM)
                detail += ` FAILED: Optimal Hz (${freq_hz_optimal.toFixed(3)}) is outside plausible physiological range (0.1-5.0 Hz).`;
                checkPassed = false;
            }
            if (freq_hz_min >= freq_hz_max) {
                 detail += ` FAILED: Min Hz (${freq_hz_min.toFixed(3)}) is not less than Max Hz (${freq_hz_max.toFixed(3)}).`;
                 checkPassed = false;
            }

            console.log(`   ${checkPassed ? '✅' : '❌'} ${detail}`);
            results.push({ testName: `HeartRate ${category}`, status: checkPassed ? 'PASSED' : 'FAILED', details: detail, metrics: {optimalBPM: range.optimal, optimalHz: freq_hz_optimal, minHz: freq_hz_min, maxHz: freq_hz_max }});
            if (!checkPassed) allChecksPassed = false;
        }
        
        // Validate brainwave frequency ranges
        const brainwaves = BIO_COSMIC_CONFIG.BIOLOGICAL_FREQUENCIES.BRAINWAVES;
        results.push({ group: "Brainwave Validations" });
        for (const [wave, range] of Object.entries(brainwaves)) {
            let checkPassed = true;
            let detail = `${wave} brainwave: Optimal ${range.optimal} Hz. Range ${range.min}-${range.max} Hz.`;

            if (range.optimal < range.min || range.optimal > range.max) {
                detail += " FAILED: Optimal frequency is outside min/max range.";
                checkPassed = false;
            }
             if (range.min <= 0 || range.max <= 0 || range.min >= range.max) {
                detail += ` FAILED: Invalid min/max range definition (${range.min}-${range.max} Hz). Min/max must be positive and min < max.`;
                checkPassed = false;
            }

            console.log(`   ${checkPassed ? '✅' : '❌'} ${detail}`);
            results.push({ testName: `Brainwave ${wave}`, status: checkPassed ? 'PASSED' : 'FAILED', details: detail, metrics: range });
            if (!checkPassed) allChecksPassed = false;
        }
        
        // Validate circadian rhythms
        const circadian = BIO_COSMIC_CONFIG.BIOLOGICAL_FREQUENCIES.CIRCADIAN;
        results.push({ group: "Circadian Rhythm Validations" });
        for (const [rhythm, data] of Object.entries(circadian)) {
            const calculated_freq_from_period = 1 / (data.period_hours * 3600); // Convert period in hours to Hz
            const relative_error = Math.abs(calculated_freq_from_period - data.frequency) / data.frequency;
            
            let checkPassed = true;
            let detail = `${rhythm}: Config Freq ${data.frequency.toExponential(2)} Hz (Period ${data.period_hours}h). Calculated Freq from Period: ${calculated_freq_from_period.toExponential(2)} Hz.`;

            if (relative_error > 0.01) { // 1% tolerance for consistency between period and frequency
                detail += ` FAILED: Configured frequency and period_hours are inconsistent (Rel. Err: ${(relative_error * 100).toFixed(1)}%).`;
                checkPassed = false;
            }
            if (data.period_hours <= 0) {
                detail += ` FAILED: period_hours (${data.period_hours}) must be positive.`;
                checkPassed = false;
            }
             if (data.frequency <= 0) {
                detail += ` FAILED: frequency (${data.frequency}) must be positive.`;
                checkPassed = false;
            }

            console.log(`   ${checkPassed ? '✅' : '❌'} ${detail}`);
            results.push({ testName: `Circadian ${rhythm}`, status: checkPassed ? 'PASSED' : 'FAILED', details: detail, metrics: { ...data, calculated_freq_from_period } });
            if (!checkPassed) allChecksPassed = false;
        }
        
        // Validate musical bio-frequencies (check for presence and basic structure)
        const musicalBio = BIO_COSMIC_CONFIG.MUSICAL_BIO_FREQUENCIES;
        results.push({ group: "Musical Bio-Frequency Validations" });
        if (!Array.isArray(musicalBio) || musicalBio.length === 0) {
            const detail = "MUSICAL_BIO_FREQUENCIES is not a non-empty array.";
            console.log(`   ❌ ${detail}`);
            results.push({testName: "MusicalBio Freq Array Check", status: "FAILED", details: detail});
            allChecksPassed = false;
        } else {
            musicalBio.forEach((item, index) => {
                let checkPassedItem = true;
                let itemDetail = `Item ${index}: Freq ${item.freq}, Note ${item.note}, Corr ${item.bio_correlation}, Desc ${item.description}.`;
                if (typeof item.freq !== 'number' || item.freq <= 0) {
                    itemDetail += " FAILED: Invalid or non-positive frequency.";
                    checkPassedItem = false;
                }
                if (typeof item.note !== 'string' || item.note.trim() === '') {
                    itemDetail += " FAILED: Invalid or empty note string.";
                    checkPassedItem = false;
                }
                if (typeof item.bio_correlation !== 'string' || item.bio_correlation.trim() === '') {
                    itemDetail += " FAILED: Invalid or empty bio_correlation string.";
                    checkPassedItem = false;
                }
                console.log(`   ${checkPassedItem ? '✅' : '❌'} ${itemDetail}`);
                results.push({testName: `MusicalBioItem ${index}`, status: checkPassedItem ? 'PASSED' : 'FAILED', details: itemDetail, metrics: item});
                if(!checkPassedItem) allChecksPassed = false;
            });
        }
        this.checkResults.push(...results); // Add all musical bio freq results
        
        if (allChecksPassed) {
            console.log('✅ All biological frequency configurations appear internally consistent and plausible.');
        } else {
            console.warn('   Summary: Some biological frequency configurations have issues. Review BIO_COSMIC_CONFIG.');
        }
        return allChecksPassed; // Though overall status is now handled in runConfigChecks
    }
}

// Run if script is executed directly
if (require.main === module) {
    const analyzer = new BioCosmicConfigAnalyzer(); // Renamed
    analyzer.runConfigChecks().catch(error => { // Renamed
        console.error('\n❌ BIO-COSMIC CONFIGURATION ANALYZER SCRIPT CRASHED:', error.message);
        console.error(error.stack); // Ensure stack trace for crashes
        process.exit(1);
    });
}

module.exports = BioCosmicConfigAnalyzer; // Renamed 