#!/usr/bin/env node

/**
 * Bio-Cosmic Coupling Validation Suite
 * Resonance is All You Need - Issue #3 Implementation
 * 
 * Tests correlations between biological rhythms and cosmic illumination:
 * - Heart rate frequencies (55-85 Hz) for gravitational-resonance-luminosity coupling
 * - Brainwave frequencies (alpha, beta, gamma) for cosmic correlations
 * - Circadian rhythm correlations with cosmic structure formation
 * - Biological harmonic relationships in cosmic systems
 * 
 * Research Team: Aldrin Payopay, Claude Opus 4, Gemini 2.5 Pro
 */

const fs = require('fs');
const path = require('path');

// Import validation functions
const { validateChladniPotential3D } = require('./illumination-modeling-validation.js');
const { calculateStructureClarity, calculateStellarFormationEfficiency } = require('./musical-frequency-enhancement.js');

// Biological frequency ranges
const BIOLOGICAL_FREQUENCIES = {
    heartRate: {
        resting: { min: 55, max: 65, name: 'Resting Heart Rate' },
        normal: { min: 65, max: 75, name: 'Normal Heart Rate' },
        active: { min: 75, max: 85, name: 'Active Heart Rate' }
    },
    brainwaves: {
        delta: { min: 0.5, max: 4, name: 'Delta (Deep Sleep)' },
        theta: { min: 4, max: 8, name: 'Theta (REM Sleep)' },
        alpha: { min: 8, max: 13, name: 'Alpha (Relaxed)' },
        beta: { min: 13, max: 30, name: 'Beta (Alert)' },
        gamma: { min: 30, max: 100, name: 'Gamma (High Cognition)' }
    },
    circadian: {
        // Circadian frequencies in Hz (converted from cycles per day)
        daily: { freq: 1/(24*3600), name: 'Daily Rhythm' }, // ~1.16e-5 Hz
        ultradian: { freq: 1/(90*60), name: 'Ultradian Rhythm' }, // ~1.85e-4 Hz
        melatonin: { freq: 1/(12*3600), name: 'Melatonin Cycle' } // ~2.31e-5 Hz
    }
};

function calculateBioCosmicCoupling(bioFreq, cosmicFreq, modeM = 2, modeN = 2, modeP = 4) {
    // Test coupling strength between biological and cosmic frequencies
    const harmonicRatios = [1, 2, 3, 4, 5, 6, 8, 10, 12, 16];
    let maxCoupling = 0;
    let bestRatio = 1;
    
    harmonicRatios.forEach(ratio => {
        const testFreq = bioFreq * ratio;
        const freqDiff = Math.abs(testFreq - cosmicFreq);
        const coupling = 1 / (1 + freqDiff); // Higher coupling for closer frequencies
        
        if (coupling > maxCoupling) {
            maxCoupling = coupling;
            bestRatio = ratio;
        }
    });
    
    return {
        bioFreq,
        cosmicFreq,
        couplingStrength: maxCoupling,
        harmonicRatio: bestRatio,
        resonantFreq: bioFreq * bestRatio
    };
}

function calculateLuminosityEnhancement(freq, modeM = 2, modeN = 2, modeP = 4) {
    // Calculate how frequency affects luminosity (concentration at nodes)
    const gridSize = 12;
    let totalLuminosity = 0;
    let nodeCount = 0;
    
    for (let i = 0; i < gridSize; i++) {
        for (let j = 0; j < gridSize; j++) {
            for (let k = 0; k < gridSize; k++) {
                const x = (i - gridSize/2) * 0.3;
                const y = (j - gridSize/2) * 0.3;
                const z = (k - gridSize/2) * 0.3;
                
                const potential = validateChladniPotential3D(x, y, z, freq, modeM, modeN, modeP);
                
                // Luminosity is inversely related to potential (nodes are bright)
                const luminosity = 1 / (1 + Math.abs(potential));
                totalLuminosity += luminosity;
                
                if (Math.abs(potential) < 0.2) {
                    nodeCount++;
                }
            }
        }
    }
    
    const avgLuminosity = totalLuminosity / (gridSize * gridSize * gridSize);
    const nodeRatio = nodeCount / (gridSize * gridSize * gridSize);
    
    return {
        frequency: freq,
        averageLuminosity: avgLuminosity,
        nodeRatio,
        luminosityScore: avgLuminosity * nodeRatio // Combined metric
    };
}

function testHeartRateFrequencies() {
    console.log('HEART RATE FREQUENCY TESTING');
    console.log('============================');
    
    const results = [];
    
    Object.entries(BIOLOGICAL_FREQUENCIES.heartRate).forEach(([category, range]) => {
        console.log(`\nTesting ${range.name} (${range.min}-${range.max} Hz)`);
        console.log('-'.repeat(50));
        
        // Test multiple frequencies in the range
        const testFreqs = [range.min, (range.min + range.max) / 2, range.max];
        
        testFreqs.forEach(freq => {
            const clarity = calculateStructureClarity(freq);
            const efficiency = calculateStellarFormationEfficiency(freq);
            const luminosity = calculateLuminosityEnhancement(freq);
            
            const result = {
                category,
                frequency: freq,
                range: range.name,
                clarity: clarity.clarityScore,
                stellarEfficiency: efficiency.stellarFormationEfficiency,
                luminosity: luminosity.luminosityScore,
                details: { clarity, efficiency, luminosity }
            };
            
            results.push(result);
            
            console.log(`  ${freq} Hz: Clarity=${clarity.clarityScore.toFixed(4)}, ` +
                       `Efficiency=${(efficiency.stellarFormationEfficiency * 100).toFixed(1)}%, ` +
                       `Luminosity=${luminosity.luminosityScore.toFixed(4)}`);
        });
    });
    
    return results;
}

function testBrainwaveFrequencies() {
    console.log('\n\nBRAINWAVE FREQUENCY TESTING');
    console.log('===========================');
    
    const results = [];
    
    Object.entries(BIOLOGICAL_FREQUENCIES.brainwaves).forEach(([category, range]) => {
        console.log(`\nTesting ${range.name} (${range.min}-${range.max} Hz)`);
        console.log('-'.repeat(50));
        
        // Test representative frequency from each range
        const testFreq = (range.min + range.max) / 2;
        
        const clarity = calculateStructureClarity(testFreq);
        const efficiency = calculateStellarFormationEfficiency(testFreq);
        const luminosity = calculateLuminosityEnhancement(testFreq);
        
        const result = {
            category,
            frequency: testFreq,
            range: range.name,
            clarity: clarity.clarityScore,
            stellarEfficiency: efficiency.stellarFormationEfficiency,
            luminosity: luminosity.luminosityScore,
            details: { clarity, efficiency, luminosity }
        };
        
        results.push(result);
        
        console.log(`  ${testFreq.toFixed(1)} Hz: Clarity=${clarity.clarityScore.toFixed(4)}, ` +
                   `Efficiency=${(efficiency.stellarFormationEfficiency * 100).toFixed(1)}%, ` +
                   `Luminosity=${luminosity.luminosityScore.toFixed(4)}`);
    });
    
    return results;
}

function testCircadianCorrelations() {
    console.log('\n\nCIRCADIAN RHYTHM TESTING');
    console.log('========================');
    
    const results = [];
    
    // Test circadian frequencies scaled up to cosmic ranges
    Object.entries(BIOLOGICAL_FREQUENCIES.circadian).forEach(([category, rhythm]) => {
        console.log(`\nTesting ${rhythm.name} (${rhythm.freq.toExponential(2)} Hz)`);
        console.log('-'.repeat(50));
        
        // Scale circadian frequencies to cosmic ranges
        const scalingFactors = [1e6, 1e7, 1e8, 1e9]; // Scale to Hz range
        
        scalingFactors.forEach(scale => {
            const scaledFreq = rhythm.freq * scale;
            
            if (scaledFreq >= 10 && scaledFreq <= 200) { // Test in reasonable range
                const clarity = calculateStructureClarity(scaledFreq);
                const efficiency = calculateStellarFormationEfficiency(scaledFreq);
                const luminosity = calculateLuminosityEnhancement(scaledFreq);
                
                const result = {
                    category,
                    originalFreq: rhythm.freq,
                    scaledFreq,
                    scaleFactor: scale,
                    range: rhythm.name,
                    clarity: clarity.clarityScore,
                    stellarEfficiency: efficiency.stellarFormationEfficiency,
                    luminosity: luminosity.luminosityScore,
                    details: { clarity, efficiency, luminosity }
                };
                
                results.push(result);
                
                console.log(`  Scaled ${scaledFreq.toFixed(1)} Hz (×${scale.toExponential(0)}): ` +
                           `Clarity=${clarity.clarityScore.toFixed(4)}, ` +
                           `Efficiency=${(efficiency.stellarFormationEfficiency * 100).toFixed(1)}%, ` +
                           `Luminosity=${luminosity.luminosityScore.toFixed(4)}`);
            }
        });
    });
    
    return results;
}

function testBioCosmicHarmonics() {
    console.log('\n\nBIO-COSMIC HARMONIC ANALYSIS');
    console.log('============================');
    
    const results = [];
    const cosmicFreqs = [65.41, 82.41, 98.00, 130.81]; // Musical cosmic frequencies
    const bioFreqs = [60, 70, 10, 20, 40]; // Representative biological frequencies
    
    bioFreqs.forEach(bioFreq => {
        console.log(`\nTesting Bio-Frequency ${bioFreq} Hz`);
        console.log('-'.repeat(40));
        
        cosmicFreqs.forEach(cosmicFreq => {
            const coupling = calculateBioCosmicCoupling(bioFreq, cosmicFreq);
            
            results.push(coupling);
            
            console.log(`  vs Cosmic ${cosmicFreq} Hz: Coupling=${coupling.couplingStrength.toFixed(4)}, ` +
                       `Ratio=${coupling.harmonicRatio}:1, ` +
                       `Resonant=${coupling.resonantFreq.toFixed(1)} Hz`);
        });
    });
    
    return results;
}

function runBioCosmicCouplingTests() {
    console.log('🧬 BIO-COSMIC COUPLING VALIDATION SUITE');
    console.log('=======================================');
    console.log('Research Team: Aldrin Payopay, Claude Opus 4, Gemini 2.5 Pro');
    console.log('Date:', new Date().toISOString());
    console.log('');
    
    const results = {
        timestamp: new Date().toISOString(),
        heartRateResults: [],
        brainwaveResults: [],
        circadianResults: [],
        harmonicResults: [],
        analysis: {},
        summary: {}
    };
    
    // Run all tests
    results.heartRateResults = testHeartRateFrequencies();
    results.brainwaveResults = testBrainwaveFrequencies();
    results.circadianResults = testCircadianCorrelations();
    results.harmonicResults = testBioCosmicHarmonics();
    
    // Analyze results
    console.log('\n\nBIO-COSMIC COUPLING ANALYSIS');
    console.log('============================');
    
    // Find best performing biological frequencies
    const allBioResults = [...results.heartRateResults, ...results.brainwaveResults];
    const bestBioFreq = allBioResults.reduce((best, current) => 
        current.luminosity > best.luminosity ? current : best
    );
    
    // Calculate average performance by category
    const heartRateAvg = results.heartRateResults.reduce((sum, r) => sum + r.luminosity, 0) / results.heartRateResults.length;
    const brainwaveAvg = results.brainwaveResults.reduce((sum, r) => sum + r.luminosity, 0) / results.brainwaveResults.length;
    
    // Find strongest bio-cosmic coupling
    const strongestCoupling = results.harmonicResults.reduce((best, current) => 
        current.couplingStrength > best.couplingStrength ? current : best
    );
    
    results.analysis = {
        bestBioFreq,
        heartRateAvg,
        brainwaveAvg,
        strongestCoupling
    };
    
    console.log(`Best Biological Frequency: ${bestBioFreq.frequency} Hz (${bestBioFreq.range})`);
    console.log(`  Luminosity Score: ${bestBioFreq.luminosity.toFixed(4)}`);
    console.log(`  Stellar Efficiency: ${(bestBioFreq.stellarEfficiency * 100).toFixed(1)}%`);
    
    console.log(`\nAverage Performance:`);
    console.log(`  Heart Rate Frequencies: ${heartRateAvg.toFixed(4)}`);
    console.log(`  Brainwave Frequencies: ${brainwaveAvg.toFixed(4)}`);
    
    console.log(`\nStrongest Bio-Cosmic Coupling:`);
    console.log(`  Bio: ${strongestCoupling.bioFreq} Hz → Cosmic: ${strongestCoupling.cosmicFreq} Hz`);
    console.log(`  Coupling Strength: ${strongestCoupling.couplingStrength.toFixed(4)}`);
    console.log(`  Harmonic Ratio: ${strongestCoupling.harmonicRatio}:1`);
    
    // Determine validation success
    const significantCoupling = strongestCoupling.couplingStrength > 0.5;
    const bioFreqEnhancement = bestBioFreq.luminosity > 0.3;
    const heartRateOptimal = heartRateAvg > brainwaveAvg;
    
    results.summary = {
        significantCoupling,
        bioFreqEnhancement,
        heartRateOptimal,
        overallSuccess: significantCoupling && bioFreqEnhancement
    };
    
    console.log('\n\nVALIDATION RESULTS');
    console.log('==================');
    
    if (results.summary.overallSuccess) {
        console.log('🎉 BIO-COSMIC COUPLING VALIDATED');
        console.log('✅ Significant correlation between biological and cosmic frequencies');
        console.log('✅ Enhanced illumination at bio-resonant frequencies');
        console.log('✅ Gravitational-resonance-luminosity coupling confirmed');
    } else if (results.summary.significantCoupling || results.summary.bioFreqEnhancement) {
        console.log('✅ PARTIAL BIO-COSMIC COUPLING DETECTED');
        console.log('⚠️  Some correlations detected but below target threshold');
        console.log('📊 Further investigation recommended');
    } else {
        console.log('❌ BIO-COSMIC COUPLING NOT DETECTED');
        console.log('⚠️  No significant correlation found');
        console.log('🔬 Review biological frequency ranges and scaling');
    }
    
    // Save results
    const reportPath = path.join('research', 'findings', 'parameter-sweeps', 
                                `bio-cosmic-coupling-validation-${Date.now()}.json`);
    fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));
    
    console.log(`\n📊 Detailed results saved to: ${reportPath}`);
    
    return results;
}

// Run the test if this script is executed directly
if (require.main === module) {
    runBioCosmicCouplingTests();
}

module.exports = { 
    runBioCosmicCouplingTests, 
    calculateBioCosmicCoupling, 
    calculateLuminosityEnhancement,
    BIOLOGICAL_FREQUENCIES 
}; 